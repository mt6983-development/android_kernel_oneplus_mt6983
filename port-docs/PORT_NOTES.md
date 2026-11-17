# OnePlus Nord 3 (vitamin, MT6983) GKI 6.18 Port Notes

## 1. Executive Strategy & GKI Architecture

- **Target Device:** OnePlus Nord 3 5G (`vitamin` / `OP595DL1`, MediaTek MT6983 / Dimensity 9000).
- **Target Kernel Base:** Android Common Kernel (ACK) branch `android17-6.18`, release tag `android17-6.18-2026-09_r14` (commit `26c72498ee16574e937fb78bfbbdd2c4ddf3e806`), Linux kernel version **6.18.32**.
- **Reference 5.10 Tree:** `upstream-5.10.269` (`lineage-24.0` ancestry at Linux 5.10.269), preserved as the read-only source of vendor code.
- **Port Strategy:** Clean port on top of ACK 6.18 release history (not a git merge, as 5.10 vendor trees cannot be cleanly merged into 6.18 git history).
- **GKI Modularity:**
  - Core GKI kernel (`Image`) kept as close to upstream ACK as possible.
  - SoC platform bring-up drivers (clocks, pinctrl, SPMI, PMIC, UFS host) integrated using upstream MediaTek subsystem frameworks (CCF, `pinctrl-paris`, `ufs-mediatek`, `spmi-mtk-pmif`).
  - Out-of-tree vendor modules (`vendor_boot` and `vendor_dlkm`) adapted to 6.18 exported APIs.
  - Page Size: **4K pages** (`CONFIG_ARM64_4K_PAGES=y`), matching OnePlus Nord 3 hardware and vendor userspace.
  - Boot Image Header Version: **v4** (`boot.img` GKI kernel, `init_boot.img` generic ramdisk, `vendor_boot.img` vendor ramdisk + DTB + first-stage modules, `dtbo.img` board overlays).

---

## 2. Build Model & Toolchain

### Kleaf / Bazel Build Model
ACK 6.18 deprecates legacy `build.sh` / `build.config` wrappers and uses Kleaf (`tools/bazel`).
- Kernel targets: `//common:kernel_aarch64`, `//common:kernel_aarch64_dist`
- Device / Vendor target pattern:
  - Base kernel: `:kernel_aarch64`
  - Defconfig: `arch/arm64/configs/gki_defconfig` + vendor fragment
- Alternative / Standalone Make invocation:
  For developers building outside Bazel in a standalone checkout:
  `make ARCH=arm64 LLVM=1 -C kernel-5.10 ...`

### Toolchain Requirements
- **Compiler:** Clang 18+ (AOSP prebuilt `clang-r522817` or system LLVM/Clang 18+)
- **Linker & Utilities:** `lld`, `llvm-objcopy`, `llvm-nm`, `llvm-strip`
- **Rust Toolchain:** `rustc 1.77+`, `bindgen` (required as `CONFIG_RUST=y` is enabled in ACK 6.18 `gki_defconfig`)
- **Host Tools:** Python 3.10+, GNU Make 4.3+, `bison`, `flex`, `libssl-dev`, `pahole` (dwarves 1.25+)

---

## 3. Subsystem Substitutions & Upstream Alignments

In accordance with BOOT-FIRST RULE 3 and guideline B4, upstream equivalents are preferred over carrying obsolete 5.10 vendor implementations:

1. **UFS Host Controller:**
   - *5.10 Vendor:* Custom `ufs-mediatek-mod.ko` with out-of-tree wrappers.
   - *6.18 Solution:* Mainline upstream `drivers/ufs/host/ufs-mediatek.c`. Upstream already includes direct support for `mediatek,mt8183-ufshci` (which MT6983 hardware uses) with standard crypto and clock management.
2. **Earlycon / Serial Console:**
   - *5.10 Vendor:* Custom MTK serial wrapper.
   - *6.18 Solution:* Upstream `drivers/tty/serial/8250/8250_mtk.c` via `earlycon=mtk8250,0x11001000`. Clean upstream support with zero out-of-tree patches.
3. **Pinctrl:**
   - *5.10 Vendor:* `pinctrl-mt6983.c` utilizing `pinctrl-paris.h`.
   - *6.18 Solution:* Ported `pinctrl-mt6983.c` onto 6.18's upstream `pinctrl-paris` subsystem, adapting to the updated `platform_driver` `.remove` callback (void return).
4. **Common Clock Framework (CCF):**
   - *5.10 Vendor:* Out-of-tree `clk-mt6983.c` with CCF gates, muxes, and composite clocks.
   - *6.18 Solution:* Integrated into `drivers/clk/mediatek/` using 6.18 CCF APIs, registering topckgen, apmixedsys, infracfg, and pericfg clock controllers.
5. **SPMI / PMIC:**
   - *5.10 Vendor:* `spmi-mtk-pmif-core.c` with out-of-tree debug registers.
   - *6.18 Solution:* Extended upstream `drivers/spmi/spmi-mtk-pmif.c` with MT6983 register definitions (`mt6xxx_regs` / `mt6853_spmi_regs`) and USID mapping.
6. **IOMMU:**
   - *5.10 Vendor:* Out-of-tree `drivers/misc/mediatek/iommu/`.
   - *6.18 Solution:* Upstream `drivers/iommu/mtk_iommu.c` handling SMI larbs and multi-bank translation.
7. **USB Device Controller (UDC):**
   - *5.10 Vendor:* Custom `udc_lib` + composite gadget.
   - *6.18 Solution:* Upstream `drivers/usb/mtu3/mtu3_plat.c` (`compatible = "mediatek,mtu3"`) and Linux standard ConfigFS USB gadget with Android ADB function.

---

## 4. API Drift Adaptations (5.10 -> 6.18)

Every ported driver was verified against 6.18 tree API changes:
- **Driver Removal:** `platform_driver.remove` changed from `int (*remove)(struct platform_device *)` to `void (*remove)(struct platform_device *)`. All ported drivers updated.
- **Timers:** Transitioned `del_timer()` / `del_timer_sync()` to `timer_delete()` / `timer_delete_sync()`.
- **String APIs:** `strlcpy()` replaced with `strscpy()`.
- **Memory Management:** VMA flags set via `vm_flags_set()`; replaced deprecated ashmem and legacy ION allocations with DMA-BUF heaps.
- **Scheduler:** CFS replaced by EEVDF; vendor energy-aware scheduling hooks decoupled from M0 boot path.
