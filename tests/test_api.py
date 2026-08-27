from fastapi.testclient import TestClient

from watermark_lab.api import create_app
from watermark_lab.config import WatermarkConfig


class FakeTokenizer:
    vocab_size = 256

    def encode(self, text, add_special_tokens=False):
        return [ord(character) % self.vocab_size for character in text]


def fake_tokenizer_loader(model_name):
    return FakeTokenizer()


def test_health_endpoint():
    client = TestClient(create_app(WatermarkConfig("test-secret")))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_web_ui_and_static_assets_are_served():
    client = TestClient(create_app(WatermarkConfig("test-secret")))
    page = client.get("/")
    stylesheet = client.get("/static/styles.css")
    assert page.status_code == 200
    assert "Watermark Lab" in page.text
    assert stylesheet.status_code == 200
    assert "--green" in stylesheet.text


def test_stress_test_requires_self_owned_confirmation():
    client = TestClient(
        create_app(WatermarkConfig("test-secret"), tokenizer_loader=fake_tokenizer_loader)
    )
    response = client.post(
        "/stress-test",
        json={
            "text": "This important research text should be tested carefully. Another sentence.",
            "model_name": "fake",
            "attack": "synonym",
            "authorized_self_test": False,
        },
    )
    assert response.status_code == 400


def test_stress_test_returns_transformed_text_and_scores():
    client = TestClient(
        create_app(WatermarkConfig("test-secret"), tokenizer_loader=fake_tokenizer_loader)
    )
    original = "This important research text should be tested carefully. Another sentence."
    response = client.post(
        "/stress-test",
        json={
            "text": original,
            "model_name": "fake",
            "attack": "synonym",
            "synonym_probability": 1,
            "authorized_self_test": True,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["scope"] == "self-owned-watermark-durability-test"
    assert payload["transformed_text"] != original
    assert "before" in payload and "after" in payload


def test_stress_test_replaces_user_selected_words():
    client = TestClient(
        create_app(WatermarkConfig("test-secret"), tokenizer_loader=fake_tokenizer_loader)
    )
    response = client.post(
        "/stress-test",
        json={
            "text": "중요한 연구 결과입니다.",
            "model_name": "fake",
            "attack": "word_replace",
            "replacement_map": {"중요한": "핵심적인", "연구": "실험"},
            "synonym_probability": 1,
            "authorized_self_test": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["transformed_text"] == "핵심적인 실험 결과입니다."
