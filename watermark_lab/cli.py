import argparse
import json

from .config import WatermarkConfig
from .generator import generate_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate self-watermarked research text")
    parser.add_argument("prompt")
    parser.add_argument("--model", default="distilgpt2")
    parser.add_argument("--secret", required=True)
    parser.add_argument("--max-new-tokens", type=int, default=128)
    args = parser.parse_args()
    text = generate_text(args.prompt, args.model, WatermarkConfig(args.secret), args.max_new_tokens)
    print(json.dumps({"text": text}, ensure_ascii=False))


if __name__ == "__main__":
    main()
