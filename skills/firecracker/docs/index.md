# Firecracker Documentation Index

## General Documentation
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
