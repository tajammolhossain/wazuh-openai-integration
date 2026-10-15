#!/usr/bin/env python3
"""
Wazuh SIEM — OpenAI API Integration
Author: S. M. Tajammol Hossain
Description: Automatically analyzes Wazuh security alerts using OpenAI GPT models,
             enriches alerts with AI-generated risk assessments and remediation steps,
             and logs structured output for downstream pipelines (e.g. Telegram alerts).
"""

import json
import sys
import urllib.request

# Wazuh Integrator passes the alert file first and <api_key> second.
OPENAI_API_KEY = sys.argv[2] if len(sys.argv) > 2 else ""
OPENAI_MODEL = "gpt-4o-mini"
OUTPUT_LOG_PATH = "/var/ossec/logs/openai-alerts.json"


def analyze_alert_with_openai(alert_data: dict) -> str:
    """
    Send a Wazuh alert to OpenAI and return a concise risk assessment
    with actionable remediation steps.
    """
    url = "https://api.openai.com/v1/chat/completions"

    prompt = (
        "Analyze this Wazuh security alert and provide:\n"
        "1. A concise risk assessment (severity, attack type)\n"
        "2. Likely attack vector or cause\n"
        "3. Actionable remediation steps\n\n"
        f"{json.dumps(alert_data, indent=2)}"
    )

    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert SOC Analyst assisting in threat analysis. "
                    "Be concise, structured, and actionable."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"OpenAI API Error: {str(e)}"


def process_alert_file(alert_file: str) -> None:
    """Read a Wazuh alert file line-by-line, enrich it, and append JSON output."""
    with open(alert_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            alert = json.loads(line)
            alert["openai_analysis"] = analyze_alert_with_openai(alert)

            with open(OUTPUT_LOG_PATH, "a", encoding="utf-8") as out_file:
                out_file.write(json.dumps(alert) + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 3 or not OPENAI_API_KEY:
        sys.stderr.write("Usage: custom-openai <alert_file> <api_key>\n")
        sys.exit(1)

    try:
        process_alert_file(sys.argv[1])
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
