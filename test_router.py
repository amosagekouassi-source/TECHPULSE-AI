from app.rag.intent_router import IntentRouter, Intent

r = IntentRouter()

tests = [
    # CAS 1 : Salutations / Conversation Générale / État Système
    ("bonjour", Intent.GENERAL_CONVERSATION),
    ("qui es-tu ?", Intent.GENERAL_CONVERSATION),
    ("comment vas-tu ?", Intent.GENERAL_CONVERSATION),
    ("etat du systeme", Intent.GENERAL_CONVERSATION),
    
    # CAS 2 : Sécurisation Préventive & Architecture
    ("comment securiser nos API Amadeus ?", Intent.PREVENTIVE_SECURITY),
    ("qu'est-ce qu'une CVE ?", Intent.PREVENTIVE_SECURITY),
    ("securiser notre passerelle de paiement PCI-DSS", Intent.PREVENTIVE_SECURITY),
    
    # CAS 3 : Incident / Attaque / Faille Spécifique
    ("risque RCE sur nos API Amadeus", Intent.CYBER_INCIDENT),
    ("vulnerabilite CVE-2025-1234 dans notre serveur", Intent.CYBER_INCIDENT),
    ("attaque ransomware sur un hotel", Intent.CYBER_INCIDENT),
    
    # CAS 4 : Rapport Global / Bilan 24h
    ("que s'est-il passe ces dernieres 24h ?", Intent.GLOBAL_REPORT),
    ("genere un rapport de securite", Intent.GLOBAL_REPORT),
    ("bilan global des menaces", Intent.GLOBAL_REPORT),
]

print("=== Intent Router Decision Matrix Validation ===")
all_ok = True
for msg, expected in tests:
    result = r.classify(msg)
    status = "OK" if result == expected else "FAIL"
    if status == "FAIL":
        all_ok = False
    print(f"  [{status}] \"{msg[:50]}\" -> {result.value} (expected: {expected.value})")

print()
print("All Decision Matrix tests passed successfully!" if all_ok else "Some tests FAILED!")
