# Wazuh SIEM + OpenAI Alert Analysis

Analyze selected Wazuh security alerts with OpenAI, then append the risk assessment and suggested remediation to /var/ossec/logs/openai-alerts.json.

> API calls may incur charges. Never commit or share a real API key. The output is a separate JSON log and does not automatically appear as an enriched event in Wazuh Dashboard.

## Requirements

- Wazuh Manager 4.x
- Python 3 (standard library only)
- OpenAI API key with API billing/usage enabled

## Install

Run these commands on the Wazuh Manager:

~~~bash
git clone https://github.com/tajammolhossain/wazuh-openai-integration.git
cd wazuh-openai-integration
sudo install -o root -g wazuh -m 750 custom-openai.py /var/ossec/integrations/custom-openai
~~~

The installed executable is named custom-openai to match the integration config. Wazuh passes the alert JSON file to the script as its first argument and the configured API key as its second.

## Configure

Open the Manager configuration:

~~~bash
sudo nano /var/ossec/etc/ossec.conf
~~~

Add this inside an <ossec_config> block. Replace the placeholder locally with your API key:

~~~xml
<integration>
  <name>custom-openai</name>
  <api_key>YOUR_OPENAI_API_KEY</api_key>
  <level>10</level>
  <alert_format>json</alert_format>
</integration>
~~~

The level filter sends alerts at that level or above. Choose a threshold appropriate to your alert volume and API budget. In nano, save with Ctrl+O, Enter; exit with Ctrl+X.

## Validate and restart

~~~bash
sudo /var/ossec/bin/wazuh-analysisd -t
sudo systemctl restart wazuh-manager
sudo systemctl status wazuh-manager --no-pager
sudo grep -i custom-openai /var/ossec/logs/ossec.log | tail -n 20
~~~

## Narrow test (optional)

To test only the manager-started alert, temporarily add these XML lines inside the integration block:

~~~xml
<rule_id>502</rule_id>
<level>3</level>
~~~

These lines belong in ossec.conf, not in the terminal. Save the config, validate it, and restart the Manager. Then inspect the output:

~~~bash
sudo tail -n 5 /var/ossec/logs/openai-alerts.json
~~~

After the test, remove the rule_id filter and restore your intended threshold. Do not leave level 3 enabled without a narrow rule filter.

## Output and downstream use

Each processed alert is appended as a JSON line to /var/ossec/logs/openai-alerts.json with an openai_analysis field. You can connect this file to a separate downstream pipeline, such as a notification service. Configure Wazuh separately if you want the log parsed and displayed in Dashboard events.

## Troubleshooting

- **Integration file not found:** confirm /var/ossec/integrations/custom-openai exists, is executable, and is owned by root:wazuh.
- **No output file:** no alert matching the configured filter may have arrived yet.
- **HTTP 429:** check the API project's billing/credits, usage, and rate limits; avoid repeated restarts.
- **HTTP 401:** check that the key in ossec.conf is valid and active.
- **Exposed API key:** revoke it, create a replacement, and never commit the real key.

## License

MIT
