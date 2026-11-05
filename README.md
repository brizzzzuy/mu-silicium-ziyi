# Mu-Silicium for Xiaomi 13 Lite (ziyi)

<!-- ![Banner](https://github.com/Project-Silicium/Mu-Silicium/blob/main/Resources/Pictures/Banner.png) -->

Experimental Xiaomi 13 Lite port of [Project Silicium](https://github.com/Project-Silicium/Mu-Silicium).
Target: Snapdragon 7 Gen 1, SM7450 / Diwali, 8 GB RAM, 1080x2400 display.

## ziyi status

- Graphical UEFI boot-device menu, volume navigation and power-button confirmation work on the test phone.
- Another Android phone detects USB Mass Storage; complete storage I/O is not validated.
- ADC is intentionally unavailable. No Windows/Linux boot, ziyi ACPI tables or Windows drivers are supplied.
- Added bring-up traces are removed; native DEBUG output and real errors remain.

**Test with `fastboot boot` only. Do not flash this experimental image over Android boot or other firmware partitions.**

## Build the ziyi port

Install native build dependencies described in [Building.md](Building.md#xiaomi-13-lite-ziyi), then:

```bash
git clone --recurse-submodules https://github.com/wannqn/mu-silicium-ziyi.git
cd mu-silicium-ziyi
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r pip-requirements.txt pefile unicorn

# Binaries is an upstream submodule: install the tracked ziyi vendor overlay.
cp -a Resources/DeviceBinaries/ziyi Binaries/
python Resources/Scripts/patch_ziyi_pmic.py
python Resources/Scripts/patch_ziyi_ufs.py
python Resources/Scripts/patch_ziyi_qsee.py
python Resources/Scripts/patch_ziyi_buttons.py

export CLANGPDB_AARCH64_PREFIX=aarch64-linux-gnu-
python build_uefi.py -d ziyi -r DEBUG
```

Output: `Mu-ziyi.img`. Test from a host with Android platform-tools:

```text
fastboot boot Mu-ziyi.img
```

See [build notes and firmware provenance](Building.md#xiaomi-13-lite-ziyi) for limitations,
native regression commands and bring-up evidence. Vendor firmware inputs are tracked
under `Resources/DeviceBinaries/ziyi`; patched drivers are regenerated, not committed.


## Description

This Project focuses on Making ARM-Based Devices Boot Operating Systems like Windows or Linux using Custom UEFI Firmware.

## Resources

- [Status](Status.md)
- [Building](Building.md)
- [Guides](https://github.com/Project-Silicium/Guides/blob/main/README.md)
- [Discord Server](https://discord.gg/Dx2QgMx7Sv)

## Frequently asked Questions

### **Is my Device Supported in this Project?**
- To Check if your Device is Supported, Take a Look at the Status Page Referenced in the Section Above.

### **What do I do if my Device isn't Supported in this Project?**
- We made some Guides that Explain How to Port your Device that are Referenced in the Section Above.

## Credits

[Microsoft](https://github.com/microsoft/) for their [Project Mu](https://microsoft.github.io/mu/) which Powers this Project. <br>
[WOA-Project](https://github.com/WOA-Project/) for their [mu_andromeda_platforms](https://github.com/WOA-Project/mu_andromeda_platforms/) which is used as Base for this Project. <br>
[Project Aloha](https://github.com/Project-Aloha/) for their [mu_aloha_platforms](https://github.com/Project-Aloha/mu_aloha_platforms/) which is used as Reference for some SoCs. <br>
[Open Surface RT](https://openrt.gitbook.io/open-surfacert/) for their Help on Tegra Related Stuff.

[sonic011gamer](https://github.com/sonic011gamer/) and [halal-beef](https://github.com/halal-beef/) for their Amazing Work on Exynos Related Stuff.

## License

All code except drivers in `GPLDrivers` & `GPLApplications` & `GPLLibrary` directories are licensed under BSD-2-Clause. <br />
GPL Drivers are licensed under `GPLv2` or later license.

The extracted vendor firmware inputs in `Resources/DeviceBinaries/ziyi` are not
open-source driver implementations and are not relicensed by this fork. Their
original ownership and licensing apply; provenance is recorded in `Building.md`.
