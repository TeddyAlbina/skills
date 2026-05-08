# vLLM metrics catalog
This describes the core metrics exposed by vLLM.

**Cross-references**: Use `SKILL.md` (overview)
---

Metrics are categorized below. Use `curl http://<service>:8000/metrics` to see the live list on any running pod.

#### General Metrics (Core Observability – Most Important for Monitoring)

| Metric Name                              | Type      | Description |
|------------------------------------------|-----------|-------------|
| `vllm:num_requests_running`              | Gauge     | Number of requests currently in model execution batches. |
| `vllm:num_requests_waiting`              | Gauge     | Number of requests waiting to be processed. |
| `vllm:num_requests_waiting_by_reason`    | Gauge     | Breakdown of waiting requests (`capacity`, `deferred` – LoRA, KV transfer, etc.). |
| `vllm:kv_cache_usage_perc`               | Gauge     | KV-cache usage (0–1; `1` = 100%). Critical for OOM prevention. |
| `vllm:engine_sleep_state`                | Gauge     | Engine sleep state (`awake`, `weights_offloaded`, `discard_all`). |
| `vllm:prefix_cache_hits`                 | Counter   | Prefix cache hits (tokens). |
| `vllm:prefix_cache_queries`              | Counter   | Prefix cache queries (tokens). |
| `vllm:external_prefix_cache_hits`        | Counter   | External (cross-instance) prefix cache hits via KV connector. |
| `vllm:external_prefix_cache_queries`     | Counter   | External prefix cache queries. |
| `vllm:prompt_tokens`                     | Counter   | Total prefill/prompt tokens processed. |
| `vllm:generation_tokens`                 | Counter   | Total generation tokens processed. |
| `vllm:prompt_tokens_cached`              | Counter   | Cached prompt tokens (local + external). |
| `vllm:request_success`                   | Counter   | Successfully processed requests (labeled by `finished_reason`: `stop`, `length`, `abort`). |
| `vllm:corrupted_requests`                | Counter   | Requests with NaNs in logits. |
| `vllm:mm_cache_hits` / `vllm:mm_cache_queries` | Counter | Multi-modal cache hits/queries. |
| `vllm:num_preemptions`                   | Counter   | Cumulative preemptions by the engine. |
| `vllm:lora_requests_info`                | Gauge     | LoRA adapter usage stats (running/waiting/max). |

#### Latency & Performance Histograms (Key SLO Metrics)

| Metric Name                                      | Type       | Description |
|--------------------------------------------------|------------|-------------|
| `vllm:time_to_first_token_seconds`               | Histogram  | Time to first token (TTFT). |
| `vllm:inter_token_latency_seconds`               | Histogram  | Inter-token latency (TPOT – Time Per Output Token). |
| `vllm:e2e_request_latency_seconds`               | Histogram  | End-to-end request latency. |
| `vllm:request_queue_time_seconds`                | Histogram  | Time spent in WAITING phase. |
| `vllm:request_prefill_time_seconds`              | Histogram  | Time spent in PREFILL phase. |
| `vllm:request_decode_time_seconds`               | Histogram  | Time spent in DECODE phase. |
| `vllm:request_inference_time_seconds`            | Histogram  | Total time in RUNNING phase. |
| `vllm:request_time_per_output_token_seconds`     | Histogram  | Time per output token per request. |
| `vllm:iteration_tokens_total`                    | Histogram  | Tokens processed per engine iteration. |

#### Request Parameter Histograms

| Metric Name                              | Type       | Description |
|------------------------------------------|------------|-------------|
| `vllm:request_prompt_tokens`             | Histogram  | Input prompt token count per request. |
| `vllm:request_generation_tokens`         | Histogram  | Generation tokens per request. |
| `vllm:request_max_num_generation_tokens` | Histogram  | Max tokens requested. |
| `vllm:request_params_max_tokens`         | Histogram  | `max_tokens` parameter value. |
| `vllm:request_params_n`                  | Histogram  | `n` (parallel sampling) parameter. |
| `vllm:request_prefill_kv_computed_tokens` | Histogram | New KV tokens computed during prefill (excl. cached). |

#### Speculative Decoding Metrics

- `vllm:spec_decode_num_accepted_tokens`
- `vllm:spec_decode_num_draft_tokens`
- `vllm:spec_decode_num_drafts`
- `vllm:spec_decode_num_accepted_tokens_per_pos`

#### KV Cache Residency (Sampled – Enable with `--kv-cache-metrics-sample`)

- `vllm:kv_block_lifetime_seconds`
- `vllm:kv_block_idle_before_evict_seconds`
- `vllm:kv_block_reuse_gap_seconds`

#### NIXL KV Connector Metrics (Advanced Cross-Instance Sharing)

- `vllm:nixl_num_failed_notifications`, `vllm:nixl_num_failed_transfers`, etc.
- Histograms for bytes transferred, descriptors, post time, xfer time.

#### Model Flops Utilization (MFU) Metrics (Enable with `--enable-mfu-metrics`)

- `vllm:estimated_flops_per_gpu_total`
- `vllm:estimated_read_bytes_per_gpu_total`
- `vllm:estimated_write_bytes_per_gpu_total`

**Additional Notes**:
- **HTTP metrics** (via FastAPI instrumentator): `http_requests_total`, `http_request_duration_seconds`, etc.
- **Cache config info**: `vllm:cache_config_info` (Gauge with labels like `block_size`, `gpu_memory_utilization`).
- **Legacy / Removed**: `cpu_cache_usage_perc`, `num_requests_swapped`, `tokens_total` (no longer present in v1).
- **PromQL Examples**:
  - Prefix cache hit rate: `rate(vllm:prefix_cache_hits[5m]) / rate(vllm:prefix_cache_queries[5m])`
  - Requests per second: `rate(vllm:request_success[1m])`
  - Avg TTFT: `histogram_quantile(0.95, sum(rate(vllm:time_to_first_token_seconds_bucket[5m])) by (le))`

## Official documentation
- https://docs.vllm.ai/en/stable/usage/metrics/
- https://docs.vllm.ai/en/stable/design/metrics/