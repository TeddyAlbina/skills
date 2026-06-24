# cli-reference.md - vLLM Exhaustive CLI Command Flags

**Agent Skill Module**: vLLM CLI Reference (Child of SKILL.md)  
**Focus**: Complete, production-ready reference for every vLLM CLI command with **exhaustive flags**, options, defaults, types, descriptions, and usage patterns.  
**Version**: Based on vLLM stable documentation (as of May 2026) at https://docs.vllm.ai/en/stable/cli/.  
**Cross-references**: See `SKILL.md` (overview), `usage-reference.md` (patterns), `api-reference.md` (config classes).  
**Pro Tip for Agents**: All commands support advanced help:
- `vllm <command> --help` → full flag list
- `vllm <command> --help=listgroup` → list all config groups
- `vllm <command> --help=ModelConfig` (or CacheConfig, ParallelConfig, etc.) → group-specific flags

**JSON CLI Arguments** (all commands that accept complex configs):
- Nested JSON: `--json-arg '{"key1": "value1", "key2": {"key3": "value2"}}'`
- Dot notation: `--json-arg.key1 value1 --json-arg.key2.key3 value2`
- Lists: `--json-arg.key4+ value3 --json-arg.key4+='value4,value5'`


**References**:
- https://docs.vllm.ai/en/stable/cli/

---

## 1. Core Commands Overview

| Command              | Purpose                                      | Primary Use Case                     |
|----------------------|----------------------------------------------|--------------------------------------|
| `vllm serve`        | Launch OpenAI-compatible HTTP/gRPC server    | Production serving                  |
| `vllm chat`         | Interactive chat against a running server    | Quick testing / scripts             |
| `vllm complete`     | Non-chat completion against a running server | Prompt → completion testing         |
| `vllm bench`        | Benchmarking (latency / serve / throughput)  | Performance measurement             |
| `vllm run-batch`    | Offline batch processing from JSONL file     | Large-scale offline inference       |
| `vllm collect-env`  | Collect environment & hardware info          | Debugging / support                 |

---

## 2. `vllm serve` – OpenAI-Compatible Server (Most Important)

**Usage**:
```bash
vllm serve [OPTIONS] MODEL
```

**Key Global / Engine Flags** (partial exhaustive list from docs):
- `--headless` (bool, default: `False`) — Run in headless mode (for multi-node data parallel).
- `--api-server-count`, `-asc` (int) — Number of API server processes (defaults to `data_parallel_size`).
- `--config` (str, path to YAML) — Load all options from a YAML config file.
- `--grpc` (bool, default: `False`) — Launch gRPC server instead of HTTP (requires `pip install vllm[grpc]`).
- `--disable-log-stats` (bool, default: `False`)
- `--aggregate-engine-logging` (bool, default: `False`) — Aggregate logs in data-parallel mode.
- `--fail-on-environ-validation` / `--no-fail-on-environ-validation` (bool, default: `False`)
- `--shutdown-timeout` (int, default: `0`) — Seconds to wait before abort (0 = immediate abort).
- `--gdn-prefill-backend` (str: `flashinfer` | `triton`)
- `--enable-log-requests` / `--no-enable-log-requests` (bool, default: `False`)

**Frontend Arguments** (OpenAI-compatible server):
- `--host` (str) — Default: `0.0.0.0` (inferred)
- `--port` (int, default: `8000`)
- `--uds` (str) — Unix domain socket (overrides host/port)
- `--uvicorn-log-level` (str: `critical|debug|error|info|trace|warning`, default: `info`)
- `--disable-uvicorn-access-log` / `--no-disable-uvicorn-access-log` (bool, default: `False`)
- `--disable-access-log-for-endpoints` (comma-separated list, e.g. `/health,/metrics`)
- `--allow-credentials` / `--no-allow-credentials` (bool, default: `False`)
- `--allowed-origins` (list[str], default: `['*']`)
- `--allowed-methods` (list[str], default: `['*']`)
- `--allowed-headers` (list[str], default: `['*']`)
- `--api-key` (str) — Required API key(s) — supports multiple via space separation or env var `VLLM_API_KEY`
- `--ssl-keyfile`, `--ssl-certfile`, `--ssl-ca-certs`, `--ssl-cert-reqs`, `--ssl-keyfile-password`, `--ssl-ciphers`, `--ssl-version` (SSL/TLS options)

**Common Model / Engine Config Flags** (passed directly; full list via `--help=ModelConfig` etc.):
- `--model` (required) — HF repo ID or local path
- `--dtype` (`auto` | `float16` | `bfloat16` | `float32`)
- `--quantization` (awq, gptq, fp8, etc.)
- `--tensor-parallel-size`, `--pipeline-parallel-size`, `--data-parallel-size`
- `--gpu-memory-utilization` (float, default: `0.92`)
- `--max-model-len`, `--max-num-seqs`, `--enforce-eager`
- `--chat-template`, `--chat-template-content-format` (`auto` | `openai` | `string`, default: `auto`)
- `--lora-modules`, `--enable-lora`, `--max-loras`
- `--structured-outputs-config.backend` (auto | xgrammar | etc.)

**Full Source / More Details**: https://docs.vllm.ai/en/stable/cli/serve/

---

## 3. `vllm chat` – Chat Interface

**Usage**:
```bash
vllm chat [OPTIONS] [MESSAGE]...
```

**Exhaustive Flags**:
- `--url` (str, default: `http://localhost:8000/v1`) — Target server URL
- `--model-name` (str) — Overrides model name (defaults to first model from `/v1/models`)
- `--api-key` (str) — API key (overrides env var; only for OpenAI-compatible endpoints)
- `--system-prompt` (str) — Prepend system prompt
- `-q`, `--quick` (flag) — Send single prompt and exit immediately

**Examples**:
```bash
vllm chat --quick "Write a haiku about AI"
vllm chat --url http://remote:8000/v1 --api-key sk-xxx
```

**Full Source / More Details**: https://docs.vllm.ai/en/stable/cli/chat/

---

## 4. `vllm complete` – Text Completion Interface

**Usage**:
```bash
vllm complete [OPTIONS] PROMPT
```

**Exhaustive Flags**:
- `--url` (str, default: `http://localhost:8000/v1`)
- `--model-name` (str)
- `--api-key` (str)
- `--max-tokens` (int)
- `-q`, `--quick` (flag) — Single prompt + immediate exit

**Examples** (see usage patterns in usage-reference.md):
```bash
vllm complete -q --model-name meta-llama/Llama-3.2-1B-Instruct "The future of AI is"
```

**Full Source / More Details**: https://docs.vllm.ai/en/stable/cli/complete/

---

## 5. `vllm run-batch` – Offline Batch Processing

**Usage**:
```bash
vllm run-batch [OPTIONS]
```

**Key Flags** (shared with serve + batch-specific):
- `-i`, `--input-file` (str, required) — Input JSONL (local path or http/https URL)
- `-o`, `--output-file` (str, required) — Output JSONL (local or http PUT URL)
- `--output-tmp-dir` (str) — Temporary directory for output before upload
- All engine flags from `vllm serve` (disable-log-stats, enable-log-requests, etc.)
- All Frontend flags (chat-template, lora-modules, etc.)

**Notes**: Ideal for large-scale offline inference using the same engine as serving.

**Full Source / More Details**: https://docs.vllm.ai/en/stable/cli/run-batch/

---

## 6. `vllm bench` – Benchmarking Suite

**Subcommands**:
- `vllm bench latency` — Single-request latency benchmarking
- `vllm bench serve` — Full server throughput benchmarking
- `vllm bench throughput` — Offline throughput benchmarking

**Common Flags** (inherited from engine):
- `--model`, `--input-len`, `--output-len`, `--num-prompts`, `--tensor-parallel-size`, etc.
- Full EngineArgs / ModelConfig flags available via `--help=...`

**Full Source / More Details**: https://docs.vllm.ai/en/stable/cli/bench/ (use `vllm bench <subcommand> --help` for exact flags)

---

## 7. `vllm collect-env` – Environment Diagnostics

**Usage**:
```bash
vllm collect-env
```

**Flags**: Minimal (mostly no arguments). Collects:
- CUDA / ROCm / TPU version
- PyTorch / vLLM versions
- GPU memory, driver info, etc.

**Purpose**: Debugging, GitHub issues, support tickets.

**Full Source / More Details**: https://docs.vllm.ai/en/stable/cli/collect-env/

---

## 8. Best Practices & Agent Tips

- **Production Serving**: Always use `--api-key`, `--host 0.0.0.0`, and consider `--ssl-*` flags + reverse proxy.
- **Debugging**: `vllm collect-env` + `VLLM_LOGGING_LEVEL=DEBUG`
- **Config Reuse**: Use `--config myconfig.yaml` for repeatable deployments.
- **Help Commands** (memorize):
  ```bash
  vllm serve --help=ModelConfig
  vllm serve --help=CacheConfig
  vllm serve --help=ParallelConfig
```
- **Deprecated / Advanced**: Check docs for any hardware-specific flags (TPU, AMD, etc.).

**Maintenance Note**: Refresh against https://docs.vllm.ai/en/stable/cli/ and subpages when new subcommands or flags (e.g., new benchmark modes, gRPC enhancements) are added.


