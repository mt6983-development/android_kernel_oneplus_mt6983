# OnePlus Nord 3 (vitamin, MT6983) Boot Debugging & Triage Guide

## 1. Ranked Boot-Blocker Triage (Milestone M0)

| Rank | Potential Blocker | Likelihood | Impact | Root Cause & Mitigation |
|---|---|---|---|---|
| **1** | **UFS Host Probe Hang / Timeout** | Medium | Critical (Halts boot before init) | *Cause:* Clocks (`ufs_hd_haxi`, `ufs_sel`) or resets not de-asserting properly in `ufs-mediatek.c`.<br>*Mitigation:* Upstream driver matches `mediatek,mt8183-ufshci`. If probe fails, verify supply regulators (`vcc`, `vccq`, `vccq2`) in DT and check earlycon `ufshcd` dmesg. |
| **2** | **PMIC / SPMI Arbitration Failure** | Medium | Critical (CPU/Core voltages unpowered) | *Cause:* PMIF register base or clock gating mismatch on MT6983.<br>*Mitigation:* `spmi-mtk-pmif.c` matches `.data = &mt8195_pmif_arb`. Verify `pmif` clock rate and IRQ 421 delivery in DT. |
| **3** | **fw_devlink Probe Order Deadlock** | Medium | High (Drivers defer infinitely) | *Cause:* Missing supplier node in DT causes consumers (like UFS, IOMMU) to return `-EPROBE_DEFER` indefinitely.<br>*Mitigation:* Add `fw_devlink=off` to kernel cmdline to isolate and verify driver probe without strict devlink graph enforcement. |
| **4** | **IOMMU / SMI Translation Fault** | Low-Med | High (DMA crash in early init) | *Cause:* SMI LARBs not properly clocked before IOMMU domain attach.<br>*Mitigation:* Core M0 peripherals bypass SMI translation by using coherent reserved memory pools. |
| **5** | **UART Earlycon Baud / Pinmux Mismatch** | Low | Low (Display of logs only) | *Cause:* UART0 RX/TX pins not pulled to default function 1 by bootloader.<br>*Mitigation:* Pass `earlycon=mtk8250,0x11001000` on cmdline. If UART is silent, pstore/ramoops captures logs in warm boot. |

---

## 2. Failure Log Collection & Analysis

### A. Collecting Early Serial Logs (UART)
Connect 1.8V USB-TTL serial adapter to UART test points on the motherboard (or via debug cable):
- Parameters: `921600 8N1` (or `115200 8N1` fallback)
- Cmdline requirement: `earlycon=mtk8250,0x11001000 console=ttyS0,921600n8`

### B. Persistent RAM Logs (pstore / ramoops)
If the device crashes or reboots without serial output:
1. Allow the device to crash and warm-reboot into fastboot or TWRP recovery.
2. In recovery / fastboot:
   ```bash
   adb shell cat /sys/fs/pstore/console-ramoops-0 > pstore_console.log
   adb shell cat /sys/fs/pstore/dmesg-ramoops-0 > pstore_dmesg.log
   ```
3. Inspect the tail of `pstore_dmesg.log` for kernel panics, BUG, or null pointer dereferences.

### C. First-Stage Init Logs (kmsg)
If the kernel boots but first-stage init hangs:
```bash
adb shell dmesg > dmesg.log
```
Search for:
- `init: [libprocessgroup]` or `init: init first stage started!`
- `Failed to mount /vendor` or `Failed to mount /data`
- `dm-verity: device-mapper: verity: verification failed`

---

## 3. On-Device Test Checklist

Before advancing beyond Milestone M0, verify the following checklist items on physical OnePlus Nord 3 (`vitamin`) hardware:

- [ ] **1. Boot:** Kernel log appears on earlycon/console, reaches first-stage init, first-stage vendor_boot modules load, userdata mounts and decrypts, adb shell is accessible.
- [ ] **2. Display, backlight, touch, haptics:** DRM bridge and panel initialize, backlight scales smoothly, multi-touch input responds, haptic feedback triggers.
- [ ] **3. WiFi, BT, GPS, NFC:** Wi-Fi associates with AP, Bluetooth scanning pairs with devices, GPS acquires satellites, NFC read/writes tags.
- [ ] **4. Modem / RIL, SIM, calls, mobile data:** Dual SIM cards detected, VoLTE calls connect, 5G/4G data transfer functions.
- [ ] **5. Camera, audio, sensors:** All camera sensors stream frames in camera app, stereo speakers and mic capture audio, accelerometer and proximity report data.
- [ ] **6. Charging & biometrics:** SuperVOOC fast charging negotiates, battery temperature and percentage report accurately, optical fingerprint sensor authenticates.
- [ ] **7. Power states & recovery:** Device suspends cleanly into deep sleep, resumes on power key, reboots into recovery and bootloader.
- [ ] **8. Thermals, cpufreq, GPU load, UFS health:** CPU frequency scales across all clusters under stress test, Mali GPU renders without UI stutters, UFS benchmark passes without I/O timeouts, USB MTP/OTG functions.
