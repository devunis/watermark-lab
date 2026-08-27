import os
from pathlib import Path
from typing import Any, Callable, Dict, Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .attacks import (
    add_noise,
    reorder_sentences,
    replace_selected_words,
    replace_synonyms,
    truncate,
)
from .benchmark import run_benchmark
from .config import WatermarkConfig
from .detector import WatermarkDetector
from .generator import generate_text

STATIC_DIR = Path(__file__).parent / "static"


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


class StressTestRequest(BenchmarkRequest):
    attack: Literal["word_replace", "synonym", "sentence_edit", "truncation", "noise"]
    sentence_mode: Literal["reverse", "rotate"] = "reverse"
    replacement_map: Dict[str, str] = Field(default_factory=dict, max_length=50)
    attack_seed: int = 0
    authorized_self_test: bool = False


def create_app(
    config: Optional[WatermarkConfig] = None,
    tokenizer_loader: Optional[Callable[[str], Any]] = None,
    text_generator: Optional[Callable[..., str]] = None,
) -> FastAPI:
    app = FastAPI(title="Watermark Lab", version="0.1.0")
    active_config = config or WatermarkConfig(
        secret=os.getenv("WATERMARK_SECRET", "development-only-secret"),
    )
    detector = WatermarkDetector(active_config)
    generator_fn = text_generator or generate_text

    def tokenizer_for(model_name: str):
        if tokenizer_loader is not None:
            return tokenizer_loader(model_name)
        try:
            from transformers import AutoTokenizer

            return AutoTokenizer.from_pretrained(model_name)
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Tokenizer unavailable: {exc}")

    def apply_attack(request: StressTestRequest) -> str:
        if request.attack == "word_replace":
            try:
                return replace_selected_words(
                    request.text,
                    request.replacement_map,
                    request.synonym_probability,
                    request.attack_seed,
                )
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc))
        if request.attack == "synonym":
            return replace_synonyms(request.text, request.synonym_probability)
        if request.attack == "sentence_edit":
            return reorder_sentences(request.text, request.sentence_mode)
        if request.attack == "truncation":
            return truncate(request.text, request.truncation_fraction)
        return add_noise(request.text, request.noise_probability)

    @app.get("/", include_in_schema=False)
    def web_ui():
        return FileResponse(STATIC_DIR / "index.html")

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
            text = generator_fn(
                request.prompt,
                request.model_name,
                active_config,
                request.max_new_tokens,
                request.temperature,
                request.top_p,
                request.seed,
            )
        except Exception as exc:
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

    @app.post("/stress-test")
    def stress_test(request: StressTestRequest):
        if not request.authorized_self_test:
            raise HTTPException(
                status_code=400,
                detail="Confirm that this is a self-owned watermark durability test.",
            )
        tokenizer = tokenizer_for(request.model_name)
        transformed = apply_attack(request)
        before = detector.detect_text(request.text, tokenizer).as_dict()
        after = detector.detect_text(transformed, tokenizer).as_dict()
        return {
            "scope": "self-owned-watermark-durability-test",
            "attack": request.attack,
            "transformed_text": transformed,
            "before": before,
            "after": after,
            "signal_drop": round(before["z_score"] - after["z_score"], 6),
        }

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    return app


app = create_app()
