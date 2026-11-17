# OnePlus Nord 3 (vitamin, MT6983) Device Tree & ROM Integration Notes

## 1. Boot Image & Partition Layout Comparison

| Parameter | 5.10 Working Layout | 6.18 GKI Layout | Changes / Requirements |
|---|---|---|---|
| **Boot Header Version** | v4 | v4 | Maintained. GKI standard layout. |
| **`boot.img`** | Kernel `Image.gz` (vendor custom) | Generic Kernel Image `Image` (uncompressed ACK GKI) | Switched from custom 5.10 kernel to 6.18 GKI. |
| **`init_boot.img`** | Generic ramdisk (first-stage init) | Generic ramdisk (first-stage init) | Maintained; Android 13/14/15/16/17 init standard. |
| **`vendor_boot.img`** | Vendor ramdisk + `vendor_boot` modules + `mt6983.dtb` | Vendor ramdisk + updated 6.18 modules + 6.18 `mt6983.dtb` | DTB updated with 6.18 binding conventions. |
| **`dtbo.img`** | `oplus6983_22823.dtbo` | Modernized `oplus6983_22823.dtbo` | Compiled with `-@` flags against 6.18 base DTB. |
| **`vendor_dlkm.img`** | 5.10 vendor modules | 6.18 vendor modules | Re-compiled modules matching 6.18 vermagic and CRC symbol list. |
| **Boot Config / Cmdline** | Kernel commandline (`bootargs`) | `bootargs` + Android `bootconfig` trailer | GKI 6.x relies on `bootconfig` appended to initramfs for `androidboot.*` properties. |
| **AVB / vbmeta** | AVB 2.0 signed | AVB 2.0 with verification flags disabled during bringup | Use `--disable-verity --disable-verification` on vbmeta for initial boot tests. |

---

## 2. Kernel Commandline & Bootconfig

### Standard Bringup Commandline
```text
earlycon=mtk8250,0x11001000 console=ttyS0,921600n8 loglevel=8 androidboot.hardware=mt6983
```

### Android 17 / 6.18 Bootconfig Parameters
```text
androidboot.hardware = mt6983
androidboot.boot_devices = soc/112b0000.ufshci
androidboot.fstab_suffix = default
```

---

## 3. Userspace HAL Risks & UAPI Analysis

| Subsystem HAL | Interface / Driver | Risk Level | Mitigation & Hardware Testing Plan |
|---|---|---|---|
| **Camera (ImgSensor / ISP)** | `/dev/camera-isp`, `/dev/kd_camera_hw` | **High (Needs-Hardware)** | MediaTek proprietary camera HAL expects custom ioctls in `imgsensor`. Deferred to M4. |
| **Display (DRM / Gralloc)** | `/dev/dri/card0`, DRM atomic ioctl | **Medium** | Mainline DRM atomic API is stable, but vendor frame-update ioctl requires verification in M2. |
| **Audio (ASoC / TinyALSA)** | `/dev/snd/*` ALSA PCM devices | **Low** | Standard ALSA UAPI; mixer controls need mapping in M4. |
| **Mali GPU (Valhall G710)** | `/dev/mali0` | **High (Needs-Hardware)** | ARM Mali DDK version must match userspace `libGLES_mali.so`. Deferred to M4. |
| **Fingerprint (Goodix / Silead)** | `/dev/oplus_fp` | **Medium** | Netlink/ioctl events for optical FP sensor; deferred to M4. |
| **Modem (CCCI / RIL)** | `/dev/ccci_*` | **High (Needs-Hardware)** | CCCI protocol requires firmware shared-memory handshake. Deferred to M5. |

---

## 4. ROM Side Patches for LineageOS / AOSP

The patch files in `port-docs/rom-patches/` must be applied to the ROM device tree (`device/oneplus/vitamin`):
- `0001-BoardConfig-update-kernel-to-6.18-GKI.patch`: Updates `BOARD_KERNEL_VERSION`, `BOARD_BOOT_HEADER_VERSION`, module load lists, and prebuilt paths.
- `0002-device-tree-cmdline-and-bootconfig.patch`: Sets earlycon, loglevel, and bootconfig keys.
