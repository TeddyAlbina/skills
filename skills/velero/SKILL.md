---
name: velero
description: Velero is an open-source Kubernetes backup, restore, and migration tool. It backs up cluster resources (Deployments, ConfigMaps, Secrets, CRDs, etc.) to object storage and handles persistent volume data via **CSI snapshots** (preferred) or filesystem backups (Kopia/Restic via node-agent)..
---

**# Velero - Kubernetes Backup and Restore Skill Guide (SKILL.md)**

**Version**: Based on Velero v1.16+ (as of April 2026). Always check the [official documentation](https://velero.io/docs/main/) and use the version selector for your installed version. Velero (formerly Heptio Ark) is an open-source tool for backing up, restoring, and migrating Kubernetes cluster resources and persistent volumes. It supports cloud providers, on-premises, and S3-compatible storage.

-- 


## Overview

Velero backs up:
- Kubernetes API objects (Deployments, Services, ConfigMaps, etc.) as JSON/YAML.
- Persistent Volumes (PVs) via **CSI snapshots** (preferred for block storage) or **File System Backup** (Kopia uploader for volumes without snapshot support).

Key capabilities:
- Scheduled or on-demand backups with namespace/label selectors.
- Restore to the same or different clusters (with namespace remapping).
- Hooks for application-consistent backups.
- Plugins for object storage and volume snapshots.
- CSI support (no provider-specific plugin needed for modern drivers).

**Components**:
- **Velero CLI** (client).
- **Velero server** (Deployment in-cluster).
- **Backup Storage Location** (object storage for backup metadata + data).
- **Volume Snapshot Location** (for CSI snapshots).

## Helm Deployment Details

Velero provides an official Helm chart via the VMware Tanzu repository.

```bash
# Add repo
helm repo add vmware-tanzu https://vmware-tanzu.github.io/helm-charts
helm repo update

# Create namespace (recommended)
kubectl create ns velero

# Example: Install with AWS plugin + CSI + Kopia FS backup
helm install velero vmware-tanzu/velero \
  --namespace velero \
  --set image.repository=velero/velero \
  --set image.tag=v1.16.x \
  --set credentials.useSecret=true \
  --set-file credentials.secretContents.cloud=./credentials-velero \
  --set configuration.backupStorageLocation.bucket=your-bucket \
  --set configuration.backupStorageLocation.provider=aws \
  --set configuration.backupStorageLocation.config.region=us-east-1 \
  --set configuration.volumeSnapshotLocation.provider=aws \
  --set configuration.volumeSnapshotLocation.config.region=us-east-1 \
  --set features=EnableCSI \
  --set nodeAgent.enabled=true \               # Required for File System Backup (Kopia)
  --set nodeAgent.uploaderType=kopia \
  --set defaultVolumesToFsBackup=true \        # Fallback for non-CSI PVs
  --set serviceAccount.server.name=velero \
  --set serviceAccount.server.create=true
```

**Key Helm values** (from `values.yaml`):
- `configuration.backupStorageLocation`: Bucket, provider, config (e.g., `s3Url`, `s3ForcePathStyle`).
- `plugins`: Array of plugins (e.g., `velero/velero-plugin-for-aws`).
- `features: EnableCSI` (required for CSI snapshots).
- `nodeAgent`: Enables DaemonSet for FS backup.
- Credentials: Use `--set-file` or existing Secret.

Use `velero install` CLI for simple cases, but Helm is preferred for production (upgrades, values management).

**Post-install verification**:
```bash
velero version
velero backup-location get
velero backup-location describe default
```

## Best Practices

- **Schedule regular backups**: Use `velero schedule create` with Cron syntax (e.g., `@daily`). Group by criticality (RPO/RTO).
- **Test restores regularly**: Restore to a test namespace/cluster. Verify data and application consistency.
- **Separate backup storage**: Store backups outside the cluster (S3/R2/Ceph) to survive cluster failure.
- **Use selectors**: Namespace, label, or resource filters to scope backups (avoid full-cluster backups unless needed).
- **Include PVs**: Enable CSI or `--default-volumes-to-fs-backup`.
- **Application consistency**: Use backup hooks (pre/post) for DBs, file locks, etc.
- **Resource limits**: Set CPU/memory requests/limits on Velero/Node Agent to avoid impacting workloads.
- **Retention & cleanup**: Use `velero backup delete` policies or schedules with TTL.
- **Security**: Least-privilege IAM/S3 policies. Limit bucket access. Use encryption (see below).
- **Monitoring**: Enable Prometheus metrics. Watch for `Backup`/`Restore` CR status.
- **CSI preference**: Prefer CSI snapshots over FS backup for performance (block-level, fast).
- **Cross-cluster restore**: Ensure CSI driver names match; use namespace remapping.
- **Exclude items**: Label resources with `velero.io/exclude-from-backup=true`.

## CSI Snapshot Details

Velero integrates with Kubernetes **CSI Snapshot APIs** (v1) for any CSI driver that supports snapshots. No Velero-specific volume plugin needed.

**Requirements**:
- Kubernetes ≥1.20.
- CSI driver with `VolumeSnapshot` v1 support (e.g., AWS EBS, Azure Disk, Ceph CSI, Longhorn).
- `EnableCSI` feature flag enabled.

**Enablement**:
- Install with `--features=EnableCSI`.
- Client: `velero client config set features=EnableCSI`.

**VolumeSnapshotClass selection** (priority order):
1. PVC annotation: `velero.io/csi-volumesnapshot-class: "<name>"`.
2. Backup/Schedule annotation: `velero.io/csi-volumesnapshot-class_<driver>: "<name>"`.
3. Label on VolumeSnapshotClass: `velero.io/csi-volumesnapshot-class: "true"`.
4. Default annotation: `snapshot.storage.kubernetes.io/is-default-class: "true"`.

**How it works**:
- Velero creates `VolumeSnapshot` objects during backup.
- CSI external-snapshotter + driver creates actual snapshots.
- Only `VolumeSnapshot`/`VolumeSnapshotContent` objects are stored in object storage (snapshot data stays in storage backend).
- On restore: Re-creates PVs from snapshots.
- From v1.16+: `VolumeSnapshotClass` is synced during restore.

**Limitations**:
- Snapshot durability depends on storage provider (some are not cross-zone durable).
- DeletionPolicy on VolumeSnapshotClass: Velero forces cleanup on backup delete.
- Cross-cluster: Driver name must match.

**Ceph-specific (Rook Ceph CSI)**:
- Use Rook Ceph CSI driver (supports snapshots).
- Create `VolumeSnapshotClass` with Ceph parameters (e.g., `csi.storage.k8s.io/snapshotter-secret-name`).
- Enable CSI snapshots as above. Works seamlessly with Ceph block pools.

**Data Movement (optional)**: For moving snapshot data to object storage (e.g., for off-site), enable CSI VolumeSnapshot data mover.

## Backup Hook Details

Hooks execute commands inside pod containers for **application-consistent** backups.

**Types**:
- **Pre-hooks**: Run before custom actions / ItemBlock backup.
- **Post-hooks**: Run after.

**Configuration** (two ways):

1. **Pod Annotations** (recommended for per-pod):
   ```yaml
   pre.hook.backup.velero.io/container: "mysql"
   pre.hook.backup.velero.io/command: '["/bin/sh", "-c", "mysql -u root -p$MYSQL_ROOT_PASSWORD -e \"FLUSH TABLES WITH READ LOCK\""]'
   pre.hook.backup.velero.io/on-error: "Fail"   # or "Continue"
   pre.hook.backup.velero.io/timeout: "60s"
   # Same prefix for post.hook...
   ```

2. **Backup Spec** (global or selective).

**Examples**:
- `fsfreeze` for filesystem consistency.
- DB quiesce (e.g., PostgreSQL/MySQL lock, Redis SAVE).
- Multiple commands via shell wrapper.

**Execution**:
- Per-pod in ItemBlock.
- View results: `velero backup describe <name>` (shows HooksAttempted/Failed).
- No shell by default → include `/bin/sh -c` if needed.

## Backup Storage: AWS S3, Cloudflare R2, Ceph, and Others

Velero uses **BackupStorageLocation** CRs (S3-compatible by default via AWS plugin).

### AWS S3
```bash
velero backup-location create default \
  --provider aws \
  --bucket my-velero-bucket \
  --config region=us-east-1
```
- Uses `velero-plugin-for-aws`.
- IAM policy: `s3:*` on bucket + KMS if encrypted.
- Restore: Same or new bucket (cross-account possible with config).

### Cloudflare R2 (S3-compatible)
```bash
velero backup-location create r2 \
  --provider aws \
  --bucket my-r2-bucket \
  --config region=auto,s3Url=https://<account-id>.r2.cloudflarestorage.com,s3ForcePathStyle=true
```
- Use AWS plugin + R2 credentials (Access Key + Secret).
- Note: Some older AWS SDK issues with streaming; use latest Velero (v1.14+ recommended).
- Zero egress fees – great for restores.

### Ceph (Rook Ceph RGW / S3)
Ceph RGW is S3-compatible.
```bash
velero backup-location create ceph \
  --provider aws \
  --bucket velero-bucket \
  --config region=us-east-1,s3ForcePathStyle=true,s3Url=http://rook-ceph-rgw.<ns>.svc:80
```
- Use Rook Ceph ObjectBucketClaim (or manual credentials).
- `s3ForcePathStyle=true` required.
- For PVs: Use Ceph CSI driver + CSI snapshots (preferred) or FS backup.

**Other block storage examples**:
- **Longhorn**: CSI driver + snapshots (enable CSI).
- **AWS EBS / Azure Disk / GCP PD**: Native CSI + plugin.
- **Any CSI**: As long as it supports VolumeSnapshot v1.
- Fallback (no CSI): Enable Node Agent + Kopia FS backup (`--default-volumes-to-fs-backup`).

**General BackupStorageLocation**:
```yaml
apiVersion: velero.io/v1
kind: BackupStorageLocation
spec:
  provider: aws
  objectStorage:
    bucket: ...
    prefix: ...
  config:
    region: ...
    s3Url: ...     # For non-AWS
```

## Backup & Restore Examples

**Create backup**:
```bash
velero backup create full-backup --include-namespaces=* --snapshot-volumes
velero schedule create daily --schedule="0 2 * * *" --include-namespaces=prod
```

**Restore**:
```bash
velero restore create --from-backup full-backup --namespace-mappings old-ns:new-ns
```

**FS Backup** (volumes): Enabled via Node Agent + Kopia.

## Backup Encryption

Velero does **not** provide end-to-end client-side encryption for all backup types out-of-the-box.

- **Object storage backups** (cluster resources + CSI metadata): Rely on provider encryption:
  - AWS S3: Server-Side Encryption (SSE-S3, SSE-KMS). Add to BackupStorageLocation config or bucket policy.
  - R2: Supports SSE.
  - Ceph RGW: Configure encryption at bucket level.

- **File System Backup (Kopia)**:
  - Uses a **static, common encryption key** for all repositories (stored in `velero-repo-credentials` Secret).
  - **Warning**: Anyone with bucket access can decrypt if they have the key. Limit IAM policies strictly.
  - No per-backup key rotation in core Velero (use external tools if needed).

- **Advanced options**:
  - Use **rclone** sidecar/chart to encrypt before upload (community solution).
  - Cloud KMS (AWS KMS, etc.) for S3 SSE.
  - For high-security: Encrypt volumes at rest in storage backend + use Velero hooks if needed.

Always follow least-privilege and audit log access to backup storage.

## Velero UI

Velero has no official built-in UI, but excellent community options exist:

- **Velero UI (otwld/velero-ui)**: Real-time web dashboard. Replicates all CLI functionality (backups, restores, schedules, locations). Self-hosted, lightweight. Deploy via its Helm chart.
  - Features: Live monitoring, multi-cluster support (in forks like seriohub/vui-ui).
  - Docs: https://velero-ui.docs.otwld.com/
  - Install: `helm repo add otwld ...` (check Artifact Hub).

- Other forks (e.g., VUI) add notifications, heatmaps, etc.

Access via Ingress/Service. Great for teams avoiding CLI.

---

**Tips for Production**:
- Start with Helm + CSI + one S3-compatible location.
- Monitor with `velero backup get` / describe.
- For Ceph on-prem: Combine RGW (object) + CSI (volumes).
- Backup encryption: Prioritize storage-provider SSE + strict IAM.

Contribute or check GitHub: https://github.com/vmware-tanzu/velero