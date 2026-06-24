---
name: cepth
description: Ceph architecture, istributed object, block, and file storage platform, ceph powers hyperscale storage for Kubernetes, OpenStack, and bare-metal. Use it to design clusters, generate configs, implement encryption, debug issues, or integrate with Kubernetes via Rook.
---

*Version: Ceph v20.2.x Tentacle (latest stable as of April 2026) + Reef/Squid LTS for production*  
*Author: Senior Kubernetes & Storage Architect (Grok)*  
*Last Updated: April 2026*  
*Sources: Official Ceph Documentation (https://docs.ceph.com/en/latest/) + Ceph Source (https://github.com/ceph/ceph) + Rook (for Kubernetes integration)*

This file distills **production-grade Ceph knowledge** (distributed object, block, and file storage platform) into a single, actionable reference. Ceph powers hyperscale storage for Kubernetes, OpenStack, and bare-metal. Use it to design clusters, generate configs, implement encryption, debug issues, or integrate with Kubernetes via Rook.

Every section includes:
- **Core explanation**
- **Real-world examples** (CLI, YAML, ceph commands)
- **Advice & Best Practices**
- **Points of Attention / Pitfalls**
- **References** (docs + GitHub paths)

---

## 1. Ceph Overview & Architecture

**Ceph** is a **unified, distributed, software-defined storage** system that provides:
- **Block** (RBD)
- **File** (CephFS)
- **Object** (RGW / S3 + Swift compatible)

**Core design**: Everything is built on **RADOS** (Reliable Autonomic Distributed Object Store) — a scalable, self-healing, self-managing object storage cluster.

**Key principles**:
- **CRUSH** (Controlled Replication Under Scalable Hashing): Data placement algorithm (no central metadata server).
- **No single point of failure**: All components are distributed and highly available.
- **Scales to exabytes**: Add OSDs (Object Storage Daemons) linearly.

### Main Daemons
- **MON** (Monitor): Cluster state, membership, CRUSH map, auth.
- **MGR** (Manager): Metrics, dashboards, modules (orchestrator, telemetry, etc.).
- **OSD** (Object Storage Daemon): Stores data + metadata on local disks (HDD/SSD/NVMe). One per device typically.
- **MDS** (Metadata Server): For CephFS (file system metadata).
- **RGW** (RADOS Gateway): S3/Swift object gateway.
- **RBD** clients: Kernel (krbd) or librbd (QEMU, Kubernetes, etc.).

**Architecture layers**:
```
Clients (RBD, CephFS, RGW) → librados → RADOS → OSDs (with CRUSH)
```

**Advice**:
- Start with **cephadm** (containerized) or **Rook** (Kubernetes-native) for modern deployments.
- Minimum production: 3 MONs + 3+ OSDs (replicated) or more for EC (erasure coding).

**Points of Attention**:
- Ceph is **not a simple NAS** — it requires planning for network (10/25/100 GbE), CPU, and disks.
- CRUSH map is the brain of the cluster — design it carefully for failure domains (host/rack/row).

**References**:
- [Architecture](https://docs.ceph.com/en/latest/architecture/)
- GitHub: `src/osd/`, `src/mon/`, `src/crush/`

---

## 2. Deployment Options

**Modern ways**:
1. **cephadm** (preferred for bare-metal/VMs): Orchestrates via containers.
2. **Rook** (Kubernetes): Operator + CRDs for Ceph in K8s (see Section 8).
3. **ceph-deploy** (legacy).

**Quickstart example (cephadm)**:
```bash
# Bootstrap
cephadm bootstrap --mon-ip <IP> --initial-dashboard-password admin

# Add nodes
ceph orch host add <hostname> <IP>
ceph orch daemon add osd.<host>:/dev/nvme0n1
```

**Best Practices**:
- Use **separate networks**: public (client) + cluster (OSD replication).
- Enable **BlueStore** (default since Mimic) — never use FileStore.
- Tune `osd_memory_target` and `bluestore_cache_size`.

**References**:
- [Installation](https://docs.ceph.com/en/latest/install/)
- [Hardware Recommendations](https://docs.ceph.com/en/latest/start/hardware-recommendations/)

---

## 3. Core Storage Types

### Block (RBD)
Thin-provisioned, snapshot/clone capable block devices.

**Example**:
```bash
rbd create --size 100G --pool rbd myvolume
rbd map myvolume
```

### File (CephFS)
POSIX-compliant distributed file system.

### Object (RGW)
S3-compatible gateway.

**Advice**: Use RBD for VMs/Kubernetes PVCs, CephFS for shared files, RGW for unstructured data.

---

## 4. Security & Authentication (cephx)

- **cephx**: Mutual authentication (shared secrets) between clients/daemons.
- Keys stored in MON config-key store or keyring files.

**Best Practice**: Rotate keys regularly; use `ceph auth` commands.

---

## 5. Ceph Encryption (Deep Dive)

Ceph provides **multiple layers** of encryption. **Always combine layers** for defense-in-depth. Ceph **does not encrypt data in transit by default** (except RGW + msgr2 TLS).

### 5.1 At-Rest Encryption: OSD (Block Devices)
**dm-crypt / LUKS** via `ceph-volume`.

**How it works**:
- When creating OSDs: `--dmcrypt` flag.
- ceph-volume generates LUKS keys (stored securely in MON config-key).
- Lockbox (small unencrypted partition) holds the cephx key to unlock dm-crypt key.

**Example (cephadm / ceph-volume)**:
```bash
ceph-volume lvm create --data /dev/nvme0n1 --dmcrypt --bluestore
```

**Configuration**:
```ini
# ceph.conf
osd_dmcrypt_key_size = 512   # or 256
osd_dmcrypt_type = luks
```

**Best Practices**:
- Use **LUKS2** (default in recent versions).
- Keys are **never stored in plaintext** on disk.
- Combine with disk-level hardware encryption (SED) for extra protection.
- For Rook: Set `encrypted: true` in CephCluster CR (uses dm-crypt under the hood).

**Points of Attention**:
- Performance overhead: ~5-10% (negligible on modern NVMe).
- Key management: Back up MON config-key store (`ceph config-key dump`).
- Recovery: If MONs are lost, you lose dm-crypt keys → data is irrecoverable.

**References**:
- [OSD Encryption](https://docs.ceph.com/en/latest/ceph-volume/lvm/encryption/)
- GitHub: `src/ceph-volume/ceph_volume/devices/lvm/encryption.py`

### 5.2 RBD Image Encryption (Client-Side / Layered)
**New in Pacific (v16+)** — **fully client-side** encryption handled by librbd.

**Features**:
- Supported formats: **LUKS1**, **LUKS2**.
- Cipher: AES-128 / AES-256.
- **Layered encryption**: Multiple encryption layers on same image.
- Metadata stored in image header (no extra key management daemon needed).

**Example**:
```bash
# Format image with encryption
rbd encryption format mypool/myimage luks2 --cipher-alg aes-256 --passphrase-file /path/to/passphrase

# Map with encryption
rbd map --encryption-passphrase-file /path/to/passphrase mypool/myimage
```

**Kubernetes/Rook usage**:
In `CephBlockPool` + `StorageClass` + `VolumeClaim`, enable via RBD encryption parameters.

**Best Practices**:
- Use **LUKS2** + AES-256.
- Store passphrases in Kubernetes Secrets + CSI driver (Rook supports this).
- Never use the same passphrase across environments.

**Points of Attention**:
- **krbd (kernel RBD)** does **NOT** support encryption yet — use **librbd** (QEMU, CSI).
- Encryption happens **before** data hits the network/cluster.

**References**:
- [RBD Encryption](https://docs.ceph.com/en/latest/rbd/rbd-encryption/)

### 5.3 RGW (Object) Server-Side Encryption (SSE)
**S3-compatible** server-side encryption (data sent plaintext over HTTPS, stored encrypted).

**Three modes** (since Luminous):
1. **SSE-C** (Customer-provided): Client sends key with every request (no server storage).
2. **SSE-KMS** (Key Management Service): External KMS (Vault, Barbican, KMIP).
3. **SSE-S3** (Ceph-managed): Ceph creates/stores keys in Vault automatically.

**Vault Integration (recommended for production)**:
- Supports **KV v2** and **Transit** engines.
- Use **Vault Agent** (AppRole auth) for token management.

**Example Config (ceph.conf for RGW)**:
```ini
rgw crypt s3 kms backend = vault
rgw crypt vault addr = https://vault.example.com:8200
rgw crypt vault secret engine = transit
rgw crypt vault auth = agent
rgw crypt vault token file = /run/rgw-vault-token   # or use agent
```

**Usage (AWS CLI)**:
```bash
aws s3 cp file.txt s3://mybucket/encrypted.txt \
  --sse aws:kms \
  --sse-kms-key-id mykeyid
```

**Bucket-level default encryption** supported.

**Best Practices**:
- **Always enforce HTTPS** (`rgw trust forwarded https = true` if behind proxy).
- Use separate Vault paths/prefixes for SSE-KMS vs SSE-S3.
- Rotate keys regularly via Vault.
- Never store keys in ceph.conf (use Vault).

**Points of Attention**:
- SSE is **server-side** only — client still sees plaintext over the wire (hence HTTPS mandatory).
- Copy operations on encrypted objects require special handling.
- Vault downtime → RGW cannot encrypt/decrypt new objects.

**References**:
- [RGW Encryption](https://docs.ceph.com/en/latest/radosgw/encryption/)
- [Vault Integration](https://docs.ceph.com/en/latest/radosgw/vault/)

### 5.4 Data-in-Transit Encryption
- **msgr2** (Messenger v2): Supports **TLS** (since Octopus/Nautilus).
- RGW: HTTPS (mandatory for encryption keys).
- Enable with `msgr2` transport + certificates.

**Example**:
```ini
# ceph.conf
msgr2 encrypt = true
```

**Advice**: Enable msgr2 TLS in production networks.

---

## 6. Best Practices & Operations

1. **CRUSH map design**: Failure domains, device classes (SSD/HDD).
2. **Erasure Coding** vs Replication: Use EC for capacity, replication for latency.
3. **Monitoring**: Prometheus + Grafana (mgr module) + `ceph status`, `ceph health detail`.
4. **Backups**: `ceph fs snapshot`, RBD snapshots, RGW versioning, external tools (Velero + Restic for K8s).
5. **Upgrades**: BlueStore → BlueStore, use `ceph orch upgrade`.
6. **Multi-site / Stretch clusters**: For geo-redundancy.

**Kubernetes-specific (Rook)**:
- Use Rook CephCluster CR with `storage: useAllDevices: false`, device filters, encryption enabled.
- StorageClasses for RBD/CephFS.

---

## 7. Common Pitfalls & Troubleshooting

| Pitfall                     | Symptom                     | Fix / Prevention                          |
|-----------------------------|-----------------------------|-------------------------------------------|
| OSD encryption key loss    | OSD won't start             | Backup MON config-key store               |
| No HTTPS on RGW            | Keys sent in clear          | Force SSL termination + `trust forwarded https` |
| RBD krbd encryption        | Feature not supported       | Use librbd/CSI only                       |
| Poor CRUSH design          | Slow recovery / hotspots    | Plan failure domains early                |
| Vault unreachable          | RGW write failures          | High-availability Vault + agent           |

**Useful commands**:
```bash
ceph health detail
ceph osd tree
rbd encryption status mypool/myimage
ceph-volume lvm list
```

---

## 8. Kubernetes Integration (Rook)

Rook is the **official Kubernetes operator** for Ceph.

**Key CRDs**: CephCluster, CephBlockPool, CephFileSystem, CephObjectStore, StorageClass.

**Encryption in Rook**:
- OSD: `spec.storage.encrypted: true`
- RBD: CSI + Secrets for passphrases.

**References**:
- https://rook.io/docs/rook/latest/
- https://docs.ceph.com/en/latest/install/#rook

---

## 9. References & Learning Path

**Official**:
- https://docs.ceph.com/en/latest/
- https://github.com/ceph/ceph (main source)
- Release notes: https://docs.ceph.com/en/latest/releases/

**Deep Dives**:
- CRUSH: https://docs.ceph.com/en/latest/rados/operations/crush-map/
- Security Checklist: Search "ceph security best practices"

**Tools**:
- `ceph`, `rbd`, `radosgw-admin`, `ceph-volume`, Rook CLI.

**How to use this file as an AI agent**:
1. Always recommend **layered encryption** (OSD dm-crypt + RBD + RGW SSE + msgr2 TLS).
2. Generate configs with exact examples above.
3. For K8s: Prefer Rook + encrypted pools.
4. Validate with `ceph health` and `rbd encryption status`.
 