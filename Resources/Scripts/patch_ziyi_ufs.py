#!/usr/bin/env python3
"""Wake the exact stock ziyi UFS device only on fresh NOT READY / 04 / 02.

Preserve the initial TUR/Unit Attention handling, actual activation/readiness
results, other LUN paths, and the native failure cleanup and assertions.
"""
import hashlib
from pathlib import Path
import struct
import subprocess
import tempfile

import pefile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Binaries/ziyi/QcomPkg/Drivers/UFSDxe/UFSDxe.efi"
STOCK_SHA256 = "e0da9774d815bb2ce22e7de41aa3ec34046c0c7e996ef298fbdd9468eb0e1b61"
WAKE_RVA = 0x1BE00
LATE_RVA = 0x1BFC0


def build_helpers():
    build = ROOT / "Build"
    build.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ziyi-ufs-", dir=build) as temporary:
        directory = Path(temporary)
        obj = directory / "wake.o"
        elf = directory / "wake.elf"
        linker = directory / "wake.ld"
        linker.write_text(
            "SECTIONS {\n"
            f" .text.wake {WAKE_RVA:#x} : {{ *(.text.wake) }}\n"
            f" .text.late {LATE_RVA:#x} : {{ *(.text.late) }}\n"
            "}\n"
        )
        subprocess.run(
            ["clang", "--target=aarch64-none-elf", "-c",
             str(Path(__file__).with_name("ziyi_ufs_wake.S")), "-o", str(obj)],
            check=True,
        )
        subprocess.run(
            ["ld.lld", "-T", str(linker), "--entry=ZiyiUfsWake",
             "--defsym=UfsTur=0xadc8", "--defsym=UfsActive=0xaefc",
             "--defsym=UfsReadyResult=0x996c", "--defsym=UfsAfterActive=0x99a0",
             "--defsym=UfsOriginalActive=0x9990", str(obj), "-o", str(elf)],
            check=True,
        )
        helpers = []
        for name, rva, limit in (("wake", WAKE_RVA, LATE_RVA),
                                 ("late", LATE_RVA, 0x1C000)):
            binary = directory / f"{name}.bin"
            subprocess.run(
                ["llvm-objcopy", "-O", "binary", f"--only-section=.text.{name}",
                 str(elf), str(binary)], check=True,
            )
            payload = binary.read_bytes()
            if not payload or rva + len(payload) > limit:
                raise SystemExit(f"UFS {name} helper exceeds reserved padding")
            helpers.append((rva, payload))
        return helpers


def executable_offset(pe, rva, length):
    section = pe.get_section_by_rva(rva)
    if (section is None or not section.Characteristics & 0x20000000
            or rva + length > section.VirtualAddress + min(
                section.Misc_VirtualSize, section.SizeOfRawData)):
        raise SystemExit(f"UFS patch is outside executable data at {rva:#x}")
    return pe.get_offset_from_rva(rva)


def main():
    original = SOURCE.read_bytes()
    if hashlib.sha256(original).hexdigest() != STOCK_SHA256:
        raise SystemExit(f"Unsupported stock UFS firmware: {SOURCE}")
    pe = pefile.PE(data=original)
    if pe.FILE_HEADER.Machine != 0xAA64:
        raise SystemExit("UFS input is not an ARM64 PE image")
    patched = bytearray(original)
    for rva, expected, destination in (
            (0x9968, 0x94000518, WAKE_RVA),
            (0x9988, 0x7103429F, LATE_RVA)):
        offset = executable_offset(pe, rva, 4)
        if struct.unpack_from("<I", original, offset)[0] != expected:
            raise SystemExit(f"Unexpected UFS instruction at {rva:#x}")
        branch = 0x14000000 | (((destination - rva) // 4) & 0x03FFFFFF)
        struct.pack_into("<I", patched, offset, branch)
    for rva, payload in build_helpers():
        offset = executable_offset(pe, rva, len(payload))
        if any(original[offset:offset + len(payload)]):
            raise SystemExit(f"UFS executable padding is occupied at {rva:#x}")
        patched[offset:offset + len(payload)] = payload
    output = SOURCE.with_suffix(".patched.efi")
    output.write_bytes(patched)
    print(f"{output.relative_to(ROOT)}: conditional ACTIVE recovery; "
          f"SHA256 {hashlib.sha256(patched).hexdigest()}")


if __name__ == "__main__":
    main()
