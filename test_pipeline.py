import sys

from app.rag.pipeline import RAGPipeline


def safe_print(text: str) -> None:
    """Print text safely, replacing unencodable characters for Windows cp1252 terminals."""
    encoded = text.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
        sys.stdout.encoding or "utf-8", errors="replace"
    )
    print(encoded)


p = RAGPipeline()
messages = [
    "bonjour",
    "tu peux me faire le bilan sur l'etat actuel du systeme ?",
    "que s'est-il passe ces dernieres 24h ?",
    "vulnerabilite RCE sur les API Amadeus Sabre",
]
for msg in messages:
    result = p.chat(msg)
    safe_print(f"[{result['intent']}] {msg[:60]}")
    safe_print(f"  -> {result['response_text'][:200]}")
    print()
