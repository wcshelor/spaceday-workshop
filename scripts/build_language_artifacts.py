#!/usr/bin/env python3
"""
Build language-v1 artifacts: encode prompt bank with paired CLAP text encoder.
If ONNX encoder not provisioned, creates placeholder artifacts for UI development and records blocker.
"""
import json, hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "prompts-v1.json"
OUT = ROOT / "artifacts" / "language-v1"
OUT.mkdir(parents=True, exist_ok=True)

def main():
    existing = OUT / "meta.json"
    if existing.exists() and json.loads(existing.read_text()).get("placeholder") is False:
        sys.exit("Retired builder: real description artifacts already exist. Use build_description_artifacts.py; refusing to overwrite them.")
    prompts = json.loads(CONTENT.read_text())
    bank = prompts["prompts"] if isinstance(prompts, dict) and "prompts" in prompts else prompts
    print(f"Prompt bank {len(bank)} entries, version {prompts.get('version','unknown')}")
    bank_hash = hashlib.sha256(CONTENT.read_bytes()).hexdigest()
    # Check for ONNX encoder
    onnx = OUT / "text_encoder.onnx"
    tokenizer = OUT / "tokenizer.json"
    if not onnx.exists() or not tokenizer.exists():
        print(f"ONNX encoder not found at {onnx} or tokenizer missing")
        print("Creating placeholder artifacts for UI development (not real CLAP). See docs/MODEL_SETUP.md")
        # placeholder vectors already created via earlier one-off; ensure meta reflects placeholder
        meta = {
            "version": "language-v1",
            "prompt_version": prompts.get("version","prompts-v1"),
            "prompt_count": len(bank),
            "prompt_bank_sha256": bank_hash,
            "placeholder": True,
            "encoder_id": "fake-placeholder",
            "pipeline_version": "laion/clap-htsat-unfused+frontend1+artifact1+pool1+fp32",
            "note": "Placeholder until ONNX encoder provisioned. Do not claim language experiment is finished."
        }
        (OUT / "meta.json").write_text(json.dumps(meta, indent=2))
        print(f"Wrote placeholder {OUT/'meta.json'}")
        # Also ensure fake embeddings exist
        import numpy as np
        vec_path = OUT / "prompt_embeddings.f32"
        if not vec_path.exists():
            vecs=[]
            for p in bank:
                h=hashlib.sha256(p["text"].encode()).digest()
                seed=int.from_bytes(h[:4],'little')
                rng=np.random.RandomState(seed)
                v=rng.randn(512); v/=np.linalg.norm(v)
                vecs.append(v)
            np.array(vecs, dtype='<f4').tofile(str(vec_path))
            print(f"Wrote fake embeddings {vec_path} ({vec_path.stat().st_size} bytes)")
        sys.exit(2)
    # Real encoding path
    print("Encoding with real ONNX encoder...")
    import numpy as np, onnxruntime as ort
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(tokenizer))
    sess = ort.InferenceSession(str(onnx), providers=["CPUExecutionProvider"])
    vecs=[]
    for p in bank:
        enc=tok.encode(p["text"])
        ids=np.array([enc.ids[:77]+[0]*(77-len(enc.ids[:77]))], dtype=np.int64)
        mask=np.array([[1]*min(77,len(enc.ids))+[0]*max(0,77-len(enc.ids))], dtype=np.int64)
        out=sess.run(None, {"input_ids": ids, "attention_mask": mask})[0][0]
        n=np.linalg.norm(out)
        if n==0 or not np.isfinite(n):
            raise RuntimeError("invalid vector")
        vecs.append((out/n).tolist())
    mat=np.array(vecs, dtype='<f4')
    mat.tofile(str(OUT/"prompt_embeddings.f32"))
    # Build text-reference calibration tables from frozen prompt bank (separate from audio-audio)
    # For each method seed count we need cross-modal score distribution; for now we record prompt count
    meta={
        "version":"language-v1",
        "prompt_version":prompts.get("version","prompts-v1"),
        "prompt_count":len(bank),
        "prompt_bank_sha256":bank_hash,
        "placeholder":False,
        "encoder_id": "onnx:"+hashlib.sha256(onnx.read_bytes()).hexdigest()[:12],
        "tokenizer_sha256": hashlib.sha256(tokenizer.read_bytes()).hexdigest(),
        "pipeline_version":"laion/clap-htsat-unfused+frontend1+artifact1+pool1+fp32",
        "calibration_note":"Text-to-audio percentile reference from this prompt bank, not universal calibration."
    }
    (OUT/"meta.json").write_text(json.dumps(meta, indent=2))
    print(f"Wrote {OUT/'meta.json'} and {OUT/'prompt_embeddings.f32'}")

if __name__=="__main__":
    main()
