  INF MdeModulePkg/Core/Dxe/DxeMain.inf
  INF MdeModulePkg/Universal/PCD/Dxe/Pcd.inf

  INF Binaries/ziyi/QcomPkg/Drivers/EnvDxe/EnvDxe.inf

  INF MdeModulePkg/Universal/ReportStatusCodeRouter/RuntimeDxe/ReportStatusCodeRouterRuntimeDxe.inf
  INF MdeModulePkg/Universal/StatusCodeHandler/RuntimeDxe/StatusCodeHandlerRuntimeDxe.inf
  INF ArmPkg/Drivers/CpuDxe/CpuDxe.inf
  INF MdeModulePkg/Core/RuntimeDxe/RuntimeDxe.inf
  INF MdeModulePkg/Universal/SecurityStubDxe/SecurityStubDxe.inf

  INF Binaries/ziyi/QcomPkg/Drivers/ShmBridgeDxe/ShmBridgeDxeLA.inf
  INF Binaries/ziyi/QcomPkg/Drivers/TzDxe/ScmDxeLA.inf
  INF Binaries/ziyi/QcomPkg/Drivers/TzDxe/TzDxeLA.inf

  INF MdeModulePkg/Universal/WatchdogTimerDxe/WatchdogTimer.inf
  INF MdeModulePkg/Universal/CapsuleRuntimeDxe/CapsuleRuntimeDxe.inf
  INF MdeModulePkg/Universal/Variable/RuntimeDxe/VariableRuntimeDxe.inf
  INF EmbeddedPkg/EmbeddedMonotonicCounter/EmbeddedMonotonicCounter.inf
  INF MdeModulePkg/Universal/ResetSystemRuntimeDxe/ResetSystemRuntimeDxe.inf
  INF EmbeddedPkg/RealTimeClockRuntimeDxe/RealTimeClockRuntimeDxe.inf
  INF EmbeddedPkg/MetronomeDxe/MetronomeDxe.inf
  INF MdeModulePkg/Universal/HiiDatabaseDxe/HiiDatabaseDxe.inf
  INF ArmPkg/Drivers/ArmGicDxe/ArmGicDxe.inf
  INF ArmPkg/Drivers/TimerDxe/TimerDxe.inf

  INF Binaries/ziyi/QcomPkg/Drivers/ChipInfoDxe/ChipInfoDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/IPCCDxe/IPCCDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/GLinkDxe/GLinkDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/PlatformInfoDxe/PlatformInfoDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/ProjectInfoDxe/ProjectInfoDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/DALSYSDxe/DALSYSDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/HALIOMMUDxe/HALIOMMUDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/HWIODxe/HWIODxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/I2CDxe/I2CDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/TLMMDxe/TLMMDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/PmicDxe/PmicDxeLa.inf

  INF MdeModulePkg/Universal/DevicePathDxe/DevicePathDxe.inf
  INF MdeModulePkg/Universal/Disk/DiskIoDxe/DiskIoDxe.inf
  INF MdeModulePkg/Universal/Disk/PartitionDxe/PartitionDxe.inf
  INF FatPkg/EnhancedFatDxe/Fat.inf
  INF MdeModulePkg/Universal/Disk/UnicodeCollation/EnglishDxe/EnglishDxe.inf

  INF Binaries/ziyi/QcomPkg/Drivers/UFSDxe/UFSDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/CmdDbDxe/CmdDbDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/PwrUtilsDxe/PwrUtilsDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/RpmhDxe/RpmhDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/NpaDxe/NpaDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/ULogDxe/ULogDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/VcsDxe/VcsDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/ClockDxe/ClockDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/SPMIDxe/SPMIDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/ICBDxe/ICBDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/SmemDxe/SmemDxe.inf
  INF MdeModulePkg/Universal/BdsDxe/BdsDxe.inf
  INF EmbeddedPkg/SimpleTextInOutSerial/SimpleTextInOutSerial.inf
  INF MdeModulePkg/Universal/PrintDxe/PrintDxe.inf
  INF MdeModulePkg/Universal/Console/ConPlatformDxe/ConPlatformDxe.inf
  INF MdeModulePkg/Universal/Console/ConSplitterDxe/ConSplitterDxe.inf
  INF MdeModulePkg/Universal/Console/GraphicsConsoleDxe/GraphicsConsoleDxe.inf

!if $(USE_CUSTOM_DISPLAY_DRIVER) == 1
  INF Binaries/ziyi/QcomPkg/Drivers/CPRDxe/CPRDxe.inf
!endif
  INF Binaries/ziyi/QcomPkg/Drivers/GpiDxe/GpiDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/SPIDxe/SPIDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/SdccDxe/SdccDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/FeatureEnablerDxe/FeatureEnablerDxe.inf

!if $(USE_CUSTOM_DISPLAY_DRIVER) == 1
  INF Binaries/ziyi/QcomPkg/Drivers/DisplayDxe/DisplayDxe.inf
!else
  INF SiliciumPkg/Drivers/SimpleFbDxe/SimpleFbDxe.inf
!endif

  INF Binaries/ziyi/QcomPkg/Drivers/ButtonsDxe/ButtonsDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/ChargerExDxe/ChargerExDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/PmicGlinkDxe/PmicGlinkDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/QcomChargerDxe/QcomChargerDxeLA.inf
  INF Binaries/ziyi/QcomPkg/Drivers/UsbPwrCtrlDxe/UsbPwrCtrlDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/TsensDxe/TsensDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/LimitsDxe/LimitsDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/DDRInfoDxe/DDRInfoDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/UsbfnDwc3Dxe/UsbfnDwc3Dxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/XhciPciEmulationDxe/XhciPciEmulationDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/XhciDxe/XhciDxe.inf

  INF MdeModulePkg/Bus/Usb/UsbBusDxe/UsbBusDxe.inf
  INF MdeModulePkg/Bus/Usb/UsbKbDxe/UsbKbDxe.inf
  INF MdeModulePkg/Bus/Usb/UsbMassStorageDxe/UsbMassStorageDxe.inf

  INF Binaries/ziyi/QcomPkg/Drivers/UsbMsdDxe/UsbMsdDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/UsbDeviceDxe/UsbDeviceDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/UsbConfigDxe/UsbConfigDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/UsbInitDxe/UsbInitDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/UCDxe/UCDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/RNGDxe/RngDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/PILDxe/PILDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/PILProxyDxe/PILProxyDxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/SecRSADxe/SecRSADxe.inf
  INF Binaries/ziyi/QcomPkg/Drivers/ASN1X509Dxe/ASN1X509Dxe.inf
