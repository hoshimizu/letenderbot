import discord
from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='help', description='ヘルプを表示します。')
    async def help(self, interaction: discord.Interaction):
        help_embed = discord.Embed(title='ヘルプ', color=discord.Color.blue())
        help_embed.add_field(name='/help', value='ヘルプを表示します。', inline=False)
        help_embed.add_field(name='/createinvite', value='招待リンクを作成します。', inline=False)
        help_embed.add_field(name='/welcomemessage', value='ウェルカムメッセージを設定します。', inline=False)
        help_embed.add_field(name='/welcomeoff', value='ウェルカムメッセージを削除します。', inline=False)
        help_embed.add_field(name='/welcomecheck', value='現在のウェルカムメッセージ設定を確認します。', inline=False)
        await interaction.response.send_message(embed=help_embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Help(bot))
