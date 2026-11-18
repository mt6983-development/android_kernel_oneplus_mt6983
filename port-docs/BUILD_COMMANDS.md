# OnePlus Nord 3 (vitamin, MT6983) Build & Bringup Commands

> **IMPORTANT:** In accordance with HARD RULE 1, NO compilation commands were run during repository preparation. All build commands below are provided for the user to execute in a suitable build environment equipped with Clang 18+ and Rustc/bindgen.

---

## 1. Environment Setup

```bash
# Set environment variables for LLVM/Clang cross-compilation
export ARCH=arm64
export SUBARCH=arm64
export LLVM=1
export LLVM_IAS=1
export CROSS_COMPILE=aarch64-linux-gnu-

# Path to kernel source tree
export KERNEL_DIR=/home/adarsh027/kernel/kernel-5.10
export OUT_DIR=${KERNEL_DIR}/out/ack-6.18
export DIST_DIR=${OUT_DIR}/dist

mkdir -p ${OUT_DIR} ${DIST_DIR}
```

---

## 2. Configuration & Build Commands

### Variant A: Normal Release Build (Milestone M0)

```bash
cd ${KERNEL_DIR}

# 1. Generate base defconfig + vitamin fragment
make O=${OUT_DIR} gki_defconfig
${KERNEL_DIR}/scripts/kconfig/merge_config.sh -m -O ${OUT_DIR} \
    ${OUT_DIR}/.config \
    ${KERNEL_DIR}/arch/arm64/configs/vitamin_gki.fragment

make O=${OUT_DIR} olddefconfig

# 2. Build Kernel Image, DTBs, and In-Tree Modules
make -j$(nproc) O=${OUT_DIR} Image mediatek/mt6983.dtb mediatek/oplus6983_22823.dtbo modules

# 3. Stage build outputs
cp ${OUT_DIR}/arch/arm64/boot/Image ${DIST_DIR}/
cp ${OUT_DIR}/arch/arm64/boot/dts/mediatek/mt6983.dtb ${DIST_DIR}/
cp ${OUT_DIR}/arch/arm64/boot/dts/mediatek/oplus6983_22823.dtbo ${DIST_DIR}/
```

### Variant B: Debug Diagnostic Build (Verbose Earlycon + Ramoops)

```bash
cd ${KERNEL_DIR}

# Merge with debug fragment (BOOT-FIRST RULE 4)
${KERNEL_DIR}/scripts/kconfig/merge_config.sh -m -O ${OUT_DIR} \
    ${OUT_DIR}/.config \
    ${KERNEL_DIR}/arch/arm64/configs/vitamin_debug.config

make O=${OUT_DIR} olddefconfig

# Compile debug image
make -j$(nproc) O=${OUT_DIR} Image mediatek/mt6983.dtb mediatek/oplus6983_22823.dtbo modules
cp ${OUT_DIR}/arch/arm64/boot/Image ${DIST_DIR}/Image-debug
```

### Variant C: Bazel / Kleaf Build (AOSP Standard)

If using a full AOSP workspace with Kleaf:

> **Note:** Kleaf `*_dist` targets are `pkg_install` executable rules. Use `tools/bazel run` to execute the installer and stage files into `out/.../dist/`. (Using `tools/bazel build` only compiles into `bazel-bin/` without copying out).

### `--config=fast` Flag Details (Kleaf Configuration)
The `--config=fast` option is defined in `build/kernel/kleaf/bazelrc/fast.bazelrc` and sets:
- `--@kleaf//build/kernel/kleaf:config_fast`: Signals Kleaf rules to enable optimizations for developer turnaround.
- `--config=local`: Inherits from `build/kernel/kleaf/bazelrc/local.bazelrc`, setting `--@kleaf//build/kernel/kleaf:config_local` and `--strategy=KernelModuleProcessWrapperSandbox=processwrapper-sandbox`. This minimizes Bazel action sandboxing overhead to maximize local build performance.
- **LTO Mode:** In ACK 6.18 Kleaf, the legacy `--lto` flag is deprecated/no-op; LTO mode is dictated directly by Kconfig. For `vitamin`, `arch/arm64/configs/vitamin_gki.fragment` configures `CONFIG_LTO_CLANG=y` and `CONFIG_LTO_CLANG_THIN=y` (ThinLTO), which is preserved during fast builds.

1. **OnePlus Nord 3 (vitamin) Release Distribution:**
   Builds the kernel Image with `vitamin_gki.fragment`, MT6983 base DTB, OnePlus Nord 3 board DTBO, and modules:
   ```bash
   tools/bazel run --config=fast //common:vitamin_dist
   ```
   Artifacts are staged to `out/vitamin/dist/`:
   - `Image`
   - `mt6983.dtb`
   - `oplus6983_22823.dtbo`
   - In-tree `.ko` modules

2. **OnePlus Nord 3 (vitamin) Debug Diagnostic Distribution:**
   Builds with verbose earlycon, boottime tracing, ftrace, and ramoops diagnostic config:
   ```bash
   tools/bazel run --config=fast //common:vitamin_debug_dist
   ```
   Artifacts are staged to `out/vitamin_debug/dist/`.

3. **Generic Kernel Image (GKI) Only:**
   ```bash
   tools/bazel run --config=fast //common:kernel_aarch64_dist
   ```
   Artifacts are staged to `out/kernel_aarch64/dist/`.

---

## 3. Image Packaging & Staging

```bash
# Package DTBO image
mkdtboimg create ${DIST_DIR}/dtbo.img ${DIST_DIR}/oplus6983_22823.dtbo

# Package vendor_boot.img (Header Version 4)
mkbootimg \
    --header_version 4 \
    --kernel ${DIST_DIR}/Image \
    --dtb ${DIST_DIR}/mt6983.dtb \
    --ramdisk /path/to/extracted/vendor_ramdisk.cpio.gz \
    --cmdline "earlycon=mtk8250,0x11001000 console=ttyS0,921600n8 loglevel=8 androidboot.hardware=mt6983" \
    --output ${DIST_DIR}/vendor_boot.img
```

---

## 4. Expected Errors & Resolved Build Fixes

The BUILD AND FIX loop on branch `upstream-6.18` resolved the following build issues:

| Component / File | Error / Failure Encountered | Root Cause & Resolution |
|---|---|---|
| `scripts/gendwarfksyms.h` | `fatal error: 'dwarf.h' file not found` | `CONFIG_GENDWARFKSYMS=y` requires `libdw-dev`. Enabling `CONFIG_LTO_CLANG_THIN=y` in `.config` and `vitamin_gki.fragment` disables gendwarfksyms (`depends on !LTO`). |
| `arch/arm64/boot/dts/mediatek/oplus6983_22823.dtbo` | `No rule to make target '.../oplus6983_22823.dtbo'` | Kbuild 6.18 rules generate `.dtbo` overlay targets strictly from `.dtso` source files (`scripts/Makefile.dtbs`). Renamed `oplus6983_22823.dts` to `oplus6983_22823.dtso`. |
| `scripts/Makefile.dtbs` | `fatal error: 'mediatek/...dtsi' file not found` | Upstream DTC search paths only included `scripts/dtc/include-prefixes`. Added `$(srctree)/arch/$(SRCARCH)/boot/dts` and `$(srctree)/arch/$(SRCARCH)/boot/dts/mediatek` to `DTC_INCLUDE`. |
| `include/dt-bindings/memory/mtk-memory-port.h` | `Unexpected 'MTK_M4U_PORT_ID'` / syntax error | Upstream memory port header was missing 64-larb macro definition. Added `MTK_M4U_PORT_ID`, `MTK_M4U_DOM_ID`, and table extraction macros. |
| `drivers/pinctrl/mediatek/pinctrl-paris.h` | `call to undeclared function 'MTK_PIN_NODRV'` / `MTK_PIN_EINT` | Upstream 6.18 Paris header omitted non-driving and external eint pin macros; restored definitions and default `EINT_NO_GPIO 9999`. |
| `drivers/pinctrl/mediatek/pinctrl-mt6983.c` | Incompatible struct types (`mtk_eh_pin_pinmux`, `FLAG_RACE_FREE_ACCESS`) | Adapted `mt6983_data` to 6.18 Paris pinctrl API using standard `mt6983_pinctrl_register_base_names` (14 IOCFG bases) and `PINCTRL_PIN_REG_DRV_ADV`. |
| `drivers/clk/mediatek/clk-mux.h` | `call to undeclared function 'MUX_HWV'` | Mapped `MUX_HWV` to 6.18 `MUX_GATE_HWV_FENC_CLR_SET_UPD_FLAGS` with `mtk_mux_gate_hwv_fenc_clr_set_upd_ops`. |
| `drivers/clk/mediatek/clk-mtk.h` | `use of undeclared identifier 'CLK_USE_HW_VOTER'` | Defined `CLK_USE_HW_VOTER 0` as upstream CCF handles voting in 6.18. |
| `drivers/clk/mediatek/clk-mt6983.c` | `array has incomplete element type 'const struct mtk_pll_data'` | `struct mtk_pll_data`, `HAVE_RST_BAR`, and `PLL_AO` moved to `clk-pll.h` in 6.18. Added `#include "clk-pll.h"` and simplified `PLL_HV` to wrap `PLL`. |
| `common/arch/arm64/configs/vitamin_gki.fragment` | `check_defconfig` mismatches: `CONFIG_RUST`, `CONFIG_GENDWARFKSYMS`, `CONFIG_ASHMEM`, `CONFIG_ANDROID_BINDER_IPC_RUST`, `CONFIG_RUST_INLINE_HELPERS`, `CONFIG_DM_VERITY_AVB`, `CONFIG_EROFS_FS_ZIP_LZ4`, `CONFIG_USB_CONFIGFS_F_ACC`, `CONFIG_OPLUS_CHG`, `CONFIG_OPLUS_CHG_V2`, `CONFIG_UFF_FINGERPRINT` | Thin LTO (`CONFIG_LTO_CLANG_THIN=y`) forced `CONFIG_GENDWARFKSYMS` off, cascading into disabled `CONFIG_RUST` and dependent Rust modules. Obsolete and out-of-tree symbols also failed `check_defconfig`. Aligned fragment with 6.18 ACK standards by removing LTO overrides and obsolete/out-of-tree symbols. |
| `common/BUILD.bazel` | `KernelBuild` error: `The following kernel modules are built but not copied. Add these lines to the module_outs attribute of @@//common:vitamin` | In-tree modules built by `kernel_build` were not declared in `module_outs`. Defined `_VITAMIN_MODULE_OUTS` with the complete list of 126 in-tree modules and wired `module_outs = _VITAMIN_MODULE_OUTS` to `:vitamin` and `:vitamin_debug`. |

---

## 5. First-Boot Procedure on Hardware

1. **Back up existing partitions:**
   ```bash
   adb reboot bootloader
   fastboot fetch boot boot_backup.img
   fastboot fetch vendor_boot vendor_boot_backup.img
   fastboot fetch dtbo dtbo_backup.img
   ```
2. **Flash vbmeta with verification disabled:**
   ```bash
   fastboot --disable-verity --disable-verification flash vbmeta vbmeta.img
   ```
3. **Flash test images:**
   ```bash
   fastboot flash boot ${DIST_DIR}/Image
   fastboot flash vendor_boot ${DIST_DIR}/vendor_boot.img
   fastboot flash dtbo ${DIST_DIR}/dtbo.img
   ```
4. **Boot and collect logs:**
   ```bash
   fastboot reboot
   ```
   If boot stalls, hold `Power + Vol Down` to re-enter fastboot or recovery, then dump `/sys/fs/pstore/` via recovery adb.
