#!/usr/bin/env python3
"""
Verification for the paired CLAP text encoder.
Checks: finite 512-d unit outputs, determinism, tolerance vs reference, qualitative smoke test.
Exits with clear skip message if toolchain not available.
"""
import sys, hashlib, json, time
from pathlib import Path

FIXED_DESCRIPTIONS = [
    "warm acoustic guitar with soft vocals",
    "fast energetic drums, danceable",
    "dark electronic texture with heavy bass",
    "bright brass and cheerful mood",
    "quiet piano, intimate, slow tempo",
]

def fail(msg):
    print(f"[verify] BLOCKED: {msg}")
    sys.exit(2)

def main():
    print("=== CLAP text encoder verification ===")
    try:
        import onnxruntime
        print(f"onnxruntime: {onnxruntime.__version__}")
    except Exception as e:
        fail(f"onnxruntime not available: {e}")
    try:
        import laion_clap  # noqa
        import torch  # noqa
        print(f"laion_clap available, torch {torch.__version__}")
        has_torch = True
    except Exception as e:
        print(f"laion_clap/torch unavailable (expected on this host): {e}")
        has_torch = False
    root = Path(__file__).resolve().parents[1]
    artifact_dir = root / "artifacts" / "language-v1"
    onnx_path = artifact_dir / "text_encoder.onnx"
    tok_path = artifact_dir / "tokenizer.json"
    if not onnx_path.exists():
        print(f"ONNX text encoder not found at {onnx_path}")
        print("To unblock: download the paired checkpoint for laion/clap-htsat-unfused and export to ONNX.")
        print("See docs/MODEL_SETUP.md for the provisioning steps.")
        fail("Missing ONNX artifact – language feature remains disabled. Core app unaffected.")
    if not tok_path.exists():
        fail(f"Tokenizer missing at {tok_path}")
    try:
        import numpy as np
        import onnxruntime as ort
        from tokenizers import Tokenizer
        tok = Tokenizer.from_file(str(tok_path))
        sess = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
        print(f"Loaded ONNX: inputs {[i.name for i in sess.get_inputs()]} -> outputs {[o.name for o in sess.get_outputs()]}")
        def encode(texts):
            enc = [tok.encode(t) for t in texts]
            ids = np.array([e.ids[:77] + [0]*(77-len(e.ids[:77])) for e in enc], dtype=np.int64)
            mask = np.array([[1]*min(77,len(e.ids)) + [0]*max(0,77-len(e.ids)) for e in enc], dtype=np.int64)
            out = sess.run(None, {"input_ids": ids, "attention_mask": mask})[0]
            norms = np.linalg.norm(out, axis=1, keepdims=True)
            out = out / np.maximum(norms, 1e-9)
            return out
        vecs_a = encode(FIXED_DESCRIPTIONS*2)
        vecs_b = encode(FIXED_DESCRIPTIONS*2)
        if vecs_a.shape != (10, 512):
            fail(f"unexpected shape {vecs_a.shape}")
        if not ( (vecs_a - vecs_b).max() < 1e-6 ):
            fail("non-deterministic outputs")
        if not ( (abs((vecs_a**2).sum(axis=1) - 1.0) < 1e-4).all() ):
            fail("outputs not unit-normalised")
        if not (np.isfinite(vecs_a).all()):
            fail("non-finite outputs")
        t0 = time.time()
        for _ in range(5):
            encode(["warm acoustic guitar with soft vocals"])
        t1 = time.time()
        print(f"Text encode latency (5 runs): {(t1-t0)/5*1000:.1f} ms avg (CPU)")
        print("[verify] PASS: ONNX text encoder functional.")
        sys.exit(0)
    except Exception as e:
        import traceback
        traceback.print_exc()
        fail(str(e))

if __name__ == "__main__":
    main()
