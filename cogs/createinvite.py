import discord
from discord import app_commands
from discord.ext import commands


class Createinvite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='createinvite', description='招待リンクを作成します。')
    @app_commands.default_permissions(administrator=True)
    async def createinvite(self, interaction: discord.Interaction):
        try:
            invite_link = await interaction.channel.create_invite(max_age=0, max_uses=0, unique=False)
        except discord.Forbidden:
            await interaction.response.send_message('招待リンクを作成する権限がありません。', ephemeral=True)
            return
        except Exception as e:
            await interaction.response.send_message(f'招待リンクの作成に失敗しました: {e}', ephemeral=True)
            return

        invite_embed = discord.Embed(title='招待リンクを作成しました！', color=discord.Color.green())
        invite_embed.add_field(name='招待リンク:', value=f'{invite_link}', inline=False)
        await interaction.response.send_message(embed=invite_embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Createinvite(bot))
