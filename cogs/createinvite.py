import os

import discord
from discord import app_commands
from discord.ext import commands

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'welcome_config.json')


def is_admin(interaction: discord.Interaction) -> bool:
    return (interaction.user.guild_permissions.administrator
            or interaction.user.id == interaction.guild.owner_id)


class Createinvite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='createinvite', description='招待リンクを作成します。')
    @app_commands.default_permissions(administrator=True)
    async def createinvite(self, interaction: discord.Interaction):
        if not is_admin(interaction):
            await interaction.response.send_message('管理者のみ実行できます。', ephemeral=True)
            return

        try:
            invite_link = await interaction.channel.create_invite(max_age=-1, max_uses=-1, unique=False)
        except discord.Forbidden:
            await interaction.response.send_message('招待リンクを作成する権限がありません。', ephemeral=True)
            return
        except Exception:
            print(f'[ERROR] 招待リンク作成失敗 (guild={interaction.guild.id}, user={interaction.user.id})')
            await interaction.response.send_message('招待リンクの作成に失敗しました。', ephemeral=True)
            return

        invite_embed = discord.Embed(title='招待リンクを作成しました！', color=discord.Color.green())
        invite_embed.add_field(name='招待リンク:', value=f'{invite_link}', inline=False)
        invite_embed.add_field(name='有効期限:', value='なし', inline=False)
        invite_embed.add_field(name='使用回数制限:', value='1なし', inline=False)
        await interaction.response.send_message(embed=invite_embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Createinvite(bot))
