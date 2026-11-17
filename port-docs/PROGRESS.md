# OnePlus Nord 3 (vitamin / MT6983) Kernel Port Progress

## Status Summary
- **Current Stage:** Transitioning from Stage A to Stage B (Port to ACK android17-6.18)
- **Current Branch (Kernel):** `upstream-5.10.269` -> Preparing `upstream-6.18`
- **Current Branch (Modules):** `upstream-5.10.269` -> Preparing `upstream-6.18`
- **ACK 6.18 Target Release Tag:** `android17-6.18-2026-09_r14` (Kernel 6.18.32) / ASB tag `ASB-2026-11-02_17-6.18` (Kernel 6.18.33)
- **Active Milestone:** Milestone M0 (Minimal Boot: GKI Image + vitamin DTB, earlycon/UART, clocks, pinctrl, PMIC, UFS, IOMMU/EMI, USB gadget)

---

## Completed (Done)
- [x] **Phase 0: Environment & Discovery**
  - Toolchain and build scripts analyzed: Clang 12.0.5 (`r416183b`), GNU aarch64 cross-toolchain, hermetic build tools.
  - Defconfig structure recorded: `oplus6983_defconfig` derived from `gki_defconfig` + `mgk_64_k510_defconfig` + `oplus6983.config`.
  - Modules integration verified: External out-of-tree `M=` module builds via `build/build.sh` targeting `vendor/mediatek` and `vendor/oplus`.
  - Boot layout verified: Header version 4, GKI `boot.img` + `init_boot.img` + `vendor_boot.img` (with `mt6983.dtb`) + `dtbo.img` (from `oplus6983_22823.dts`) + `vendor_dlkm.img`.
- [x] **Stage A: 5.10.236 to 5.10.269 Upgrade**
  - Confirmed `lineage-24.0` holds complete upstream merge sequence up to ACK release `android13-5.10-2026-10` (SUBLEVEL = 269).
  - All vendor hooks, f2fs, mm, binder, and scheduling hooks intact and verified statically.
  - Static checks passed (`git diff --check`, zero conflict markers, zero `.rej`/`.orig` files, Makefile verified 5.10.269).
  - Remote branches `test-5.10.269` synchronized and verified.
  - `port-docs/UPSTREAM_NOTES.md` established.
- [x] **ACK 6.18 Tag Discovery**
  - Remote repository: `https://android.googlesource.com/kernel/common`
  - Verified branch: `android17-6.18`
  - Identified latest release tag: `android17-6.18-2026-09_r14` (commit `26c72498ee16574e937fb78bfbbdd2c4ddf3e806`, SUBLEVEL = 32)
  - Identified latest ASB tag: `ASB-2026-11-02_17-6.18` (commit `01c7e6b174af760d2ae7d975ab8d6f2597c2d1ec`, SUBLEVEL = 33)

---

## In Progress / Next Up
- [ ] **Stage B Setup (B1 & B2)**
  - Setup local `upstream-6.18` branch in kernel and modules repositories.
  - Document GKI Kleaf / Bazel build model and toolchain requirements in `port-docs/PORT_NOTES.md`.
- [ ] **Port Manifest (B3)**
  - Write `port-docs/PORT_MANIFEST.md` categorizing all MT6983 / vitamin SoC and peripheral drivers.
- [ ] **Milestone M0 (Minimal Boot)**
  - Adapt MT6983 clocks, pinctrl, PMIC (SPMI), UFS host, IOMMU/reserved-memory, and USB gadget.
  - Port base DTS (`mt6983.dts`) and board DTBO (`oplus6983_22823.dts`) to 6.18 conventions.
  - Create 6.18 GKI defconfig fragment and debug config fragment.
  - Write `port-docs/CONFIG_DIFF.md`, `port-docs/BOOT_DEBUG.md`, `port-docs/BUILD_COMMANDS.md`, and `DEVICE_TREE_CHANGES.md`.
  - Run static checks, commit, push to `test-6.18`, and tag `checkpoint-M0`.

---

## Blockers / Open Items
- None currently. Hardware tests and actual builds are deferred to the user per HARD RULE 1 (NO BUILDS).
