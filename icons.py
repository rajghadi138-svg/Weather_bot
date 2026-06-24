"""
icons.py  —  YOUR custom emoji IDs go here.
────────────────────────────────────────────
After you upload the PNGs to your server as emojis, grab each ID
(type  \\:emojiname:  in chat → it reveals  <:emojiname:1234567890> )
and paste the full token below.

Format:  "<:name:ID>"

If an emoji isn't uploaded yet, leave the fallback unicode — the bot
still works, it just won't show your custom art for that one.
"""

# ───────────────  WEATHER ICONS  ───────────────
# replace each value with your real <:name:id>
ICON = {
    # weather
    "sunny":        "☀️",   # <:sunny:000>
    "cloudy":       "☁️",   # <:cloudy:000>
    "partly_cloudy":"⛅",   # <:partly_cloudy:000>
    "rain":         "🌧️",   # <:rain:000>
    "showers":      "🌦️",   # <:showers:000>
    "snow":         "❄️",   # <:snow:000>
    "thunderstorm": "⛈️",   # <:thunderstorm:000>
    "fog":          "🌫️",   # <:fog:000>
    "wind":         "💨",   # <:wind:000>
    "humidity":     "💧",   # <:humidity:000>
    "temperature":  "🌡️",   # <:temperature:000>
    "sunrise":      "🌅",   # <:sunrise:000>
    "sunset":       "🌇",   # <:sunset:000>

    # ui
    "location":     "📍",   # <:location:000>
    "search":       "🔍",   # <:search:000>
    "settings":     "⚙️",   # <:settings:000>
    "info":         "ℹ️",   # <:info:000>
    "calendar":     "📅",   # <:calendar:000>
    "clock":        "🕐",   # <:clock:000>
    "arrow_up":     "🔺",   # <:arrow_up:000>
    "arrow_down":   "🔻",   # <:arrow_down:000>
    "refresh":      "🔄",   # <:refresh:000>
    "globe":        "🌐",   # <:globe:000>
    "bell":         "🔔",   # <:bell:000>
}


# ──────  WMO weather code → which weather icon to show  ──────
def weather_icon_for(code: int) -> str:
    if code == 0:
        return ICON["sunny"]
    if code in (1, 2):
        return ICON["partly_cloudy"]
    if code == 3:
        return ICON["cloudy"]
    if code in (45, 48):
        return ICON["fog"]
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67):
        return ICON["rain"]
    if code in (80, 81, 82):
        return ICON["showers"]
    if code in (71, 73, 75, 77, 85, 86):
        return ICON["snow"]
    if code in (95, 96, 99):
        return ICON["thunderstorm"]
    return ICON["cloudy"]
