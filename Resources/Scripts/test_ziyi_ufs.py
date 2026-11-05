#!/usr/bin/env python3
"""Run native ziyi UFS open/TUR/ACTIVE code against a stateful SCSI model.

Host setup and descriptor services are modeled; actual ARM64 command builders,
sense decoding, error cleanup and readiness/power control flow execute unchanged.
This is not a UFS controller, DMA, media, or complete UEFI emulator.
"""
from pathlib import Path
import struct
import unittest

import pefile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn import arm64_const as reg

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / "Binaries/ziyi/QcomPkg/Drivers/UFSDxe/UFSDxe.patched.efi"
BASE = 0x100000
HANDLE = 0x300000
HBA = 0x310000
STACK = 0x400000
STOP = 0x500000


def fixed_sense(key, asc, ascq):
    data = bytearray(18)
    data[0], data[2], data[7], data[12], data[13] = 0x70, key, 10, asc, ascq
    return bytes(data)


class ScsiDevice:
    def __init__(self, *, active=False, attention=False, activation_error=False,
                 persistent_notready=False, sense=(2, 4, 2), sense_length=18,
                 transport_error=False):
        self.active = active
        self.attention = attention
        self.activation_error = activation_error
        self.persistent_notready = persistent_notready
        self.sense = sense
        self.sense_length = sense_length
        self.transport_error = transport_error
        self.ready_confirmed = False
        self.startstop_attempts = 0

    def command(self, cpu, packet, cdb):
        opcode = cdb[0]
        lun = cpu.mem_read(packet + 8, 1)[0]
        if opcode not in (0x00, 0x1B):
            raise AssertionError(f"Unexpected command in readiness path: {opcode:#x}")
        if opcode == 0x1B:
            self.startstop_attempts += 1
            if lun != 0xD0 or cdb[4] != 0x10:
                raise AssertionError("Activation is not Device-WLUN ACTIVE")
        cpu.mem_write(packet + 0x20, bytes(0x30))
        if self.transport_error:
            return -5
        if self.attention:
            self.attention = False
            return self.check_condition(cpu, packet, (6, 0x29, 0), 18)
        if opcode == 0x1B:
            if self.activation_error:
                return -5
            if not self.active:
                self.ready_confirmed = False
            self.active = True
            return 0
        if not self.active or self.persistent_notready:
            return self.check_condition(cpu, packet, self.sense, self.sense_length)
        self.ready_confirmed = True
        return 0

    @staticmethod
    def check_condition(cpu, packet, sense, length):
        cpu.mem_write(packet + 0x20, b"\x02" + struct.pack(">H", length))
        cpu.mem_write(packet + 0x23, fixed_sense(*sense))
        return -1000


def open_device(device, *, lun=0xD0, core=0, stale_sense=False):
    pe = pefile.PE(str(IMAGE))
    pe.relocate_image(BASE)
    cpu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    cpu.mem_map(BASE, (pe.OPTIONAL_HEADER.SizeOfImage + 0xFFF) & ~0xFFF)
    cpu.mem_write(BASE, pe.get_memory_mapped_image())
    for address, size in ((HANDLE, 0x1000), (HBA, 0x10000),
                          (STACK, 0x20000), (STOP, 0x1000)):
        cpu.mem_map(address, size)
    cpu.mem_write(HANDLE, struct.pack("<Q", HBA))
    cpu.mem_write(HANDLE + 8, b"\xf0")
    cpu.mem_write(HANDLE + 0xC, struct.pack("<I", 0x105189AB))
    if stale_sense:
        cpu.mem_write(HBA + 0x480, fixed_sense(2, 4, 2))
    caller_sp = STACK + 0x10000
    cpu.reg_write(reg.UC_ARM64_REG_SP, caller_sp)
    cpu.reg_write(reg.UC_ARM64_REG_LR, STOP)
    saved = {n: 0xCA0000 + n for n in range(19, 30)}
    for number, value in saved.items():
        cpu.reg_write(getattr(reg, f"UC_ARM64_REG_X{number}"), value)
    cpu.reg_write(reg.UC_ARM64_REG_X0, core)
    cpu.reg_write(reg.UC_ARM64_REG_X1, lun)

    def return_value(machine, value):
        machine.reg_write(reg.UC_ARM64_REG_X0, value & 0xFFFFFFFFFFFFFFFF)
        machine.reg_write(reg.UC_ARM64_REG_PC, machine.reg_read(reg.UC_ARM64_REG_LR))

    # Hardware setup and descriptor operations outside the readiness change.
    services = {0x9850, 0x98AC, 0xBB58, 0xB010, 0xB12C, 0xB560, 0xB854,
                0xB4CC, 0xB2B4, 0xB9D4, 0xC258, 0xC388, 0xBD30}

    def on_code(machine, address, size, _):
        rva = address - BASE
        if rva == 0xA2FC:
            return_value(machine, HANDLE)
        elif rva in services:
            if rva == 0xBB58 and not device.ready_confirmed:
                raise AssertionError("Device initialization proceeded without a successful TUR")
            return_value(machine, 0)
        elif rva == 0xD40C:
            packet = machine.reg_read(reg.UC_ARM64_REG_X0)
            cdb = bytes(machine.mem_read(machine.reg_read(reg.UC_ARM64_REG_X1), 16))
            if struct.unpack("<Q", machine.mem_read(packet, 8))[0] != HBA:
                raise AssertionError("Command used an invalid host context")
            result = device.command(machine, packet, cdb)
            return_value(machine, result & 0xFFFFFFFF)
        elif rva == 0x1681C:
            # Do not require Qualcomm's optional serial output service.
            return_value(machine, 0)

    cpu.hook_add(UC_HOOK_CODE, on_code)
    cpu.emu_start(BASE + 0x98E0, STOP, count=1000000)
    if cpu.reg_read(reg.UC_ARM64_REG_PC) != STOP:
        raise AssertionError("UFS open did not return within the instruction limit")
    if cpu.reg_read(reg.UC_ARM64_REG_SP) != caller_sp:
        raise AssertionError("UFS recovery corrupted SP")
    for number, value in saved.items():
        if cpu.reg_read(getattr(reg, f"UC_ARM64_REG_X{number}")) != value:
            raise AssertionError(f"UFS recovery corrupted callee-saved X{number}")
    if cpu.mem_read(HANDLE + 9, 1)[0] != core:
        raise AssertionError("Recovery flag overwrote the handle's controller index")
    result = cpu.reg_read(reg.UC_ARM64_REG_X0)
    if not result and cpu.mem_read(HANDLE + 8, 1)[0] != 0:
        raise AssertionError("Failed UFS open left a valid handle")
    return result


class UfsWakeTests(unittest.TestCase):
    def test_inactive_device_is_activated_and_rechecked_once(self):
        device = ScsiDevice()
        self.assertEqual(open_device(device), HANDLE)
        self.assertTrue(device.active)
        self.assertTrue(device.ready_confirmed)
        self.assertEqual(device.startstop_attempts, 1)

    def test_unit_attention_is_cleared_before_activation(self):
        device = ScsiDevice(attention=True)
        self.assertEqual(open_device(device, core=1), HANDLE)
        self.assertTrue(device.ready_confirmed)
        self.assertEqual(device.startstop_attempts, 1)

    def test_ready_device_retains_normal_activation(self):
        device = ScsiDevice(active=True)
        self.assertEqual(open_device(device), HANDLE)
        self.assertTrue(device.ready_confirmed)
        self.assertEqual(device.startstop_attempts, 1)

    def test_activation_or_post_activation_readiness_failure_is_not_hidden(self):
        for options in ({"activation_error": True}, {"persistent_notready": True}):
            with self.subTest(options=options):
                device = ScsiDevice(**options)
                self.assertEqual(open_device(device), 0)
                self.assertFalse(device.ready_confirmed)
                self.assertEqual(device.startstop_attempts, 1)

    def test_other_sense_or_stale_or_short_sense_does_not_activate(self):
        for options in ({"sense": (2, 4, 1)}, {"sense": (5, 0x20, 0)},
                        {"transport_error": True}, {"sense_length": 12}):
            with self.subTest(options=options):
                device = ScsiDevice(**options)
                self.assertEqual(open_device(device, stale_sense=True), 0)
                self.assertEqual(device.startstop_attempts, 0)

    def test_other_luns_keep_their_original_power_behavior(self):
        for lun in (0, 7, 0xB0, 0xC4):
            for active in (False, True):
                with self.subTest(lun=lun, active=active):
                    device = ScsiDevice(active=active)
                    self.assertEqual(open_device(device, lun=lun, core=1), HANDLE if active else 0)
                    self.assertEqual(device.startstop_attempts, 0)


if __name__ == "__main__":
    unittest.main()
