---
name: discord-notifications
description: Send Jarvis reminders, project updates, task completions, and important alerts to Thomas through a private Discord channel using a local Discord webhook bridge.
---

# Discord Notifications

Use this skill when the user asks Jarvis to send a notification, reminder, project update, alert, or status message to Discord.

## Safety

- Never reveal, print, log, or ask the user to paste the Discord webhook URL into chat.
- The webhook secret is stored outside this skill in the local bridge's environment.
- Do not send a Discord message unless the user explicitly requested a notification, or a scheduled task explicitly requires one.
- Do not include private credentials, API keys, passwords, or unnecessary sensitive information in notifications.

## Sending a message

The local Discord bridge runs on:

http://127.0.0.1:8765

Send a notification by using the Odysseus shell tool to POST JSON to:

http://127.0.0.1:8765/notify

PowerShell example:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/notify -ContentType 'application/json' -Body (@{
    content = "🤖 **Jarvis reminder**`nWork on the robot dog project."
} | ConvertTo-Json)
