/**
  Copyright (c) 2011-2012, ARM Limited. All rights reserved.
  Copyright (c) 2023-2026, Project Silicium Authors.
  SPDX-License-Identifier: BSD-2-Clause-Patent
**/

#include <Library/IoLib.h>
#include <Library/PlatformSecLib.h>
#include <Library/ConfigurationMapHelperLib.h>
#include <Library/ArmSmmuDetachLib.h>

#include "PlatformRegisters.h"

VOID
WakeUpCores ()
{
  EFI_STATUS Status;
  UINT32     EarlyInitCoreCnt;

  // Get Early Cores Count
  Status = LocateConfigurationEntry32 ("EarlyInitCoreCnt", &EarlyInitCoreCnt);
  if (EFI_ERROR (Status)) {
    return;
  }

  // Update GIC Wakers
  for (UINTN i = 0; i < EarlyInitCoreCnt; i++) {
    MmioAnd32 (GICR_WAKER_CPU (i), ~GIC_WAKER_PROCESSORSLEEP);
  }
}

VOID
PlatformInitialize ()
{
  // Wake Up Cores
  WakeUpCores ();

  // Preserve display contexts declared in diwali-sde.dtsi. The SMMU helper
  // matches each configured SMR's mask, including the unsecure 0x402 mask.
  CONST UINT16 MdpStreams[] = { 0x2800, 0x2801, 0x2C01 };

  // Detach other IOMMU domains without disrupting the bootloader scanout.
  ArmSmmuDetach (MdpStreams, ARRAY_SIZE (MdpStreams));
}
