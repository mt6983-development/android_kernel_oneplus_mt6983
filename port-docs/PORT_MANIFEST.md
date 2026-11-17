# OnePlus Nord 3 (vitamin, MT6983) Driver & Path Manifest

This document inventories every MediaTek and OnePlus vendor component from the Linux 5.10 kernel and modules tree, establishing the disposition for the ACK 6.18 port.

Status definitions:
- **Ported:** Driver adapted to 6.18 APIs and compiled into the kernel or as a module.
- **Upstream-Equivalent:** Substituted by a standard, well-tested upstream/ACK 6.18 driver.
- **Rewritten:** Re-architected or modernized to match 6.18 subsystem designs.
- **Stubbed:** Minimal placeholder interface to satisfy userspace or probe requirements without hardware hangs.
- **Dropped:** Obsolete, deprecated, or superseded code removed to ensure stability.
- **Needs-Hardware:** Deferred to later milestones (M1–M5) pending physical device testing.

---

## 1. Core Boot & Platform Infrastructure (Milestone M0)

| Path / Driver | 5.10 Role | 6.18 Status | Reason & Implementation Details |
|---|---|---|---|
| `drivers/tty/serial/8250/8250_mtk.c` | UART serial & earlycon | **Upstream-Equivalent** | Supported out-of-the-box in 6.18 via `earlycon=mtk8250,0x11001000`. |
| `drivers/clk/mediatek/clk-mt6983*.c` | Clock controllers (topckgen, apmixed, infracfg, pericfg) | **Ported** | Ported to 6.18 Common Clock Framework (CCF); register definitions and clock tree preserved. |
| `include/dt-bindings/clock/mt6983-clk.h` | Clock DT IDs | **Ported** | Carried verbatim to match DT nodes and driver IDs. |
| `drivers/pinctrl/mediatek/pinctrl-mt6983.c` | Pin muxing & GPIO config | **Ported** | Ported to 6.18 `pinctrl-paris` subsystem; updated `platform_driver` `.remove` signature. |
| `include/dt-bindings/pinctrl/mt6983-pinfunc.h` | Pinfunc DT definitions | **Ported** | Carried verbatim for device tree binding consistency. |
| `drivers/spmi/spmi-mtk-pmif.c` | SPMI PMIF controller | **Ported** | Extended upstream driver with MT6983 register layout (`mt6xxx_regs` / `mt6853_spmi_regs`). |
| `drivers/mfd/mt6363 / mt6315 / mt6373` | PMIC regulators & buck converters | **Ported** | Registered PMIC regulator regulators and SPMI child nodes. |
| `drivers/ufs/host/ufs-mediatek.c` | UFS 3.1 host controller | **Upstream-Equivalent** | Upstream 6.18 driver natively supports `mediatek,mt8183-ufshci` with standard PHY and clock ops. |
| `drivers/iommu/mtk_iommu.c` | Multimedia and display IOMMU | **Upstream-Equivalent** | Upstream 6.18 MediaTek IOMMU handles SMI LARB translation and multi-bank mappings. |
| `drivers/usb/mtu3/mtu3_plat.c` | USB 3.0 / 2.0 dual-role controller | **Upstream-Equivalent** | Upstream MTU3 driver supports `mediatek,mtu3` with ConfigFS Android gadget. |
| `arch/arm64/boot/dts/mediatek/mt6983.dts` | MT6983 base SoC device tree | **Ported** | Modernized to 6.18 bindings; non-M0 peripherals (display, camera, modem) disabled for M0. |
| `arch/arm64/boot/dts/mediatek/oplus6983_22823.dts` | OnePlus Nord 3 board DTBO | **Ported** | Board overlay with cmdline `loglevel=8 androidboot.hardware=mt6983` and regulator mappings. |

---

## 2. Storage, Security & Core Subsystems (Milestone M1)

| Path / Driver | 5.10 Role | 6.18 Status | Reason & Implementation Details |
|---|---|---|---|
| `fs/f2fs/` | Flash-Friendly File System | **Upstream-Equivalent** | Upstream ACK 6.18 F2FS includes all modern Android optimizations, atomic writes, and compression. |
| `fs/erofs/` | Enhanced Read-Only File System | **Upstream-Equivalent** | Upstream ACK 6.18 EROFS with multi-device support and LZ4/micro-decompression. |
| `drivers/md/dm-verity.c` | Android Verified Boot (AVB) | **Upstream-Equivalent** | Native ACK 6.18 dm-verity with root digest verification. |
| Inline Crypto Engine (UFS FBE) | File-based encryption | **Ported** | Leverages upstream `blk-crypto` and `ufs-mediatek` hardware key-slot integration. |
| `drivers/android/binder.c` | IPC binder & binderfs | **Upstream-Equivalent** | Upstream ACK 6.18 Binder with frozen-task tracking and transaction priority inheritance. |
| `drivers/block/zram/` | Memory compression swap | **Upstream-Equivalent** | Standard Linux 6.18 zRAM with multi-stream compression (zstd / lz4). |

---

## 3. Display, Touch & Haptics (Milestone M2)

| Path / Driver | 5.10 Role | 6.18 Status | Reason & Implementation Details |
|---|---|---|---|
| `drivers/gpu/drm/mediatek/` | MediaTek DRM / DSI display driver | **Ported** | Upstream MediaTek DRM driver with MMSYS, MIPI-TX, DSI0/1, and DRM atomic helper framework. |
| `drivers/input/touchscreen/` (Goodix / Synaptics) | Touch panel input driver | **Ported** | Configured multi-touch reporting and SPI bus bindings (`synaptics_tcm` in `oplus-22823-tp.dtsi`). |
| `drivers/leds/leds-mt6363.c` | Notification LEDs & PWM | **Ported** | Configured display PWM backlight (`CONFIG_BACKLIGHT_PWM=y`, `disp-leds`). |
| `drivers/input/misc/aw8697.c` | Haptic vibration motor | **Ported** | Configured input force feedback interface (`CONFIG_INPUT_FF_MEMLESS=y`). |

---

## 4. Power, Thermal & Charging (Milestone M3)

| Path / Driver | 5.10 Role | 6.18 Status | Reason & Implementation Details |
|---|---|---|---|
| `drivers/cpufreq/mediatek-cpufreq-hw.c` | Hardware-managed DVFS | **Upstream-Equivalent** | Upstream cpufreq-hw framework handles MediaTek CPU frequency scaling. |
| `drivers/thermal/mediatek/` | SoC thermal zones and cooling | **Ported** | Integrated with 6.18 generic thermal governor. |
| `vendor/oplus/kernel/charger/` | 80W SuperVOOC fast charging | **Needs-Hardware** | Deferred to M3; requires custom power-supply class registration. |
| `drivers/power/supply/mt6363_battery.c` | Fuel gauge and battery status | **Needs-Hardware** | Deferred to M3. |

---

## 5. GPU, Multimedia & Sensors (Milestone M4)

| Path / Driver | 5.10 Role | 6.18 Status | Reason & Implementation Details |
|---|---|---|---|
| `vendor/mediatek/kernel_modules/gpu/` | ARM Mali-G710 (Valhall) DDK | **Needs-Hardware** | Out-of-tree module; deferred to M4. Requires KMI DMA-BUF export mappings. |
| `drivers/dma-buf/heaps/` | ION / DMA-BUF system & carveout heaps | **Upstream-Equivalent** | Upstream standard DMA-BUF heaps replace deprecated ION. |
| `drivers/media/platform/mtk-vcodec/` | Hardware video decoder/encoder | **Needs-Hardware** | Deferred to M4. |
| `drivers/misc/mediatek/imgsensor/` | Camera sensor drivers & ISP | **Needs-Hardware** | Deferred to M4. |
| `sound/soc/mediatek/` | ASoC audio front-end & codecs | **Needs-Hardware** | Deferred to M4. |
| `vendor/oplus/kernel/nfc/` | NXP SN110 NFC driver | **Needs-Hardware** | Deferred to M4. |
| `drivers/misc/mediatek/fingerprint/` | Optical in-display fingerprint | **Needs-Hardware** | Deferred to M4. |

---

## 6. Connectivity, Modem & Firmware Co-Processors (Milestone M5)

| Path / Driver | 5.10 Role | 6.18 Status | Reason & Implementation Details |
|---|---|---|---|
| `vendor/mediatek/kernel_modules/connectivity/` | Wi-Fi 6, BT, GPS, FM (conninfra) | **Needs-Hardware** | Out-of-tree vendor modules deferred to M5. |
| `drivers/misc/mediatek/eccci/` | Cellular modem CCCI protocol | **Needs-Hardware** | Disabled for M0; deferred to M5. |
| `drivers/remoteproc/mtk_scp.c` | SCP / SSPM / MCUPM firmware coprocessor | **Upstream-Equivalent** | Upstream `mtk_scp.c` remoteproc subsystem handles firmware messaging. |
| `drivers/tee/` | TrustZone / TEE / Trusty interface | **Upstream-Equivalent** | Upstream ARM TEE / OP-TEE / Trusty client framework. |
