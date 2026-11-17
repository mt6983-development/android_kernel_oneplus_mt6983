# OnePlus Nord 3 (vitamin, MT6983) Kernel Configuration Audit & Diff: 5.10 -> 6.18

## 1. Overview & Derivation Strategy

The 6.18 kernel configuration for the OnePlus Nord 3 (`vitamin`, MT6983) is derived from:
- **Base:** Android Common Kernel (ACK) 6.18 standard `arch/arm64/configs/gki_defconfig`.
- **Platform Fragment:** `arch/arm64/configs/vitamin_gki.fragment`.
- **Debug Diagnostic Fragment:** `arch/arm64/configs/vitamin_debug.config` (BOOT-FIRST RULE 4).

This design ensures compliance with Google GKI architecture while enabling the essential MediaTek SoC and board peripherals for hardware bringup.

---

## 2. Boot-Critical Configuration Audit (M0 Requirements)

| Subsystem | Configuration Option | 5.10 State | 6.18 State | Rationale |
|---|---|---|---|---|
| **dm-verity** | `CONFIG_DM_VERITY=y`, `CONFIG_DM_VERITY_AVB=y` | Active | Active | Required for Android Verified Boot 2.0 (AVB) rootfs mount. |
| **FBE / Inline Crypto** | `CONFIG_FS_ENCRYPTION=y`, `CONFIG_FS_ENCRYPTION_INLINE_CRYPT=y` | Active | Active | Hardware-accelerated file-based encryption for userdata partition. |
| **SELinux** | `CONFIG_SECURITY_SELINUX=y` | Active | Active | Enforcing mandatory access controls required by Android userspace. |
| **Binder IPC** | `CONFIG_ANDROID_BINDER_IPC=y`, `CONFIG_ANDROID_BINDERFS=y` | Active | Active | Core Android IPC communication channel. |
| **DMA-BUF Heaps** | `CONFIG_DMABUF_HEAPS=y`, `CONFIG_DMABUF_HEAPS_SYSTEM=y` | Active | Active | Modern replacement for obsolete Android ION memory allocators. |
| **Storage / Filesystems** | `CONFIG_F2FS_FS=y`, `CONFIG_EROFS_FS=y`, `CONFIG_EXT4_FS=y` | Active | Active | High-performance flash filesystem for userdata, compressed EROFS for system/vendor partitions. |
| **zRAM** | `CONFIG_ZRAM=m` | Active | Active | Compressed RAM swap for low-memory handling. |
| **UFS Host Controller** | `CONFIG_SCSI_UFS_MEDIATEK=y` | Out-of-tree module | In-tree upstream driver | Natively supports `mediatek,mt8183-ufshci` with standard clock gating and PHY management. |
| **MediaTek Clocks** | `CONFIG_COMMON_CLK_MEDIATEK=y`, `CONFIG_COMMON_CLK_MT6983=y` | Active | Active | Registers topckgen, apmixedsys, infracfg, and pericfg clock trees. |
| **MediaTek Pinctrl** | `CONFIG_PINCTRL_MTK_PARIS=y`, `CONFIG_PINCTRL_MT6983=y` | Active | Active | Paris-framework GPIO and pinmux controller for MT6983. |
| **PMIC / SPMI** | `CONFIG_SPMI_MTK_PMIF=y`, `CONFIG_REGULATOR=y` | Active | Active | SPMI bus interface controller and voltage regulator subsystem. |
| **Early Console** | `CONFIG_SERIAL_8250_MT6577=y`, `CONFIG_SERIAL_8250_CONSOLE=y` | Active | Active | Early UART console support for boot troubleshooting via `earlycon=mtk8250,0x11001000`. |
| **USB / ADB Gadget** | `CONFIG_USB_MTU3=y`, `CONFIG_USB_CONFIGFS=y` | Active | Active | MediaTek MTU3 dual-role controller with ConfigFS Android gadget. |
| **Pstore / Ramoops** | `CONFIG_PSTORE=y`, `CONFIG_PSTORE_RAM=y`, `CONFIG_PSTORE_CONSOLE=y` | Active | Active | Preserves crash logs in persistent RAM across warm reboots. |

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
