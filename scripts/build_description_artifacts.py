#!/usr/bin/env python3
"""Offline-only CLAP text bank build. Runtime needs numpy, never torch or a live encoder.

Install torch, transformers and numpy in a preparation environment. Downloads the
publisher's paired checkpoint, pins its revision, and saves only prepared text vectors.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = "laion/clap-htsat-unfused"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--revision", default="main", help="Use the recorded commit to reproduce a build")
    args = parser.parse_args()
    import numpy as np
    import torch
    import transformers
    from huggingface_hub import HfApi
    from transformers import AutoTokenizer, ClapTextModelWithProjection

    revision = HfApi().model_info(MODEL, revision=args.revision).sha
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=revision, cache_dir=args.cache_dir)
    model, loading = ClapTextModelWithProjection.from_pretrained(
        MODEL, revision=revision, cache_dir=args.cache_dir, output_loading_info=True
    )
    if loading.get("missing_keys") or loading.get("mismatched_keys") or loading.get("error_msgs"):
        raise RuntimeError(f"Incomplete pretrained text encoder: {loading}")
    model.eval()
    torch.set_num_threads(4)
    bank_path = ROOT / "content/prompts-v1.json"
    bank_bytes = bank_path.read_bytes()
    bank = json.loads(bank_bytes)
    prompts = bank["prompts"]

    def encode(texts):
        batch = tokenizer(texts, padding="max_length", truncation=True, max_length=77, return_tensors="pt")
        with torch.inference_mode():
            vectors = model(**batch).text_embeds
            vectors = torch.nn.functional.normalize(vectors, dim=-1)
        return vectors.cpu().numpy().astype("<f4")

    first = encode([p["text"] for p in prompts[:4]])
    if not np.allclose(first, encode([p["text"] for p in prompts[:4]]), atol=1e-6):
        raise RuntimeError("Encoder not deterministic")
    vectors = np.concatenate([encode([p["text"] for p in prompts[i:i+16]]) for i in range(0, len(prompts), 16)])
    if vectors.shape != (len(prompts), 512) or not np.isfinite(vectors).all() or not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-4):
        raise RuntimeError("Invalid text embeddings")
    raw = vectors.tobytes()
    manifest = json.loads((ROOT / "data/workshop/manifest.json").read_text())
    meta = {
        "version": "language-v1", "prompt_version": bank["version"],
        "prompt_count": len(prompts), "placeholder": False,
        "prompt_bank_sha256": hashlib.sha256(bank_bytes).hexdigest(),
        "embeddings_sha256": hashlib.sha256(raw).hexdigest(),
        "pipeline_version": manifest["pipeline_version"],
        "encoder_id": f"{MODEL}@{revision}", "checkpoint_revision": revision,
        "max_length": 77, "normalization": "L2", "dimensions": 512,
        "torch_version": torch.__version__, "transformers_version": transformers.__version__,
        "note": "Real paired pretrained CLAP text vectors. Offline song-to-description retrieval only; live text search retired. Upstream audio checkpoint hash is not independently established by its pipeline name.",
    }
    out = ROOT / "artifacts/language-v1"
    (out / "prompt_embeddings.f32").write_bytes(raw)
    (out / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"Built {len(prompts)} real description embeddings from {revision}")


if __name__ == "__main__":
    main()
