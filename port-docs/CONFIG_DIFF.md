# OnePlus Nord 3 (vitamin, MT6983) Kernel Configuration Audit & Diff: 5.10 -> 6.18

## 1. Overview & Derivation Strategy

The 6.18 kernel configuration for the OnePlus Nord 3 (`vitamin`, MT6983) is derived from:
- **Base:** Android Common Kernel (ACK) 6.18 standard `arch/arm64/configs/gki_defconfig`.
- **Platform Fragment:** `arch/arm64/configs/vitamin_gki.fragment`.
- **Debug Diagnostic Fragment:** `arch/arm64/configs/vitamin_debug.config` (BOOT-FIRST RULE 4).

This design ensures compliance with Google GKI architecture while enabling the essential MediaTek SoC and board peripherals for hardware bringup.

---

## 2. Platform & Peripherals Configuration Audit (Milestones M0–M5)

| Subsystem / Milestone | Configuration Option | 5.10 State | 6.18 State | Rationale |
|---|---|---|---|---|
| **Early Console (M0)** | `CONFIG_SERIAL_8250_MT6577=y`, `CONFIG_SERIAL_8250_CONSOLE=y` | Active | Active | Early UART console support for boot troubleshooting via `earlycon=mtk8250,0x11001000`. |
| **MediaTek Clocks (M0)** | `CONFIG_COMMON_CLK_MEDIATEK=y`, `CONFIG_COMMON_CLK_MT6983=y` | Active | Active | Registers topckgen, apmixedsys, infracfg, and pericfg clock trees. |
| **MediaTek Pinctrl (M0)** | `CONFIG_PINCTRL_MTK_PARIS=y`, `CONFIG_PINCTRL_MT6983=y` | Active | Active | Paris-framework GPIO and pinmux controller for MT6983. |
| **PMIC / SPMI (M0)** | `CONFIG_SPMI_MTK_PMIF=y`, `CONFIG_REGULATOR=y` | Active | Active | SPMI bus interface controller and voltage regulator subsystem. |
| **UFS Host Controller (M0)** | `CONFIG_SCSI_UFS_MEDIATEK=y` | Out-of-tree module | In-tree upstream driver | Natively supports `mediatek,mt8183-ufshci` with standard clock gating and PHY management. |
| **USB / ADB Gadget (M0)** | `CONFIG_USB_MTU3=y`, `CONFIG_USB_CONFIGFS=y` | Active | Active | MediaTek MTU3 dual-role controller with ConfigFS Android gadget. |
| **dm-verity (M1)** | `CONFIG_DM_VERITY=y`, `CONFIG_DM_VERITY_AVB=y`, `CONFIG_DM_VERITY_FEC=y` | Active | Active | Required for Android Verified Boot 2.0 (AVB) rootfs mount with forward error correction. |
| **FBE / Inline Crypto (M1)** | `CONFIG_FS_ENCRYPTION=y`, `CONFIG_FS_ENCRYPTION_INLINE_CRYPT=y`, `CONFIG_SCSI_UFS_CRYPTO=y` | Active | Active | Hardware-accelerated file-based encryption for userdata partition via blk-crypto and UFS ICE. |
| **SELinux & IPC (M1)** | `CONFIG_SECURITY_SELINUX=y`, `CONFIG_ANDROID_BINDER_IPC=y`, `CONFIG_ANDROID_BINDERFS=y` | Active | Active | Enforcing mandatory access controls and Binder IPC channels. |
| **Storage / Filesystems (M1)** | `CONFIG_F2FS_FS=y`, `CONFIG_EROFS_FS=y`, `CONFIG_EXT4_FS=y` | Active | Active | F2FS with compression/security, EROFS with LZ4/ZSTD micro-decompression for system/vendor. |
| **zRAM (M1)** | `CONFIG_ZRAM=m`, `CONFIG_ZRAM_MULTI_COMP=y`, `CONFIG_ZRAM_ANDROID_IOCTL=y` | Active | Active | Multi-compression stream RAM swap for background memory management. |
| **Display Subsystem (M2)** | `CONFIG_DRM_MEDIATEK=m`, `CONFIG_DRM_MEDIATEK_DP=m`, `CONFIG_MTK_MMSYS=y` | Active | Active | MediaTek DRM atomic modesetting, MMSYS controller, MIPI-TX and DSI0/1 routing. |
| **Backlight & LEDs (M2)** | `CONFIG_BACKLIGHT_PWM=y`, `CONFIG_LEDS_CLASS=y` | Active | Active | PWM-driven display backlight and notification LEDs. |
| **Touchscreen & Haptics (M2)** | `CONFIG_INPUT_TOUCHSCREEN=y`, `CONFIG_INPUT_MISC=y`, `CONFIG_INPUT_FF_MEMLESS=y` | Active | Active | Multi-touch input framework, Synaptics S3910 SPI interface, and AW8697 force feedback. |
| **DVFS & CPUFreq (M3)** | `CONFIG_ARM_MEDIATEK_CPUFREQ=y`, `CONFIG_ARM_MEDIATEK_CPUFREQ_HW=y` | Active | Active | Upstream hardware-managed frequency scaling for Cortex-X2, A710, and A510 cores. |
| **Thermal Subsystem (M3)** | `CONFIG_MTK_THERMAL=y`, `CONFIG_MTK_SOC_THERMAL=y`, `CONFIG_MTK_LVTS_THERMAL=y` | Active | Active | Low Voltage Thermal Sensor (LVTS) temperature monitoring and thermal throttling. |
| **Charging & Fuel Gauge (M3)** | `CONFIG_POWER_SUPPLY=y`, `CONFIG_OPLUS_CHG=m`, `CONFIG_OPLUS_CHG_V2=m` | Active | Active | Power supply class, BQ27541 fuel gauge, and 80W SuperVOOC fast charging stack. |
| **GPU Subsystem (M4)** | `CONFIG_DMABUF_HEAPS=y`, `CONFIG_DMABUF_HEAPS_SYSTEM=y` | Active | Active | ARM Mali-G710 (Valhall MC10) DDK module (`mali_kbase.ko`) over DMA-BUF memory heaps. |
| **Video Codec (M4)** | `CONFIG_VIDEO_MEDIATEK_VCODEC=m` | Active | Active | Hardware video decoding/encoding (`mtk-vcodec-dec.ko`, `mtk-vcodec-enc.ko`). |
| **Audio Architecture (M4)** | `CONFIG_SOUND=y`, `CONFIG_SND_SOC=y`, `CONFIG_SND_SOC_MTK_BTCVSD=m` | Active | Active | ASoC platform sound card (`snd-soc-mt6983.ko`, `snd-soc-mtk-common.ko`). |
| **Sensors, NFC & FP (M4)** | `CONFIG_IIO=y`, `CONFIG_NFC=m`, `CONFIG_UFF_FINGERPRINT=m` | Active | Active | IIO sensors, NXP SN110 NFC controller, and OnePlus optical in-display fingerprint. |
| **Connectivity & Modem (M5)** | `CONFIG_CFG80211=m`, `CONFIG_MAC80211=m`, `CONFIG_BT=m`, `CONFIG_RFKILL=m` | Active | Active | Modular Wi-Fi 6, Bluetooth, GPS (`conninfra.ko`, `wlan_drv_gen4m.ko`), and CCCI modem IPC. |
| **Coprocessors & TEE (M5)** | `CONFIG_MTK_SCP=y`, `CONFIG_RPMSG_MTK_SCP=y`, `CONFIG_TEE=y`, `CONFIG_OPTEE=y` | Active | Active | System Companion Processor (SCP) remoteproc and ARM Trusted Execution Environment. |

---

## 3. Configuration Differences (5.10.269 vs 6.18 GKI)

### Removed / Obsolete 5.10 Kconfig Symbols
1. `CONFIG_ASHMEM`: Removed upstream in Linux 5.18+. Replaced entirely by anonymous shared memory (`memfd_create()`) and DMA-BUF heaps.
2. `CONFIG_ION`: Staging ION memory allocator completely deprecated and removed in mainline. Replaced by `CONFIG_DMABUF_HEAPS`.
3. `CONFIG_MTK_PERF_TRACKER` / `CONFIG_MTK_AEE_FEATURE`: Custom MediaTek out-of-tree tracing options removed from core kernel; replaced by standard ftrace, tracepoints, and pstore.
4. `CONFIG_CFS_BANDWIDTH`: Linux 6.6+ replaced CFS with EEVDF (Earliest Eligible Virtual Deadline First).
5. `CONFIG_ANDROID_VENDOR_HOOKS`: Tracepoint hooks modernized in ACK 6.18; legacy unreferenced hooks purged.

### Added 6.18 Kconfig Symbols
1. `CONFIG_RUST=y`: Kernel infrastructure for Rust language components.
2. `CONFIG_BOOT_CONFIG=y`: Modern Android boot configuration appended to initramfs (`bootconfig`).
3. `CONFIG_COMMON_CLK_MT6983=y`: Upstream CCF clock support for MT6983.
4. `CONFIG_PINCTRL_MT6983=y`: Upstream Paris pinctrl support for MT6983.
5. `CONFIG_DYNAMIC_DEBUG=y`: Runtime debug logging controllable via bootargs.

---

## 4. Debug Configuration Fragment (BOOT-FIRST RULE 4)

Path: `arch/arm64/configs/vitamin_debug.config`

Matching kernel cmdline / bootconfig parameters:
```text
earlycon=mtk8250,0x11001000 console=ttyS0,921600n8 loglevel=8 initcall_debug printk.devkmsg=on console_suspend=off panic=5 dyndbg="file drivers/clk/mediatek/* +p; file drivers/pinctrl/mediatek/* +p"
```
