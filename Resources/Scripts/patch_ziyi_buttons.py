#!/usr/bin/env python3
"""Map the observed power-key 0x102 path to native Enter."""
import hashlib
from pathlib import Path
import struct

import pefile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'Binaries/ziyi/QcomPkg/Drivers/ButtonsDxe/ButtonsDxe.efi'
STOCK_SHA256 = '7aade0b3b2b874b41dffbba5770e3212abd0497a5ae6abfaebb3709aa9b2f86a'


def checked_offset(pe, rva, size, permission):
    section = pe.get_section_by_rva(rva)
    if (section is None or not section.Characteristics & permission
            or rva + size > section.VirtualAddress + min(
                section.Misc_VirtualSize, section.SizeOfRawData)):
        raise SystemExit(f'Buttons patch has invalid section bounds/permissions at {rva:#x}')
    return pe.get_offset_from_rva(rva)


def main():
    original = SOURCE.read_bytes()
    if hashlib.sha256(original).hexdigest() != STOCK_SHA256:
        raise SystemExit(f'Unsupported stock ButtonsDxe: {SOURCE}')
    pe = pefile.PE(data=original)
    if pe.FILE_HEADER.Machine != 0xAA64:
        raise SystemExit('ButtonsDxe is not ARM64')
    power = checked_offset(pe, 0x39FC, 8, 0x20000000)
    if original[power:power + 8] != struct.pack('<2I', 0x52802048, 0x17FFFFDB):
        raise SystemExit('Unexpected native power-key conversion')
    patched = bytearray(original)
    # Only the power branch: reuse native Unicode-CR generation at 0x39D0.
    # The native translator has already zeroed the EFI_INPUT_KEY at FP+0x18.
    struct.pack_into('<I', patched, power + 4, 0x17FFFFF4)
    output = SOURCE.with_suffix('.patched.efi')
    output.write_bytes(patched)
    print(f'{output.relative_to(ROOT)}: power-to-Enter; SHA256 {hashlib.sha256(patched).hexdigest()}')


if __name__ == '__main__':
    main()
