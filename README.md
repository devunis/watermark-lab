# Watermark Lab

Research tooling for a **self-owned AI text watermark**. The project inserts a reproducible green-list signal during Hugging Face generation, detects that signal with a z-score, and measures how it changes under controlled text edits.

This repository is intentionally scoped to watermark research on a scheme that you control. It does **not** remove or bypass third-party provider watermarks, provenance markers, or safety controls.

## Included

- `generator`: Hugging Face `LogitsProcessor` that biases a deterministic green list.
- `detector`: token-level and local-window detection using the matching secret.
- `scoring`: green fraction, z-score, one-sided p-value, confidence, and thresholding.
- `attacks`: transparent robustness tests for synonym replacement, sentence reordering, truncation, and mild noise.
- `benchmark`: original-vs-edited z-score and detection-rate comparison.
- `api`: FastAPI endpoints for health, generation, detection, and benchmarking.
- `web UI`: browser console for generation, detection, and controlled durability tests.
- `tests`: deterministic unit and API smoke tests.

## Quick start

Python 3.9+ is supported. Install the package and development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

For local Hugging Face generation and tokenizer-backed detection, install the ML extras as well:

```bash
pip install -e '.[dev,ml]'
```

Run the tests:

```bash
pytest
```

Start the API:

```bash
export WATERMARK_SECRET='use-a-private-random-secret'
uvicorn watermark_lab.api:app --reload
```

Then open `http://127.0.0.1:8000` for the web interface. The stress-test panel requires an explicit confirmation that the text uses a watermark you own or control. It previews controlled edits and before/after scores; it is not a third-party provenance-removal tool.

The `/generate` endpoint downloads the selected Hugging Face model on first use. For a lightweight local smoke test, call `/health`; for actual detection and benchmarking, the tokenizer for `model_name` must be available locally or downloadable.

## API examples

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H 'content-type: application/json' \
  -d '{"prompt":"Watermark research is","model_name":"distilgpt2","max_new_tokens":64}'
```

```bash
curl -X POST http://127.0.0.1:8000/detect \
  -H 'content-type: application/json' \
  -d '{"text":"text returned by the generator","model_name":"distilgpt2"}'
```

## Method notes

At position `i`, a SHA-256-derived seed is created from the private secret and the previous token ID. That seed deterministically partitions the vocabulary into green and red candidates. The generator adds `delta` to green-list logits. The detector independently compares the resulting z-score with `z_threshold` and computes:

```text
z = (green_count - gamma * n) / sqrt(n * gamma * (1 - gamma))
```

The default detection threshold is intentionally conservative and should be calibrated on held-out watermarked and unwatermarked samples. A matching secret and generation configuration are required; this is not a universal detector for arbitrary AI text.

## Research guardrails

Use the attack modules to evaluate durability of this repository's own scheme. Record model, tokenizer, secret version, generation settings, sample lengths, and attack parameters in experiments. Do not use this project to evade a third party's watermark or provenance system.

## License

MIT. See `pyproject.toml` for package metadata.
