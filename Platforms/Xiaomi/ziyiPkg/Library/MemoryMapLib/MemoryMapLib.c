#include <Library/MemoryMapLib.h>

/**
  Memory Map for Xiaomi 13 Lite (ziyi) - Snapdragon 7 Gen 1 (SM7450 / Diwali).
  Based on stock Xiaomi ziyi uefiplat.cfg; overlapping reservations are split below.

  Note on Ramoops:
  In the Xiaomi device tree (xiaomi-sm7450-common.dtsi), Linux defines a ramoops region
  at 0xA7000000 - 0xA7400000. In Qualcomm's boot flow, this memory range is stage-dependent:
  during the bootloader stage, 0xA7000000 - 0xA7600000 is used exclusively for the UEFI FD
  and FD reserved scratch areas. Once UEFI exits and Linux initializes, Linux reuses this area
  for pmsg/ramoops. During UEFI execution, the memory is reserved for UEFI FD / BsData.
**/

STATIC
EFI_MEMORY_REGION_DESCRIPTOR
gMemoryDescriptor[] = {
  // Name, Address, Length, HobOption, ResourceType, ResourceAttribute, MemoryType, ArmAttribute

  // DDR Regions (verified from stock uefiplat.cfg)
  {"HYP",               0x80000000, 0x00600000, AddMem, MEM_RES, SYS_MEM_CAP, Reserv, NS_DEVICE},
  {"DT BLOB",           0x80600000, 0x00040000, AddMem, MEM_RES, SYS_MEM_CAP, Reserv, WRITE_BACK_XN},
  {"XBL RAMDUMP",       0x80640000, 0x001C0000, AddMem, MEM_RES, UNCACHEABLE, Conv,   UNCACHED_UNBUFFERED_XN},
  {"AOP",               0x80800000, 0x000A0000, AddMem, MEM_RES, UNCACHEABLE, Reserv, UNCACHED_UNBUFFERED_XN},
  {"SMEM",              0x80900000, 0x00200000, AddMem, MEM_RES, UNCACHEABLE, Reserv, UNCACHED_UNBUFFERED_XN},
  // Stock PIL extends into Demura; reserve their union without overlapping HOBs.
  {"PIL Reserved",      0x84E00000, 0x1C600000, AddMem, MEM_RES, UNCACHEABLE, Reserv, UNCACHED_UNBUFFERED_XN},
  {"Display Demura",    0xA1400000, 0x02B00000, AddMem, MEM_RES, SYS_MEM_CAP, Reserv, WRITE_THROUGH_XN},
  {"DBI Dump",          0xA6000000, 0x00F00000, NoHob,  MMAP_IO, INITIALIZED, Conv,   UNCACHED_UNBUFFERED_XN},
  {"FD Reserved",       0xA7000000, 0x00100000, AddMem, SYS_MEM, SYS_MEM_CAP, BsData, WRITE_BACK},
  {"UEFI FD",           0xA7100000, 0x00300000, AddMem, SYS_MEM, SYS_MEM_CAP, BsData, WRITE_BACK},
  {"UEFI FD Reserved",  0xA7400000, 0x00200000, AddMem, SYS_MEM, SYS_MEM_CAP, BsData, WRITE_BACK},
  {"CPU Vectors",       0xA7600000, 0x00001000, AddMem, SYS_MEM, SYS_MEM_CAP, BsData, WRITE_BACK},
  {"Info Blk",          0xA7601000, 0x00001000, AddMem, SYS_MEM, SYS_MEM_CAP, RtData, WRITE_BACK_XN},
  {"MMU PageTables",    0xA7602000, 0x00003000, AddMem, SYS_MEM, SYS_MEM_CAP, BsData, WRITE_BACK_XN},
  {"Log Buffer",        0xA7605000, 0x00008000, AddMem, SYS_MEM, SYS_MEM_CAP, RtData, WRITE_BACK_XN},
  {"UEFI Stack",        0xA760D000, 0x00040000, AddMem, SYS_MEM, SYS_MEM_CAP, BsData, WRITE_BACK_XN},
  {"SEC Heap",          0xA764D000, 0x0008C000, AddMem, SYS_MEM, SYS_MEM_CAP, BsData, WRITE_BACK_XN},
  {"Sched Heap",        0xA76D9000, 0x00400000, AddMem, SYS_MEM, SYS_MEM_CAP, BsData, WRITE_BACK_XN},
  {"FV Region",         0xA7AD9000, 0x00400000, AddMem, SYS_MEM, SYS_MEM_CAP, BsData, WRITE_BACK_XN},
  {"UEFI RESV",         0xA7ED9000, 0x00127000, AddMem, SYS_MEM, SYS_MEM_CAP, BsData, WRITE_BACK_XN},
  // HakiOS: the boot shim copies the "XNUP" payload to 0xB0000000 (devices/ziyi/boot.conf, PAYLOAD_BASE): the middle of
  // the kernel reservation ABL loads the boot image into (at 0xA8080000, a few MiB), which this map keeps reserved.
  // redwood's 0xF0000000 is inside "TZApps Reserved" here; 0xF8000000, the bottom of the DXE heap, reset the phone
  // before this UEFI drew anything (6 November): stock firmware's resident state lives there.
  {"Kernel",            0xA8000000, 0x08000000, AddMem, SYS_MEM, SYS_MEM_CAP, Reserv, WRITE_BACK_XN},
  {"XNU Payload",       0xB0000000, 0x04000000, AddMem, SYS_MEM, SYS_MEM_CAP, Reserv, WRITE_BACK_XN},
  {"Kernel",            0xB4000000, 0x04000000, AddMem, SYS_MEM, SYS_MEM_CAP, Reserv, WRITE_BACK_XN},
  {"Display Reserved",  0xB8000000, 0x02B00000, AddMem, MEM_RES, SYS_MEM_CAP, Reserv, WRITE_THROUGH_XN},
  {"OEM VM",            0xBB000000, 0x05000000, AddMem, SYS_MEM, SYS_MEM_CAP, Reserv, WRITE_BACK_XN},
  {"MTE Reserved",      0xC0000000, 0x20000000, AddMem, SYS_MEM, SYS_MEM_CAP, Reserv, WRITE_BACK_XN},
  {"VM PIL",            0xE0000000, 0x05700000, AddMem, SYS_MEM, SYS_MEM_CAP, Reserv, WRITE_BACK_XN},
  {"TZApps Reserved",   0xEA000000, 0x07400000, AddMem, MEM_RES, UNCACHEABLE, Reserv, UNCACHED_UNBUFFERED_XN},
  {"DXE Heap",          0xF8000000, 0x07C00000, AddMem, SYS_MEM, SYS_MEM_CAP, Conv,   WRITE_BACK_XN},
  // Stock 0x830000000 HYP is AddDynamicMem, not RAM on the 8 GB ziyi.
  // Do not turn that optional 32+ GB reservation into a static system-memory HOB.

  // Other Memory Regions
  {"IMEM Base",         0x14680000, 0x0002A000, NoHob,  MMAP_IO, INITIALIZED, Conv,   NS_DEVICE},
  {"IMEM Cookie Base",  0x146AA000, 0x00016000, AddDev, MMAP_IO, INITIALIZED, Conv,   NS_DEVICE},

  // Register Regions (verified against diwali.dtsi)
  {"IPC_ROUTER_TOP",    0x00400000, 0x00100000, AddDev, MMAP_IO, UNCACHEABLE, MmIO,   NS_DEVICE},
  {"SECURITY CONTROL",  0x00780000, 0x00007000, AddDev, MMAP_IO, UNCACHEABLE, MmIO,   NS_DEVICE},
  {"QUP",               0x00800000, 0x00300000, AddDev, MMAP_IO, UNCACHEABLE, MmIO,   NS_DEVICE},
  {"PRNG_CFG_PRNG",     0x010C0000, 0x0000C000, AddDev, MMAP_IO, UNCACHEABLE, MmIO,   NS_DEVICE},
  {"CRYPTO0 CRYPTO",    0x01DC0000, 0x00040000, AddDev, MMAP_IO, UNCACHEABLE, MmIO,   NS_DEVICE},
  {"TCSR_TCSR_REGS",    0x01FC0000, 0x00030000, AddDev, MMAP_IO, UNCACHEABLE, MmIO,   NS_DEVICE},
  {"PERIPH_SS",         0x08800000, 0x00100000, AddDev, MMAP_IO, UNCACHEABLE, MmIO,   NS_DEVICE},
  {"USB",               0x0A600000, 0x00200000, AddDev, MMAP_IO, UNCACHEABLE, MmIO,   NS_DEVICE},
  {"AOSS",              0x0B000000, 0x04000000, AddDev, MMAP_IO, UNCACHEABLE, MmIO,   NS_DEVICE},
  {"TLMM",              0x0F000000, 0x01000000, AddDev, MMAP_IO, UNCACHEABLE, MmIO,   NS_DEVICE},
  {"SMMU",              0x15000000, 0x00200000, AddDev, MMAP_IO, UNCACHEABLE, MmIO,   NS_DEVICE},
  {"APSS_HM",           0x17000000, 0x02000000, AddDev, MMAP_IO, UNCACHEABLE, MmIO,   NS_DEVICE}
};

VOID
GetMemoryMap (
  OUT EFI_MEMORY_REGION_DESCRIPTOR **MemoryDescriptor,
  OUT UINT8                         *MemoryDescriptorCount)
{
  // Pass Data
  *MemoryDescriptor      = gMemoryDescriptor;
  *MemoryDescriptorCount = ARRAY_SIZE (gMemoryDescriptor);
}
