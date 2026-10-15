# 🤖 Wazuh SIEM × OpenAI — Intelligent Threat Analysis Pipeline

> Automatically analyzes **Wazuh SIEM** security alerts using **OpenAI GPT** models — providing real-time risk assessments, attack descriptions, and actionable remediation steps for SOC analysts.

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://python.org)
[![Wazuh](https://img.shields.io/badge/Wazuh-SIEM-00adef)](https://wazuh.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?logo=openai)](https://platform.openai.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture & Workflow](#-architecture--workflow)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Restart Wazuh Manager](#-restart-wazuh-manager)
- [Output Format](#-output-format)
- [Chaining with Telegram Alerts](#-chaining-with-telegram-alerts)
- [Troubleshooting](#-troubleshooting)
- [Author](#-author)

---

## 🌐 Overview

This integration sits between Wazuh's alert engine and your SOC workflow. When a security event crosses the configured severity threshold, the script:

1. Receives the raw alert JSON from Wazuh
2. Sends it to OpenAI's GPT model with a structured SOC analyst prompt
3. Receives a risk assessment + remediation plan
4. Enriches the original alert with the AI analysis
5. Appends the enriched record to a structured log file

No third-party Python packages required — only the standard library.

---

## ⚙️ Architecture & Workflow

```
Wazuh Manager
     │
     │  Alert (level 7+) in JSON format
     ▼
custom-openai.py
     │
     │  POST → OpenAI API (gpt-4o-mini)
     ▼
AI Analysis (risk score, attack type, remediation)
     │
     │  Enriched alert appended
     ▼
/var/ossec/logs/openai-alerts.json
     │
     │  (Optional: feed into Telegram pipeline)
     ▼
SOC Analyst / Telegram Channel 📲
```

---

## ✅ Prerequisites

| Requirement | Details |
|---|---|
| Wazuh Manager | v4.x or later |
| Python | 3.6+ (standard library only) |
| OpenAI API Key | [platform.openai.com](https://platform.openai.com) |
| OpenAI Model | `gpt-4o-mini` (configurable) |

---

## 🚀 Installation

### Step 1 — Clone the repository

```bash
git clone https://github.com/tajammolhossain/wazuh-openai-integration.git
cd wazuh-openai-integration
```

### Step 2 — Copy the integration script

```bash
sudo cp custom-openai.py /var/ossec/integrations/custom-openai.py
```

### Step 3 — Set correct permissions

```bash
sudo chmod 750 /var/ossec/integrations/custom-openai.py
sudo chown root:wazuh /var/ossec/integrations/custom-openai.py
```

---

## 🔧 Configuration

### 1. Add your OpenAI API key

Open `/var/ossec/integrations/custom-openai.py` and set your key:

```python
OPENAI_API_KEY = "sk-..."   # Your OpenAI API key
OPENAI_MODEL   = "gpt-4o-mini"   # Or "gpt-4o" for higher accuracy
```

> ⚠️ **Never commit your real API key to Git.** Use an environment variable or secrets manager in production.

### 2. Update `ossec.conf`

Add the integration block to `/var/ossec/etc/ossec.conf`  
(see [`ossec-config-snippet.xml`](ossec-config-snippet.xml) for the full snippet):

```xml
<integration>
  <name>custom-openai</name>
  <level>7</level>
  <alert_format>json</alert_format>
</integration>
```

> **Tip:** Adjust `<level>` to control which alerts are analyzed:
> | Level | Meaning |
> |---|---|
> | `5` | Notice — low severity |
> | `7` | Warning — medium severity ✅ recommended |
> | `10` | Critical only |

---

## 🔄 Restart Wazuh Manager

**Docker deployment:**
```bash
sudo docker exec single-node-wazuh.manager-1 /var/ossec/bin/wazuh-control restart
```

**Native Linux installation:**
```bash
sudo systemctl restart wazuh-manager
```

---

## 📄 Output Format

Each enriched alert is appended as a single JSON line to `/var/ossec/logs/openai-alerts.json`:

```json
{
  "id": "1718023456.12345",
  "rule": { "id": "5710", "level": 7, "description": "SSH brute force attempt" },
  "agent": { "name": "web-server-01" },
  "srcip": "192.168.1.105",
  "openai_analysis": "**Risk Assessment:** HIGH\n**Attack Type:** SSH Brute Force\n**Remediation:** Block source IP via firewall, enforce key-based auth, review /var/log/auth.log."
}
```

---

## 🔗 Chaining with Telegram Alerts

This pipeline pairs directly with the **[Wazuh → Telegram Alert Pipeline](https://github.com/tajammolhossain/wazuh-telegram-alert)**. The Telegram integration reads `openai-alerts.json` and forwards the `openai_analysis` field as a formatted message to your Telegram channel.

```
Wazuh → custom-openai.py → openai-alerts.json → Telegram Bot → 📲
```

---

## 🛠️ Troubleshooting

| Issue | Fix |
|---|---|
| `OpenAI API Error: HTTP 401` | Check that your API key is valid and active |
| `OpenAI API Error: HTTP 429` | Rate limit hit — add retry logic or upgrade plan |
| Script not triggered by Wazuh | Verify `<integration>` block is inside `<ossec_config>` |
| Output log not created | Ensure Wazuh process has write access to `/var/ossec/logs/` |
| `Permission denied` on script | Re-run `chmod 750` and `chown root:wazuh` |

Check Wazuh logs for integration errors:
```bash
tail -f /var/ossec/logs/ossec.log | grep custom-openai
```

---

## 👤 Author

**S. M. Tajammol Hossain**

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
