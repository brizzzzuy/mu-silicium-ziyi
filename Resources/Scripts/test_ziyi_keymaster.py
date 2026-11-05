#!/usr/bin/env python3
"""Execute native Keymaster bootstrap and lookup; model external UEFI/SCM services.

Not a TrustZone authentication or device emulator. Genuine lookup responses and
image-load failures are supplied at service boundaries, never inside the helper.
"""
from pathlib import Path
import struct
import unittest

import pefile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn import arm64_const as reg

ROOT = Path(__file__).resolve().parents[2]
DRIVER = ROOT / 'Binaries/ziyi/QcomPkg/Drivers/TzDxe/TzDxeLA'
BASE, ARENA, STACK, STOP = 0x100000, 0x300000, 0x400000, 0x500000
ERROR = 0x8000000000000007


def bootstrap(residents, *, adapted=True, lookup_status=0, flags=0xC4, load_status=ERROR,
              native_logging=False):
    pe = pefile.PE(str(DRIVER.with_suffix('.patched.efi' if adapted else '.efi')))
    pe.relocate_image(BASE)
    cpu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    cpu.mem_map(BASE, 0x11000)
    cpu.mem_write(BASE, pe.get_memory_mapped_image())
    for address, size in ((ARENA, 0x10000), (STACK, 0x20000), (STOP, 0x1000)):
        cpu.mem_map(address, size)
    cpu.mem_write(BASE + 0xF428, struct.pack('<Q', ARENA))
    cpu.mem_write(ARENA + 0x28, struct.pack('<Q', STOP + 0x100))
    caller_sp = STACK + 0x10000
    cpu.reg_write(reg.UC_ARM64_REG_SP, caller_sp)
    cpu.reg_write(reg.UC_ARM64_REG_LR, STOP)
    saved = {n: 0xCA0000 + n for n in range(19, 30)}
    for n, value in saved.items():
        cpu.reg_write(getattr(reg, f'UC_ARM64_REG_X{n}'), value)
    cpu.reg_write(reg.UC_ARM64_REG_X0, ARENA + 0x100)
    state = {'loads': 0, 'fallbacks': 0, 'asserted': False, 'ids': [], 'messages': []}

    def returned(value):
        for n in range(19):
            cpu.reg_write(getattr(reg, f'UC_ARM64_REG_X{n}'), 0xEE0000 + n)
        cpu.reg_write(reg.UC_ARM64_REG_X0, value)
        cpu.reg_write(reg.UC_ARM64_REG_PC, cpu.reg_read(reg.UC_ARM64_REG_LR))

    def hook(machine, address, size, _):
        rva = address - BASE
        if rva == 0x1C48:
            cpu.mem_write(cpu.reg_read(reg.UC_ARM64_REG_X1), struct.pack('<I', 0x400000))
            returned(0)
        elif rva == 0x33CC:
            cpu.mem_write(cpu.reg_read(reg.UC_ARM64_REG_X1), struct.pack('<I', flags))
            returned(0)
        elif address == STOP + 0x100:
            if cpu.reg_read(reg.UC_ARM64_REG_X1) != 3:
                raise AssertionError('Resident path issued a non-lookup SCM command')
            pointer = cpu.reg_read(reg.UC_ARM64_REG_X3)
            name = bytes(cpu.mem_read(pointer, 32)).split(b'\0', 1)[0].decode('ascii')
            app_id = residents.get(name, 0)
            state['ids'].append(app_id)
            cpu.mem_write(cpu.reg_read(reg.UC_ARM64_REG_X2), struct.pack('<I', app_id))
            returned(lookup_status)
        elif rva == 0x2414:
            state['loads'] += 1
            cpu.mem_write(cpu.reg_read(reg.UC_ARM64_REG_X4), struct.pack('<I', 55))
            returned(load_status)
        elif rva == 0x2058:
            state['fallbacks'] += 1
            returned(0x800000000000000E)
        elif rva == 0x5114 and not native_logging:
            pointer = cpu.reg_read(reg.UC_ARM64_REG_X1)
            state['messages'].append(bytes(cpu.mem_read(pointer, 96)).split(b'\0', 1)[0].decode('ascii'))
            returned(0)
        elif rva == 0x5214:
            state['asserted'] = True
            cpu.emu_stop()
        elif rva == 0xADB4:
            pointer = cpu.reg_read(reg.UC_ARM64_REG_X0)
            length = cpu.reg_read(reg.UC_ARM64_REG_X1)
            state['messages'].append(bytes(cpu.mem_read(pointer, length)).decode('ascii'))
            returned(length)

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start(BASE + 0x2FB0, STOP, count=100000)
    if not state['asserted']:
        if cpu.reg_read(reg.UC_ARM64_REG_PC) != STOP:
            raise AssertionError('Bootstrap did not return')
        if cpu.reg_read(reg.UC_ARM64_REG_SP) != caller_sp:
            raise AssertionError('Bootstrap corrupted SP')
        for n, value in saved.items():
            if cpu.reg_read(getattr(reg, f'UC_ARM64_REG_X{n}')) != value:
                raise AssertionError(f'Bootstrap corrupted X{n}')
    state['status'] = cpu.reg_read(reg.UC_ARM64_REG_X0)
    return state


class KeymasterResidentTests(unittest.TestCase):
    def test_existing_app_avoids_duplicate_load_and_preserves_abi(self):
        before = bootstrap({'keymaster64': 1}, adapted=False)
        self.assertTrue(before['asserted'])
        for resident in ({'keymaster64': 1}, {'keymaster': 17}):
            with self.subTest(resident=resident):
                after = bootstrap(resident)
                self.assertFalse(after['asserted'])
                self.assertEqual(after['status'], 0)
                self.assertEqual(after['loads'], 0)
                self.assertEqual(after['fallbacks'], 0)
                self.assertEqual(after['messages'], [])

    def test_absence_lookup_errors_and_invalid_ids_keep_real_load_failure(self):
        for residents, status in (({}, 0), ({'keymaster64': 1}, ERROR),
                                  ({'keymaster64': 0xFFFFFFFF, 'keymaster': 0xFFFFFFFF}, 0)):
            with self.subTest(residents=residents, status=status):
                result = bootstrap(residents, lookup_status=status)
                self.assertTrue(result['asserted'])
                self.assertEqual(result['loads'], 1)
                self.assertEqual(result['fallbacks'], 1)

    def test_absent_app_can_still_be_loaded_by_native_path(self):
        result = bootstrap({}, load_status=0)
        self.assertFalse(result['asserted'])
        self.assertEqual(result['status'], 0)
        self.assertEqual(result['loads'], 1)
        self.assertEqual(result['fallbacks'], 0)

    def test_security_policy_gate_is_preserved(self):
        result = bootstrap({'keymaster64': 1}, flags=0x44)
        self.assertFalse(result['asserted'])
        self.assertEqual(result['status'], 0)
        self.assertEqual(result['ids'], [])
        self.assertEqual(result['loads'], 0)


if __name__ == '__main__':
    unittest.main()
