##
#  Copyright (c) 2011 - 2022, ARM Limited. All rights reserved.
#  Copyright (c) 2014, Linaro Limited. All rights reserved.
#  Copyright (c) 2015 - 2020, Intel Corporation. All rights reserved.
#  Copyright (c) 2018, Bingxing Wang. All rights reserved.
#  Copyright (c) Microsoft Corporation.
#  Copyright (c) 2023 - 2026, Project Silicium Authors.
#
#  SPDX-License-Identifier: BSD-2-Clause-Patent
##

################################################################################
#
# Defines Section - statements that will be processed to create a Makefile.
#
################################################################################
[Defines]
  PLATFORM_NAME                  = ziyi
  PLATFORM_GUID                  = 82D42CA2-4A73-4554-B972-8C83C01237A8
  PLATFORM_VERSION               = 0.1
  DSC_SPECIFICATION              = 0x00010005
  OUTPUT_DIRECTORY               = Build/ziyiPkg
  SUPPORTED_ARCHITECTURES        = AARCH64
  BUILD_TARGETS                  = RELEASE|DEBUG
  SKUID_IDENTIFIER               = DEFAULT
  FLASH_DEFINITION               = ziyiPkg/ziyi.fdf
  USE_CUSTOM_DISPLAY_DRIVER      = 0

!include DiwaliPkg/DiwaliPkg.dsc.inc

[BuildOptions]
  #
  # HakiOS (devices/ziyi/boot.conf): where the payload is on this phone, and nothing written to its storage
  # (the boot manager's XNU hook keeps its log in RAM instead of the logdump partition, and shows on the screen
  # what it did, waiting 60 s before it resets: XNU_SCREEN_LOG).
  #
  *_CLANGPDB_*_CC_FLAGS = -D XNU_PAYLOAD_BASE=0xB0000000ULL -D XNU_NO_STORAGE_WRITES -D XNU_SCREEN_LOG

[PcdsFixedAtBuild]
  #
  # DDR Memory
  #
  gArmTokenSpaceGuid.PcdSystemMemoryBase|0x80000000

  #
  # UEFI Stack (verified from stock uefiplat.cfg)
  #
  gArmPlatformTokenSpaceGuid.PcdCPUCoresStackBase|0xA760D000
  gArmPlatformTokenSpaceGuid.PcdCPUCorePrimaryStackSize|0x40000

  #
  # SMBIOS
  #
  gSiliciumPkgTokenSpaceGuid.PcdSmbiosSystemManufacturer|"Xiaomi"
  gSiliciumPkgTokenSpaceGuid.PcdSmbiosSystemModel|"Xiaomi 13 Lite"
  gSiliciumPkgTokenSpaceGuid.PcdSmbiosSystemRetailModel|"ziyi"
  gSiliciumPkgTokenSpaceGuid.PcdSmbiosSystemRetailSku|"Xiaomi_13_Lite_ziyi"
  gSiliciumPkgTokenSpaceGuid.PcdSmbiosSystemBoardModel|"ziyi"

  #
  # Simple Frame Buffer (verified 1080x2400 from panel DT)
  #
  gSiliciumPkgTokenSpaceGuid.PcdFrameBufferWidth|1080
  gSiliciumPkgTokenSpaceGuid.PcdFrameBufferHeight|2400
  gSiliciumPkgTokenSpaceGuid.PcdFrameBufferColorDepth|32

  #
  # Platform PEI
  #
  gQcomPkgTokenSpaceGuid.PcdPlatformType|"LA"

[LibraryClasses]
  #
  # Memory Libraries
  #
  MemoryMapLib|ziyiPkg/Library/MemoryMapLib/MemoryMapLib.inf

  #
  # QCOM Libraries
  #
  ConfigurationMapLib|ziyiPkg/Library/ConfigurationMapLib/ConfigurationMapLib.inf

