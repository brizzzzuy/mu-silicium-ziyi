#!/usr/bin/env python3
"""Execute native button polling/translation with modeled PMIC and log boundaries.

Not physical PMIC, button, menu or complete UEFI emulation.
"""
from pathlib import Path
import struct
import unittest

import pefile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn import arm64_const as r

ROOT = Path(__file__).resolve().parents[2]
DRIVER = ROOT / 'Binaries/ziyi/QcomPkg/Drivers/ButtonsDxe/ButtonsDxe'
BASE, ARENA, STACK, STOP = 0x100000, 0x300000, 0x400000, 0x500000
ERROR = 0x8000000000000007


class NativeButtons:
    def __init__(self, *, adapted=True, native_logging=False):
        pe = pefile.PE(str(DRIVER.with_suffix('.patched.efi' if adapted else '.efi')))
        pe.relocate_image(BASE)
        self.cpu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
        self.cpu.mem_map(BASE, 0xA000)
        self.cpu.mem_write(BASE, pe.get_memory_mapped_image())
        for address, size in ((ARENA, 0x10000), (STACK, 0x20000), (STOP, 0x1000)):
            self.cpu.mem_map(address, size)
        self.cpu.mem_write(BASE + 0x85B0, struct.pack('<Q', ARENA))
        self.cpu.mem_write(ARENA + 0x18, struct.pack('<Q', STOP + 0x100))
        self.status, self.value = 0, 0
        self.reads = 0
        self.messages = []
        self.native_logging = native_logging
        self.serial_rva = None
        self.cpu.hook_add(UC_HOOK_CODE, self.on_code)

    def string(self, pointer):
        return bytes(self.cpu.mem_read(pointer, 128)).split(b'\0', 1)[0].decode('ascii')

    def returned(self, value):
        for n in range(19):
            self.cpu.reg_write(getattr(r, f'UC_ARM64_REG_X{n}'), 0xEE0000 + n)
        self.cpu.reg_write(r.UC_ARM64_REG_X0, value)
        self.cpu.reg_write(r.UC_ARM64_REG_PC, self.cpu.reg_read(r.UC_ARM64_REG_LR))

    def on_code(self, cpu, address, size, _):
        if address == STOP + 0x100:
            if (cpu.reg_read(r.UC_ARM64_REG_X0), cpu.reg_read(r.UC_ARM64_REG_X1)) != (0, 0):
                raise AssertionError('Buttons changed PMIC device or power IRQ selector')
            self.reads += 1
            if not self.status & (1 << 63):
                cpu.mem_write(cpu.reg_read(r.UC_ARM64_REG_X2), bytes([self.value]))
            self.returned(self.status)
        elif address == BASE + 0x2074 and not self.native_logging:
            self.messages.append(self.string(cpu.reg_read(r.UC_ARM64_REG_X1)))
            self.returned(0)
        elif self.serial_rva is not None and address == BASE + self.serial_rva:
            pointer = cpu.reg_read(r.UC_ARM64_REG_X0)
            length = cpu.reg_read(r.UC_ARM64_REG_X1)
            self.messages.append(bytes(cpu.mem_read(pointer, length)).decode('ascii'))
            self.returned(length)

    def call(self, entry, args):
        saved = {n: 0xCA0000 + n for n in range(19, 30)}
        for n, value in saved.items():
            self.cpu.reg_write(getattr(r, f'UC_ARM64_REG_X{n}'), value)
        for n, value in enumerate(args):
            self.cpu.reg_write(getattr(r, f'UC_ARM64_REG_X{n}'), value)
        self.cpu.reg_write(r.UC_ARM64_REG_SP, STACK + 0x10000)
        self.cpu.reg_write(r.UC_ARM64_REG_LR, STOP)
        self.cpu.emu_start(BASE + entry, STOP, count=200000)
        if self.cpu.reg_read(r.UC_ARM64_REG_PC) != STOP:
            raise AssertionError('Native button function did not return')
        if self.cpu.reg_read(r.UC_ARM64_REG_SP) != STACK + 0x10000:
            raise AssertionError('Buttons corrupted SP')
        for n, value in saved.items():
            if self.cpu.reg_read(getattr(r, f'UC_ARM64_REG_X{n}')) != value:
                raise AssertionError(f'Buttons corrupted X{n}')
        return self.cpu.reg_read(r.UC_ARM64_REG_X0)

    def poll(self, value=0, status=0):
        self.value, self.status = value, status
        self.cpu.mem_write(ARENA + 0x200, b'\xaa')
        result = self.call(0x3DFC, (ARENA + 0x200,))
        return result, bytes(self.cpu.mem_read(ARENA + 0x200, 1))

    def translate(self, first, second, *, held=0):
        if len(first) != len(second):
            raise ValueError('Native caller supplies equally sized key arrays')
        self.cpu.mem_write(ARENA + 0x300, struct.pack('<' + 'I' * len(first), *first) or b'\0' * 4)
        self.cpu.mem_write(ARENA + 0x400, struct.pack('<' + 'I' * len(second), *second) or b'\0' * 4)
        self.cpu.mem_write(ARENA + 0x500, b'\xcc' * 32)
        result = self.call(0x3804, (ARENA + 0x300, held, ARENA + 0x400, 0,
                                   len(first), ARENA + 0x500, ARENA + 0x600))
        count = self.cpu.mem_read(ARENA + 0x600, 1)[0]
        return result, count, bytes(self.cpu.mem_read(ARENA + 0x500, count * 4))


class ButtonsTests(unittest.TestCase):
    def test_power_press_release_values_and_errors_remain_native(self):
        before, after = NativeButtons(adapted=False), NativeButtons()
        sequence = ((0, 0), (1, 0), (1, 0), (0, 0), (1, ERROR), (0, ERROR), (0, 0))
        for value, status in sequence:
            with self.subTest(value=value, status=status):
                self.assertEqual(after.poll(value, status), before.poll(value, status))
        self.assertEqual(after.reads, len(sequence))
        self.assertEqual(after.reads, before.reads)

    def test_volume_enter_empty_and_other_combinations_are_not_changed(self):
        for first, second in (([2], [2]), ([3], [3]), ([5], [5]),
                               ([5], [0]), ([0], [5]), ([], []), ([2, 3], [2, 3])):
            with self.subTest(first=first, second=second):
                before, after = NativeButtons(adapted=False), NativeButtons()
                self.assertEqual(after.translate(first, second), before.translate(first, second))
        result, count, data = NativeButtons().translate([5], [5])
        self.assertEqual((result, count, data), (0, 1, b'\0\0\r\0'))

    def test_held_key_suppression_and_release_rearming_are_not_changed(self):
        before, after = NativeButtons(adapted=False), NativeButtons()
        for held in (1, 1, 0, 1, 0):
            self.assertEqual(after.translate([5], [5], held=held),
                             before.translate([5], [5], held=held))

    def test_physical_power_event_becomes_enter_not_platform_scan_102(self):
        stock = NativeButtons(adapted=False)
        self.assertEqual(stock.translate([1], [0]),
                         (0, 1, b'\x02\x01\0\0'))
        self.assertEqual(NativeButtons().translate([1], [0]),
                         (0, 1, b'\0\0\r\0'))

    def test_power_hold_does_not_repeat_and_release_rearms_enter(self):
        device = NativeButtons()
        self.assertEqual(device.translate([1], [0], held=1),
                         (0, 1, b'\0\0\r\0'))
        self.assertEqual(device.translate([1], [0], held=1)[1:], (0, b''))
        self.assertEqual(device.translate([0], [1], held=0)[1:], (0, b''))
        self.assertEqual(device.translate([1], [0], held=1),
                         (0, 1, b'\0\0\r\0'))

    def test_normal_power_and_keys_do_not_emit_added_logs(self):
        device = NativeButtons()
        for value in (0, 1, 1, 0):
            device.poll(value)
        device.translate([2], [2])
        device.translate([3], [3])
        device.translate([1], [0])
        self.assertEqual(device.messages, [])


if __name__ == '__main__':
    unittest.main()
