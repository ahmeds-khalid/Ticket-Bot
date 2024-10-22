import nextcord
from nextcord.ext import commands

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.sync_application_commands()  # Synchronize the slash commands
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

bot.load_extension("ticket") # Load the TicketBot cog from ticket.py
bot.load_extension("embed_builder")
bot.load_extension("application")

bot.run("MTI5MjkxMTg1NTYwOTU3NzYwNQ.Ggx6oI.r62NcJiHDK-MasjuF0Zij0SB0_qbRbVMX7PcwQ")
