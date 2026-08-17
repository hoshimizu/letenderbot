# 前のファイルが消えました(´;ω;｀)
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    if not os.path.exists("./cogs"):
        return
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("_"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded: cogs.{filename[:-3]}")
            except Exception as e:
                print(f"Failed to load: cogs.{filename[:-3]} - {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")

async def main():
    async with bot:
        await load_extensions()
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            print("Error: missing DISCORD_TOKEN")
            return
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
