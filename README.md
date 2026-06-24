# 🌤️ Premium Weather Bot

A Discord weather bot with **Components V2 premium cards**, powered by **Open-Meteo** (free, no API key), with **daily auto-posting** and your **custom white emoji icons**.

---

## ✨ Features

- `/weather <city>` — on-demand premium weather card
- `/setweather <city> <HH:MM>` — daily auto-post in the current channel
- `/unsetweather` — stop the daily post
- Components V2 cards with white accent bar, dividers, and your custom icons
- No API key needed (Open-Meteo is free)

---

## 📦 Setup (step by step)

### 1. Install Python deps
```bash
pip install -r requirements.txt
```
Needs **Python 3.11+** (uses `zoneinfo`).

### 2. Create the bot & get a token
1. Go to https://discord.com/developers/applications → **New Application**
2. **Bot** tab → **Reset Token** → copy it
3. Under **Privileged Gateway Intents**: none required (default intents only)
4. **Installation** / **OAuth2 → URL Generator**: scopes `bot` + `applications.commands`, bot permissions: **Send Messages**, **Embed Links**, **Use External Emojis**
5. Open the generated URL → invite the bot to your server

### 3. Set your token
**Linux/macOS:**
```bash
export DISCORD_TOKEN="your_token_here"
```
**Windows (PowerShell):**
```powershell
$env:DISCORD_TOKEN="your_token_here"
```
Or paste it directly into `bot.py` (the `TOKEN =` line).

### 4. Upload your emoji icons & wire them up
1. **Server Settings → Emoji → Upload Emoji** — upload the PNGs from the icons zip
   (name them like `sunny`, `rain`, `humidity`, `wind`, `location`, etc.)
2. For each, grab the ID: type `\:sunny:` in any channel → it reveals `<:sunny:123456789>`
3. Open **`icons.py`** and replace each fallback value with your real `<:name:id>`:
   ```python
   "sunny":  "<:sunny:123456789>",
   "rain":   "<:rain:987654321>",
   ...
   ```
   > Emojis you don't upload keep their unicode fallback — the bot still runs.

### 5. Run it
```bash
python bot.py
```
You'll see `✓ Logged in as ...` and `✓ Commands synced`.

---

## 🕐 Daily auto-post

In the channel you want the forecast:
```
/setweather city: Pune time: 08:00
```
The bot posts a fresh card every day at that time.
**Timezone** is set in `bot.py` → `DEFAULT_TZ` (default `Asia/Kolkata`). Change if needed.

To stop:
```
/unsetweather
```

Settings are saved per-channel in **`config.json`** (auto-created).

---

## 🎨 Customizing the card

- **Accent color**: `ACCENT = 0xFFFFFF` in `bot.py` (the left bar). White by default.
- **Card layout**: edit `build_weather_card()` in `bot.py` — it's plain Components V2 JSON.
- **Add more icons**: drop them into `icons.py` and use `ICON["yourname"]` anywhere.

---

## 🧩 How Components V2 works here

discord.py doesn't natively send V2 yet, so the bot hits Discord's REST routes directly
with the `flags: 32768` (IS_COMPONENTS_V2) payload. Component type ints:

| type | meaning        |
|------|----------------|
| `17` | Container (card) |
| `10` | Text Display    |
| `14` | Separator / Divider |

That's why you get real dividers + custom-emoji headers (impossible in plain embeds).

---

## 🛠️ Files

```
weatherbot/
├── bot.py            # main bot + slash commands + daily loop + card builder
├── weather_api.py    # Open-Meteo geocode + forecast wrapper
├── icons.py          # YOUR custom emoji IDs (edit this!)
├── requirements.txt
├── config.json       # auto-created, per-channel daily settings
└── README.md
```

---

## ❓ Troubleshooting

- **Slash commands not showing** → wait a minute after first run, or re-invite with the
  `applications.commands` scope. Global sync can take a few minutes.
- **Custom emojis show as `:sunny:` text** → the bot needs **Use External Emojis** permission,
  and the IDs in `icons.py` must be correct.
- **`City not found`** → try a more specific name (e.g. `Pune, IN`).
- **Daily post didn't fire** → check `DEFAULT_TZ` matches the time you expect, and the bot
  was running at that minute.
