---
name: vllm
description: comprehensive knowledge of vLLM (a fast, easy-to-use library for LLM inference and serving). The agent can install, configure, run offline/online inference, serve OpenAI-compatible APIs, benchmark, contribute to the project, and use the full Python API/CLI..
version: "2.0"
---

**Core Capabilities**:
- Explain vLLM architecture, features, and performance advantages.
- Provide installation instructions for NVIDIA, AMD, TPU, and other hardware.
- Generate code for offline batched inference, chat templates, and multi-modal support.
- Launch and interact with the OpenAI-compatible server.
- Use CLI commands for serving, benchmarking, and batch processing.
- Navigate the Python API (LLM class, configs, engines).
- Follow contribution guidelines for PRs, testing, and documentation.
- Troubleshoot common issues (CUDA versions, quantization, memory management).
---


## 1. Overview

vLLM is a **fast and easy-to-use library for LLM inference and serving**, originally developed in the Sky Computing Lab at UC Berkeley. It powers high-throughput serving of open-source models with minimal code.

### Key Features & Benefits
- **Performance**: PagedAttention (KV cache management), continuous batching, chunked prefill, prefix caching, CUDA/HIP graphs, optimized kernels (FlashAttention, FlashInfer, CUTLASS, etc.), speculative decoding (EAGLE, n-gram, etc.), and `torch.compile` support. Claims up to **23x throughput improvement** over naive serving.
- **Quantization**: FP8, INT4/8, GPTQ/AWQ, GGUF, TorchAO, ModelOpt, compressed-tensors, and more.
- **Flexibility**: Hugging Face integration, tensor/pipeline/expert/context parallelism, streaming, structured outputs (xgrammar), tool calling, LoRA support (dense & MoE).
- **Serving**: OpenAI-compatible API server + Anthropic Messages + gRPC.
- **Hardware**: NVIDIA/AMD GPUs, x86/ARM/PowerPC CPUs, Google TPUs, Intel Gaudi, Apple Silicon, Huawei Ascend, and more.
- **Models**: 200+ architectures (Llama, Qwen, Mixtral, Mamba, LLaVA, embedding/reward models, etc.). Full list in official supported models section.

**Project Links**:
- GitHub: https://github.com/vllm-project/vllm
- Paper: https://arxiv.org/abs/2309.06180
- Blog: https://blog.vllm.ai/2023/06/20/vllm.html

**License**: Apache 2.0 (see LICENSE in repo).

---

## 2. Installation & Quickstart

**Prerequisites**:
- Linux OS
- Python 3.10–3.13
- NVIDIA: CUDA 12.x (auto-detected)
- AMD: ROCm 7.0 + glibc ≥2.35
- TPU: `vllm-tpu` package

### Recommended Installation (uv)

```bash
uv venv --python 3.12 --seed
source .venv/bin/activate
uv pip install vllm --torch-backend=auto
```

**Alternatives:**

- Specific CUDA: `uv pip install vllm --torch-backend=cu126` or export `UV_TORCH_BACKEND=cu126`
- Conda: `conda create -n myenv python=3.12 && conda activate myenv && uv pip install vllm --torch-backend=auto`
- AMD (ROCm): `uv pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/`
- TPU: `uv pip install vllm-tpu`
- Nightly/Docker: `Official vllm/vllm-openai images (AMD: vllm/vllm-openai-rocm:nightly)`

**From source** or advanced setups → see full installation guide.

**Offline Batched Inference (Python)**

```python
from vllm import LLM, SamplingParams

prompts = [
    "Hello, my name is",
    "The president of the United States is",
]

sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

# Load model (HF by default; use VLLM_USE_MODELSCOPE=True for ModelScope)
llm = LLM(model="facebook/opt-125m")  # or "Qwen/Qwen2.5-1.5B-Instruct"

outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(f"Prompt: {output.prompt!r}")
    print(f"Generated: {output.outputs[0].text!r}")
```

**Chat models:**

- Use `tokenizer.apply_chat_template(...)` from `transformers`, or
- `llm.chat(messages_list, sampling_params)`

Override generation config: `LLM(..., generation_config="vllm")`

**Online Serving (OpenAI-Compatible Server)**

```bash
vllm serve Qwen/Qwen2.5-1.5B-Instruct --host 0.0.0.0 --port 8000
```

**API Key:**
```bash
vllm serve ... --api-key mykey1 mykey2
# or
export VLLM_API_KEY=mykey1
```

**Test with curl / openai Python client** (see examples below in CLI section).

## 3. Usage Patterns (High-Level)

vLLM supports three main usage modes (detailed in child file `usage-reference.md` if expanded):

- **Inference & Serving:** Single-instance offline/online (LLM class + OpenAI server).
- **Deployment:** Docker, Kubernetes scaling, multi-node parallelism.
- **Training:** RLHF / fine-tuning support.

Key advanced topics (reference official sub-pages):

Quantization, speculative decoding, multi-modal (LLaVA, Qwen-VL), LoRA, structured outputs, disaggregated prefill/decode.


## 4. Usage Patterns (High-Level)


**Core Commands** (run `vllm <command>` --help for full flags):

| Command          | Description                               | Example                                                    |
|------------------|-------------------------------------------|------------------------------------------------------------|
| `vllm serve`       | OpenAI-compatible API server              | `vllm serve meta-llama/Llama-3.2-1B-Instruct`                |
| `vllm chat`        | Chat completions via running server       | `vllm chat --quick "hi"`                                   |
| `vllm complete`    | Text completions via running server       | `vllm complete --quick "The future of AI is"`              |
| `vllm bench`       | Benchmarking (latency, serve, throughput) | `vllm bench latency --model ... --input-len 32`              |
| `vllm collect-env` | Collect environment info for debugging    | `vllm collect-env`                                           |
| `vllm run-batch`   | Batch prompts from JSONL → output file    | `vllm run-batch -i input.jsonl -o results.jsonl --model ...` |


**Help Tips:**

- `--help=listgroup`, `--help=ModelConfig`, `--help=max-num-seqs`, `--help=page`
- Benchmark extra: `pip install vllm[bench]`

cURL Examples (after `vllm serve`):

```bash
curl http://localhost:8000/v1/completions -H "Content-Type: application/json" \
  -d '{"model": "Qwen/Qwen2.5-1.5B-Instruct", "prompt": "San Francisco is a", "max_tokens": 7}'
```

Full details → child file `cli-reference.md`.

## 5. Python API Reference (High-Level)
**Main Modules & Classes:**

- **Configuration** (`vllm.config`):
  - `ModelConfig`, `CacheConfig`, `ParallelConfig`, `SchedulerConfig`, `LoRAConfig`, `MultiModalConfig`, `VllmConfig`, etc.

- **Offline Inference:**
  - `vllm.LLM` — primary class for batched generation.
  - `vllm.inputs.llm` — prompt schema.

- **Engines:**
  - `LLMEngine` / `AsyncLLMEngine` (for custom online serving).

- **Multi-Modality (experimental):**
  - `vllm.multimodal`, `MULTIMODAL_REGISTRY`, `MultiModalKwargsItem`, etc.

- **Model Development:**
  - `vllm.model_executor.models.interfaces` and `adapters`.

**Typical Usage:**

```python
from vllm import LLM, SamplingParams
llm = LLM(model=..., **config_kwargs)
```

Detailed method signatures and examples → child file `api-reference.md` (or official API index).

## 6. Best Practices & Troubleshooting (Agent Tips)

- Always check `generation_config.json` override with `generation_config="vllm"`.
- For production: Use `--api-key`, Docker, and parallelism configs.
- Memory issues → enable PagedAttention (default), quantization, or prefix caching.
- Model not supported? Check supported models list.
- Debugging: `vllm collect-env`, set `VLLM_LOGGING_LEVEL=DEBUG`.

**Agent Usage Example:**
When user asks “How do I serve Llama 3 with vLLM?”, respond with exact `vllm serve` command + Python client snippet + performance tips.


## Official references
- https://docs.vllm.ai/en/stable/
- https://docs.vllm.ai/en/stable/usage/
- https://docs.vllm.ai/en/stable/api/
- https://docs.vllm.ai/en/stable/cli/