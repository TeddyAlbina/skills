# api-reference.md - vLLM Full Python API Reference (Expandable)

**Agent Skill Module**: vLLM Python API (Child of SKILL.md)  
**Focus**: Complete, copy-paste-ready references for all major classes, methods, and configuration objects used in offline inference, engines, and advanced customization.  
**Version**: Based on vLLM stable documentation (as of May 2026).  
**Cross-references**: See `SKILL.md` for overview, `usage-reference.md` for patterns, `cli-reference.md` for commands.  
**Expandability**: Each section includes a "Full Source / More Details" note linking to the official docs. Agent can expand any class on demand by referencing the exact docs URLs or code.

**Official API Index**: https://docs.vllm.ai/en/stable/api/

---

## 1. Core Offline Inference (High-Level Entry Point)

### 1.1 `vllm.LLM` (Primary Class)

**Description**: High-level class for offline batched inference. Bundles tokenizer, model (possibly distributed), KV cache, and engine. Automatically handles batching, memory management, and multi-modal inputs.  
**Not for online serving** — use `AsyncLLMEngine` instead.

**Full `__init__` Signature** (most common parameters):
```python
class vllm.LLM:
    def __init__(
        self,
        model: str,
        *,
        runner: RunnerOption = "auto",
        convert: ConvertOption = "auto",
        tokenizer: str | None = None,
        tokenizer_mode: TokenizerMode | str = "auto",
        skip_tokenizer_init: bool = False,
        trust_remote_code: bool = False,
        allowed_local_media_path: str = "",
        allowed_media_domains: list[str] | None = None,
        tensor_parallel_size: int = 1,
        dtype: ModelDType = "auto",
        quantization: QuantizationMethods | None = None,
        revision: str | None = None,
        tokenizer_revision: str | None = None,
        chat_template: Path | str | None = None,
        seed: int = 0,
        gpu_memory_utilization: float = 0.92,
        cpu_offload_gb: float = 0,
        offload_group_size: int = 0,
        offload_num_in_group: int = 1,
        offload_prefetch_step: int = 1,
        offload_params: set[str] | None = None,
        enforce_eager: bool = False,
        enable_return_routed_experts: bool = False,
        disable_custom_all_reduce: bool = False,
        hf_token: bool | str | None = None,
        hf_overrides: HfOverrides | None = None,
        mm_processor_kwargs: dict[str, Any] | None = None,
        pooler_config: PoolerConfig | None = None,
        structured_outputs_config: dict[str, Any] | StructuredOutputsConfig | None = None,
        profiler_config: dict[str, Any] | ProfilerConfig | None = None,
        attention_config: dict[str, Any] | AttentionConfig | None = None,
        kv_cache_memory_bytes: int | None = None,
        compilation_config: int | dict[str, Any] | CompilationConfig | None = None,
        quantization_config: dict[str, Any] | OnlineQuantizationConfigArgs | None = None,
        logits_processors: list[str | type[LogitsProcessor]] | None = None,
        **kwargs: Any,
    ) -> None:
```

**Key Public Methods** (most frequently used):

| Method      | Signature (simplified)                              | Return Type                                           | Description                                            |
|-------------|-----------------------------------------------------|-------------------------------------------------------|--------------------------------------------------------|
| `generate`    | `generate(prompts: PromptType, ...)`                       | `Sequence[PromptType], sampling_params: SamplingParams` | `Sequence[SamplingParams]`                               |
| `chat`        | `chat(messages: list[ChatCompletionMessageParam], ...)`      | `Sequence[...], ...)`                                  | `list[RequestOutput]`                                    |
| `embed`       | `embed(prompts: PromptType,    ...)`                         | `Sequence[PromptType], ...)`                           | `list[EmbeddingRequestOutput]`                           |
| `encode`      | `encode(prompts: PromptType,    ...)`                        | `Sequence[PromptType], ...)`                           | `list[PoolingRequestOutput]`                             |
| `classify`    | `classify(prompts: PromptType,    ...)`                      | `Sequence[PromptType], ...)`                           | `list[ClassificationRequestOutput]`                      |
| `beam_search` | `beam_search(prompts, params: BeamSearchParams, ...)` | `list[BeamSearchOutput]`                                | Beam search (non-greedy).                              |
| `apply_model` | `apply_model(func: Callable[[Module], _R])`           | `list[_R]`                                              | Run arbitrary function on model weights (distributed). |

**Notes:**
- `**kwargs` are forwarded to `EngineArgs`.
- Deprecated: `swap_space` (ignored with warning).
- Data-parallel (`data_parallel_size > 1`) only works with external launcher or TPU.

**Full Source / More Details**: https://docs.vllm.ai/en/stable/api/vllm/entrypoints/llm/


## 2. Sampling & Generation Parameters

## 2.1 `vllm.SamplingParams`

**Description**: Controls decoding behavior. Mirrors OpenAI Completion API + extra features (beam search, structured outputs, etc.).

```python
class vllm.SamplingParams(
    n: int = 1,
    presence_penalty: float = 0.0,
    frequency_penalty: float = 0.0,
    repetition_penalty: float = 1.0,
    temperature: float = 1.0,
    top_p: float = 1.0,
    top_k: int = 0,
    min_p: float = 0.0,
    seed: int | None = None,
    stop: str | list[str] | None = None,
    stop_token_ids: list[int] | None = None,
    ignore_eos: bool = False,
    max_tokens: int | None = 16,
    min_tokens: int = 0,
    logprobs: int | None = None,
    prompt_logprobs: int | None = None,
    logprob_token_ids: list[int] | None = None,
    flat_logprobs: bool = False,
    detokenize: bool = True,
    skip_special_tokens: bool = True,
    spaces_between_special_tokens: bool = True,
    include_stop_str_in_output: bool = False,
    output_kind: RequestOutputKind = RequestOutputKind.CUMULATIVE,
    structured_outputs: StructuredOutputsParams | None = None,
    logit_bias: dict[int, float] | None = None,
    allowed_token_ids: list[int] | None = None,
    extra_args: dict[str, Any] | None = None,
    bad_words: list[str] | None = None,
    thinking_token_budget: int | None = None,
    repetition_detection: RepetitionDetectionParams | None = None,
    **kwargs,
)
```

**Key Parameters Explained**:
- `temperature=0` → greedy decoding.
- `n` → number of independent generations per prompt.
- `logprobs` / prompt_logprobs → return probabilities (great for scoring).
- `structured_outputs` → enables JSON / regex / grammar guided decoding.
- `repetition_detection` → early-stop repetitive patterns.

**Methods**:

- `from_optional(...)` (static) – convenient factory.
- `__post_init__` / _verify_args – automatic validation.

**Full Source / More Details**: https://docs.vllm.ai/en/stable/api/vllm/sampling_params/


## 3. Engine Classes (Low-Level / Async Serving)

### 3.1 `vllm.LLMEngine` & `vllm.AsyncLLMEngine`
- `LLMEngine` → synchronous engine (used internally by `LLM`).
- `AsyncLLMEngine` → async engine (used by `vllm serve` and custom servers). Alias to `vllm.v1.engine.async_llm.AsyncLLM`.

**Typical Usage** (advanced):

```python
from vllm import LLMEngine, EngineArgs, AsyncLLMEngine

engine_args = EngineArgs(model="Qwen/Qwen2.5-1.5B-Instruct", ...)
engine = LLMEngine.from_engine_args(engine_args)          # sync
# or
async_engine = AsyncLLMEngine.from_engine_args(engine_args)  # async
```

**Key Methods** (shared):
- `add_request(...)`, `step()`, `abort_request()`, `get_metrics()`, etc.

**Full Source / More Details**: https://docs.vllm.ai/en/stable/api/vllm/v1/engine/

## 4. Configuration (`vllm.config`)

All configs are dataclasses that can be passed to `LLM(..., **config_dict)` or `EngineArgs`.

### 4.1 Main Config Classes

| Class                                                                | Purpose                                  | Key Parameters (selected)                                        |
|----------------------------------------------------------------------|------------------------------------------|------------------------------------------------------------------|
| `ModelConfig`                                                          | Model architecture & loading             | `model`, `dtype`, `quantization`, `max_model_len`, `runner`                |
| `CacheConfig`                                                          | KV cache management                      | `block_size`, `gpu_memory_utilization`, `enable_prefix_caching`        |
| `ParallelConfig`                                                       | Distributed execution                    | `tensor_parallel_size`, `pipeline_parallel_size`, `data_parallel_size` |
| `LoRAConfig`                                                           | LoRA / adapter support                   | `max_loras`, `max_lora_rank`, `lora_dtype`                             |
| `MultiModalConfig`                                                     | Images, video, audio                     | `limit_per_prompt`, `mm_processor_kwargs`                            |
| `CompilationConfig`                                                    | `torch.compile` + CUDA graphs              | `mode`, `cudagraph_mode`                                             |
| `VllmConfig`                                                           | Aggregates all configs above             | — (container class)                                              |
| `LoadConfig`, `DeviceConfig`, `ObservabilityConfig`, `KVTransferConfig`, ... | Loading, device, metrics, disaggregation | See full docs                                                    |


**Usage Example:**

```python
from vllm.config import VllmConfig, ModelConfig, CacheConfig, ...

config = VllmConfig(
    model_config=ModelConfig(model="..."),
    cache_config=CacheConfig(...),
    # ...
)
llm = LLM(vllm_config=config)  # or pass individual kwargs
```

**Full Source / More Details**: https://docs.vllm.ai/en/stable/api/vllm/config/

## 5. Inputs & Multi-Modal

- `vllm.inputs.PromptType` / `TextPrompt` / `TokensPrompt` / `DataPrompt`
- `vllm.multimodal.MULTIMODAL_REGISTRY`, MultiModalKwargsItem`, etc.
- Chat messages follow OpenAI format + `{"type": "image_url", ...}`


## 6. Agent Tips & Expandability

- **Most common pattern**: `LLM(...)` + `SamplingParams(...)` + `.generate(...)` or `.chat(...)`.
- **Advanced**: Use `AsyncLLMEngine` + custom request loops for serving.
- **Profiling / Observability**: Pass `profiler_config` / `observability_confi`g.
- **When to expand this file**:
  - Need full method signatures for a specific class? Ask agent to pull from exact docs URL.
  - New backend (e.g., new quantization, new model runner)? Check `vllm.model_executor.models.interfaces`.


**Maintenance Note**: Refresh against https://docs.vllm.ai/en/stable/api/ when new classes (e.g., new v1 engine internals) appear.