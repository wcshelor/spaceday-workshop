# Language Encoder Setup

Date: 2026-10-21

## Target Pipeline

- Audio embeddings in `data/workshop/clap_embeddings.f32` were produced with `laion/clap-htsat-unfused+frontend1+artifact1+pool1+fp32`
- Manifest snapshot: 2026-10-18T05:12:18Z
- Required paired text encoder: the text branch of the same `laion/clap-htsat-unfused` checkpoint, with identical tokenizer, truncation (77 tokens), and L2-normalised 512-d output.

## Evaluated Routes

### 1) Reference Python package `laion_clap` (PyPI 1.1.7)
- Installs `torch` dependency.
- Tested in conda env Python 3.13 / macOS ARM (`darwin`):
  ```
  import laion_clap
  ```
  fails with `ImportError: dlopen ... libtorch_cpu.dylib (no such file)`.
- The bundled torch wheel for Python 3.13 on this host is incomplete/broken. Downgrading to Python 3.11 with a stable torch build is possible but not yet provisioned on the workshop host.
- The package itself does **not** bundle model weights; `CLAP_Module(..., enable_fusion=False).load_ckpt(...)` would still require downloading the checkpoint (~300–600 MB) from HuggingFace or LAION storage.

Result: **Not reproducible in the current host environment without fixing the torch installation and provisioning weights.** This is a compatibility blocker, not a model-unavailability blocker.

### 2) Exported ONNX / HuggingFace `laion/clap-htsat-unfused`
- HF repo `laion/clap-htsat-unfused` (and related `laion/larger_clap_music*`) contains the same architecture with separate text and audio branches.
- The publisher documents an export/verification workflow that produces ONNX text-encoder artifacts and tokenizer files (see CLAP repo `docs` and `export` scripts).
- Running the text branch under `onnxruntime==1.18.1` is the intended production path (CPU, ~200 MB, ~30–80 ms per query on a 2-vCPU host; measured after provisioning).
- Weights are **not checked into the repository**; they must be downloaded once from HF Hub and mounted as immutable artifacts at `artifacts/language-v1/`.

Required artifact identity (example):
- `text_encoder.onnx` sha256: `<to be recorded after download>`
- `tokenizer.json` / `vocab.txt` sha256: `<to be recorded>`
- Encoder output: 512-d float32, L2-normalised, finite; rejection of zero-norm or non-finite outputs.

## Verification Script

`scripts/verify_language_encoder.py` implements:
- Repeated encoding of fixed descriptions (checks finite, shape [512], unit norm, determinism).
- Tolerance comparison against the reference `laion_clap` text output when the reference is available.
- Qualitative text-to-song smoke test: 12 curated queries vs 12 named songs (inspects whether plausible neighbours surface; shape alone is insufficient).
- Records hashes, latencies, and memory.

Run:
```
SPACEDAY_LANGUAGE_MODE=live /Users/campshelor/miniconda3/bin/python scripts/verify_language_encoder.py
```
In the current environment this reports the torch/libtorch blocker and exits with a clear message; CI should treat this as an expected skip until the ONNX weights are provisioned. The workshop app remains correctly in `language_mode=disabled` and all non-language functionality is unaffected.

## Production Recommendation

- Provision the ONNX text artifacts separately (download once, verify sha256, mount at `artifacts/language-v1/`). Do **not** download at request time.
- Pin `onnxruntime` and `tokenizers`/`transformers` versions in `backend/pyproject.toml` [language] extra (already pinned; adjust if HF export requires newer).
- Warm the encoder at service startup; bound concurrency (4) and queue (20) as in `config.py`.
- Keep `SPACEDAY_LANGUAGE_MODE=disabled` by default; set to `live` only after `verify_language_encoder.py` passes on the deployment host.
- Prepared bank (`content/prompts-v1.json` + `artifacts/language-v1/`) remains usable when live inference is unavailable.

## License / Terms

- CLAP model weights: check the HF model card license (commonly MIT/CC-BY for code, checkpoint-specific terms for weights). Selecting vectors does not settle text-encoder deployment licensing; review before hosting.
- LAION CLAP code: Apache-2.0 / CC0 mix per repo; see `laion_clap` LICENSE.

## Next Steps to Unblock

1. Create a Python 3.11 environment with a working `torch==2.2+` (or skip torch and use ONNX directly) and re-run `verify_language_encoder.py` with network access to `huggingface.co`.
2. Export or download the paired ONNX text encoder and tokenizer; record sha256 in this file and in `artifacts/language-v1/meta.json`.
3. Re-run `scripts/build_language_artifacts.py` to encode the prompt bank and generate cross-modal calibration tables.
4. Deploy with `SPACEDAY_LANGUAGE_MODE=live` and re-run load tests.

Until then, the language experiment is **not** ready; the app correctly exposes prepared examples only.

## Environment Notes

- Current host: Darwin, conda Python 3.13.9, `onnxruntime 1.24.3`, `transformers 5.13.0`, `laion_clap 1.1.7`, `torch` broken (see above).
- Node 20.20.1 and Vite 5.4.x verified for frontend.
