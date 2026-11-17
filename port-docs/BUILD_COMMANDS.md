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
```bash
tools/bazel build --config=fast //common:kernel_aarch64_dist
```

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

## 4. Expected Errors & Static Warnings

| File / Component | Potential Failure Point | Root Cause & Resolution |
|---|---|---|
| `drivers/clk/mediatek/clk-mt6983.c` | Type mismatch in `mtk_clk_register_*` | 6.18 requires `struct device *` as first parameter. If custom PLL registration complains, ensure `pdev->dev` is passed. |
| `drivers/pinctrl/mediatek/pinctrl-mt6983.c` | Unknown field `.remove` | 6.18 Paris pinctrl handles removal internally; keep `.remove` omitted or typed `void (*remove)(struct platform_device *)`. |
| `scripts/dtc/dtc` | `-@` overlay resolution warning | Base DTS nodes require `#address-cells` and `#size-cells` for overlay plugins to attach cleanly. |
| `rust/bindgen` | Missing LLVM `libclang` | If `CONFIG_RUST=y` fails to locate bindgen, ensure `export BINDGEN_EXTRA_CLANG_ARGS` points to target sysroot. |

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
