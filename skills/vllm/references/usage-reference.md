# usage-reference.md - vLLM Detailed Serving & Offline Inference Patterns

**Agent Skill Module**: vLLM Usage Patterns (Child of SKILL.md)  
**Focus**: Comprehensive patterns for **offline inference** (LLM class, Ray Data, examples) and **online serving** (OpenAI-compatible server via `vllm serve`).  
**Version**: Based on vLLM stable documentation (as of May 2026).  
**Cross-references**: See `SKILL.md` for overview/installation, `api-reference.md` for full class signatures, `cli-reference.md` for exhaustive flags.

This file organizes **production-ready patterns** with verbatim code examples, configuration options, best practices, and advanced usage. All patterns are drawn directly from the official docs at `/serving/offline_inference.html` and `/serving/openai_compatible_server/`, plus linked examples.


**References**
- https://docs.vllm.ai/en/stable/usage/

---

## 1. Offline Inference Patterns

Offline inference uses the `vllm.LLM` class (or Ray Data wrapper) for batch processing inside your own Python code — no separate server required.

### 1.1 Basic LLM Class Usage (Core Pattern)
```python
from vllm import LLM

# Initialize engine (downloads from HF by default)
llm = LLM(model="facebook/opt-125m")   # or any supported model

# After init, use model-type-specific APIs:
# - Generative models → .generate() / .chat()
# - Pooling models → hidden states
```

**Key Initialization Options** (passed to `LLM(...)`):

- `model`: HF repo ID or local path
- `dtype`: auto (recommended), `float16`, `bfloat16`, etc.
- `quantization`: `awq`, `gptq`, `fp8`, etc.
- `tensor_parallel_size`, `pipeline_parallel_size`
- `enable_lora`, `max_loras`, `lora_dtype`
- `max_model_len`, `max_num_seqs`, `gpu_memory_utilization`
- `enforce_eager` (for debugging)

### 1.2 Generation APIs
Use `SamplingParams` for control (temperature, top_p, etc.).
**Full example** (common pattern):

```python
from vllm import LLM, SamplingParams

llm = LLM(model="Qwen/Qwen2.5-1.5B-Instruct")

sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.95,
    max_tokens=256,
    stop=["\n\n"]
)

prompts = ["Hello, my name is", "The capital of France is"]
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(f"Prompt: {output.prompt}")
    print(f"Generated: {output.outputs[0].text}")
```

**Chat API** (for instruction-tuned models):

```python
messages_list = [
    [{"role": "user", "content": "Write a haiku about AI"}],
    # ... more conversations
]
outputs = llm.chat(messages_list, sampling_params)
```

### 1.3 Ray Data LLM API (Large-Scale / Distributed Offline)

For datasets too big for memory, automatic sharding, continuous batching, and Ray cluster scaling.

```python
import ray
from ray.data.llm import vLLMEngineProcessorConfig, build_llm_processor

config = vLLMEngineProcessorConfig(
    model_source="unsloth/Llama-3.2-1B-Instruct",
    # tensor_parallel_size=2, etc.
)

processor = build_llm_processor(
    config,
    preprocess=lambda row: {
        "messages": [
            {"role": "system", "content": "You are a bot that completes unfinished haikus."},
            {"role": "user", "content": row["item"]},
        ],
        "sampling_params": {"temperature": 0.3, "max_tokens": 250},
    },
    postprocess=lambda row: {"answer": row["generated_text"]},
)

ds = ray.data.from_items(["An old silent pond..."])
ds = processor(ds)
ds.write_parquet("local:///tmp/data/")
```

**When to use**: Petabyte-scale inference, multi-GPU clusters, fault-tolerant pipelines.

### 1.4 Advanced Offline Patterns (Examples from vLLM repo)

- **Multi-LoRA Inference:** Load multiple LoRAs simultaneously → `examples/offline_inference/multilora_inference/`
- **Vision-Language Models:** Correct prompt format for LLaVA, Qwen-VL → `examples/offline_inference/vision_language/`
- **Qwen3 / Qwen2.5-Omni:** Audio + image + video (thinker-only or full) → `examples/offline_inference/qwen3_omni/ and qwen2_5_omni/`
- **Context Extension (YARN):** Extend max position embeddings → `examples/offline_inference/context_extension/`
- **Disaggregated Prefill:** Separate prefill/decode GPUs → `examples/offline_inference/disaggregated_prefill/`
- **OpenAI Batch File Format:** Mix chat/completion/embedding in one JSONL batch → `examples/offline_inference/openai_batch/`

**Best Practice:** Start with basic `LLM` for prototyping, move to Ray Data or examples for scale.

## 2. Online Serving Patterns (OpenAI-Compatible Server)

Launch a production-grade HTTP server with one command. Drop-in replacement for OpenAI API.

### 2.1 Quickstart `vllm serve` Command

```python
vllm serve NousResearch/Meta-Llama-3-8B-Instruct \
  --dtype auto \
  --api-key token-abc123 \
  --host 0.0.0.0 \
  --port 8000
```


**Common Flags** (full list in cli-reference.md):

- `--api-key` / `VLLM_API_KEY`: Authentication
- `--generation-config vllm`: Disable HF generation_config.json
- `--chat-template ./custom.jinja`: Manual chat template
- `--enable-request-id-headers`: Add `X-Request-Id`
- `--enable-offline-docs`: Enable `/docs` in air-gapped envs
- `--structured-outputs-config.backend auto`: Choose structured output backend


### 2.2 Client Interaction Patterns
**Python OpenAI Client:**

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="token-abc123",
)

completion = client.chat.completions.create(
    model="NousResearch/Meta-Llama-3-8B-Instruct",
    messages=[{"role": "user", "content": "Hello!"}],
    extra_body={"top_k": 50},   # vLLM-specific param
)
print(completion.choices[0].message)
```

**cURL Example** (Completions):

```python
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token-abc123" \
  -d '{
    "model": "NousResearch/Meta-Llama-3-8B-Instruct",
    "prompt": "San Francisco is a",
    "max_tokens": 7
  }'
```

### 2.3 Supported APIs & Special Features

| API Endpoint             | Use Case                        | Notes                   |
|--------------------------|---------------------------------|-------------------------|
| `/v1/chat/completions`     | Chat models                     | Requires chat template  |
| `/v1/completions`         | Text generation                 | `suffix` not supported    |
| `/v1/responses`            | OpenAI Responses API            | Reasoning models        |
| `/v1/embeddings`           | Embedding models                | —                       |
| `/v1/audio/transcriptions` | ASR models                      | `pip install vllm[audio]` |
| `/v1/rerank`               | Reranking (Jina/Cohere)         | —                       |
| `/tokenize`, `/detokenize`   | Custom tokenizer ops            | Any model               |
| `/pooling`, `/classify`      | Pooling / classification models | —                       |


**Multi-Modal Chat Messages:**

```python
messages = [{
    "role": "user",
    "content": [
        {"type": "text", "text": "Describe this image"},
        {"type": "image_url", "image_url": {"url": "https://..."}}
    ]
}]
```
**Structured Outputs / Tool Calling:**
Pass via `extra_body` or native OpenAI fields. Use `--structured-outputs-config.backend` flag.

### 2.4 Advanced Serving Patterns

- **LoRA / Multi-LoRA serving**: Enable at launch with `--enable-lora`
- **Parallelism**: Tensor/pipeline/expert/context parallel via config flags
- **Observability**: `/metrics` endpoint (Prometheus), OpenTelemetry
- **Security**:
  - Use -`-api-key`
  - Run behind reverse proxy (nginx/Envoy)
  - Network isolation for multi-node
  - `--allowed-media-domains` for multimodal file URLs
- **Docker Deployment**: Official vllm/vllm-openai images
- **Disaggregated Prefill/Decode**: Separate processes for ultra-low latency

**Best Practice**: Always set `--api-key` in production. Use `extra_body` for vLLM-only params. Monitor `/metrics` for throughput/latency.

## 3. When to Choose Offline vs. Serving

| Scenario                         | Recommended Pattern      | Why                     |
|----------------------------------|--------------------------|-------------------------|
| Batch processing large dataset   | Offline (`LLM` + Ray Data) | No HTTP overhead        |
| Real-time API for many clients   | `vllm serve`               | OpenAI compatibility    |
| Production micro-service         | `vllm serve` + Kubernetes  | Scaling & observability |
| Research / single GPU experiment | Offline `LLM`             | Simpler code            |

##4. Best Practices & Troubleshooting (Agent Tips)

- **Performance**: Use PagedAttention (default), quantization, prefix caching, speculative decoding.
- **Chat Templates**: Always verify with `tokenizer.apply_chat_template` or provide `--chat-template`.
- **Memory**: Tune `gpu_memory_utilization` (default 0.9) and `max_num_seqs`.
- **Debug**: `vllm collect-env`, set `VLLM_LOGGING_LEVEL=DEBUG`.
- **Scaling**: Ray Data for offline clusters; `--api-server-count` for multi-process serving.
- **Examples Repo**: All advanced patterns live at `https://github.com/vllm-project/vllm/tree/main/examples` (offline_inference/ and online_serving/).
  
**Agent Usage**: When user asks for a specific pattern (e.g., “serve Llama with LoRA” or “batch inference on 10k prompts”), return the exact code block above + relevant flags.
Maintenance: Refresh against https://docs.vllm.ai/en/stable/serving/offline_inference/ and https://docs.vllm.ai/en/stable/serving/openai_compatible_server/ when new features (e.g., new APIs, kernels) appear.