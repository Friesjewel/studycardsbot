import discord
from discord import app_commands
from discord.ext import commands
import random
import difflib
import asyncio

class WoordjesQuiz:
    def __init__(self, bot: commands.Bot, tree: app_commands.CommandTree, active_sessions: dict):
        self.bot = bot
        self.tree = tree
        self.active_sessions = active_sessions
        self.register_commands()

    def register_commands(self):
        @self.tree.command(name="woordjes", description="Oefen een woordenlijst")
        async def woordjes_command(interaction: discord.Interaction):
            await interaction.response.send_message(
                "Stuur je woordenlijst in het format:\n```\nwoord-betekenis\nwoord-betekenis\n```",
                ephemeral=True
            )

            def check(m: discord.Message):
                return m.author == interaction.user and m.channel == interaction.channel

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=120)
                woorden = []
                for line in msg.content.split("\n"):
                    if "-" in line:
                        word, meaning = line.split("-", 1)
                        woorden.append((word.strip(), meaning.strip()))

                if not woorden:
                    await interaction.followup.send("Geen geldige woordenlijst gevonden.", ephemeral=True)
                    return

                # Nieuw kanaal
                guild = interaction.guild
                kanaal_naam = f"{interaction.user.name}-{random.randint(1000,9999)}"
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                }
                kanaal = await guild.create_text_channel(name=kanaal_naam, overwrites=overwrites)

                # Voeg gebruiker toe aan active_sessions
                self.active_sessions[interaction.user.id] = {"type": "woordjes", "name": interaction.user.name}

                await kanaal.send(f"{interaction.user.mention}, je sessie is gestart!")

                random.shuffle(woorden)
                for word, meaning in woorden:
                    await kanaal.send(f"**Woord:** {word}")

                    correct = False
                    while not correct:
                        try:
                            antwoord_msg = await self.bot.wait_for(
                                "message", check=lambda m: m.author == interaction.user and m.channel == kanaal, timeout=60
                            )
                        except asyncio.TimeoutError:
                            await kanaal.send(f"⏰ Tijd voorbij! Correct antwoord: **{meaning}**")
                            break

                        user_answer = antwoord_msg.content.strip()
                        if user_answer.lower() == meaning.lower():
                            await kanaal.send("✅ Correct!")
                            correct = True
                        else:
                            similarity = difflib.SequenceMatcher(None, user_answer.lower(), meaning.lower()).ratio()
                            if similarity >= 0.8:
                                await kanaal.send(f"⚠️ Bijna goed! Antwoord wordt als correct gerekend: **{meaning}**")
                                correct = True
                            else:
                                await kanaal.send(f"❌ Fout! Correct antwoord: **{meaning}**")
                                correct = True

                # Einde sessie
                del self.active_sessions[interaction.user.id]
                await self.bot.change_presence(activity=discord.Game(name="Type /help voor commands"))
                await kanaal.send("✅ Woordenlijst voltooid!")

            except Exception as e:
                await interaction.followup.send(f"Er is iets misgegaan: {e}", ephemeral=True)

        # Quiz
        @self.tree.command(name="quiz", description="Start een quiz")
        async def quiz_command(interaction: discord.Interaction):
            try:
                vragen = [
                    {"vraag": "Wat is de hoofdstad van Frankrijk?", "opties": ["Parijs", "Londen", "Berlijn", "Rome"], "antwoord": "Parijs"},
                    {"vraag": "Wat is 2 + 2?", "opties": ["3", "4", "5", "6"], "antwoord": "4"}
                ]
                kanaal = interaction.channel
                self.active_sessions[interaction.user.id] = {"type": "quiz", "name": interaction.user.name}

                await kanaal.send(f"{interaction.user.mention} Quiz gestart!")

                for q in vragen:
                    view = discord.ui.View(timeout=None)
                    for opt in q["opties"]:
                        button = discord.ui.Button(label=opt, style=discord.ButtonStyle.secondary)

                        async def button_callback(interaction2: discord.Interaction, opt=opt, correct=q["antwoord"]):
                            if opt == correct:
                                await interaction2.response.send_message("✅ Correct!", ephemeral=True)
                            else:
                                await interaction2.response.send_message(f"❌ Fout! Correct: {correct}", ephemeral=True)

                        button.callback = button_callback
                        view.add_item(button)

                    await kanaal.send(f"**Vraag:** {q['vraag']}", view=view)

                del self.active_sessions[interaction.user.id]
                await self.bot.change_presence(activity=discord.Game(name="Type /help voor commands"))
                await kanaal.send("✅ Quiz voltooid!")

            except Exception as e:
                await interaction.followup.send(f"Er is iets misgegaan: {e}", ephemeral=True)
