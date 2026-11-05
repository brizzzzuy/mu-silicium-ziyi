#!/usr/bin/env python3
"""Execute the actual QSEE start wrapper; model only firmware service boundaries.

Proves failed starts retain failure and successful starts retain real handles.
Not a TrustZone, image-authentication, storage or full UEFI emulator.
"""
from pathlib import Path
import struct
import unittest

import pefile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn import arm64_const as reg

ROOT = Path(__file__).resolve().parents[2]
DRIVER = ROOT / "Binaries/ziyi/QcomPkg/Drivers/TzDxe/TzDxeLA"
BASE, ARENA, STACK, STOP = 0x100000, 0x300000, 0x400000, 0x500000
REQUEST, PROTOCOL, BUFFER, SCM = ARENA + 0x1000, ARENA + 0x2000, ARENA + 0x3000, STOP + 0x100


def run_start(*, adapted, status, app_id=23):
    pe = pefile.PE(str(DRIVER.with_suffix(".patched.efi" if adapted else ".efi")))
    pe.relocate_image(BASE)
    cpu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    cpu.mem_map(BASE, (pe.OPTIONAL_HEADER.SizeOfImage + 0xFFF) & ~0xFFF)
    cpu.mem_write(BASE, pe.get_memory_mapped_image())
    for address, size in ((ARENA, 0x10000), (STACK, 0x20000), (STOP, 0x1000)):
        cpu.mem_map(address, size)
    cpu.mem_write(BASE + 0xF428, struct.pack("<Q", PROTOCOL))
    cpu.mem_write(PROTOCOL + 0x28, struct.pack("<Q", SCM))
    cpu.mem_write(BUFFER, b"\x7fELF")
    caller_sp = STACK + 0x10000
    cpu.reg_write(reg.UC_ARM64_REG_SP, caller_sp)
    cpu.reg_write(reg.UC_ARM64_REG_LR, STOP)
    saved = {number: 0xCA0000 + number for number in range(19, 30)}
    for number, value in saved.items():
        cpu.reg_write(getattr(reg, f"UC_ARM64_REG_X{number}"), value)
    for number, value in enumerate((0, 0x80000, BUFFER, BASE + 0xB593)):
        cpu.reg_write(getattr(reg, f"UC_ARM64_REG_X{number}"), value)
    events = []


    def return_value(machine, value, *, clobber=False):
        if clobber:
            for number in range(19):
                machine.reg_write(getattr(reg, f"UC_ARM64_REG_X{number}"), 0xEE0000 + number)
        machine.reg_write(reg.UC_ARM64_REG_X0, value)
        machine.reg_write(reg.UC_ARM64_REG_PC, machine.reg_read(reg.UC_ARM64_REG_LR))

    def on_code(machine, address, size, _):
        rva = address - BASE
        if rva == 0x4EF0:
            return_value(machine, REQUEST)
        elif rva == 0x50A8:
            if machine.reg_read(reg.UC_ARM64_REG_X0) != REQUEST:
                raise AssertionError("QSEE request cleanup lost its allocation")
            events.append("free")
            return_value(machine, 0, clobber=True)
        elif address == SCM:
            command = machine.reg_read(reg.UC_ARM64_REG_X1)
            output = machine.reg_read(reg.UC_ARM64_REG_X2)
            if command == 1:
                events.append("start")
                machine.mem_write(output, struct.pack("<I", app_id))
                return_value(machine, status, clobber=True)
            else:
                raise AssertionError(f"Unexpected SCM command: {command}")
        elif rva == 0x3454:
            events.append("tz-log")
            return_value(machine, 0, clobber=True)
        elif rva == 0x5114:
            events.append("debug")
            return_value(machine, 0, clobber=True)

    cpu.hook_add(UC_HOOK_CODE, on_code)
    cpu.emu_start(BASE + 0x1D08, STOP, count=100000)
    if cpu.reg_read(reg.UC_ARM64_REG_PC) != STOP:
        raise AssertionError("QSEE start wrapper did not return")
    if cpu.reg_read(reg.UC_ARM64_REG_SP) != caller_sp:
        raise AssertionError("QSEE start wrapper corrupted SP")
    for number, value in saved.items():
        if cpu.reg_read(getattr(reg, f"UC_ARM64_REG_X{number}")) != value:
            raise AssertionError(f"QSEE start wrapper corrupted callee-saved X{number}")
    if events.count("start") != 1 or events.count("free") != 1:
        raise AssertionError("Start wrapper repeated startup or changed request cleanup")
    return cpu.reg_read(reg.UC_ARM64_REG_X0), events


class QseeStartTests(unittest.TestCase):
    def test_failed_start_stays_failed(self):
        for status in (1, 0x8000000000000003, 0x8000000000000007):
            with self.subTest(status=status):
                before, _ = run_start(adapted=False, status=status)
                after, _ = run_start(adapted=True, status=status)
                self.assertEqual(before, 0)
                self.assertEqual(after, before)

    def test_success_retains_real_handle_without_extra_calls_or_output(self):
        for adapted in (False, True):
            handle, events = run_start(adapted=adapted, status=0)
            self.assertEqual(handle, 23)
            self.assertEqual(events, ["start", "free"])



if __name__ == "__main__":
    unittest.main()
