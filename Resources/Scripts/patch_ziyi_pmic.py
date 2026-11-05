#!/usr/bin/env python3
"""Adapt the hash-pinned ziyi PMIC/SPMI drivers to post-ABL UEFI re-entry.

Preserve inherited hardware configuration and enforce cached SPMI write ownership
before accessing a write window. Observer reads and owned transactions retain
their original implementations; denied writes use the driver's native error path.
Optional ADC initialization is explicitly unsupported in this diagnostic build;
the native failure path returns EFI_UNSUPPORTED without installing its protocol.
This is not suitable for initializing PMIC hardware from reset.
"""

import hashlib
from pathlib import Path
import struct
import subprocess
import tempfile

import pefile


ROOT = Path(__file__).resolve().parents[2]
DRIVERS = ROOT / "Binaries/ziyi/QcomPkg/Drivers"
# File, exact original SHA-256, branch site RVA, original instruction, resume RVA.
PATCHES = (
    (
        "SPMIDxe/SPMIDxe.efi",
        "689d7f723b77a5a12c439b28f4548c7eaa66afa76a866e4b1e3d626798c0767c",
        0x2618,
        0x340001C9,  # CBZ W9, 0x2650: condition guarding the PIC setup loop.
        0x2650,
    ),
    (
        "PmicDxe/PmicDxeLa.efi",
        "e5c15b1ce7fcc51c464a84e9c7902ff3c558b4cb3ba47e29ea740b40c4262875",
        0x163C,
        0x9400460D,  # BL 0x12E70: post-init hardware reset/configuration.
        0x1644,      # Resume after this omitted pass's status accumulation.
    ),
)

GUARD_RVA = 0x7D00
GUARD_SITE = 0x3684


def build_write_guard():
    build = ROOT / "Build"
    build.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ziyi-spmi-", dir=build) as temporary:
        directory = Path(temporary)
        obj = directory / "guard.o"
        elf = directory / "guard.elf"
        binary = directory / "guard.bin"
        subprocess.run(
            ["clang", "--target=aarch64-none-elf", "-c",
             str(Path(__file__).with_name("ziyi_spmi_guard.S")), "-o", str(obj)],
            check=True,
        )
        subprocess.run(
            ["ld.lld", f"-Ttext={GUARD_RVA:#x}", "--entry=ziyi_spmi_write_guard",
             "--defsym=SpmiDenied=0x39f4",
             "--defsym=SpmiResume=0x3688", str(obj), "-o", str(elf)],
            check=True,
        )
        subprocess.run(
            ["llvm-objcopy", "-O", "binary", "--only-section=.text",
             str(elf), str(binary)],
            check=True,
        )
        return binary.read_bytes()


def add_write_guard(original, patched, pe, guard):
    section = pe.get_section_by_rva(GUARD_RVA)
    if (section is None or not section.Characteristics & 0x20000000
            or not guard or GUARD_RVA + len(guard) > 0x8000):
        raise SystemExit("SPMI write guard does not fit executable padding")
    offset = pe.get_offset_from_rva(GUARD_RVA)
    if any(original[offset:offset + len(guard)]):
        raise SystemExit("SPMI write guard padding is not empty")
    site = pe.get_offset_from_rva(GUARD_SITE)
    if struct.unpack_from("<I", original, site)[0] != 0x79408AE9:
        raise SystemExit("Unexpected SPMI ownership guard insertion site")
    patched[offset:offset + len(guard)] = guard
    branch = 0x14000000 | (((GUARD_RVA - GUARD_SITE) // 4) & 0x03FFFFFF)
    struct.pack_into("<I", patched, site, branch)


def main():
    planned = []
    for relative, expected_hash, site_rva, expected_instruction, resume_rva in PATCHES:
        source = DRIVERS / relative
        original = source.read_bytes()
        if hashlib.sha256(original).hexdigest() != expected_hash:
            raise SystemExit(f"Unsupported stock firmware: {source}")

        pe = pefile.PE(data=original)
        if pe.FILE_HEADER.Machine != 0xAA64:
            raise SystemExit(f"Not an ARM64 PE image: {source}")
        section = pe.get_section_by_rva(site_rva)
        if section is None or not section.Characteristics & 0x20000000:
            raise SystemExit(f"Startup branch is not executable: {source}")
        offset = pe.get_offset_from_rva(site_rva)
        instruction = struct.unpack_from("<I", original, offset)[0]
        if instruction != expected_instruction:
            raise SystemExit(f"Unexpected startup branch at {site_rva:#x}: {source}")

        patched = bytearray(original)
        # Omit only this post-ABL configuration pass, without faking a read,
        # clearing existing errors, or replacing the underlying implementation.
        # B resumes at the same continuation with the prior status intact.
        branch = 0x14000000 | (((resume_rva - site_rva) // 4) & 0x03FFFFFF)
        struct.pack_into("<I", patched, offset, branch)
        if relative.startswith("SPMIDxe/"):
            add_write_guard(original, patched, pe, build_write_guard())
        elif relative.startswith("PmicDxe/"):
            # User-approved diagnostic limitation: do not attach the ADC DAL
            # device. Follow the existing unsupported path, not a success stub.
            adc_offset = pe.get_offset_from_rva(0x4088)
            if struct.unpack_from("<I", original, adc_offset)[0] != 0x94006129:
                raise SystemExit("Unexpected PMIC ADC attach instruction")
            struct.pack_into("<I", patched, adc_offset, 0x14000002)  # B 0x4090.
        output = source.with_suffix(".patched.efi")
        planned.append((output, patched, site_rva))

    # Validate both original images before producing the paired outputs.
    for output, patched, site_rva in planned:
        output.write_bytes(patched)
        print(f"{output.relative_to(ROOT)}: startup branch {site_rva:#x}; "
              f"SHA256 {hashlib.sha256(patched).hexdigest()}")
        if site_rva == 0x2618:
            print(f"  write ownership guard at {GUARD_SITE:#x} -> {GUARD_RVA:#x}")
        else:
            print("  ADC unavailable: native EFI_UNSUPPORTED path; no ADC protocol")


if __name__ == "__main__":
    main()
