export const translations = {
  fr: {
    // Header & Global
    brandTitle: "TECHPULSE-AI",
    brandSubtitle: "Intelligence Cyber & Sécurité du Voyage",
    agencyLabel: "Agence",
    agencies: {
      abidjan: "Abidjan Tourisme Suite",
      paris: "Paris Travel & Booking Hub",
      global: "Global Amadeus Agency Network",
    },
    statusProtected: "🟢 Systèmes Protégés",
    statusAlert: "🟠 Vigilance Requise",
    statusCritical: "🔴 Alerte Critique",
    languageBtn: "FR 🇫🇷",
    switchLanguage: "Passer en Anglais",

    // Navigation Sidebar
    nav: {
      dashboard: "Tableau de Bord",
      assistant: "Assistant Cyber",
      gdsSecurity: "Sécurité API & GDS",
      settings: "Paramètres",
    },
    systemStatusTitle: "Moteur IA Ops",
    systemStatusOnline: "Tous les services opérationnels",
    activeSession: "Session : ",

    // Tab 1: Executive Dashboard
    dashboard: {
      title: "Tableau de Bord de Cybersécurité Executif",
      subtitle: "Vue unifiée des vulnérabilités, API de réservation GDS et menaces cyber du secteur voyage.",
      kpis: {
        monitoredApis: "APIs Surveillées",
        activeThreats: "Menaces Actives",
        securityScore: "Score de Sécurité",
        protectedTx: "Conformité PCI-DSS",
      },
      charts: {
        trendTitle: "Évolution des Menaces vs Réservations (24h)",
        severityTitle: "Vulnérabilités par Sévérité",
        severityLabels: {
          critical: "Critique",
          high: "Élevée",
          medium: "Moyenne",
          low: "Faible",
        },
      },
      quickActions: {
        title: "Actions Rapides & Recommandations Priority",
        auditPayment: "Auditer la passerelle de paiement",
        auditPaymentDesc: "Lancer un scan automatisé des jetons PCI-DSS sur Stripe et Worldpay.",
        verifyAmadeus: "Vérifier API GDS Amadeus",
        verifyAmadeusDesc: "Vérifier la validité des certs TLS 1.3 et le rate-limiting des flux billetterie.",
        scanEndpoints: "Scanner endpoints de réservation",
        scanEndpointsDesc: "Inspecter les vulnérabilités de type injection & RCE sur les webhooks.",
        generateReport: "Générer Rapport PDF 24h",
        generateReportDesc: "Exporter une synthèse exécutive prête pour le comité de direction.",
        actionSuccess: "Action lancée avec succès !",
      },
    },

    // Tab 2: Cyber Assistant
    assistant: {
      title: "Assistant IA Cyber TECHPULSE (RAG & Advisory)",
      subtitle: "Posez vos questions ou décrivez un incident pour obtenir des recommandations métier spécialisées Tourisme & GDS.",
      initialGreeting: "Bonjour ! Je suis **TECHPULSE-AI**, votre assistant virtuel en cybersécurité dédié au secteur du voyage. Comment puis-je vous aider aujourd'hui ?",
      promptChipsTitle: "💡 Exemples de requêtes rapides (cliquez pour tester) :",
      promptChips: [
        "Qu'est-ce qu'une CVE ?",
        "Comment sécuriser nos API GDS Amadeus ?",
        "Nous avons détecté une vulnérabilité critique RCE sur notre serveur de réservation.",
        "Quels sont les risques de fraude sur les paiements par carte en agence ?",
      ],
      inputPlaceholder: "Posez votre question cybersécurité (ex: failles API, ransomware, conformité PCI-DSS)...",
      sendBtn: "Envoyer",
      processing: "TECHPULSE-AI analyse la demande via FAISS & DistilBERT...",
      cveSourcesLabel: "Sources RAG & CVE Consultées :",
      intentLabel: "Intention Détectée :",
      severityLabel: "Sévérité DistilBERT :",
      modulesUsed: "Modules Utilisés :",
    },

    // Tab 3: API & GDS Security
    gdsSecurity: {
      title: "Moniteur de Sécurité API & Connecteurs GDS",
      subtitle: "Surveillance en temps réel des API de réservation, GDS (Amadeus, Sabre, Galileo) et passerelles de paiement.",
      tableHeaders: {
        system: "Système / Connecteur",
        type: "Type d'Intégration",
        status: "Statut Sécurité",
        latency: "Temps de Réponse",
        tls: "Conformité TLS",
        anomaly: "Anomalie Récente",
      },
      systems: [
        {
          name: "Amadeus Flight GDS API",
          type: "GDS Billetterie Aérienne",
          status: "Protégé",
          latency: "42 ms",
          tls: "TLS 1.3 (Valide)",
          anomaly: "Aucune",
        },
        {
          name: "Sabre Hotel Booking Webhook",
          type: "Moteur Hôtellerie",
          status: "Vigilance",
          latency: "115 ms",
          tls: "TLS 1.2 (Renouvellement requis)",
          anomaly: "Tentatives de force brute bloquées (23 req/s)",
        },
        {
          name: "Stripe Payment Gateway",
          type: "Passerelle Carte Bancaire",
          status: "Protégé",
          latency: "28 ms",
          tls: "PCI-DSS v4.0",
          anomaly: "Aucune",
        },
        {
          name: "Galileo Rail & Bus Connector",
          type: "Transport Terrestre",
          status: "Protégé",
          latency: "64 ms",
          tls: "TLS 1.3 (Valide)",
          anomaly: "Aucune",
        },
      ],
    },

    // Tab 4: Settings
    settings: {
      title: "Paramètres & Configuration de la Plateforme",
      subtitle: "Gérez les fournisseurs LLM, les seuils d'alertes et la configuration système.",
      llmProviderTitle: "Fournisseur LLM Actif",
      llmProviders: {
        gemini: "Google Gemini 2.5 Flash (Recommandé - Mode Cloud)",
        openai: "OpenAI GPT-4o Mini",
        offline: "Moteur Hors Ligne TECHPULSE (Template local)",
      },
      alertThresholdsTitle: "Seuil de Notification d'Alerte",
      criticalOnly: "Critique Uniquement (CVSS > 9.0)",
      highAndCritical: "Élevé et Critique (CVSS > 7.0) - Recommandé",
      allAlerts: "Toutes les vulnérabilités",
      apiKeyStatus: "Clé API Gemini / Google : Configurée (GEMINI_API_KEY)",
      saveBtn: "Enregistrer la Configuration",
      saveSuccess: "Configuration mise à jour avec succès !",
    },
  },

  en: {
    // Header & Global
    brandTitle: "TECHPULSE-AI",
    brandSubtitle: "Cyber Intelligence & Travel Security Suite",
    agencyLabel: "Agency",
    agencies: {
      abidjan: "Abidjan Tourism Suite",
      paris: "Paris Travel & Booking Hub",
      global: "Global Amadeus Agency Network",
    },
    statusProtected: "🟢 Systems Protected",
    statusAlert: "🟠 Vigilance Required",
    statusCritical: "🔴 Critical Alert",
    languageBtn: "EN 🇬🇧",
    switchLanguage: "Switch to French",

    // Navigation Sidebar
    nav: {
      dashboard: "Dashboard",
      assistant: "Cyber Assistant",
      gdsSecurity: "API & GDS Security",
      settings: "Settings",
    },
    systemStatusTitle: "AI Engine Ops",
    systemStatusOnline: "All services operational",
    activeSession: "Session: ",

    // Tab 1: Executive Dashboard
    dashboard: {
      title: "Executive Cybersecurity Dashboard",
      subtitle: "Unified view of vulnerabilities, GDS booking APIs, and cyber threats in the travel industry.",
      kpis: {
        monitoredApis: "Monitored APIs",
        activeThreats: "Active Threats",
        securityScore: "Security Score",
        protectedTx: "PCI-DSS Compliance",
      },
      charts: {
        trendTitle: "Threat vs Bookings Trend (24h)",
        severityTitle: "Vulnerabilities by Severity",
        severityLabels: {
          critical: "Critical",
          high: "High",
          medium: "Medium",
          low: "Low",
        },
      },

      quickActions: {
        title: "Quick Actions & Priority Recommendations",
        auditPayment: "Audit Payment Gateway",
        auditPaymentDesc: "Run an automated scan of PCI-DSS tokens on Stripe and Worldpay.",
        verifyAmadeus: "Verify Amadeus GDS API",
        verifyAmadeusDesc: "Verify TLS 1.3 certificates and rate-limiting on ticketing flows.",
        scanEndpoints: "Scan Booking Endpoints",
        scanEndpointsDesc: "Inspect webhook vulnerabilities for injection & RCE flaws.",
        generateReport: "Generate 24h PDF Report",
        generateReportDesc: "Export an executive summary ready for the board of directors.",
        actionSuccess: "Action initiated successfully!",
      },
    },

    // Tab 2: Cyber Assistant
    assistant: {
      title: "TECHPULSE AI Cyber Assistant (RAG & Advisory)",
      subtitle: "Ask questions or describe an incident for specialized Travel & GDS security advisories.",
      initialGreeting: "Hello! I am **TECHPULSE-AI**, your virtual cybersecurity assistant dedicated to the travel industry. How can I assist you today?",
      promptChipsTitle: "💡 Quick prompt examples (click to try):",
      promptChips: [
        "What is a CVE?",
        "How to secure our Amadeus GDS APIs?",
        "We detected a critical RCE vulnerability on our booking server.",
        "What are the risks of credit card payment fraud in travel agencies?",
      ],
      inputPlaceholder: "Ask a cybersecurity question (e.g., API vulnerabilities, ransomware, PCI-DSS compliance)...",
      sendBtn: "Send",
      processing: "TECHPULSE-AI is analyzing your request via FAISS & DistilBERT...",
      cveSourcesLabel: "RAG & CVE Sources Consulted:",
      intentLabel: "Detected Intent:",
      severityLabel: "DistilBERT Severity:",
      modulesUsed: "Modules Used:",
    },

    // Tab 3: API & GDS Security
    gdsSecurity: {
      title: "API Security & GDS Connectors Monitor",
      subtitle: "Real-time surveillance of reservation APIs, GDS systems (Amadeus, Sabre, Galileo) and payment gateways.",
      tableHeaders: {
        system: "System / Connector",
        type: "Integration Type",
        status: "Security Status",
        latency: "Response Time",
        tls: "TLS Compliance",
        anomaly: "Recent Anomaly",
      },
      systems: [
        {
          name: "Amadeus Flight GDS API",
          type: "Airline Ticketing GDS",
          status: "Protected",
          latency: "42 ms",
          tls: "TLS 1.3 (Valid)",
          anomaly: "None",
        },
        {
          name: "Sabre Hotel Booking Webhook",
          type: "Hospitality Engine",
          status: "Vigilance",
          latency: "115 ms",
          tls: "TLS 1.2 (Renewal required)",
          anomaly: "Blocked brute force attempts (23 req/s)",
        },
        {
          name: "Stripe Payment Gateway",
          type: "Credit Card Gateway",
          status: "Protected",
          latency: "28 ms",
          tls: "PCI-DSS v4.0",
          anomaly: "None",
        },
        {
          name: "Galileo Rail & Bus Connector",
          type: "Ground Transport",
          status: "Protected",
          latency: "64 ms",
          tls: "TLS 1.3 (Valid)",
          anomaly: "None",
        },
      ],
    },

    // Tab 4: Settings
    settings: {
      title: "Platform Settings & Configuration",
      subtitle: "Manage LLM providers, notification thresholds, and system preferences.",
      llmProviderTitle: "Active LLM Provider",
      llmProviders: {
        gemini: "Google Gemini 2.5 Flash (Recommended - Cloud Mode)",
        openai: "OpenAI GPT-4o Mini",
        offline: "TECHPULSE Offline Engine (Local Template)",
      },
      alertThresholdsTitle: "Alert Notification Threshold",
      criticalOnly: "Critical Only (CVSS > 9.0)",
      highAndCritical: "High and Critical (CVSS > 7.0) - Recommended",
      allAlerts: "All Vulnerabilities",
      apiKeyStatus: "Gemini / Google API Key: Configured (GEMINI_API_KEY)",
      saveBtn: "Save Configuration",
      saveSuccess: "Configuration updated successfully!",
    },
  },
};
