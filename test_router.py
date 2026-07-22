from app.rag.intent_router import IntentRouter, Intent

r = IntentRouter()

tests = [
    ("bonjour", Intent.GENERAL_CONVERSATION),
    ("qui es-tu ?", Intent.GENERAL_CONVERSATION),
    ("qu'est-ce qu'une CVE ?", Intent.GENERAL_CONVERSATION),
    ("etat du systeme", Intent.GENERAL_CONVERSATION),
    ("que s'est-il passe ces dernieres 24h ?", Intent.GLOBAL_REPORT),
    ("genere un rapport de securite", Intent.GLOBAL_REPORT),
    ("bilan global des menaces", Intent.GLOBAL_REPORT),
    ("risque RCE sur nos API Amadeus", Intent.CYBER_THREAT),
    ("vulnerabilite CVE-2025-1234 dans notre serveur", Intent.CYBER_THREAT),
    ("securiser notre passerelle de paiement PCI-DSS", Intent.CYBER_THREAT),
    ("attaque ransomware sur un hotel", Intent.CYBER_THREAT),
]

print("=== Intent Router Validation ===")
all_ok = True
for msg, expected in tests:
    result = r.classify(msg)
    status = "OK" if result == expected else "FAIL"
    if status == "FAIL":
        all_ok = False
    print(f"  [{status}] \"{msg[:50]}\" -> {result.value} (expected: {expected.value})")

print()
print("All tests passed!" if all_ok else "Some tests FAILED!")
