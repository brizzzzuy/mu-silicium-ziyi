# Building

> [!TIP]
> For the Compilation, a Linux OS is recommended.

## Cloning the Source Code

To Compile this UEFI Project in the first Place, You have to Download the Source Code. <br>
You can do this by using the `git` Command:
```
git clone https://github.com/Project-Silicium/Mu-Silicium.git --recursive
```
The entire Source is about ~5GB in Size, so the Download Time depends on your Internet Speed and Storage Speed.
At the End you should see a new Folder called `Mu-Silicium`.

## Platform Specific Steps

<details>
<summary>Windows</summary>

## Requirements
  - [Git](https://git-scm.com/install/windows)
  - [Python](https://www.python.org/downloads/) Version 3.11 or higher
  - [LLVM](https://github.com/llvm/llvm-project/releases/)
  - [VS Build Tools](https://aka.ms/vs/stable/vs_BuildTools.exe)
  - [GnuMake32](https://gnuwin32.sourceforge.net/packages/make.htm)

## Setting Up PATH

Since GnuMake32 doesn't add itself to PATH, you have to add it manually. <br>
You can Update the PATH Variable using UI in Windows, Simply Enter "Path" in your Search Bar. <br>
Once you Open the Window, Go to System PATH and add two new Entries.

The Entry should Point to the Install `bin` Folder of GnuMake32. <br>
The Install Location Depends on what Path you Extracted it to.

## Installing pip Dependencies

Before you can Start to Compile this UEFI Project, You have to Install the pip Dependencies. <br>
Open a Command Prompt Window in the same Folder as the Source Code. <br>
Once you did that, Run this Command to Install all pip Dependencies:
```cmd
python3 -m pip install -r pip-requirements.txt
```

---

</details>

<details>
<summary>Linux</summary>

## Installing Dependencies

Before you can Start to Compile this UEFI Project, You have to Install the Dependencies. <br>
Open a Terminal in the same Folder as the Source Code. <br>
Once you did that, Run this Command to Install all Dependencies:
```bash
./setup_env.sh -p [PACKAGE_MANAGER_NAME]
```
The `[PACKAGE_MANAGER_NAME]` Argument here is the Name of your Distro Package Manager. <br>
For Example, for Ubuntu or Debian users the Name would be `apt`.

</details>

## Compiling UEFI

> [!IMPORTANT]
> Depending on your Python Install, You might have to use `python` instead of `python3`.

After you have Done all the Steps from before, You're now ready to Compile UEFI with this Command:
```
python3 build_uefi.py -d [DEVICE_CODENAME]
```
The `[DEVICE_CODENAME]` Argument here is the Codename of your Device. <br>
You can Find the Codename of the Device in the [Status Page](Status.md).

# Updating

To get these new Updates and Changes you can use the `-u` Parameter to Update your Local Repo when Building:
```
python3 build_uefi.py -d [DEVICE_CODENAME] -u
```

# Tips & Tricks

## Faster Build Times on Windows

If you're Compiling on Windows, you probably Experience slow Builds Times. <br>
Here are some Suggestions to Improve this:

### Setting Up a Dev Drive

One Way to Improve the Build Times is using a Dev Drive in Windows. <br>
You can Find more Details, the Requirements and How to Set it Up on the [Microsoft Website](https://learn.microsoft.com/en-us/windows/dev-drive/).

### Adding a Antivirus Exception

> [!CAUTION]
> This will Disable Security in the `Mu-Silicium` Folder! <br>
> Only follow this if you're Comfortable with that.

Another Way to Improve the Build Times is adding the `Mu-Silicium` as an Exception in your Antivirus. <br>
How to do that Highly depends on the Antivirus you're using, On Microsoft Defender you can do it like this:
```
Virus & thread protection -> Virus & thread protection settings -> Exclusions -> Add or remove exclusions
```
In there you can Add the `Mu-Silicium` Folder as an Exclusion.

## Xiaomi 13 Lite (ziyi)

The `ziyi` target uses Snapdragon 7 Gen 1 (SM7450 / Diwali), not SM8450.
The closest existing layout used is Xiaomi ingres / Waipio; its proprietary
drivers are **not** reused. Hardware specifications: [Xiaomi specifications](https://www.mi.com/global/product/xiaomi-13-lite/specs/).

Build from the repository root after installing the dependencies above:

```bash
python3 build_uefi.py -d ziyi -r DEBUG
```

`Resources/DeviceBinaries/ziyi` tracks the vendor inputs needed by this port.
`Binaries` remains the upstream submodule, whose pinned revision does not contain
ziyi. After a recursive clone, install the overlay before regenerating patches:

```bash
cp -a Resources/DeviceBinaries/ziyi Binaries/
python3 Resources/Scripts/patch_ziyi_pmic.py
python3 Resources/Scripts/patch_ziyi_ufs.py
python3 Resources/Scripts/patch_ziyi_qsee.py
python3 Resources/Scripts/patch_ziyi_buttons.py
```

The overlay excludes generated `.patched.efi` outputs; the commands above
recreate them from hash-pinned stock payloads. Do not substitute ingres drivers.

### Current build: added diagnostics removed

The current source retains the phone-confirmed power-to-Enter mapping, genuine
resident Keymaster reuse, conditional UFS activation, PMIC re-entry adaptation
and SPMI cached-owner write guard. ADC remains explicitly unavailable as agreed.
It removes the added `ziyi PWR`, `ziyi KEY`, QSEE metadata/reuse and `[ziyi W3]`
messages, button polling/key hooks and state, failed-start diagnostic queries,
and SPMI breadcrumb/snapshot overhead. Native error logs, TZ error dumps and
assertions remain; this is still a DEBUG build, not a globally silent firmware.

`patch_ziyi_buttons.py` now changes only the native power branch at `0x3A00`.
`patch_ziyi_qsee.py` installs only `ziyi_keymaster_resident.S` at `0xE400`;
the native failed-start wrapper is untouched. SPMI resumes native operations
without additional diagnostic MMIO. All selected adapted binaries use
`.patched.efi`; obsolete diagnostic generators, assembly and generated driver
outputs were removed. Historical image links and bring-up evidence below remain.

All 24 current native regressions pass. The obsolete snapshot/breadcrumb and
diagnostic-header-only tests were removed rather than pinned to new internals.
A separate smoke executes native button polling/translation and formatting,
resident bootstrap and SPMI transactions with modeled external services:
power still emits EFI Enter, resident bootstrap performs no duplicate load,
normal paths emit no added output, and a real modeled PMIC read error still
prints its native diagnostics. This is not physical device validation.

- Quiet ButtonsDxe SHA-256: `eed4603cd2b12e1579272471d5ebe8e76823fc21fd5456345b712c5d298a33b6`.
- Quiet TzDxeLA SHA-256: `b5c76bff451fcd14b19d9d3f97364aba05851647dad9f9b42fdccdc6f445354a`.
- Quiet SPMIDxe SHA-256: `2b43aa552cd924ce5bf6adad84fa9da28c7fa6ab50f182f8f2ed2afd02b87ec4`.
- `Mu-ziyi-no-extra-logs.img`: 3551232 bytes; SHA-256 `8beeb55215a19191aa8f53e94eccbc9a8419de53aef15d421279202437d8e1a3`.

The DEBUG build verifies 49 PE images. Decoding the final compressed main FV
confirms that only ButtonsDxe, TzDxeLA and SPMIDxe differ from the phone-tested
`Mu-ziyi-power-enter.img`; each packaged driver matches the exercised quiet
binary exactly and contains none of the removed custom message markers.
PMIC, UFS, USB and all other main-FV files, BootShim/header and DTB are unchanged.
The latest quiet image still requires a temporary phone boot test.

Download: [`Mu-ziyi-no-extra-logs.img`](https://gofile.io/d/uHB5nZ7t).
Use `fastboot boot Mu-ziyi-no-extra-logs.img`, not flashing. Verify ordinary
volume navigation and short-power confirmation; no diagnostic key sequence
is needed. Stock DEBUG output may remain.

### Initial build verification (historical)

The DEBUG build succeeded under Arch Linux / WSL2 with LLVM 18.1.8 and Python
3.14.7; the existing post-build validator verified 49 PE images. The build emits
an inherited `ArmPsciResetSystemLib` / `HwResetSystemLib` library-class warning.
Build in the Linux filesystem rather than `/mnt/c`; Windows checkout scanning
timed out during this bring-up.

The generated `Mu-ziyi.img` is 3,551,232 bytes. Its Android v4 header, uncompressed
kernel payload, 3 MiB firmware volume and appended DTB were checked. Executing
the actual image's BootShim in ARM64 emulation confirmed both relocated and
already-in-place payload paths, preserving `x0` and copying the entire firmware.
Execution stops at the firmware entry: this does not validate UEFI or peripherals.

SHA-256 of this DEBUG image:
`0269f160a3102e534b270d64e18c554dfae9b379ae5cee922f9ca118571fcdb7`.
Build timestamps affect subsequent images.

### ARM64 header correction after the first hardware attempt

The user reported `fastboot boot` returning `OKAY`, followed by a black screen.
Without pressing buttons or rebooting, `fastboot getvar product` still returned
`ziyi`. This does not establish that execution reached Mu; loader rejection,
return, or an early restart must be distinguished before debugging scanout.

The original `text_offset = 0xA7100000` incorrectly used the FD destination as
the ARM64 Image's load offset. In the public [Qualcomm ABL `UpdateBootParams`](https://github.com/TheGammaSqueeze/edk2/blob/uefi.lnx.5.0.r13-rel/QcomModulePkg/Library/BootLib/BootLinux.c),
an uncompressed Image's nonzero `image_size` causes `text_offset` to be added
directly to the kernel reservation's base. With stock ziyi's `0xA8000000` base,
the old value gives `0x14F100000`, outside its 256 MiB kernel reservation.
The corrected relative offset is `0x80000`; FD relocation still targets
`0xA7100000`. Public ABL code is a reference, not a verified dump of this phone's
loader version. Its fastboot handler can acknowledge the command before loading
completes, so host-side `OKAY` is not proof of handoff.

The original `image_size = 0x300000` also omitted the 112-byte BootShim.
It is now `FD_SIZE + (_Payload - _Head) = 0x300070`, covering the full Image.
See the [ARM64 boot protocol](https://www.kernel.org/doc/html/latest/arch/arm64/booting.html).
Boot header v4 normally obtains its DTB from the existing `vendor_boot`, not
the kernel suffix; the appended DTB is retained unchanged for this comparison.
An FDT lookup at `image_size` tests the boundary, not the actual v4 DTB route.

`Mu-ziyi-boot-header-fix.img` changes only those two 8-byte ARM64 header fields
relative to the uploaded image. Firmware, copy instructions, framebuffer, DTB
and Android header version are unchanged. The old address fails a model of
the Qualcomm load-address bound; the new address fits. Both actual payload
relocation paths were executed in ARM64 emulation, preserving the DT pointer.
No Xiaomi loader or peripherals were executed locally. Other SEC/cache and
driver re-entry risks remain unchanged to isolate this loader-contract test;
this is not proof that the corrected image boots on hardware.

SHA-256 of the corrected image:
`e67cdd4e0f77aba704137a58f5b0c10ab39f8da01257250bd2fce9bbae07d027`.

### Hardware sources

- [Device trees](https://github.com/LineageOS/android_kernel_xiaomi_sm8450-devicetrees/tree/2e649a7f3e762903eedad43d8256b91e28b512d8),
  specifically `diwali.dts`, `ziyi-sm7450-overlay.dts`, `ziyi-sm7450.dtsi`,
  `xiaomi-sm7450-common.dtsi` and the Diwali display includes.
- [Kernel binding headers](https://github.com/LineageOS/android_kernel_xiaomi_sm8450/tree/eff4b40407a1b6f1b1ab84554cbb540bcb495175/include).
- [Android device configuration](https://github.com/cupid-development/android_device_xiaomi_ziyi/blob/lineage-23.2/BoardConfig.mk)
  and its [common boot configuration](https://github.com/cupid-development/android_device_xiaomi_sm8450-common/blob/lineage-24.0/BoardConfigCommon.mk):
  uncompressed ARM64 Image, Android boot header version 4.
- [Stock firmware package OS3.0.5.0.VLLMIXM](https://github.com/XiaomiFirmwareUpdaterReleases/firmware_xiaomi_ziyi/releases/tag/stable-28.09.2026),
  `fw_ziyi_ziyi_global-ota_full-OS3.0.5.0.VLLMIXM-user-15.0-6836120ebe.zip`.
  Verified SHA-256:
  `acd1ec18f88886f53bfa250645ea98da434eb1c18ef2a18575e9aa3d54ac688f`.
  Drivers and `RawFiles/uefiplat.cfg` were extracted from its `firmware-update/uefi.img`
  using [UEFIReader](https://github.com/MSMTools/UEFIReader).
  Its build ID is `BOOT.MXF.2.0-01018.3-WAIPIO-1`; that shared firmware identifier
  does not change the device's SoC to SM8450. Original PE payloads are preserved;
  PMIC/SPMI use the derived re-entry adaptations described below.

`Resources/DTBs/ziyi.dtb` is a source-built Diwali base plus the ziyi overlay,
not a live `/sys/firmware/fdt` dump. Overlay root selection properties were
retained explicitly: MSM IDs 506/547/564, board ID 34, Xiaomi board ID 9.
It retains upstream bootloader-populated memory fields, including an empty
`/memory/reg`; it is not a standalone Linux handoff tree. Device-tree compilation
emits upstream structural warnings; merging and decoding succeed.

### PMIC/SPMI re-entry correction from hardware video

The header-corrected image reaches DXE and prints logs on the phone. The user's
video `video_2026-11-04_21-03-52.mp4` then shows an external data abort:

- `ELR = 0xFE354790`, SPMI runtime base `0xFE351000`, fault RVA `0x3790`.
- Instruction `ldr w9, [x24]`, with `x24 = FAR = 0x0C789008`.
- `ESR = 0x96000010`: same-EL data abort, synchronous external abort on a read,
  not a page-table translation fault.
- PMIC return RVAs `0x13228` and `0x1640` identify the startup pass at `0x12E70`,
  called from `0x163C`. It reaches the SPMI transaction while preparing a write
  of `0x03` to slave 0 register `0x0640`; the abort is the controller status read.
  The exact interconnect/security ownership reason is not observable from this log.

The adaptation preserves the hardware setup inherited from ABL rather than
repeating its PMIC and SPMI PIC configuration. This follows the paired adaptation
documented in `Binaries/nuwa/README.md`. The ziyi PIC routine at `0x2DA0` has
0x9c bytes identical to ingres's corresponding routine at `0x2E80`; offsets
were derived from the ziyi binary, not copied from ingres.

The first re-entry image replaced one 4-byte branch instruction in each driver:

| Driver | Site RVA | Original control flow | Adapted control flow |
|:-------|:---------|:----------------------|:---------------------|
| SPMI | `0x2618` | Conditional entry into the PIC setup loop | Branch to the existing continuation at `0x2650` |
| PMIC | `0x163C` | Call the post-init hardware configuration at `0x12E70` | Branch to `0x1644`, omitting that pass and its status accumulation |

That image used no success-return transaction stubs or exception-handler changes.
Prior initialization errors remained intact. Driver entry points, read/write
functions, protocol installation and ExitBootServices callbacks were unchanged.
Other platforms' ADC/ExitBootServices no-op patches were not included.

- First re-entry SPMI SHA-256: `538166615cb848239625aba979d1b02f65683a473aec01f69f46d9f3250f9741`.
- Adapted PMIC SHA-256: `210d9406e747dc0010151dbd42f442efc6d1059a02c0284c25bc3d4cf79d9c96`.
- `Mu-ziyi-pmic-reentry-fix.img` SHA-256: `0ea24303e33722b602741a37a17481438742ceaff3176963daed9ab2958aa0cc`.

Its DEBUG build and compressed-volume checks passed. The second hardware video
confirms execution beyond the omitted PMIC startup pass, but shows the later ADC
fault described below; it did not reach a usable UEFI session.

### SPMI write-owner correction from the second hardware video

`video_2026-11-04_21-29-16.mp4` shows the same SPMI load at RVA `0x3790`,
with `ESR = 0x96000010` but a different `FAR = 0x0C780008`. This is APID 640's
write-channel status window: `0x0C500000 + 640 * 0x1000 + 8`.
The ziyi DT specifies EE 0 and the matching core, observer and channel regions.
APID is a dynamic channel index, not a PMIC peripheral/register number.

The new stack includes SPMI `0x2BDC` and PMIC `0x1CBBC`, `0x1C810`, `0x408C`,
and `0x16A4`. This identifies optional ADC DAL attachment (`0x02000067`).
The masked operation's observer read at SPMI `0x2BA0` has succeeded; it faults
on the subsequent write at `0x2BD8`. `FindChannel` can legitimately return an
unowned fallback APID for observer reads, but the transaction executor also
accepts that APID for writes without checking its owner.

The exact owner of APID 640 is not present in the video. Owner mismatch is a
supported hypothesis, not a measured hardware fact. The missing write check is
independently visible in the binary. Linux's
[`pmic_arb_offset_v7`](https://github.com/torvalds/linux/blob/master/drivers/spmi/spmi-pmic-arb.c)
rejects a write when the channel's `write_ee` differs from the caller EE.

The current SPMI adaptation retains both startup changes and adds this check:

- At RVA `0x3684`, branch to the guard in existing executable zero padding at
  `0x7D00` (the initial ownership/context images used `0x7F00`). It runs after argument validation and clearing bytes-transferred.
- For opcode 0 (write), compare the selected six-byte cache entry's owner
  (byte 1, bits `[4:0]`) against the caller EE. The cache is populated from the
  hardware ownership table at controller base `+0x2D000 + 4 * APID`.
- On mismatch, use the driver's native DENIED result path at `0x39F4` (status 6)
  and normal epilogue. No transaction MMIO is accessed and bytes-transferred
  remains zero. Added write tracing and metadata snapshots are removed in the quiet build.
- Reads, owned writes and invalid-opcode handling resume the original code at
  `0x3688`. The original condition flags and displaced instruction are restored.
  The guard changes neither ownership tables nor security permissions.

PMIC ADC failure is already optional in the original binary: failed DAL attach
returns `EFI_UNSUPPORTED` at `0x4090` without installing the ADC protocol.
The caller logs `PmicDxe: Unable to install ADC protocol handler` and returns
status based on its earlier PMIC initialization, not on ADC success.
The SPMI-only adaptations did not bypass ADC attachment or suppress exceptions.
The later, explicitly approved ADC-disabled diagnostic is described below.
No adaptation fabricates measurements or advertises an unavailable ADC.
Other bus faults or later ownership changes are not handled by the cached-owner check.

Regenerate from the exact original stock files, with clang/lld/llvm-objcopy:

```bash
python3 Resources/Scripts/patch_ziyi_pmic.py
python3 Resources/Scripts/patch_ziyi_ufs.py
python3 Resources/Scripts/patch_ziyi_qsee.py
python3 Resources/Scripts/patch_ziyi_buttons.py
```

The generators validate complete original SHA-256 hashes, patch instructions
and (where used) executable padding before producing `.patched.efi` outputs.
The ziyi INFs select those files; original `.efi` files remain stock.
The current QSEE/button generators retain working fixes without added logging.
`Resources/Scripts/ziyi_spmi_guard.S` is the guard source.

Verification, with optional `pefile` and `unicorn` Python packages:

```bash
python3 Resources/Scripts/test_ziyi_spmi_guard.py -v
python3 Resources/Scripts/test_ziyi_pmic_adc.py -v
python3 Resources/Scripts/test_ziyi_ufs.py -v
python3 Resources/Scripts/test_ziyi_qsee.py -v
python3 Resources/Scripts/test_ziyi_keymaster.py -v
python3 Resources/Scripts/test_ziyi_buttons.py -v
```

The real ARM64 transaction routine executes against an isolated arbiter model.
The unowned-write regression fails against the stock binary and passes with
the guard. Four behavioral tests cover denied writes with no MMIO, owned writes
retaining the stock MMIO sequence, observer reads across ownership boundaries
and invalid-opcode failures. Boundary APIDs, owner masking, nonzero bases/buses,
bytes-transferred, SP and callee-saved registers remain checked. Obsolete
breadcrumb/snapshot tests were removed with the corresponding diagnostics.
This is machine-code verification, not physical SPMI or full UEFI emulation.

- First ownership-check SPMI SHA-256: `db8f9198c60fa3b5206533170ceeec883cfbcd88480f7e7226f5e706e5f002e3`.
- PMIC SHA-256 before the ADC-disabled diagnostic: `210d9406e747dc0010151dbd42f442efc6d1059a02c0284c25bc3d4cf79d9c96`.
- `Mu-ziyi-spmi-owner-fix.img` SHA-256: `73693a0638766021aa1e7c31ae51cd80b4ad15c974283117634af7d40fa5647a`.

That ownership-check DEBUG build passed with 49 PE images validated. Decoding
its compressed main FV confirmed that only SPMI differed from the first re-entry
image. PMIC, BootShim, corrected ARM64 header and DTB were preserved.
The user's third hardware video repeats the same external abort; the owner
check did not resolve it and does not establish the cause of that hardware fault.


Previous diagnostic upload: [`Mu-ziyi-spmi-owner-fix.img`](https://gofile.io/d/lrjXo7TJ)
(SHA-256 above; temporary `fastboot boot` only).

### Third hardware test: transaction and crash-register diagnostics

`video_2026-11-04_21-55-31.mp4` still shows `ELR = 0xFE354790`,
`FAR = 0x0C780008`, `ESR = 0x96000010`, and the same optional ADC write path.
It does not expose the cached owner or establish that owner mismatch is the
cause. The fault is not considered fixed.

Stock SPMI `DebugPrint` at RVA `0x17C0` ultimately calls `SerialPortWrite`
at `0x5644`. Its optional platform lookup for `"SerialPort Lib"` can fail and return zero output.
Consequently a missing native debug line on the framebuffer does not prove
the instrumented code was never executed.

The context-image guard traces every write, including owner matches, through that
existing logger. It reports absolute APID, local cache index, cached owner, EE,
register byte offset and controller base. X0-X7, X16-X17, X9 and LR are saved
around the logger; flags are regenerated before resuming the original code.
That context image introduces no additional MMIO probes, permission writes,
driver bypasses or UART protocol substitutes.

To obtain evidence even without native logger output, the guard places
breadcrumbs in X19 and X20 before the first status read at `0x3790`:

| X19 bits | Meaning |
|:---------|:--------|
| `[63:48]` | Diagnostic tag `0x5A33` |
| `[47:40]` | Cached write owner |
| `[39:32]` | Caller EE |
| `[31:16]` | Local APID/cache index |
| `[15:0]` | Absolute APID (base plus local index) |

| X20 bits | Meaning |
|:---------|:--------|
| `[63:56]` | Diagnostic tag `0xD4` |
| `[55:48]` | Bus ID from context `+0x10` |
| `[47:32]` | Native channel limit from the structure at context `+0x30` |
| `[31:16]` | Base APID from context `+0x44` |
| `[15:0]` | Zero |

This distinguishes local/global indexing and bus context without treating a
hardware-derived APID as a PMIC register number. It does not assume that the
observed absolute APID 640 is the boundary between buses.

The original routine saves caller X19/X20 at `0x3650`, first defines X19 at
`0x3858` and X20 at `0x3850`, then first consumes those definitions at `0x38B8`
and `0x38AC`, respectively. The normal epilogue restores both caller registers.
Thus the diagnostic values are live in the known first-read crash dump without
changing transaction behavior or caller state. These are not persistent crash
logs and need not survive later faults elsewhere in the routine.

The five ARM64 tests pass, including owner/EE/APID/bus/limit decoding at the
real status-read instruction, nonzero APID bases (512 + 128 = 640 and a modeled
bus-1 local index 0 with base 640), preservation of the original owned-write
MMIO trace, and ABI preservation when the logger clobbers X0-X17 and condition
flags. These model values are not measurements from the phone.
The DEBUG build validates 49 PE images. Decompressing the actual
delivered main FV confirms that only SPMI changed from the preceding image and
contains the exact driver executed in the checks; BootShim and DTB are unchanged.

- Context SPMI SHA-256: `4c772616c2e912f47bfe53257ece1087c74f8e28d50fa6474853831ef4ec40d3`.
- `Mu-ziyi-spmi-context.img` SHA-256: `b1b4ffa4129fffb4980d517d91c116d936f8f499ccad38f1841b0fb536c9d056`.

This diagnostic was tested in the fourth video below. It confirms the injected
code executes, but did not fix the ADC/MMIO failure.


Diagnostic upload: [`Mu-ziyi-spmi-context.img`](https://gofile.io/d/SRWUfOii)
(SHA-256 above; temporary `fastboot boot` only).

### Fourth hardware test: static versus live arbiter configuration

`video_2026-11-04_22-39-48.mp4` repeats the abort at SPMI RVA `0x3790`,
`FAR = 0x0C780008`, `ESR = 0x96000010`, and exposes both diagnostic markers:

- `X19 = 0x5A33000002800280`: cached owner 0, caller EE 0, local and absolute
  APID 640.
- `X20 = 0xD400030000000000`: bus 0, configured limit 768, base APID 0.

This proves that the guard executes and admits the write because cached owner
matches EE. It does not prove the current hardware write permission or bus
partition. The original PE's bus context at RVA `0x8160` points to the descriptor
at `0x8124`; that descriptor begins with the constant 768. Thus the captured limit
is a firmware table value, not a measurement of the current controller.

For v7, Linux `_pmic_arb_init_apid_v7` derives each bus's APID count from hardware
FEATURES registers (`core + 4 + 4 * bus`) and accumulates the preceding counts
into its base APID. A mismatch with this prebuilt firmware's static split remains
a hypothesis until those registers are read; neither a bus-0 limit of 640 nor a
different boundary is established by the video.

The current `Mu-ziyi-spmi-hwinfo.img` adds four read-only controller metadata
samples, only after cached ownership matches:

| Register | Lower 32 bits | Upper 32 bits |
|:---------|:--------------|:--------------|
| X22 | Core VERSION at `core + 0` | Raw bus-0 FEATURES at `core + 4` |
| X25 | APID mapping at `core + 0x2000 + 4 * absolute APID` | Owner table at `core + 0x2D000 + 0x5000 * bus + 4 * local APID` |

On the observed bus 0/APID 640 these addresses are `0x0C400000`,
`0x0C400004`, `0x0C402A00`, and `0x0C42DA00`. The mapping/owner-table addresses
are also read by native cache initialization. Core version/features are standard
controller configuration registers, not PMIC peripheral commands.
No ownership/security registers are written and no ADC operation is bypassed.
X19/X20 retain the previous software-context markers.

X22 and X25 are saved by the native prologue and are dead until their definitions
at `0x3854` and `0x3834`, respectively, after the known first-status fault.
Their caller values are restored by the original epilogue.
The larger guard is assembled into verified zero padding at `0x7D00`.
If a metadata read itself aborts, ELR/FAR identify that failure; no exception
handler is suppressed. The image does not claim to fix the hardware failure.

All six ARM64 tests pass. They check the exact four metadata reads before an
otherwise unchanged owned transaction, no reads for a rejected cached owner,
unchanged observer transactions, register/flag preservation, and independently
seeded live version/features/mapping/owner values differing from the static
limit and cached owner. These are model inputs, not phone measurements.
The DEBUG build validates 49 PE images. The actual compressed main FV contains
the tested driver; only SPMI differs from the hardware-tested context image.
PMIC, other main-FV files, BootShim, corrected ARM64 header and DTB are unchanged.

- Hardware-info SPMI SHA-256: `fd5a56f499abcfa2828cbb8fa84a06086f6c89cc367c44cc90141ab3d2c0e7a5`.
- `Mu-ziyi-spmi-hwinfo.img` SHA-256: `2bd3fe37bfa93ba66fe7c61f3516baa6d5df177b43ad68dd7d61b9e2cacc7d2b`.

The fifth video, `video_2026-11-04_22-59-47.mp4`, captured the metadata successfully:
`X22 = 0x8004030070000000` confirms v7 and a hardware bus-0 count of 768.
`X25 = 0x0000000000018900` identifies SID 1/PID `0x89` and live owner 0.
The native table matches the measured count and owner, yet the same initial
write-window status read still aborts. Neither simple owner mismatch nor a
different bus-0 channel count explains this failure. Its cause remains unresolved.

Diagnostic upload: [`Mu-ziyi-spmi-hwinfo.img`](https://gofile.io/d/ymVysroK)
(SHA-256 above; temporary `fastboot boot` only).

### ADC-disabled diagnostic, explicitly approved by the user

The user approved trying the rest of UEFI without the optional ADC service after
the fifth hardware test. This is an explicit capability limitation, not a claim
that the SPMI hardware fault is fixed or that ADC measurements work.

In `PmicDxeLa.efi`, replace the ADC DAL attach call at RVA `0x4088`
(`BL 0x1C52C`, word `0x94006129`) with `B 0x4090` (`0x14000002`).
The existing path returns `EFI_UNSUPPORTED` (`0x8000000000000003`) and restores
the caller frame without executing ADC attachment or installing its protocol.
The entry routine retains its original optional-failure log and accumulated
non-ADC PMIC status. Other PMIC functions and event registrations are unchanged.
This does not power down the physical ADC or change stock Android firmware.

`Resources/Scripts/patch_ziyi_pmic.py` now regenerates this diagnostic by default
from the hash-pinned stock inputs; it also validates the exact ADC call before
changing it. The original stock files are preserved.
`Resources/Scripts/test_ziyi_pmic_adc.py` executes the actual ARM64 helper and
entry tail, rejecting any ADC attach or protocol-installation path.
It verifies unsupported status, stack/callee-register preservation, and that
an earlier PMIC error remains `EFI_DEVICE_ERROR` rather than being cleared.
The regression failed on the preceding binary and passes on this one.

Both ADC tests and all six SPMI tests pass; the DEBUG build validates 49 PE images.
Decoding the actual delivered main FV confirms that only PMIC differs from
`Mu-ziyi-spmi-hwinfo.img`, by exactly the one additional branch instruction.
SPMI, other main-FV files, BootShim, corrected ARM64 header and DTB are unchanged.
These checks do not establish a successful phone boot.

- ADC-disabled PMIC SHA-256: `031a63dbaceddb5eeea8cf35b533e1179815ceb0d06a2f651e5fb64fc85de015`.
- `Mu-ziyi-no-adc.img` SHA-256: `2d7c8aa66c1755f0b019e2e5038367a00aa41e64f6d5df7f3b7c74ff1863fc74`.
- Diagnostic upload: [`Mu-ziyi-no-adc.img`](https://gofile.io/d/ml2kXuXn).

ADC and dependent battery/temperature/charging functions are not supported by
this diagnostic. Other drivers, usable UEFI, and OS handoff still need hardware
validation. Test with `fastboot boot Mu-ziyi-no-adc.img` only, not by flashing.
The native `Unable to install ADC protocol handler` warning is expected if the
stock logger is visible; it is not a fabricated successful ADC initialization.

### UFS activation after the ADC-disabled hardware test

`video_2026-11-05_00-05-12.mp4` progresses past the former PMIC/ADC exception and
reaches UFSDxe. It stops at `ASSERT UFS.c:1770` with `EFI_DEVICE_ERROR`.
Fixed sense `70 00 02 ... 04 02` means `NOT READY / INITIALIZING COMMAND REQUIRED`.
The driver logs site `0x28B`; this is not a CPU data abort.
The response establishes that command exchange works far enough to report sense,
not that all DMA, media, partition access or OS handoff is validated.

The exact stock driver's caller at RVA `0x3564` opens Device WLUN `0xD0`.
Inside `0x98E0`, the initial TUR call at `0x9968` fails before the native
`START STOP UNIT ACTIVE` call at `0x9998`. Native TUR (`0xADC8`) retains its
Unit Attention loop but returns `-5` for this sense. The sense decoder at
`0xA6E4` copies the response into the host's cache at `HBA+0x480`.
An inherited non-Active state is consistent with the log, but its exact power
history is not observed.

`Binaries/garnet/README.md` documents a related UFS wake adaptation on the same
firmware branch. Its stock input differs from ziyi, so its bytes/offsets are
not copied. The ziyi adaptation preserves real TUR and activation error checks:

- Hook `0x9968` into verified executable padding at `0x1BE00`.
  Invalidate only the cached sense header/key word and ASC/ASCQ pair before the
  initial native TUR so stale or truncated sense cannot authorize recovery.
- Preserve native Unit Attention handling. Only actual failure `-5` with fresh
  fixed sense `0x70`, key 2, sufficient additional sense length and ASC/ASCQ
  `04/02` invokes the existing activation routine (`0xAEFC`, mode 1).
- Require actual activation success, then execute native TUR again once.
  Any failure follows the original cleanup at `0x991C`; the ASSERT is retained.
- Hook `0x9988` through `0x1BFC0` to skip the original late activation only when
  the early activation already succeeded. Otherwise keep the original behavior.
  Other LUN paths remain unchanged.

W21 holds the per-open early-activation flag: the original core index is already
stored in the handle at `0x9910`, and the original prologue/epilogue preserve
caller X21. No additional stack frame or global recovery state is allocated.
The only new device command is native `START STOP UNIT ACTIVE` (CDB `1B`,
power-condition byte `10`), not a block write, format, partition modification
or permission change. No generic sleep/retry loop or fake ready result is added.

`Resources/Scripts/ziyi_ufs_wake.S` supplies the hooks;
`Resources/Scripts/patch_ziyi_ufs.py` validates the exact stock image, insertion
instructions and empty padding. `UFSDxe.inf` selects `UFSDxe.patched.efi`.

The six stateful UFS tests execute native open, TUR, command construction,
sense decoding and cleanup. They fail on the original inactive-device path and
pass with the adaptation. Cases cover activation/recheck, Unit Attention,
already-active devices, genuine activation/readiness errors, unrelated/stale/
short sense, other LUNs, core-index preservation and callee registers.
Host setup/descriptor services and the SCSI device are modeled; physical UFS,
DMA, media and complete UEFI are not emulated.
The eight existing PMIC/SPMI tests also pass. The DEBUG build validates 49 PE
images. Decoding the delivered compressed main FV confirms that only UFSDxe
differs from the hardware-tested `Mu-ziyi-no-adc.img`; the exact tested driver
is packaged. ADC stays disabled; PMIC, SPMI, other main-FV files, BootShim,
corrected ARM64 header and DTB are unchanged.

- Stock UFS SHA-256: `e0da9774d815bb2ce22e7de41aa3ec34046c0c7e996ef298fbdd9468eb0e1b61`.
- Adapted UFS SHA-256: `47b4ace45b700d3975027b72a06fd6fac8d00f2e8c97c72f909928490571ecc1`.
- `Mu-ziyi-ufs-wake.img` SHA-256: `7f77daef47cb90364b69c75fad9fbd013642130391a38a0a69096fc9924098e3`.

The next hardware video (`video_2026-11-05_00-53-07.mp4`) passes the previous UFS
assert and reaches Keymaster startup. Initial sense/error logging remains visible
before recovery. This proves continued dispatch, not complete storage validation.

Diagnostic upload: [`Mu-ziyi-ufs-wake.img`](https://gofile.io/d/ljwrPkib)
(SHA-256 above; temporary `fastboot boot` only).

### QSEE / Keymaster failed-start diagnostics

The latest phone video and final photo show an encrypted TZ log, followed by
`QseeAppStartSyscall Failed 1`, Keymaster load failure, label fallback status 14,
and `ASSERT QseeComDxe.c:212`. The actual module is stock `TzDxeLA.efi`.
`Failed 1` is a literal callsite label, not the underlying error code.

Disassembly shows that the primary path locates a BlockIo partition by type GUID
`a11d2a7c-d82a-4c2f-8a01-1805240e6626`, reads its contents, and calls SCM command 1.
The start wrapper discards its nonzero SCM protocol status, clears the returned
AppID, dumps TZ diagnostics and returns zero. Its caller returns `EFI_LOAD_ERROR`.
Only the later fallback using the UTF-16 label `keymaster` returns
`EFI_NOT_FOUND`. The final status therefore does not prove a missing primary
image, damaged firmware or a signature mismatch.

The downloaded stock firmware archive contains `firmware-update/keymaster.img`:
352256 bytes, ELF64 magic `7F 45 4C 46`, SHA-256
`7ec3c01c59c27b5393619b4f9a60b702f61d5ada899a290f06a5794724cb1031`.
It is not added to the UEFI FV or written to the phone. The payload actually
read from the user's installed partition is not yet verified.

The historical `patch_ziyi_qsee_diag.py` / `ziyi_qsee_diag.S` implementation instrumented only the failed-start
branch at RVA `0x1E48`, using verified zero executable padding at `0xE100`.
After the original encrypted TZ dump, the diagnostic prints:

```text
ziyi QSEE SCM=... MDT=... IMG=... MAGIC=... K=... K64=...
```

- `SCM`: original 64-bit EFI status from the SCM protocol, not a decoded raw
  Secure World response.
- `MDT` / `IMG`: original metadata/image lengths, in hexadecimal.
- `MAGIC`: first four bytes interpreted little-endian; ELF is `464C457F`.
  Null buffers and lengths below four are not dereferenced.
- `K` / `K64`: genuine native read-only SCM command-3 lookup results for
  `keymaster` / `keymaster64`. Zero means absent **or** lookup error.
  Positive IDs are printed only; they never replace the failed start result.

No security flags, signature/rollback checks, signed-app bytes or assertions are
changed. The failed start still returns zero, frees its request, and follows
the original fallback/error path. Successful startup executes no diagnostic or
additional queries. ADC remains unavailable as previously approved.

Three native ARM64 regression tests cover unchanged successful handles, failed
starts remaining failed even when lookup reports resident apps, short/null
input safety, cleanup, SP and callee-saved registers. SCM, allocation and logging
boundaries are modeled; this does not emulate TrustZone authentication.
A separate smoke run executed the driver's actual `DebugPrint` and
`AsciiVSPrint`, observing correctly formatted metadata at the serial boundary;
it does not prove physical display output.
All 17 PMIC/SPMI/UFS/QSEE native regression tests pass. The DEBUG build verifies
49 PE images. Decoding the delivered compressed main FV confirms that only
TzDxeLA differs from `Mu-ziyi-ufs-wake.img`, and its PE payload is byte-identical
to the emulated diagnostic driver. BootShim/header, DTB and all other main-FV
files are unchanged.

- Stock TzDxeLA SHA-256: `7c7281b15b64a47ec9e112ee3a397fca8dc45d74714f51ebc81edc357c47bbd9`.
- Diagnostic TzDxeLA SHA-256: `78df7d9cd10046883b6fb86830bc9f72321b5122058ac75c7ea6983de6d6e468`.
- `Mu-ziyi-qsee-diag.img`: 3551232 bytes; SHA-256 `15d17165007b0e0210eb334b680316bb943b0161a9dc79a6192cdb20f43fdc17`.

Diagnostic upload: [`Mu-ziyi-qsee-diag.img`](https://gofile.io/d/wGtjivIq).
Temporary `fastboot boot` only; this image adds evidence, not a Keymaster fix.

The subsequent phone photo reports `SCM=8000000000000007 MDT=0 IMG=100000
MAGIC=464C457F K=0 K64=1`: the start returns `EFI_DEVICE_ERROR`, the buffer begins
with ELF magic, and the native lookup finds a resident `keymaster64`, AppID 1.
This supports testing resident reuse; it does not prove that duplicate loading
is the sole cause of the start failure or that all image bytes are correct.

### Reusing the resident Keymaster

The current adaptation checks for the existing `keymaster64`, then `keymaster`,
before the bootstrap's native GUID image load. It calls the same native SCM
command-3 lookup used by public `QseecomStartApp`; it does not invoke that public
entry recursively. Only a genuine nonzero/non-`FFFFFFFF` AppID permits successful
bootstrap completion. No fabricated ID, security flag change, patched signed app,
authentication bypass, or partition write is involved.

The hook replaces the ADRP at `0x3060` with a branch to verified executable
padding at `0xE400`. If neither lookup succeeds, it restores the displaced ADRP
and resumes at `0x3064`: the exact original image loading, fallback and ASSERT
remain reachable. Existing common-library setup and SecurityFlag gating are
unchanged. Failed-start diagnostics at `0xE100` remain available.

On the resident path the expected message is:

```text
ziyi QSEE reuse resident Keymaster AppID=1
```

Four native bootstrap regressions cover resident 64-bit/unsuffixed apps,
missing apps, failed lookups, invalid IDs, normal image-load success, genuine
load failure and disabled-policy gating. The original driver asserts in the
modeled resident-AppID-1 scenario; the adaptation returns success without
loading a duplicate image. Callee registers and SP are checked.
A separate smoke executes native bootstrap, native lookup and native
`DebugPrint`/formatting with modeled external services, observing the message
above and zero image loads. This is not a phone or Secure World emulator;
the new path still requires a user `fastboot boot` test.

- Resident-adapted TzDxeLA SHA-256: `1128a43028a72cf13a607a7a1ad4884beed9bc0af6bd7db95a35a3613f4eca02`.
- `Mu-ziyi-keymaster-reuse.img`: 3551232 bytes; SHA-256 `76a82c2fcd04e301a819bada198b9c3789ab58a03f73ed308888fa274c8b3799`.

All 21 native PMIC/SPMI/UFS/QSEE/bootstrap tests pass; the DEBUG build verifies
49 PE images. Decoding the final compressed main FV confirms that only
TzDxeLA differs from `Mu-ziyi-qsee-diag.img` and that its bytes match the
emulated adaptation exactly. All other main-FV files, BootShim/header and DTB
are unchanged.

Download: [`Mu-ziyi-keymaster-reuse.img`](https://gofile.io/d/YIjIaouC).
Use `fastboot boot Mu-ziyi-keymaster-reuse.img`, never flash.
The subsequent `video_2026-11-05_01-42-11.mp4` passes the former QSEE assert,
shows the Project Silicium graphical boot flow and ends at
`Failed to Find an Operating System!`. The user opens the boot-device menu and
confirms working volume navigation, but short power presses do not confirm.

### Power-button and EFI-key observation

The preceding observation-only image does not remap buttons, invent Enter events,
change PMIC configuration, or bypass input errors. Its original generator validated
the stock ButtonsDxe hash and executable/data padding. That image selected
`ButtonsDxe.diagnostic.efi`; the current quiet image selects `.patched.efi`.

The historical `ziyi_buttons_diag.S` wrapped the existing power read at `0x3E10`, preserving the
single native PMIC device-0 / IRQ-selector-0 query and its actual status/output.
The state at `0x8F00` records the last observed status, raw byte and poll count.
Logs occur on the first poll and status/value transitions only:

```text
ziyi PWR s=0 v=0 n=1
ziyi PWR s=0 v=1 n=2
```

`s` is the hexadecimal EFI status. `v` is the raw PMIC result; `FF` means unknown
after an error, not a valid button state. `n` counts polls, not elapsed time.
The hook does not dereference the output on error or modify it.

The second hook at `0x3998` preserves the native queue-count store and reports
each emitted EFI key without changing its bytes:

```text
ziyi KEY sc=0 uc=D ps=0 pv=1 n=2 seen=1
```

`sc`/`uc` are hexadecimal scan code/Unicode. `uc=D` with `sc=0` is Enter.
`ps`/`pv`/`n` snapshot the latest power read; `seen=0` means none observed yet.
These values distinguish PMIC read errors, a constant raw value, and key
translation/output problems without asserting which one caused the phone report.

Four native regressions compare stock/adapted power statuses and output,
volume/Enter/empty/chord translation, held-key suppression/rearming, SP and all
callee registers; constant power does not flood the log. PMIC and logger
boundaries are modeled. A separate smoke executes actual polling, translation,
DebugPrint and formatting with modeled power transitions/error, observing both
diagnostic lines at the serial boundary. The subsequent phone photo confirms
visible logs: successful PMIC reads toggle `v=0` / `v=1`, while power emits
`ziyi KEY sc=102 uc=0 ps=0 pv=1 ...`. This localizes confirmation failure to
key mapping rather than an absent power signal.

- Stock ButtonsDxe SHA-256: `7aade0b3b2b874b41dffbba5770e3212abd0497a5ae6abfaebb3709aa9b2f86a`.
- Diagnostic ButtonsDxe SHA-256: `6cc1ee5f3fab064fa213154cdaee28cd6023ebfeea5ac4c10d9c6b4c03495bca`.
- `Mu-ziyi-buttons-diag.img`: 3551232 bytes; SHA-256 `5a0da1fb3375572e5aae6e9d763ec8675d562fc42dd48ad12cc02fc8db2f14bc`.

All 25 native regressions pass; the DEBUG build verifies 49 PE images.
Decoding the delivered compressed main FV confirms that only ButtonsDxe differs
from `Mu-ziyi-keymaster-reuse.img`, and its bytes match the exercised diagnostic
driver. All other main-FV files, BootShim/header and DTB are unchanged.

Download: [`Mu-ziyi-buttons-diag.img`](https://gofile.io/d/2FpouV2W).

Phone procedure: temporary `fastboot boot` only; record continuously, open the
same menu, press/release one volume button, press/release power three times,
then press/release a volume button again. Capture `ziyi PWR` / `ziyi KEY` lines
and the resulting screen. No long power hold, flashing, formatting or menu
confirmation is required for this diagnostic.

### Power confirmation mapped to native Enter

The phone-confirmed power event reaches the translator's logical-key-1 branch
at `0x39F4`, which generates scan `0x102`, Unicode zero. The menu requests Enter.
The earlier synthetic key-5 smoke proved an Enter path existed, not that the
physical power button selected it. The hardware diagnostic resolves that gap.

The current generator changes only one additional instruction versus the tested
observation image: `0x3A00` branches to `0x39D0` instead of `0x396C`.
This reuses the existing native Unicode-CR generator. The translator has already
zeroed the four-byte EFI_INPUT_KEY, so the resulting event is scan zero,
Unicode `0x0D`. No new input is generated without the original power event.
Other key/chord priorities, queue operations, held-key suppression, release
rearming, native PMIC status/output and diagnostics are unchanged.

The real-power-event regression fails before this mapping and passes afterward.
Two additional cases cover logical-key-1 Enter generation and hold/release/
repress transitions; all six button regressions pass. A smoke executes the
actual corrected native path and formatter with modeled PMIC input, observing:

```text
ziyi PWR s=0 v=1 n=2
ziyi KEY sc=0 uc=D ps=0 pv=1 n=2 seen=1
```

This is native-code verification, not a physical menu test. On the next phone
test, select Exit with volume and briefly press/release power. Capture the
diagnostic line and whether the menu closes. Do not select formatting or mass
storage, hold power, or flash the image.

- Power-adapted ButtonsDxe SHA-256: `459666981d13b7a6c094df7c3383f9a3a2fed7c630394bfb86c3989e7c775d62`.
- `Mu-ziyi-power-enter.img`: 3551232 bytes; SHA-256 `f1154879a0ba12be4803d086a8f9be573e42b793064a3d936ee3822dde1dac00`.

All 27 native regressions pass; the DEBUG build verifies 49 PE images.
Decoding the delivered compressed main FV confirms that only ButtonsDxe differs
from the phone-tested `Mu-ziyi-buttons-diag.img`, its bytes match the exercised
power adaptation, and the driver delta is limited to the instruction at `0x3A00`.
All other main-FV files, BootShim/header and DTB are unchanged.

Download: [`Mu-ziyi-power-enter.img`](https://gofile.io/d/FYxejyN6).
Use `fastboot boot Mu-ziyi-power-enter.img`, never flash. The user subsequently
confirmed power-button selection works and another Android phone detects USB
Mass Storage. Actual file reads and operating-system boot remain unverified.

### Memory and runtime limitations

- FD is 3 MiB at `0xA7100000`; the primary stack is at `0xA760D000`, size `0x40000`.
  The map follows the extracted stock `uefiplat.cfg`. Its overlapping PIL and
  Demura reservations are split without releasing any reserved address.
  The stock optional `AddDynamicMem` HYP entry at `0x830000000` is not installed
  as physical RAM on this 8 GB device.
- Android ramoops at `0xA7000000..0xA7400000` overlaps the stock UEFI FD by boot
  stage. Entering this UEFI overwrites previous ramoops contents.
- SimpleFB is selected at 1080x2400x32; stock panel reset is not invoked.
  User video confirms early text and later graphical boot-manager output.
  Continued scanout across OS handoff remains unvalidated.
- Clock and USB drivers remain stock and have not been validated for
  re-entry after Android's bootloader. Power selection and volume navigation are
  phone-confirmed; another Android phone detects USB Mass Storage. The quiet
  build removes added input/SPMI/QSEE diagnostics while retaining UFS activation,
  resident Keymaster reuse and power-to-Enter. PMIC/SPMI omit the two documented
  startup configuration passes; SPMI also checks cached write ownership.
  Later hardware operations still need testing. SimpleFB alone does not
  eliminate other initialization risks.
- No ziyi ACPI tables or Windows drivers are supplied. Neither Windows nor Linux
  boot is validated. The phone is not directly connected to the build host;
  user-supplied video is the available hardware evidence.

Do not flash this experimental image over stock boot, XBL, UEFI or other firmware
partitions. Hardware bring-up requires a recoverable test setup and boot logs;
no partition-writing command is part of this port.
