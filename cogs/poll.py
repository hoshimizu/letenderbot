import discord
from discord import app_commands
from discord.ext import commands

POLL_REACTIONS = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='poll', description='投票を作成します。')
    @app_commands.describe(question='投票する質問', options='選択肢をカンマ区切りで（最大10個）')
    async def poll(self, interaction: discord.Interaction, question: str, options: str):
        choices = [o.strip() for o in options.split(',') if o.strip()]
        if len(choices) < 2:
            await interaction.response.send_message('選択肢は2個以上必要です。', ephemeral=True)
            return
        if len(choices) > 10:
            choices = choices[:10]

        embed = discord.Embed(title='📊 投票', description=question, color=discord.Color.blue())
        lines = []
        for i, choice in enumerate(choices):
            lines.append(f'{POLL_REACTIONS[i]} {choice}')
        embed.add_field(name='選択肢:', value='\n'.join(lines), inline=False)
        embed.set_footer(text=f'作成者: {interaction.user.display_name}')

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        for i in range(len(choices)):
            await message.add_reaction(POLL_REACTIONS[i])


async def setup(bot):
    await bot.add_cog(Poll(bot))
