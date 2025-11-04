# Create your views here.
from openai import OpenAI
import os

from pathlib import Path
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Try to load .env from project root so environment variables are available
if load_dotenv:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    try:
        load_dotenv(env_path)
    except Exception:
        # non-fatal: we'll still try os.environ values
        pass

# Support both GROQ_API_KEY (used for Groq) and OPENAI_API_KEY (common env var)
def _get_client():
    key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("Missing GROQ_API_KEY/OPENAI_API_KEY")
    return OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

MODEL_CANDIDATES = [
    "meta-llama/Llama-3.3-70B-Instruct",
    "meta-llama/Llama-3.1-70B-Instruct",
    "meta-llama/Llama-3.1-8B-Instruct",
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-instant",
    "llama-3.1-8b-instant",
]

def ask_ai(user_input):
    try:
        client = _get_client()

        try:
            available = {m.id for m in client.models.list().data}
        except Exception:
            available = set()

        prioritized = [m for m in MODEL_CANDIDATES if (not available or m in available)]
        if not prioritized and available:
            prioritized = [
                m for m in available
                if "llama" in m.lower() and ("instruct" in m.lower() or "chat" in m.lower())
            ] or list(available)

        last_err = None
        for model_id in prioritized or MODEL_CANDIDATES:
            try:
                response = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Bạn là HƯỚNG DẪN VIÊN DU LỊCH chuyên nghiệp. "
                            )
                        },
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.7,
                    max_tokens=2048
                )
                reply = (response.choices[0].message.content or "").strip()
                print(f"[✔] Phản hồi từ Groq ({model_id}): {reply[:200]}...")
                return reply
            except Exception as e:
                print(f"[❌] Lỗi với model {model_id}: {e}")
                last_err = e
                continue

        print("[❌] Lỗi gọi Groq API:", str(last_err) if last_err else "No model worked")
        return "Sorry, I could not respond at the moment."
    except Exception as e:
        print("[❌] Lỗi gọi Groq API:", str(e))
        return "Sorry, I could not respond at the moment."
