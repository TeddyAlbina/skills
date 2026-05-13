---
name: firecracker-jailer
description: Orchestrate Firecracker VMM and Jailer to deploy secure, lightweight microVMs. Full lifecycle management (create, configure, boot, snapshot) via REST API and CLI; manage VirtIO devices (Net, Block, Vsock) and rate limiting
metadata:
  version: "2.0"
---

## 1. Introduction

**Firecracker** **Virtual Machine Monitor (VMM)** it deliver:
- Hardware-level isolation of traditional VMs
- Container-like speed, density, and resource efficiency

**Jailer** provides **defense-in-depth** by sandboxing the Firecracker process itself using Linux primitives (cgroups, namespaces, chroot, seccomp, privilege dropping). **Production deployments must use the Jailer.**
  
**Official links:**
- website: https://firecracker-microvm.github.io/
- github: https://github.com/firecracker-microvm/firecracker


## 2. Architecture & Design Principles

Firecracker follows a **minimalist, security-first** design:

- **One microVM per Firecracker process** → extreme isolation and predictability.
- **Process layout (per microVM):**
  - **API thread** – Handles RESTful control-plane (HTTP over Unix socket).
  - **VMM thread** – Manages device models, rate limiters, MMDS (metadata service).
  - **vCPU threads** (one per guest vCPU) – Run the KVM_RUN loop.
- **Device model** (very small):
  - VirtIO-Net (TAP-backed)
  - VirtIO-Block (file-backed)
  - VirtIO-Vsock (guest ↔ host communication)
  - Serial console + minimal legacy devices (PIC, IOAPIC, PIT, i8042 keyboard controller)
  - **No** USB, GPU, full PCI passthrough (by design).
- **Rate limiting** built-in (token-bucket) for network and block devices.
- **KVM** provides the hardware virtualization barrier.
- **Jailer** provides the **second barrier** (user-space sandbox).

**Key design goals (from design.md):**
- Startup < 125 ms
- < 5 MiB memory overhead per microVM
- 150+ microVMs/sec creation rate on a 36-core host
- Minimal attack surface (only necessary syscalls via thread-specific seccomp filters)

## 3. The Jailer (Production Isolation Layer)

The Jailer is **mandatory** for production.

### How Jailer Works (step-by-step)
1. Validates arguments and VM ID.
2. Closes all FDs except stdio.
3. Cleans environment variables.
4. Creates chroot jail at `<chroot-base>/<exec-file-name>/<id>/root`.
5. Copies the statically-linked `firecracker` binary into the jail (prevents shared memory attacks).
6. Sets resource limits (`setrlimit`).
7. Creates and configures cgroups (v1 or v2) and moves the process into them.
8. Enters a new mount namespace → `pivot_root` → `chroot`.
9. Creates device nodes (`/dev/kvm`, `/dev/net/tun`).
10. Drops privileges (`setuid`/`setgid`).
11. `execve()` into Firecracker.

### Jailer CLI Example (production pattern)
```bash
sudo ./jailer \
  --id my-vm-001 \
  --exec-file /usr/bin/firecracker \
  --uid 1234 --gid 1234 \
  --chroot-base-dir /srv/jailer \
  --cgroup-version 2 \
  --cgroup cpu.shares=1024 \
  --cgroup memory.limit_in_bytes=512M \
  --resource-limit no-file=4096 \
  --resource-limit fsize=250000000 \
  --netns /var/run/netns/my-netns \
  --daemonize \
  -- \
  --api-sock /srv/jailer/firecracker/my-vm-001/root/api.sock \
  --config-file /srv/jailer/firecracker/my-vm-001/root/config.json
```

**Important flags:**
- `--cgroup` → set limits without extra privileged helper
- `--parent-cgroup` → support nested cgroup hierarchies
- `--new-pid-ns` → optional extra PID isolation
- `--` → everything after is passed to Firecracker

**Full Jailer docs:** `docs/jailer.md` in the repo.

## 4. Key Features & Benefits

| Feature                  | Benefit                                      | Typical Value                  |
|--------------------------|----------------------------------------------|--------------------------------|
| MicroVM density          | High multi-tenancy                           | Thousands per host             |
| Startup time             | Serverless-friendly                          | ~125 ms                        |
| Memory overhead          | Extremely low                                | < 5 MiB per microVM            |
| Attack surface           | Minimal device model + seccomp               | Very small                     |
| Rate limiting            | Fairness & noisy-neighbor protection         | Built-in token bucket          |
| API                      | Full control (REST + Unix socket)            | Dynamic hot-plug (limited)     |
| Snapshotting             | Fast restore (page-fault handling)           | Supported (with userfaultfd)   |

**Supported guests:** Linux ≥ 4.14, OSv.

## 5. Installation & Quick Setup

### Get Firecracker binary
```bash
# Prebuilt (recommended)
ARCH=$(uname -m)
LATEST=$(curl -s https://api.github.com/repos/firecracker-microvm/firecracker/releases/latest | grep tag_name | cut -d'"' -f4)
curl -L "https://github.com/firecracker-microvm/firecracker/releases/download/${LATEST}/firecracker-${LATEST}-${ARCH}.tgz" | tar -xz
mv release-*/firecracker-${LATEST}-${ARCH} firecracker
```

### Kernel + Rootfs (from Firecracker CI)
See `docs/getting-started.md` for the exact `wget` commands to latest `vmlinux` and Ubuntu ext4 rootfs, then patch SSH keys.

**Host prerequisites:**
- Linux with KVM (`/dev/kvm` readable/writable by the jailer user)
- cgroup v1 or v2 mounted
- `ip tuntap`, `iptables`, etc. for networking

## 6. Detailed Samples

### Sample 1: Minimal config.json (used with Jailer)
```json
{
  "boot-source": {
    "kernel_image_path": "./vmlinux",
    "boot_args": "console=ttyS0 reboot=k panic=1"
  },
  "drives": [
    {
      "drive_id": "rootfs",
      "path_on_host": "./rootfs.ext4",
      "is_root_device": true,
      "is_read_only": false
    }
  ],
  "network-interfaces": [
    {
      "iface_id": "eth0",
      "guest_mac": "06:00:AC:10:00:02",
      "host_dev_name": "tap0"
    }
  ],
  "machine-config": {
    "vcpu_count": 2,
    "mem_size_mib": 512,
    "track_dirty_pages": true
  },
  "logging": {
    "log_path": "firecracker.log",
    "level": "Info"
  }
}
```

### Sample 2: Full API-driven launch (without Jailer, for dev)
(See `docs/getting-started.md` for the complete bash script that does PUTs to `/logger`, `/boot-source`, `/drives`, `/network-interfaces`, then `/actions` to start the instance.)

### Sample 3: Production Jailer + config launch (one-liner pattern)
```bash
# After preparing chroot, kernel, rootfs, tap device, and config.json inside jail
sudo ./jailer --id vm-prod-42 \
  --exec-file ./firecracker \
  --uid 1000 --gid 1000 \
  --chroot-base-dir /srv/jailer \
  --cgroup cpu.shares=2048 \
  --cgroup memory.limit_in_bytes=1G \
  -- \
  --config-file /config.json
```

**Networking setup (host side – required for every VM):**
```bash
sudo ip tuntap add dev tap0 mode tap
sudo ip addr add 172.16.0.1/30 dev tap0
sudo ip link set tap0 up
# iptables NAT + forwarding (see getting-started.md)
```

## 7. Best Practices (Production)

### Host Setup (from `docs/prod-host-setup.md`)
- **Always** use Jailer + dedicated low-privilege UID/GID per VM.
- Disable swap (prevents data remanence).
- Disable SMT and KSM for strong tenant isolation.
- Apply kernel mitigations for side-channel attacks (spectre/meltdown checker).
- Use bounded logging (journald + logrotate or named pipes).
- Set `quiet loglevel=1` on host kernel cmdline.
- Deploy an **overwatcher** process that SIGKILLs unresponsive Firecracker instances.
- Use cgroup controllers aggressively (CPU, memory, blkio).
- Rate-limit **every** network and block device.
- Patch host kernel, microcode, and guest kernels regularly.

### Security
- Thread-specific seccomp filters (default = most restrictive).
- Jailer chroot + cgroup + namespace + privilege drop = multiple barriers.
- Guest kernels should be minimal (no unnecessary modules).
- Never expose Firecracker API socket outside the jail.

### Performance & Operations
- CPU templates for consistent guest CPUID.
- Memory hotplug support.
- Vsock for efficient guest ↔ host communication.
- Snapshot + restore for cold-start optimization (with `userfaultfd`).

### Monitoring
- Firecracker emits logs & metrics to named pipes (configurable).
- Use Prometheus + custom exporters or AWS CloudWatch-style scraping.

## 8. Common Pitfalls & Tips

- Firecracker binary **must** be statically linked (musl) when used with Jailer.
- Always pre-create TAP devices and network namespaces before starting Jailer.
- Rootfs must be ext4 (or supported FS) and properly sized.
- Guest kernel needs `console=ttyS0` (no graphical console).
- For high density: tune host sysctls (`net.core.somaxconn`, etc.) and use huge pages if needed.

## 9. Resources & Further Reading

- Official Docs (all in repo `/docs/`):
  - `design.md`, `jailer.md`, `prod-host-setup.md`, `getting-started.md`
  - `api_requests.md` (full OpenAPI spec)
  - `cpu_templates/`, `snapshotting/`, `vsock.md`, `memory-hotplug.md`
- SPECIFICATION.md (performance guarantees)
- firecracker-containerd (for Kubernetes/containerd integration)
- Kata Containers + Firecracker
- Community Slack: https://join.slack.com/t/firecracker-microvm/...
- Snapshotting: `references/snapshotting.md`
- Userfaultfd Handler Implementation: `references/userfaultfd.md`
- Online docs: [Online docs](https://github.com/firecracker-microvm/firecracker/tree/main/docs)


## 10. References
- **API Change Runbook**: [api-change-runbook.md](api-change-runbook.md) — Process for managing breaking and non-breaking API changes.
- **Ballooning**: [ballooning.md](ballooning.md) — Memory balloon device configuration for dynamic memory management.
- **Design**: [design.md](design.md) — Core architecture, threat containment, and machine model overview.
- **Development Machine Setup**: [dev-machine-setup.md](dev-machine-setup.md) — Guide for setting up development environments.
- **Device API**: [device-api.md](device-api.md) — Device configuration matrix for the Firecracker API.
- **Entropy**: [entropy.md](entropy.md) — virtio-rng device for providing entropy to the guest.
- **Formal Verification**: [formal-verification.md](formal-verification.md) — Safety verification using formal methods (Kani).
- **Fuzzing**: [fuzzing.md](fuzzing.md) — Documentation on fuzzing for internal code testing.
- **GDB Debugging**: [gdb-debugging.md](gdb-debugging.md) — How to debug the guest kernel using GDB.
- **Getting Started**: [getting-started.md](getting-started.md) — Quickstart guide for running Firecracker.
- **Huge Pages**: [hugepages.md](hugepages.md) — Using huge pages for guest memory performance tuning.
- **Initrd**: [initrd.md](initrd.md) — Booting Firecracker with an initial ramdisk (initrd).
- **Jailer**: [jailer.md](jailer.md) — Isolation and security mechanism for Firecracker processes.
- **Kernel Policy**: [kernel-policy.md](kernel-policy.md) — Version requirements and configuration for host and guest kernels.
- **Logger**: [logger.md](logger.md) — API and configuration for Firecracker's logging system.
- **Memory Hotplug**: [memory-hotplug.md](memory-hotplug.md) — Support for dynamic memory expansion via virtio-mem.
- **Metrics**: [metrics.md](metrics.md) — Runtime performance tracking and metrics collection.
- **Network Performance**: [network-performance.md](network-performance.md) — Benchmarking network throughput in Firecracker.
- **Network Setup**: [network-setup.md](network-setup.md) — Comprehensive guide for guest networking configuration.
- **Persistent Memory**: [pmem.md](pmem.md) — virtio-pmem device for persistent memory emulation.
- **Production Host Setup**: [prod-host-setup.md](prod-host-setup.md) — Security and performance tuning best practices for production.
- **PVH Boot**: [pvh.md](pvh.md) — Using the PVH direct boot mode on x86_64.
- **Release Policy**: [RELEASE_POLICY.md](RELEASE_POLICY.md) — Semantic versioning, support lifetime, and release planning.
- **Rootfs and Kernel Setup**: [rootfs-and-kernel-setup.md](rootfs-and-kernel-setup.md) — Guides for building guest images and the kernel.
- **Seccomp**: [seccomp.md](seccomp.md) — Syscall filtering for enhanced microVM security.
- **Seccompiler**: [seccompiler.md](seccompiler.md) — Tooling for generating BPF filters for seccomp.
- **Tracing**: [tracing.md](tracing.md) — Instrumentation-based framework for performance and debug tracing.
- **Vsock**: [vsock.md](vsock.md) — Design and configuration of the virtio-vsock device for host-guest communication.

## API Requests
- **Actions**: [api_requests/actions.md](api_requests/actions.md) — Handling vApp lifecycle actions like start, shutdown, and metrics flush.
- **Block Caching**: [api_requests/block-caching.md](api_requests/block-caching.md) — Strategies for block device caching (Writeback vs Unsafe).
- **Block I/O Engine**: [api_requests/block-io-engine.md](api_requests/block-io-engine.md) — Sync and Async engine configurations for block I/O.
- **Block vhost-user**: [api_requests/block-vhost-user.md](api_requests/block-vhost-user.md) — Using the vhost-user protocol for block device emulation.
- **Patch Block Device**: [api_requests/patch-block.md](api_requests/patch-block.md) — Support for updating block device backends at runtime.
- **Patch Network Interface**: [api_requests/patch-network-interface.md](api_requests/patch-network-interface.md) — Dynamic management of networking rate limiters.

## CPU Templates
- **Boot Protocol**: [cpu_templates/boot-protocol.md](cpu_templates/boot-protocol.md) — CPU register specifications at boot for x86_64 and aarch64.
- **CPU Template Helper**: [cpu_templates/cpu-template-helper.md](cpu_templates/cpu-template-helper.md) — Tool guide for creating and managing custom CPU templates.
- **CPU Templates**: [cpu_templates/cpu-templates.md](cpu_templates/cpu-templates.md) — Configuring static and custom templates to mask CPU features.
- **CPUID Normalization**: [cpu_templates/cpuid-normalization.md](cpu_templates/cpuid-normalization.md) — How Firecracker normalizes host CPUID for guest exposure.
- **CPU Template Schema**: [cpu_templates/schema.json](cpu_templates/schema.json) — JSON schema definition for custom CPU templates.

## MicroVM Metadata Service (MMDS)
- **MMDS Design**: [mmds/mmds-design.md](mmds/mmds-design.md) — Internal architecture of MMDS and its networking stack (Dumbo).
- **MMDS User Guide**: [mmds/mmds-user-guide.md](mmds/mmds-user-guide.md) — Instructions for configuring and using the metadata service.

## Snapshotting
- **Handling Page Faults**: [snapshotting/handling-page-faults-on-snapshot-resume.md](snapshotting/handling-page-faults-on-snapshot-resume.md) — Managing memory loading via userfaultfd on resume.
- **Network for Clones**: [snapshotting/network-for-clones.md](snapshotting/network-for-clones.md) — Strategies for maintaining network isolation when cloning snapshots.
- **Random for Clones**: [snapshotting/random-for-clones.md](snapshotting/random-for-clones.md) — Ensuring entropy and RNG uniqueness across cloned microVMs.
- **Snapshot Editor**: [snapshotting/snapshot-editor.md](snapshotting/snapshot-editor.md) — Tool for manual manipulation of snapshot vmstate and memory files.
- **Snapshot Support**: [snapshotting/snapshot-support.md](snapshotting/snapshot-support.md) — Core features, API, and best practices for snapshot creation and restoration.
- **Snapshot Versioning**: [snapshotting/versioning.md](snapshotting/versioning.md) — Snapshot data format, encoding, and compatibility policies.

**Contributing & Roadmap:** See `CONTRIBUTING.md` and GitHub Projects.
