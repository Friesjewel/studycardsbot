import discord
from discord import app_commands
from discord.ui import View, Button

class HelpMenu:
    def __init__(self, bot, active_sessions=None):
        self.bot = bot
        self.active_sessions = active_sessions or {}
        self.register_commands()

    def register_commands(self):
        @self.bot.tree.command(name="help", description="Toon alle beschikbare commands")
        async def help_command(interaction: discord.Interaction):
            embed = discord.Embed(title="StudyGo Bot Help", description="Hier zijn de beschikbare commands:", color=0x00ff00)
            embed.add_field(name="/help", value="Toont dit menu", inline=False)
            embed.add_field(name="/woordjes", value="Oefen een woordenlijst", inline=False)
            embed.add_field(name="/quiz", value="Start een quiz", inline=False)

            # Knoppen
            view = View()
            button = Button(label="Sluit dit menu", style=discord.ButtonStyle.danger)
            
            async def close_callback(interaction2: discord.Interaction):
                await interaction2.message.delete()
            button.callback = close_callback
            view.add_item(button)

            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
