"""
🌤️  Premium Weather Bot — Components V2 + Open-Meteo (no API key)
-----------------------------------------------------------------
Features:
  • /weather <city>          → premium weather card (on demand)
  • /setweather <city> <time> → configure daily auto-post for this channel
  • /unsetweather            → stop daily auto-post in this channel
  • Auto-posts a daily forecast card at the configured time

Data source : Open-Meteo (free, no key)  https://open-meteo.com
UI          : Discord Components V2 (premium container cards)
Storage     : config.json (per-channel settings)
"""

import os
import json
import asyncio
import datetime as dt
from zoneinfo import ZoneInfo

import aiohttp
import discord
from discord import app_commands
from discord.ext import tasks

from icons import ICON, weather_icon_for   # custom emoji mapping (edit icons.py!)
import weather_api as wx

# ─────────────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN", "")
CONFIG_FILE = "config.json"
DEFAULT_TZ = "Asia/Kolkata"      # timezone for the daily post time
ACCENT = 0xFFFFFF                # white accent bar on cards (#FFFFFF)

# ─────────────────────────────────────────────────────────────
#  Tiny JSON store for per-channel daily settings
#  schema: { "channel_id": {"city": str, "lat": float, "lon": float,
#                           "hour": int, "minute": int, "label": str} }
# ─────────────────────────────────────────────────────────────
def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}

def save_config(cfg: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

# ─────────────────────────────────────────────────────────────
#  Discord client
# ─────────────────────────────────────────────────────────────
class WeatherBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.session: aiohttp.ClientSession | None = None
        self.config = load_config()

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        await self.tree.sync()
        self.daily_loop.start()
        print("✓ Commands synced, daily loop started.")

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

    # runs every minute, fires posts whose time matches now
    @tasks.loop(minutes=1)
    async def daily_loop(self):
        now = dt.datetime.now(ZoneInfo(DEFAULT_TZ))
        for cid, conf in list(self.config.items()):
            if now.hour == conf["hour"] and now.minute == conf["minute"]:
                channel = self.get_channel(int(cid))
                if channel is None:
                    continue
                try:
                    data = await wx.fetch_weather(self.session, conf["lat"], conf["lon"])
                    payload = build_weather_card(conf["label"], data, daily=True)
                    await send_components_v2(channel, payload)
                except Exception as e:
                    print(f"[daily] error for channel {cid}: {e}")

    @daily_loop.before_loop
    async def _wait_ready(self):
        await self.wait_until_ready()


client = WeatherBot()

# ─────────────────────────────────────────────────────────────
#  Components V2 card builder
#  Component type ints:
#    17 = Container | 10 = Text Display | 14 = Separator/Divider
# ─────────────────────────────────────────────────────────────
def build_weather_card(label: str, data: dict, daily: bool = False) -> dict:
    cur = data["current"]
    code = cur["weather_code"]
    w_icon = weather_icon_for(code)
    desc = wx.describe(code)

    temp      = round(cur["temperature_2m"])
    feels     = round(cur["apparent_temperature"])
    humidity  = cur["relative_humidity_2m"]
    wind      = round(cur["wind_speed_10m"])
    hi        = round(data["daily"]["temperature_2m_max"][0])
    lo        = round(data["daily"]["temperature_2m_min"][0])
    sunrise   = wx.fmt_time(data["daily"]["sunrise"][0])
    sunset    = wx.fmt_time(data["daily"]["sunset"][0])
    precip    = data["daily"]["precipitation_probability_max"][0]

    header = (
        f"## {w_icon} {label}\n"
        f"{ICON['info']} {desc}  •  **{temp}°C**"
    )

    # main stats block
    stats = (
        f"{ICON['temperature']} **Feels like**  ·  {feels}°C\n"
        f"{ICON['arrow_up']} **High**  ·  {hi}°C      {ICON['arrow_down']} **Low**  ·  {lo}°C\n"
        f"{ICON['humidity']} **Humidity**  ·  {humidity}%\n"
        f"{ICON['wind']} **Wind**  ·  {wind} km/h\n"
        f"{ICON['rain']} **Rain chance**  ·  {precip}%"
    )

    sun = (
        f"{ICON['sunrise']} **Sunrise** · {sunrise}      "
        f"{ICON['sunset']} **Sunset** · {sunset}"
    )

    footer_txt = "🌅 Daily forecast" if daily else "Requested now"
    stamp = dt.datetime.now(ZoneInfo(DEFAULT_TZ)).strftime("%d %b %Y, %H:%M")

    container = {
        "type": 17,
        "accent_color": ACCENT,
        "components": [
            {"type": 10, "content": header},
            {"type": 14, "divider": True, "spacing": 2},
            {"type": 10, "content": stats},
            {"type": 14, "divider": True, "spacing": 1},
            {"type": 10, "content": sun},
            {"type": 14, "divider": True, "spacing": 1},
            {"type": 10, "content": f"-# {ICON['clock']} {footer_txt}  ·  {stamp}"},
        ],
    }
    return {"flags": 1 << 15, "components": [container]}   # 32768 = IS_COMPONENTS_V2


# helper: send a raw Components V2 payload to a channel via HTTP
async def send_components_v2(channel: discord.abc.Messageable, payload: dict):
    # discord.py doesn't natively send V2 yet → hit the REST route directly
    route = discord.http.Route(
        "POST", "/channels/{channel_id}/messages", channel_id=channel.id
    )
    await client.http.request(route, json=payload)


# same, but for an interaction response (slash command reply)
async def reply_components_v2(interaction: discord.Interaction, payload: dict):
    route = discord.http.Route(
        "POST",
        "/interactions/{id}/{token}/callback",
        id=interaction.id, token=interaction.token,
    )
    body = {"type": 4, "data": payload}   # 4 = CHANNEL_MESSAGE_WITH_SOURCE
    await client.http.request(route, json=body)


# ─────────────────────────────────────────────────────────────
#  SLASH COMMANDS
# ─────────────────────────────────────────────────────────────
@client.tree.command(name="weather", description="Get the current weather for a city")
@app_commands.describe(city="City name, e.g. Pune, Tokyo, London")
async def weather(interaction: discord.Interaction, city: str):
    await interaction.response.defer(thinking=True)
    geo = await wx.geocode(client.session, city)
    if not geo:
        await interaction.followup.send(
            f"{ICON['search']} Couldn't find **{city}**. Check the spelling?"
        )
        return
    data = await wx.fetch_weather(client.session, geo["lat"], geo["lon"])
    label = f"{geo['name']}, {geo['country']}"
    payload = build_weather_card(label, data, daily=False)

    # we deferred → must edit the original via webhook; send V2 as a followup REST call
    route = discord.http.Route(
        "POST", "/webhooks/{app_id}/{token}",
        app_id=(await client.application_info()).id, token=interaction.token,
    )
    await client.http.request(route, json=payload)


@client.tree.command(name="setweather", description="Set a daily auto-post for this channel")
@app_commands.describe(city="City to report", time="24h time HH:MM, e.g. 08:00")
async def setweather(interaction: discord.Interaction, city: str, time: str):
    # permission gate: only members who can manage the channel
    perms = interaction.channel.permissions_for(interaction.user)
    if not perms.manage_channels:
        await interaction.response.send_message(
            f"{ICON['info']} You need **Manage Channels** to set this up.", ephemeral=True
        )
        return

    try:
        hh, mm = map(int, time.strip().split(":"))
        assert 0 <= hh < 24 and 0 <= mm < 60
    except (ValueError, AssertionError):
        await interaction.response.send_message(
            f"{ICON['clock']} Time must be `HH:MM` (24-hour), e.g. `08:00`.", ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True, thinking=True)
    geo = await wx.geocode(client.session, city)
    if not geo:
        await interaction.followup.send(f"{ICON['search']} Couldn't find **{city}**.")
        return

    client.config[str(interaction.channel_id)] = {
        "city": geo["name"], "lat": geo["lat"], "lon": geo["lon"],
        "hour": hh, "minute": mm,
        "label": f"{geo['name']}, {geo['country']}",
    }
    save_config(client.config)

    await interaction.followup.send(
        f"{ICON['bell']} Daily weather for **{geo['name']}, {geo['country']}** "
        f"set to **{hh:02d}:{mm:02d}** ({DEFAULT_TZ}) in this channel. {ICON['location']}"
    )


@client.tree.command(name="unsetweather", description="Stop daily auto-post in this channel")
async def unsetweather(interaction: discord.Interaction):
    perms = interaction.channel.permissions_for(interaction.user)
    if not perms.manage_channels:
        await interaction.response.send_message(
            f"{ICON['info']} You need **Manage Channels** to do this.", ephemeral=True
        )
        return
    cid = str(interaction.channel_id)
    if cid in client.config:
        del client.config[cid]
        save_config(client.config)
        await interaction.response.send_message(
            f"{ICON['refresh']} Daily weather post disabled here.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"{ICON['info']} No daily post was set in this channel.", ephemeral=True
        )


# ─────────────────────────────────────────────────────────────
@client.event
async def on_ready():
    print(f"✓ Logged in as {client.user} (id: {client.user.id})")
    print(f"  Watching {len(client.config)} channel(s) for daily posts.")


if __name__ == "__main__":
    if TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        raise SystemExit("✗ Set your bot token in DISCORD_TOKEN env var or in bot.py")
    client.run(TOKEN)
