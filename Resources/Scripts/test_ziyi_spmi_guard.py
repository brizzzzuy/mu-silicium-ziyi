#!/usr/bin/env python3
"""Execute the real SPMI transaction code against an isolated arbiter model.

Requires pefile and unicorn. This verifies machine-code behavior, not phone I/O.
"""
from pathlib import Path
import struct
import unittest

import pefile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn import arm64_const as reg

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / "Binaries/ziyi/QcomPkg/Drivers/SPMIDxe/SPMIDxe.patched.efi"
BASE = 0x100000
CONTEXT = 0x200000
CACHE = 0x210000
BUFFER = 0x220000
COUNT = BUFFER + 0x100
STACK = 0x300000
STOP = 0x400000
ARBITER = 0x0C400000


def transaction(image, opcode, apid, owner, ee=0, base_apid=0,
                bus_id=0, channel_limit=1024):
    pe = pefile.PE(str(image))
    cpu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    cpu.mem_map(BASE, 0x10000)
    cpu.mem_write(BASE, pe.get_memory_mapped_image())
    for start, size in ((CONTEXT, 0x1000), (CACHE, 0x2000),
                        (BUFFER, 0x1000), (STACK, 0x10000), (STOP, 0x1000),
                        (ARBITER, 0x500000)):
        cpu.mem_map(start, size)
    cpu.mem_write(CONTEXT, struct.pack("<Q", ARBITER))
    cpu.mem_write(CONTEXT + 0x10, bytes([bus_id]))
    cpu.mem_write(CONTEXT + 0x30, struct.pack("<Q", CACHE + 0x1F00))
    cpu.mem_write(CACHE + 0x1F00, struct.pack("<H", channel_limit))
    cpu.mem_write(CONTEXT + 0x20, struct.pack("<Q", CACHE))
    cpu.mem_write(CONTEXT + 0x44, struct.pack("<H", base_apid))
    cpu.mem_write(CACHE + 6 * apid + 1, bytes([owner]))
    cpu.mem_write(BUFFER, b"\xa5")
    cpu.mem_write(COUNT, struct.pack("<I", 0xFFFFFFFF))
    absolute_apid = base_apid + apid
    observer = ARBITER + 0x40000 + ee * 0x8000 + absolute_apid * 0x20
    writer = ARBITER + 0x100000 + absolute_apid * 0x1000
    for channel in (observer, writer):
        cpu.mem_write(channel + 8, struct.pack("<I", 1))  # Model: DONE.
    cpu.mem_write(observer + 0x18, struct.pack("<I", 0x5A))
    original_sp = STACK + 0x8000
    cpu.mem_write(original_sp, struct.pack("<Q", COUNT))
    for number, value in enumerate((CONTEXT, opcode, 0, ee, apid, 0x46, BUFFER, 1)):
        cpu.reg_write(getattr(reg, f"UC_ARM64_REG_X{number}"), value)
    saved = {getattr(reg, f"UC_ARM64_REG_X{n}"): 0xA000 + n for n in range(19, 30)}
    for register, value in saved.items():
        cpu.reg_write(register, value)
    cpu.reg_write(reg.UC_ARM64_REG_SP, original_sp)
    cpu.reg_write(reg.UC_ARM64_REG_LR, STOP)
    accesses = []
    log_calls = 0
    stopped = False

    def on_memory(machine, access, address, size, value, _):
        accesses.append((access, address, size, value))

    def on_code(machine, address, size, _):
        nonlocal stopped, log_calls
        if address == STOP:
            stopped = True
            machine.emu_stop()
        elif address == BASE + 0x3B9C:
            # No wall-clock delay in the isolated model; status is already DONE.
            machine.reg_write(reg.UC_ARM64_REG_PC, machine.reg_read(reg.UC_ARM64_REG_LR))
        elif address == BASE + 0x17C0:
            log_calls += 1
            link = machine.reg_read(reg.UC_ARM64_REG_LR)
            # Native error logging may clobber X0-X17 and condition flags.
            for n in range(18):
                machine.reg_write(getattr(reg, f"UC_ARM64_REG_X{n}"), 0xBAD000 + n)
            machine.reg_write(reg.UC_ARM64_REG_NZCV, 0xF0000000)
            machine.reg_write(reg.UC_ARM64_REG_PC, link)

    cpu.hook_add(UC_HOOK_CODE, on_code)
    cpu.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, on_memory,
                 begin=ARBITER, end=ARBITER + 0x4FFFFF)
    cpu.emu_start(BASE + 0x3634, STOP + 4, count=10000)
    if not stopped:
        raise AssertionError("Transaction did not return within the instruction limit")
    if cpu.reg_read(reg.UC_ARM64_REG_SP) != original_sp:
        raise AssertionError("SPMI transaction corrupted SP")
    for register, value in saved.items():
        if cpu.reg_read(register) != value:
            raise AssertionError(f"SPMI transaction corrupted callee-saved register {register}")
    return {
        "result": cpu.reg_read(reg.UC_ARM64_REG_X0),
        "count": struct.unpack("<I", cpu.mem_read(COUNT, 4))[0],
        "buffer": bytes(cpu.mem_read(BUFFER, 1)),
        "accesses": accesses,
        "log_calls": log_calls,
    }


class SpmiOwnershipTests(unittest.TestCase):
    def test_unowned_write_fails_without_any_mmio(self):
        for apid, owner, ee in ((0, 1, 0), (640, 2, 0), (1023, 0xA4, 1)):
            with self.subTest(apid=apid, owner=owner, ee=ee):
                actual = transaction(IMAGE, 0, apid, owner, ee)
                self.assertEqual(actual["result"], 6)  # Native DENIED status path.
                self.assertEqual(actual["count"], 0)
                self.assertEqual(actual["buffer"], b"\xa5")
                self.assertEqual(actual["accesses"], [])

    def test_owned_writes_retain_original_transaction_behavior(self):
        stock = IMAGE.with_name("SPMIDxe.efi")
        for apid, owner, ee, base_apid, bus_id, limit in (
                (0, 0xA0, 0, 0, 0, 1024), (640, 1, 1, 0, 0, 1024),
                (1023, 4, 4, 0, 0, 1024), (128, 0, 0, 512, 1, 768),
                (0, 0, 0, 640, 1, 384)):
            with self.subTest(apid=apid, owner=owner, ee=ee, base_apid=base_apid):
                actual = transaction(IMAGE, 0, apid, owner, ee, base_apid, bus_id, limit)
                expected = transaction(stock, 0, apid, owner, ee, base_apid, bus_id, limit)
                for field in ("result", "count", "buffer", "accesses"):
                    self.assertEqual(actual[field], expected[field])
                self.assertEqual(actual["log_calls"], 0)
                self.assertEqual(actual["result"], 0)
                self.assertEqual(actual["count"], 1)

    def test_observer_reads_do_not_require_write_ownership(self):
        stock = IMAGE.with_name("SPMIDxe.efi")
        actual = transaction(IMAGE, 1, 640, 2)
        expected = transaction(stock, 1, 640, 2)
        for field in ("result", "count", "buffer", "accesses"):
            self.assertEqual(actual[field], expected[field])
        self.assertEqual(actual["result"], 0)
        self.assertEqual(actual["buffer"], b"\x5a")
        self.assertEqual(actual["count"], 1)


    def test_invalid_opcode_retains_native_failure_without_mmio(self):
        actual = transaction(IMAGE, 2, 640, 2)
        self.assertEqual(actual["result"], 3)
        self.assertEqual(actual["count"], 0)
        self.assertEqual(actual["accesses"], [])


if __name__ == "__main__":
    unittest.main()
