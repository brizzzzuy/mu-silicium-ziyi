#!/usr/bin/env python3
"""Exercise the actual ADC refusal and PMIC status paths in ARM64.

Requires pefile and unicorn. No physical PMIC or complete UEFI is emulated.
"""
from pathlib import Path
import struct
import unittest

import pefile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn import arm64_const as reg

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / "Binaries/ziyi/QcomPkg/Drivers/PmicDxe/PmicDxeLa.patched.efi"
BASE = 0x100000
STACK = 0x300000
STOP = 0x400000
EFI_UNSUPPORTED = 0x8000000000000003
EFI_DEVICE_ERROR = 0x8000000000000007


def execute_adc_path(pending_pmic_error=None):
    pe = pefile.PE(str(IMAGE))
    cpu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    cpu.mem_map(BASE, (pe.OPTIONAL_HEADER.SizeOfImage + 0xFFF) & ~0xFFF)
    cpu.mem_write(BASE, pe.get_memory_mapped_image())
    cpu.mem_map(STACK, 0x10000)
    cpu.mem_map(STOP, 0x1000)
    caller_sp = STACK + 0x8000
    saved = {n: 0xCA0000 + n for n in range(19, 30)}
    for number, value in saved.items():
        cpu.reg_write(getattr(reg, f"UC_ARM64_REG_X{number}"), value)
    cpu.reg_write(reg.UC_ARM64_REG_X0, 0x12345678)
    cpu.reg_write(reg.UC_ARM64_REG_LR, STOP)

    if pending_pmic_error is None:
        start = 0x4068
        cpu.reg_write(reg.UC_ARM64_REG_SP, caller_sp)
    else:
        # Reconstruct the existing PMIC entry frame at the optional-ADC call.
        # All earlier initialization has already accumulated its status in W21.
        start = 0x1698
        frame = caller_sp - 0x30
        cpu.mem_write(frame, struct.pack("<QQ", saved[29], STOP))
        cpu.mem_write(frame + 0x10, struct.pack("<Q", saved[21]))
        cpu.mem_write(frame + 0x20, struct.pack("<QQ", saved[20], saved[19]))
        cpu.reg_write(reg.UC_ARM64_REG_SP, frame)
        cpu.reg_write(reg.UC_ARM64_REG_FP, frame)
        cpu.reg_write(reg.UC_ARM64_REG_X21, pending_pmic_error)

    def on_code(machine, address, size, _):
        if address == BASE + 0x1C52C:
            raise AssertionError("Disabled ADC attempted DAL attachment")
        if address == BASE + 0x4098:
            raise AssertionError("Disabled ADC entered protocol installation")
        if address == BASE + 0x4990:
            # The original optional-failure logger may clobber caller registers.
            link = machine.reg_read(reg.UC_ARM64_REG_LR)
            for number in range(18):
                machine.reg_write(getattr(reg, f"UC_ARM64_REG_X{number}"), 0xBAD000 + number)
            machine.reg_write(reg.UC_ARM64_REG_NZCV, 0xF0000000)
            machine.reg_write(reg.UC_ARM64_REG_PC, link)

    cpu.hook_add(UC_HOOK_CODE, on_code)
    cpu.emu_start(BASE + start, STOP, count=1000)
    if cpu.reg_read(reg.UC_ARM64_REG_PC) != STOP:
        raise AssertionError("ADC/PMIC path did not return within the instruction limit")
    if cpu.reg_read(reg.UC_ARM64_REG_SP) != caller_sp:
        raise AssertionError("ADC refusal corrupted the caller stack")
    for number, value in saved.items():
        if cpu.reg_read(getattr(reg, f"UC_ARM64_REG_X{number}")) != value:
            raise AssertionError(f"ADC refusal corrupted callee-saved X{number}")
    return cpu.reg_read(reg.UC_ARM64_REG_X0)


class PmicAdcTests(unittest.TestCase):
    def test_adc_reports_unsupported_without_installing_protocol(self):
        self.assertEqual(execute_adc_path(), EFI_UNSUPPORTED)

    def test_optional_adc_failure_preserves_pmic_status(self):
        for pending, expected in ((0, 0), (0x40, EFI_DEVICE_ERROR)):
            with self.subTest(pending_pmic_error=pending):
                self.assertEqual(execute_adc_path(pending), expected)


if __name__ == "__main__":
    unittest.main()
