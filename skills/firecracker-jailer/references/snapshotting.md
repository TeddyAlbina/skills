**# Firecracker Snapshotting - Detailed Exploration (Updated for 2026)**

**Version:** 1.1 (based on Firecracker main branch as of April 2026)  
**Status:** Full snapshots are production-ready / Generally Available. Diff (incremental) snapshots remain in **Developer Preview** (with ongoing work toward guest_memfd integration). Snapshot format uses independent semantic versioning.

This section expands on the core SKILL.md with in-depth architecture, workflows, API details, memory handling options, cloning considerations, best practices, limitations, and tools. All information is drawn directly from official Firecracker documentation in `/docs/snapshotting/`.

## 1. What is MicroVM Snapshotting?

MicroVM snapshotting serializes a **running** Firecracker microVM (guest memory + emulated hardware/device/KVM state) into files on an external medium. These files can later restore an identical microVM in a **different** Firecracker process, resuming the guest workload exactly where it left off.

- The **original** microVM continues unaffected (except for brief pause latency during snapshot creation).
- Snapshots enable **cold-start elimination** for serverless/container workloads (e.g., AWS Lambda SnapStart uses this under the hood).
- Key benefit: Restore times in the low milliseconds range vs. full boot (~125 ms+).

**Snapshot composition** (multiple files for flexibility):
- **Guest memory file** (`.mem` or custom)
- **MicroVM state file** (`.vmstate` – serialized VMM/KVM/vCPU/device state)
- **Disk files** (managed entirely by the user – not snapshotted by Firecracker)

Firecracker **does not** flush guest disks automatically; users must ensure consistency.

## 2. Architecture & How It Works

Firecracker saves:
- Full guest memory state.
- Emulated HW state (KVM + Firecracker devices).

**Memory loading innovation** (core to performance):
- On restore, Firecracker uses `MAP_PRIVATE` mmap of the memory file → **copy-on-write (CoW)** anonymous memory.
- Pages load **on-demand** via page faults (host kernel or userfaultfd).
- Writes create private copies; original snapshot file stays read-only and shared across clones.
- Result: Extremely fast resume + memory sharing for high-density clones.

**Two memory backends** (chosen at restore time):
- **`File`** (default): Host kernel handles page faults (simple, no extra process).
- **`Uffd`** (userfaultfd): User-provided page-fault handler process (advanced control, e.g., on-demand decompression, remote fetch, shared memory cloning, pre-warming).

**Full vs. Diff Snapshots**:
- **Full**: Entire memory written (requires `track_dirty_pages: true` in machine config for future diffs).
- **Diff**: Only dirty pages since last snapshot (much faster/smaller; still Developer Preview).

Dirty-page tracking is enabled via the `machine-config` field `track_dirty_pages` (formerly `enable_diff_snapshots` – renamed in 2025).

**VMGenID support** (Linux ≥5.18 on x86, ≥6.10 or backport on ARM): Firecracker injects a new unique ID + notification on resume → kernel reseeds CSPRNG automatically for clone uniqueness.

## 3. Snapshot API Workflow

All operations via Firecracker’s Unix-socket REST API (after the microVM is **booted** and running).

### Prerequisites (common)
- MicroVM must be in **running** state.
- `track_dirty_pages: true` for any diff snapshots.

### Step-by-step
1. **Pause** the microVM (`PATCH /actions` with `"action_type": "Pause"`).
2. **CreateSnapshot** (`PUT /snapshot/create`):
   - Full or diff.
   - Outputs: memory file + state file.
3. (Optional) Rebase/inspect diffs with `snapshot-editor` tool.
4. **LoadSnapshot** + **Resume** in a **new** Firecracker process (`PUT /snapshot/load` + `PATCH /actions` with `"action_type": "Resume"`).

**Example: Create full snapshot (JSON body for PUT /snapshot/create)**
```json
{
  "snapshot_type": "Full",
  "snapshot_path": "./snapshot.vmstate",
  "mem_file_path": "./snapshot.mem",
  "version": "1.0.0"   // optional; uses latest supported
}
```

**Example: Load with File backend (simple)**
```json
{
  "snapshot_path": "./snapshot.vmstate",
  "mem_backend": {
    "backend_type": "File",
    "backend_path": "./snapshot.mem"
  }
}
```

**Example: Load with network overrides (for clones)**
```json
{
  "snapshot_path": "./snapshot.vmstate",
  "mem_backend": { ... },
  "network_overrides": [
    {
      "iface_id": "eth0",
      "host_dev_name": "vmtap01"   // new TAP name
    }
  ]
}
```

**Example: Advanced Uffd backend** (requires page-fault handler listening on UDS):
```json
{
  "snapshot_path": "./snapshot.vmstate",
  "mem_backend": {
    "backend_type": "Uffd",
    "backend_path": "/path/to/uffd-socket"
  }
}
```

**Resume** after load: `PATCH /actions` → `{"action_type": "Resume"}`.

**Userspace notifications** (optional): Firecracker can notify a Unix socket on load/resume completion for post-restore actions (e.g., RNG reseed, cleanup).

## 4. Advanced Memory Loading with Userfaultfd (Uffd)

For production-scale cloning or custom loading:
- Dedicated user-space handler process (example in Firecracker repo: `src/firecracker/examples/uffd/on_demand_handler.rs`).
- Handler mmaps the memory file privately and serves `UFFDIO_COPY` on faults.
- Supports balloon device (`UFFD_EVENT_REMOVE` → zero pages).
- Caveats: Handler crash → Firecracker hangs on next fault. Monitor and recycle.
- Jailer integration: Handler, UDS, and memory file must live inside the jail.

**Kernel requirements**:
- 5.10+: `userfaultfd` syscall.
- 6.1+: `/dev/userfaultfd` (preferred; Jailer exposes it automatically with proper perms).

## 5. Cloning Considerations

**Network for clones** (critical):
- Use **network namespaces** per clone + unique TAP names (via `jailer --netns` or `network_overrides`).
- `iptables` NAT/MASQUERADE + DNAT for ingress.
- Flush ARP tables in guest after restore.
- Full guide in `network-for-clones.md`.

**Randomness / Entropy for clones** (`random-for-clones.md`):
- Clones from same snapshot start with identical RNG state → security risk.
- **Solution**: VMGenID (auto-reseeds kernel CSPRNG on modern kernels).
- Pre-snapshot: Delete `/var/lib/systemd/random-seed`, override `/proc/sys/kernel/random/boot_id`.
- Post-restore (or via userspace notification): Use `RNDADDENTROPY` + `RNDRESEEDCRNG` ioctl (CAP_SYS_ADMIN) or attach `virtio-rng`.
- Recommendation: Snapshot **after** guest kernel boot + init randomness.

**Vsock reset**: Open connections close; listen sockets survive.

**Disks**: User-managed; use CoW filesystems (e.g., XFS reflink) for efficiency.

## 6. Tools

- **`snapshot-editor`** (in repo): Rebase diff snapshots onto base memory file (`edit-memory rebase`), inspect vmstate, edit some aarch64 registers.

## 7. Best Practices & Security

- **Always** use Jailer + cgroups v2 (V1 causes high restore latency).
- Take snapshots **after** guest kernel fully boots (avoid early-boot crashes).
- Secure snapshot files (auth + encryption) – host/files are trusted.
- Use `track_dirty_pages: true` + diff snapshots for speed/size.
- For clones: Separate network namespaces, unique IPs/TAPs, RNG reseed.
- Monitor page-fault handler if using Uffd.
- Provision host disk space ahead (snapshots can be large).
- Test restore on same kernel version (KVM state is kernel-dependent).
- Use CPU templates for consistent CPUID across hosts.
- Combine with huge pages / guest_memfd (future).

**Security notes**:
- Snapshot files contain full guest state → encrypt when crossing trust boundaries.
- CRC64 on state file (basic integrity only).
- Threat model assumes trusted host/API/snapshots.

## 8. Limitations (Official)

- Diff snapshots still Developer Preview.
- Network state **not** preserved (use overrides/namespaces).
- High restore latency on cgroups v1.
- ARM64: GICv2 ↔ GICv3 restore not possible.
- No cross-architecture or cross-CPU-model restore (unless invariant features).
- Vsock connections reset.
- Early-boot snapshots can crash on resume.
- Snapshot format changes trigger MAJOR version bump (bitcode serialization).

**Versioning**: Independent semantic versioning (e.g., 1.0.0+). Backwards-compatible best-effort; no breaking changes in patch releases.

## 9. Performance & Production Use Cases

- Restore: Milliseconds (on-demand pages).
- Create: Depends on memory size + dirty pages.
- Density: Thousands of clones sharing base memory file via CoW.
- Real-world: Serverless (Lambda), CI runners, AI sandboxes, fast FaaS.

**Where to resume**: Same or different host (as long as kernel/CPU compatible and external resources like TAPs/disks are present).

## Resources (Official)

- Core: `docs/snapshotting/snapshot-support.md`
- Page faults: `docs/snapshotting/handling-page-faults-on-snapshot-resume.md`
- Clones (network/random): `docs/snapshotting/network-for-clones.md` + `random-for-clones.md`
- Versioning: `docs/snapshotting/versioning.md`
- Snapshot editor & examples in repo.

Snapshotting is one of Firecracker’s most powerful features for high-scale, low-latency workloads. Combine with Jailer, proper networking, and RNG handling for production-grade cloning.

Happy snapshotting! 🔥

(Keep this section updated with `CHANGELOG.md` and test against your target kernel/Firecracker version.)