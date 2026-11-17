# OnePlus Nord 3 (vitamin / MT6983) Kernel Port Progress

## Status Summary
- **Current Stage:** Stage B - Milestone M1 (Storage & Security) Completed
- **Current Branch (Kernel):** `upstream-6.18`
- **Current Branch (Modules):** `upstream-6.18`
- **Base Kernel Version:** Android Common Kernel (ACK) 6.18.32 (`android17-6.18-2026-09_r14`, commit `26c72498ee16574e937fb78bfbbdd2c4ddf3e806`)
- **Reference 5.10 Branch:** `upstream-5.10.269` (`lineage-24.0` ancestry at Linux 5.10.269)
- **Active Checkpoint:** `checkpoint-M1` (Milestones M0 & M1 statically validated)

---

## Completed (Done)
- [x] **Phase 0: Environment & Discovery**
  - Build scripts, toolchain, defconfigs, modules integration, and boot layout analyzed and recorded.
- [x] **Stage A: 5.10.236 to 5.10.269 Upgrade Verification**
  - Confirmed 5.10.269 state, vendor hooks, static checks clean, documented in `UPSTREAM_NOTES.md`.
  - Local branches `upstream-5.10.269` synchronized and pushed to `test-5.10.269`.
- [x] **Stage B1: Setup**
  - Local branch `upstream-6.18` created in both repos based on verified ACK release tag `android17-6.18-2026-09_r14` (commit `26c72498ee16574e937fb78bfbbdd2c4ddf3e806`, SUBLEVEL = 32).
  - Preserved 5.10.269 vendor tree in detached worktree `kernel-5.10-ref` as read-only reference.
- [x] **Stage B2: GKI Model Decision**
  - Written `port-docs/PORT_NOTES.md` documenting Kleaf/Bazel model, toolchains (Clang 18+, Rust 1.77+), 4K page size, and v4 boot header layout.
- [x] **Stage B3: Port Manifest**
  - Written `port-docs/PORT_MANIFEST.md` categorizing all MT6983 and OnePlus drivers with porting status and rationales.
- [x] **Milestone M0: Minimal Boot Platform Port**
  - **Clocks:** Ported MT6983 CCF driver (`drivers/clk/mediatek/clk-mt6983.c` + `include/dt-bindings/clock/mt6983-clk.h`) adapted to 6.18 CCF APIs; added `CONFIG_COMMON_CLK_MT6983` to Kconfig and Makefile.
  - **Pinctrl:** Ported MT6983 Paris pinctrl driver (`drivers/pinctrl/mediatek/pinctrl-mt6983.c` + `include/dt-bindings/pinctrl/mt6983-pinfunc.h`) adapted to 6.18 APIs; added `CONFIG_PINCTRL_MT6983` to Kconfig and Makefile.
  - **SPMI:** Extended `drivers/spmi/spmi-mtk-pmif.c` with MT6983 PMIF/SPMI support.
  - **Storage & UFS:** Substituted custom 5.10 UFS driver with upstream 6.18 `ufs-mediatek.c` supporting `mediatek,mt8183-ufshci`.
  - **Device Tree:** Ported `mt6983.dts`, `mt6983-clkitg.dtsi`, `oplus6983_22823.dts`, and regulator trees; registered in `arch/arm64/boot/dts/mediatek/Makefile` with `-@` overlay flags; disabled display, touch, and modem per M0 rules.
  - **Defconfig & Diagnostics:** Created `vitamin_gki.fragment` and `vitamin_debug.config`; wrote comprehensive `port-docs/CONFIG_DIFF.md`.
  - **Modules & Packaging:** Created `modules.load.vendor_boot`, `modules.load.vendor_dlkm`, and `modules.blocklist`.
  - **ROM Integration:** Written `port-docs/DEVICE_TREE_CHANGES.md` and generated patches `0001-BoardConfig-update-kernel-to-6.18-GKI.patch` and `0002-device-tree-cmdline-and-bootconfig.patch` in `port-docs/rom-patches/`.
  - **Boot Debugging:** Written `port-docs/BOOT_DEBUG.md` (ranked blockers, logging, full on-device test checklist) and `port-docs/BUILD_COMMANDS.md` (exact build, packaging, and first-boot steps).
  - **Static Checks:** Verified `git diff --check`, zero conflict markers, zero `.rej`/`.orig` files.
- [x] **Milestone M1: Storage & Security**
  - **dm-verity & AVB:** Verified `CONFIG_DM_VERITY=y`, `CONFIG_DM_VERITY_AVB=y`, `CONFIG_DM_VERITY_FEC=y`.
  - **FBE / Inline Crypto:** Verified `CONFIG_FS_ENCRYPTION=y`, `CONFIG_FS_ENCRYPTION_INLINE_CRYPT=y`, `CONFIG_BLK_INLINE_ENCRYPTION=y`, `CONFIG_SCSI_UFS_CRYPTO=y` with upstream `ufs-mediatek.c` hardware crypto reset and key slot support.
  - **Filesystems:** Configured `CONFIG_F2FS_FS=y`, `CONFIG_F2FS_FS_SECURITY=y`, `CONFIG_F2FS_FS_COMPRESSION=y`, `CONFIG_EROFS_FS=y`, `CONFIG_EROFS_FS_ZIP_LZ4=y`, `CONFIG_EROFS_FS_ZIP_ZSTD=y`, `CONFIG_EXT4_FS=y`.
  - **Security & IPC:** Verified `CONFIG_SECURITY_SELINUX=y`, `CONFIG_ANDROID_BINDER_IPC=y`, `CONFIG_ANDROID_BINDERFS=y`.
  - **Memory & Swap:** Verified `CONFIG_ZRAM=m`, `CONFIG_ZRAM_MULTI_COMP=y`, `CONFIG_ZRAM_ANDROID_IOCTL=y`.

---

## Next Steps (Milestones M2–M5)
- [ ] Milestone M2: Display, Backlight, Touch, Haptics.
- [ ] Milestone M3: Power (DVFS, cpuidle, thermal, SuperVOOC charger, fuel gauge).
- [ ] Milestone M4: GPU (Mali Valhall), DMA-BUF heaps, vcodec, camera (imgsensor/ISP), audio, sensors, fingerprint.
- [ ] Milestone M5: Connectivity (Wi-Fi 6, BT, GPS, NFC) and modem (CCCI), SCP/SSPM coprocessors.

---

## Blockers & Open Items
- None. Static checks clean. Ready for build execution by user.
