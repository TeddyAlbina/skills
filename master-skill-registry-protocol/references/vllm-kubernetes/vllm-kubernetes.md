---
name: vllm-kubernetes
description: Comprehensive guide for deploying vLLM (OpenAI-compatible LLM serving) on Kubernetes. Covers CPU-only, NVIDIA GPU, and AMD GPU (ROCm) deployments using raw manifests, Helm, KubeRay, and Production Stack. Includes resource scheduling, health probes (HTTP + gRPC), scaling, monitoring, and best practices
version: "1.0"
---

**Last Updated**: May 2026  

---

## Overview

vLLM is a high-throughput, memory-efficient LLM inference engine. Kubernetes deployment enables scalable, production-grade serving with autoscaling, observability, and multi-GPU support.

**Key Features Supported**:
- OpenAI-compatible API (`/v1/completions`, `/v1/chat/completions`)
- Model caching via PVC
- Horizontal/vertical scaling
- Liveness/readiness probes (`/health` HTTP endpoint or gRPC)
- **Full observability**: Prometheus metrics + Thanos sidecar + Loki logs
- Hardware-agnostic (CPU, NVIDIA, AMD)

**Supported Deployment Methods**:
- Raw Kubernetes YAML (Deployment + Service)
- Helm Chart (official vLLM chart)
- KubeRay (RayCluster integration)
- vLLM Production Stack (Helm-based multi-model router)

**Cross-references**
Use `references/vllm-metrics.md` (vLLM metric catalog) for detailed descriptions of all available metrics, including those mentioned below.

---

## Prerequisites

### Cluster Requirements
- Kubernetes ≥ 1.27 (for native gRPC probes)
- NVIDIA GPUs: NVIDIA GPU Operator or device plugin installed
- AMD GPUs: ROCm k8s-device-plugin installed
- CPU-only: Standard cluster (no device plugin needed)
- Storage: PersistentVolumeClaim (PVC) for model weights (recommended 50Gi+)
- Optional: Hugging Face token Secret for gated models

### Device Plugins

**NVIDIA**:
```bash
# Install via NVIDIA GPU Operator or manual:
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/master/nvidia-device-plugin.yml
```

**AMD (ROCm)**:
```bash
kubectl create -f https://raw.githubusercontent.com/ROCm/k8s-device-plugin/master/k8s-ds-amdgpu-dp.yaml
kubectl create -f https://raw.githubusercontent.com/ROCm/k8s-device-plugin/master/k8s-ds-amdgpu-labeller.yaml
```

### Common Secrets & PVC (apply first)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: hf-token-secret
type: Opaque
stringData:
  token: "hf_XXXXXXXXXXXXXXXXXXXXXXXX"
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: vllm-models
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
```

---

## Hardware-Specific Deployments

### CPU-only Deployment
Use CPU-optimized images. No GPU resources required.

**Key Differences**:
- Image: `public.ecr.aws/q9t5s3a7/vllm-cpu-release-repo:latest` (x86_64) or ARM64 variant
- No `nvidia.com/gpu` or `amd.com/gpu`
- Lower resource requests (no GPU overhead)

**Example Deployment YAML**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-cpu
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: vllm
  template:
    metadata:
      labels:
        app.kubernetes.io/name: vllm
    spec:
      containers:
      - name: vllm
        image: public.ecr.aws/q9t5s3a7/vllm-cpu-release-repo:latest
        command: ["/bin/sh", "-c"]
        args: ["vllm serve meta-llama/Llama-3.2-1B-Instruct --host 0.0.0.0"]
        env:
        - name: HF_TOKEN
          valueFrom:
            secretKeyRef:
              name: hf-token-secret
              key: token
        ports:
          - containerPort: 8000
        resources:
          limits:
            cpu: "10"
            memory: 20Gi
          requests:
            cpu: "2"
            memory: 6Gi
        volumeMounts:
          - name: models
            mountPath: /root/.cache/huggingface
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: vllm-models
```

**Service**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: vllm-cpu
spec:
  selector:
    app.kubernetes.io/name: vllm
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### NVIDIA GPU Deployment
Requires `nvidia.com/gpu` resource. Uses official `vllm/vllm-openai` image.

**Key Configuration**:
- Resource: `nvidia.com/gpu: N` (limits = requests)
- Shared memory (`/dev/shm`) for tensor parallelism
- Node selectors / tolerations for GPU nodes (optional)

**Example Deployment YAML** (single GPU):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-nvidia
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vllm-nvidia
  template:
    metadata:
      labels:
        app: vllm-nvidia
    spec:
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        command: ["/bin/sh", "-c"]
        args: ["vllm serve mistralai/Mistral-7B-Instruct-v0.3 --trust-remote-code --enable-chunked-prefill --max_num_batched_tokens 1024"]
        env:
        - name: HF_TOKEN
          valueFrom:
            secretKeyRef:
              name: hf-token-secret
              key: token
        ports:
        - containerPort: 8000
        resources:
          limits:
            cpu: "10"
            memory: 20Gi
            nvidia.com/gpu: 1
          requests:
            cpu: "2"
            memory: 6Gi
            nvidia.com/gpu: 1
        volumeMounts:
          - name: models
            mountPath: /root/.cache/huggingface
          - name: shm
            mountPath: /dev/shm
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: vllm-models
      - name: shm
        emptyDir:
          medium: Memory
          sizeLimit: "2Gi"
```

**Multi-GPU**: Set `nvidia.com/gpu: 2+` **and** add `--tensor-parallel-size N` to vLLM args.

### AMD GPU (ROCm) Deployment
Uses `amd.com/gpu` resource + ROCm-specific image and security context.

**Key Differences from NVIDIA**:
- Resource name: `amd.com/gpu`
- Image: `rocm/vllm:rocm6.2_mi300_ubuntu20.04_py3.9_vllm_0.6.4` (or latest ROCm variant)
- Requires `hostNetwork: true`, `hostIPC: true`
- SecurityContext: `SYS_PTRACE` + Unconfined seccomp
- Larger SHM (8Gi recommended)

**Example Deployment YAML**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-amd
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vllm-amd
  template:
    metadata:
      labels:
        app: vllm-amd
    spec:
      hostNetwork: true
      hostIPC: true
      containers:
      - name: vllm
        image: rocm/vllm:rocm6.2_mi300_ubuntu20.04_py3.9_vllm_0.6.4
        securityContext:
          seccompProfile:
            type: Unconfined
          runAsGroup: 44
          capabilities:
            add:
            - SYS_PTRACE
        command: ["/bin/sh", "-c"]
        args: ["vllm serve mistralai/Mistral-7B-v0.3 --port 8000 --trust-remote-code --enable-chunked-prefill --max_num_batched_tokens 1024"]
        env:
        - name: HUGGING_FACE_HUB_TOKEN
          valueFrom:
            secretKeyRef:
              name: hf-token-secret
              key: token
        ports:
        - containerPort: 8000
        resources:
          limits:
            cpu: "10"
            memory: 20Gi
            amd.com/gpu: 1
          requests:
            cpu: "6"
            memory: 6Gi
            amd.com/gpu: 1
        volumeMounts:
          - name: models
            mountPath: /root/.cache/huggingface
          - name: shm
            mountPath: /dev/shm
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: vllm-models
      - name: shm
        emptyDir:
          medium: Memory
          sizeLimit: "8Gi"
```

---

## Deployment Methods

### Raw Kubernetes YAML Manifests
See hardware-specific examples above. Apply with:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### Helm Chart
Official chart: `https://github.com/vllm-project/vllm/tree/main/examples/online_serving/chart-helm`

**Install**:
```bash
helm upgrade --install test-vllm . --namespace ns-vllm -f values.yaml
```

**Key `values.yaml` Excerpt** (NVIDIA-focused; adapt GPU resource):
```yaml
image:
  repository: vllm/vllm-openai
  tag: latest
replicaCount: 1
resources:
  limits:
    cpu: 4
    memory: 16Gi
    nvidia.com/gpu: 1
  requests:
    cpu: 4
    memory: 16Gi
    nvidia.com/gpu: 1
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
extraInit:
  pvcStorage: "10Gi"
```

For AMD/CPU: Override `gpuModels`, image, and resources manually.

Updated `values.yaml` Excerpt (full autoscaling + GPU example):

```yaml
image:
  repository: vllm/vllm-openai
  tag: latest

replicaCount: 1                     # overridden by HPA when autoscaling.enabled = true

resources:
  limits:
    cpu: "10"
    memory: 20Gi
    nvidia.com/gpu: 1               # or amd.com/gpu: 1 for ROCm
  requests:
    cpu: "2"
    memory: 6Gi
    nvidia.com/gpu: 1

autoscaling:
  enabled: true                     # Set to true to create HPA
  minReplicas: 1
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70   # Scale when average CPU > 70%

# Optional: deployment strategy for zero-downtime rolling updates
deploymentStrategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 25%
    maxSurge: 25%
```

For AMD/CPU deployments, simply change the GPU resource key and image as shown in hardware sections.


**Scaling & Autoscaling Configurations**
vLLM on Kubernetes supports **manual scaling** (`replicas`) and **automatic scaling** via Kubernetes Horizontal Pod Autoscaler (HPA).
**Important GPU Caveat** (from Kubernetes GPU scheduling docs):
- GPU resources (`nvidia.com/gpu`, `amd.com/gpu`) **must only appear** in `limits` (requests are implicitly equal to limits).
- Standard HPA scales **only on CPU/memory** (or custom metrics). It does **not** natively scale on GPU utilization.
- For GPU-aware scaling, use **KEDA** + Prometheus (vLLM exposes `/metrics` with `vllm:num_requests_running`, `vllm:gpu_cache_usage_perc`, etc.).



#### 1. Raw Kubernetes Manifests (HPA)
Create a separate hpa.yaml (works identically for CPU, NVIDIA, and AMD pods):

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vllm-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vllm-cpu          # or vllm-nvidia / vllm-amd
  minReplicas: 1
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  # Optional: Add memory metric
  # - type: Resource
  #   resource:
  #     name: memory
  #     target:
  #       type: Utilization
  #       averageUtilization: 80
```

Apply:

```bash
kubectl apply -f hpa.yaml
```

**Advanced: KEDA for vLLM queue / GPU metrics** (recommended for production GPU workloads):

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: vllm-keda-scaler
spec:
  scaleTargetRef:
    name: vllm-nvidia          # your Deployment
  minReplicaCount: 1
  maxReplicaCount: 20
  triggers:
  - type: prometheus
    metadata:
      serverAddress: http://prometheus:9090
      metricName: vllm_num_requests_running
      query: "vllm:num_requests_running{namespace='ns-vllm'}"
      threshold: "5"           # scale when >5 pending requests
```

### 2. Helm Chart Autoscaling (Official)
Already covered in `values.yaml` above.
When `autoscaling.enabled: true`, the chart automatically creates an `autoscaling/v2` HPA targeting CPU utilization.
No GPU-metric support in the official chart (CPU-only).

### KubeRay Integration
Deploys vLLM inside RayCluster for distributed serving + Ray autoscaler.  
**Reference**: Official vLLM KubeRay guide (YAML RayCluster with vLLM worker groups).  
Use for multi-node tensor/pipeline parallelism. GPU/CPU resources defined in Ray worker specs.

#### KubeRay autoscaler

KubeRay uses **Ray’s built-in autoscaler** (not Kubernetes HPA).
Define autoscaling inside the RayCluster CRD under workerGroupSpecs:

# Excerpt from RayCluster YAML

```yaml
spec:
  workerGroupSpecs:
  - groupName: vllm-workers
    replicas: 1
    minReplicas: 1
    maxReplicas: 10
    rayStartParams:
      num-gpus: "1"          # or 0 for CPU
    autoscaling:
      enabled: true
      # Ray autoscaler config (scales based on Ray metrics + pending tasks)
```

Full KubeRay + vLLM example is in the official integration guide. GPU/CPU resources are defined per worker pod.


### vLLM Production Stack
Helm-based full stack (serving + router/gateway + Grafana observability).  
**Install**:
```bash
helm repo add vllm https://vllm-project.github.io/production-stack
helm install vllm vllm/vllm-stack -f values.yaml
```
**values.yaml** example keys: `replicaCount`, `requestGPU: 1`, `pvcStorage`, `modelSpec`.

**Manual scaling only** (no built-in HPA).
Scale per model via values.yaml:

```yaml
servingEngineSpec:
  modelSpec:
  - name: "llama3-8b"
    replicaCount: 4          # manual replicas per model
    requestCPU: 6
    requestMemory: "24Gi"
    requestGPU: 1            # or 0 for CPU
```

The gateway/router pod can be scaled independently via its own `replicaCount`.

---


## Storage: Production Scaling
While the initial configuration for the `vllm-models` PVC uses `ReadWriteOnce` (RWO), this mode is restrictive for clusters utilizing the Horizontal Pod Autoscaler (HPA).

- **RWO vs. RWX**: The `ReadWriteOnce` configuration allows only one node to mount the volume at a time. For production-grade autoscaling where replicas may be scheduled across multiple distinct nodes, you must use a storage class that supports ReadWriteMany (RWX).

- **Persistent Volume Update**:

```yaml
kind: PersistentVolumeClaim
metadata:
  name: vllm-models-rwx
spec:
  accessModes:
    - ReadWriteMany  # Required for multi-node scaling
  resources:
    requests:
      storage: 100Gi
```
- **Local Node Caching**: If your environment does not support high-performance RWX storage, utilize an initContainer to pull model weights from object storage (S3/GCS) to a hostPath or emptyDir volume on each node. This avoids the RWO mounting conflict during scale-out events.

---

## Network Security
Security is critical, particularly when hardware requirements demand elevated network privileges.

- **Hardening hostNetwork**: AMD (ROCm) deployments specifically require hostNetwork: true and hostIPC: true, which bypasses the standard Kubernetes pod network isolation. This makes the pod's port 8000 accessible via the host's IP address.
- **NetworkPolicy Implementation**: To mitigate risks, implement a NetworkPolicy to restrict traffic. This is essential even for NVIDIA/CPU deployments to ensure only authorized services (like an API Gateway or Ingress) can reach the /v1/completions endpoints.

**Example NetworkPolicy (Restricted Ingress)**:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: vllm-ingress-restriction
  namespace: ns-vllm
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: vllm
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway  # Only allow your gateway to talk to vLLM
    ports:
    - protocol: TCP
      port: 8000
```
- **Namespace Isolation**: Always deploy vLLM in a dedicated namespace (e.g., ns-vllm) to apply "Default Deny" policies without affecting other workloads.
- **Security Context**: Even when granting SYS_PTRACE for AMD ROCm, ensure the rest of the securityContext remains as restrictive as possible to prevent container breakouts.

---

## Resource Management & Scheduling

- **GPU Scheduling** (Kubernetes native): GPUs only in `limits`. Equal requests/limits.
- **Node Selectors / Affinity**: Use labels like `accelerator=nvidia` or `gpu-vendor=amd`.
- **Tolerations**: For tainted GPU nodes.
- **CPU-only**: Standard `cpu`/`memory` requests.

See Kubernetes GPU docs for MIG/time-slicing.

---

## Health Checks & Probes

**Default (HTTP - Recommended for vLLM)**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 60
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 60
  periodSeconds: 5
```

**gRPC Probes** (if using gRPC serving):
Requires vLLM server implements `grpc.health.v1.Health` service.

```yaml
livenessProbe:
  grpc:
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
```

See gRPC Health Checking Protocol for status codes (`SERVING` / `NOT_SERVING`).

---

## Scaling & Autoscaling

- **HorizontalPodAutoscaler (HPA)**: CPU-based (or custom metrics for GPU utilization via KEDA).
- **KubeRay autoscaler**: Built-in for Ray workloads.
- **Production Stack**: Replica count + router-level load balancing.

---

## Monitoring & Observability

- **Prometheus**: Scrape `/metrics` (key metrics: `vllm_num_requests_running`, `vllm_gpu_cache_usage_perc`, `vllm_request_latency_seconds`).
- **Production Stack**: Includes Grafana dashboards.
- **Kubernetes Dashboard**: Monitor GPU allocation via `kubectl describe pod`.
- Use these for **KEDA** or custom HPA metrics.
- Production Stack includes Grafana dashboards out-of-the-box.
- **Thanos**: Long-term storage and global querying via Thanos sidecar (your stack pattern).  
- **Loki**: Centralized logs from pod stdout/stderr.

## Prometheus, Thanos, and Loki Integration (Thanos Sidecar Pattern)

vLLM **natively exposes Prometheus-compatible metrics** at `/metrics` (no extra flags or environment variables required). Logs are written to `stdout`/`stderr` (text or structured).  

This section shows exactly how to connect vLLM `pods` to your existing stack that uses **Prometheus Operator + Thanos sidecar** (for metrics long-term storage and HA) and **Loki** (for logs). No changes to vLLM Deployments are needed beyond standard labels.

### 1. Prometheus Metrics Scraping

Use **ServiceMonitor** (recommended) or **PodMonitor** from the Prometheus Operator.

**ServiceMonitor YAML** (apply in the same namespace as vLLM):

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: vllm-servicemonitor
  namespace: ns-vllm
  labels:
    release: prometheus   # or your Prometheus Operator release label
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: vllm   # matches labels from your Deployment/Service
  namespaceSelector:
    matchNames:
    - ns-vllm
  endpoints:
  - port: http                     # port name defined in your vLLM Service
    path: /metrics
    interval: 30s
    scrapeTimeout: 10s
    honorLabels: true
    relabelings:
    - sourceLabels: [__meta_kubernetes_pod_label_app]
      targetLabel: app
    - sourceLabels: [__meta_kubernetes_namespace]
      targetLabel: namespace
```

**Alternative**: PodMonitor (for direct pod scraping):

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: vllm-podmonitor
  namespace: ns-vllm
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: vllm
  podMetricsEndpoints:
  - port: 8000
    path: /metrics
    interval: 30s
```

**Key vLLM metrics you will see** (curl `http://<service>:8000/metrics` to explore):

- `vllm:num_requests_running`
- `vllm:num_requests_waiting`
- `vllm:gpu_cache_usage_perc`
- `vllm:cpu_cache_usage_perc`
- `vllm:request_latency_seconds` (histograms)
- `vllm:request_success_total`
Hardware-specific: GPU utilization, KV cache stats, etc.

Prometheus will now scrape every vLLM replica (CPU, NVIDIA, or AMD).


### 2. Prometheus Metrics Scraping
 
Your stack already uses the **Thanos sidecar pattern**. No extra work is required for vLLM:

- Prometheus (scraped by the ServiceMonitor/PodMonitor above) feeds metrics into the local Thanos sidecar.
- Thanos sidecar uploads TSDB blocks to your object storage (S3, GCS, Azure Blob, etc.).
- Thanos Querier provides a global view across all Prometheus instances and long-term retention.

**Typical Thanos sidecar snippet** (already present in your Prometheus StatefulSet / Operator CR):

```yaml
# Excerpt – already in your Prometheus deployment
containers:
- name: thanos-sidecar
  image: quay.io/thanos/thanos:v0.37.0   # or newer
  args:
  - sidecar
  - --tsdb.path=/prometheus
  - --http-address=0.0.0.0:10902
  - --prometheus.url=http://localhost:9090
  - --objstore.config-file=/etc/thanos/objstore.yaml   # S3/GCS config
  volumeMounts:
  - name: objstore-config
    mountPath: /etc/thanos
```

**Thanos Querier usage** (in Grafana datasource):
- URL: http://thanos-querier:9090
- You can now query vLLM metrics across clusters with long-term history.

### 3. Loki Logs Integration
vLLM logs go to stdout/stderr. Use **Promtail** (Loki’s official agent) with Kubernetes service discovery.
**Promtail scrape config** (add to your Promtail ConfigMap):


```yaml
scrape_configs:
- job_name: vllm-logs
  kubernetes_sd_configs:
  - role: pod
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_label_app_kubernetes_io_name]
    regex: vllm.*          # matches vllm-cpu, vllm-nvidia, vllm-amd, etc.
    action: keep
  - source_labels: [__meta_kubernetes_namespace]
    target_label: namespace
  - source_labels: [__meta_kubernetes_pod_name]
    target_label: pod
  - source_labels: [__meta_kubernetes_pod_label_app]
    target_label: app
  pipeline_stages:
  - cri: {}                 # handles container runtime log format
  - match:
      selector: '{app="vllm"}'
      stages:
      - regex:
          expression: '^(?P<timestamp>\d{4}-\d{2}-\d{2}T[^ ]+) (?P<level>\w+) '
      - labels:
          level:
```

**Deployment:**

- Deploy Promtail as DaemonSet (standard Loki+Kubernetes setup).
- In Grafana, add Loki datasource and query with labels: `{namespace="ns-vllm", app="vllm"}`

**Pro tip**: For structured logs, you can configure vLLM with `--log-level` and JSON output via environment variables or custom logging config (if using a custom image).

### 4. Grafana Visualization
- Import official/community vLLM dashboards (Perses or Grafana JSON from vLLM examples).
- Combine Prometheus (Thanos Querier) + Loki datasources.
- Typical panels: requests/sec, TTFT/TPOT latency, GPU cache usage, pod logs.

### 5. Expanded vLLM Metrics Catalog

vLLM exposes **dozens of production-grade Prometheus metrics** by default (no configuration required when using the OpenAI-compatible server). All metrics are prefixed with `vllm:` and include a `model_name` label (e.g., `model_name="meta-llama/Llama-3.1-8B-Instruct"`). Some metrics also carry additional labels such as `finished_reason` or `reason`.

See `references/vllm-metrics.md` (vLLM metric catalog) for detailed descriptions of all available metrics, including those mentioned below.

---

## Best Practices & Troubleshooting

1. **Model Download**: Use init container or pre-download to PVC.
2. **Shared Memory**: Always mount `/dev/shm` for multi-GPU/TP.
3. **Security**: Use least-privilege ServiceAccount; avoid `hostNetwork` unless AMD.
4. **Common Issues**:
   - GPU not visible → Check device plugin DaemonSet.
   - OOM → Increase memory + use `--max-model-len`.
   - Slow startup → Use `startupProbe`.
5. **Testing**:
```bash
   curl http://<service-ip>/v1/models
   curl http://<service-ip>/v1/completions -d '{"model": "...", "prompt": "..."}'
```
6. **Label consistency** — Use the same app.kubernetes.io/name: vllm label everywhere for ServiceMonitor + Promtail.
7. **Scrape interval** — Start at 30s; reduce to 15s for high-traffic workloads.
8. **Thanos retention** — Configure object storage bucket policies for 30/90/365-day retention.
9. **Common issues**:
   - No metrics → Verify port 8000 is reachable and /metrics returns 200.
   - Thanos sidecar errors → Check object-store credentials.
   - Loki missing logs → Confirm Promtail is running on the same nodes (DaemonSet).
10. **Testing**:
```bash
kubectl port-forward svc/vllm-nvidia 8000:8000
curl http://localhost:8000/metrics | head -20
```
```bash
kubectl port-forward svc/vllm-nvidia 8000:8000
curl http://localhost:8000/metrics | grep -E 'vllm:(num_requests|kv_cache|time_to_first)'
```

---

### Best Practices & Troubleshooting (Autoscaling-Specific)

1. **Start with CPU-based HPA** for simplicity.
2. **Use KEDA** for production GPU workloads (scale on queue length or GPU cache usage).
3. **Cluster Autoscaler**: Ensure GPU node groups can scale up when new GPU pods are scheduled.
4. **Cooldown periods**: Set `behavior` in HPA to prevent flapping:YAMLbehavior:
```yaml
  scaleUp:
    stabilizationWindowSeconds: 60
  scaleDown:
    stabilizationWindowSeconds: 300
```

5. **Common issues**:
   - HPA not scaling → Check metrics server (kubectl get --raw /apis/metrics.k8s.io).
   - GPU pods pending → Insufficient GPU nodes (use Cluster Autoscaler + node selectors).
   - Slow scale-up → Increase initialDelaySeconds on probes.
6. **Testing autoscaling**:

```bash
kubectl autoscale deployment vllm-nvidia --cpu-percent=70 --min=1 --max=10
# Simulate load with locust / hey against /v1/chat/completions
```

---

**Sources & Further Reading**:
- vLLM K8s Guide
- vLLM Helm Chart
- vLLM Production Stack
- ROCm k8s-device-plugin vLLM example
- Kubernetes GPU Scheduling
- gRPC Health Checking + K8s gRPC Probes


## Official documentation
- https://docs.vllm.ai/en/stable/deployment/k8s/
- https://docs.vllm.ai/en/stable/deployment/frameworks/helm/
- https://docs.vllm.ai/en/stable/deployment/integrations/kuberay/
- https://docs.vllm.ai/en/stable/deployment/integrations/production-stack/
- https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/
- https://github.com/ROCm/k8s-device-plugin/tree/master/example/vllm-serve
- https://github.com/grpc/grpc/blob/master/doc/health-checking.md
- https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/#define-a-grpc-liveness-probe
- https://docs.vllm.ai/en/stable/usage/metrics/
- https://docs.vllm.ai/en/stable/design/metrics/