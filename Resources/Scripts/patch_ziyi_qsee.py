#!/usr/bin/env python3
"""Reuse a genuine resident Keymaster before loading its signed image.

Absent apps retain native loading, fallback, TZ error dumps and assertions.
Only the resident lookup adaptation is installed; no diagnostic output is added.
"""
import hashlib
from pathlib import Path
import struct
import subprocess
import tempfile

import pefile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Binaries/ziyi/QcomPkg/Drivers/TzDxe/TzDxeLA.efi"
STOCK_SHA256 = "7c7281b15b64a47ec9e112ee3a397fca8dc45d74714f51ebc81edc357c47bbd9"
RESIDENT_RVA = 0xE400


def build_helper():
    build = ROOT / "Build"
    build.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ziyi-qsee-", dir=build) as temporary:
        directory = Path(temporary)
        obj, elf, binary = (directory / name for name in ("resident.o", "resident.elf", "resident.bin"))
        linker = directory / "resident.ld"
        linker.write_text(
            f"SECTIONS {{ .text.resident {RESIDENT_RVA:#x} : {{ *(.text.resident) }} }}\n")
        subprocess.run(
            ["clang", "--target=aarch64-none-elf", "-c",
             str(Path(__file__).with_name("ziyi_keymaster_resident.S")), "-o", str(obj)],
            check=True,
        )
        subprocess.run(
            ["ld.lld", "-T", str(linker), "--entry=ZiyiKeymasterResident",
             "--defsym=QseeLookupApp=0x2d38",
             "--defsym=QseeData=0xf000", "--defsym=QseeGuidSetup=0x3064",
             "--defsym=QseeBootstrapReturn=0x3050",
             str(obj), "-o", str(elf)], check=True,
        )
        subprocess.run(
            ["llvm-objcopy", "-O", "binary", "--only-section=.text.resident",
             str(elf), str(binary)], check=True,
        )
        payload = binary.read_bytes()
        if not payload or RESIDENT_RVA + len(payload) > 0xF000:
            raise SystemExit("QSEE resident helper exceeds executable padding")
        return payload


def main():
    original = SOURCE.read_bytes()
    if hashlib.sha256(original).hexdigest() != STOCK_SHA256:
        raise SystemExit(f"Unsupported stock QSEE firmware: {SOURCE}")
    pe = pefile.PE(data=original)
    if pe.FILE_HEADER.Machine != 0xAA64:
        raise SystemExit("QSEE input is not an ARM64 PE image")
    resident_hook = pe.get_offset_from_rva(0x3060)
    if struct.unpack_from("<I", original, resident_hook)[0] != 0x90000061:
        raise SystemExit("Unexpected native Keymaster GUID setup")
    patched = bytearray(original)
    struct.pack_into("<I", patched, resident_hook,
                     0x14000000 | (((RESIDENT_RVA - 0x3060) // 4) & 0x03FFFFFF))
    payload = build_helper()
    section = pe.get_section_by_rva(RESIDENT_RVA)
    if (section is None or not section.Characteristics & 0x20000000
            or RESIDENT_RVA + len(payload) > section.VirtualAddress + min(
                section.Misc_VirtualSize, section.SizeOfRawData)):
        raise SystemExit("QSEE adaptation is outside executable data")
    offset = pe.get_offset_from_rva(RESIDENT_RVA)
    if any(original[offset:offset + len(payload)]):
        raise SystemExit("QSEE executable padding is occupied")
    patched[offset:offset + len(payload)] = payload
    output = SOURCE.with_suffix(".patched.efi")
    output.write_bytes(patched)
    print(f"{output.relative_to(ROOT)}: resident Keymaster reuse; "
          f"SHA256 {hashlib.sha256(patched).hexdigest()}")


if __name__ == "__main__":
    main()
