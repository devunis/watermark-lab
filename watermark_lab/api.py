import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .attacks import add_noise, reorder_sentences, replace_synonyms, truncate
from .benchmark import run_benchmark
from .config import WatermarkConfig
from .detector import WatermarkDetector
from .generator import generate_text


class DetectRequest(BaseModel):
    text: str = Field(min_length=1)
    model_name: str = "distilgpt2"


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1)
    model_name: str = "distilgpt2"
    max_new_tokens: int = Field(default=128, ge=1, le=1024)
    temperature: float = Field(default=0.8, gt=0, le=2)
    top_p: float = Field(default=0.95, gt=0, le=1)
    seed: int = 0


class BenchmarkRequest(DetectRequest):
    synonym_probability: float = Field(default=0.25, ge=0, le=1)
    noise_probability: float = Field(default=0.05, ge=0, le=1)
    truncation_fraction: float = Field(default=0.75, gt=0, le=1)


def create_app(config: WatermarkConfig = None) -> FastAPI:
    app = FastAPI(title="Watermark Lab", version="0.1.0")
    active_config = config or WatermarkConfig(
        secret=os.getenv("WATERMARK_SECRET", "development-only-secret"),
    )
    detector = WatermarkDetector(active_config)

    def tokenizer_for(model_name: str):
        try:
            from transformers import AutoTokenizer
            return AutoTokenizer.from_pretrained(model_name)
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Tokenizer unavailable: {exc}")

    @app.get("/health")
    def health():
        return {"status": "ok", "watermark": "self-owned-research-scheme"}

    @app.post("/detect")
    def detect(request: DetectRequest):
        tokenizer = tokenizer_for(request.model_name)
        return detector.detect_text(request.text, tokenizer).as_dict()

    @app.post("/generate")
    def generate(request: GenerateRequest):
        try:
            text = generate_text(request.prompt, request.model_name, active_config,
                                 request.max_new_tokens, request.temperature,
                                 request.top_p, request.seed)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
        return {"text": text, "watermark": "self-owned-research-scheme"}

    @app.post("/benchmark")
    def benchmark(request: BenchmarkRequest):
        tokenizer = tokenizer_for(request.model_name)
        attacks = {
            "synonym": lambda value: replace_synonyms(value, request.synonym_probability),
            "sentence_edit": reorder_sentences,
            "truncation": lambda value: truncate(value, request.truncation_fraction),
            "noise": lambda value: add_noise(value, request.noise_probability),
        }
        return run_benchmark(request.text, tokenizer, detector, attacks)

    return app


app = create_app()
