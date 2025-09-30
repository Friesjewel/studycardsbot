import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from help_menu import HelpMenu
from woordjes_quiz import WoordjesQuiz
import os
from dotenv import load_dotenv

# Laad .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("Bot token niet gevonden! Zet DISCORD_TOKEN in je .env bestand.")

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Actieve sessies
active_sessions = {}  # Format: {user_id: {"type": "woordjes/quiz", "name": gebruiker}}

# Achtergrond taak voor dynamische status
async def status_task(bot: commands.Bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        if active_sessions:
            user_id, session = next(iter(active_sessions.items()))
            if session["type"] == "woordjes":
                status_text = f"Toetst {session['name']}"
            elif session["type"] == "quiz":
                status_text = f"Quiz met {session['name']}"
            else:
                status_text = "Type /help voor commands"
        else:
            status_text = "Type /help voor commands"
        await bot.change_presence(activity=discord.Game(name=status_text))
        await asyncio.sleep(10)

# Bot subclass
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Start achtergrond taak
        self.loop.create_task(status_task(self))
        # Sync slash commands
        await self.tree.sync()

bot = MyBot()

# Voeg commands toe
HelpMenu(bot, active_sessions)
WoordjesQuiz(bot, bot.tree, active_sessions)

# Run de bot
bot.run(TOKEN)
