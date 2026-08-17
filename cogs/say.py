import discord
from discord import app_commands
from discord.ext import commands


def is_admin(interaction: discord.Interaction) -> bool:
    return (interaction.user.guild_permissions.administrator
            or interaction.user.id == interaction.guild.owner_id)


class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='say', description='ボットに発言させます（管理者のみ）。')
    @app_commands.describe(message='発言させる内容', channel='送信先チャンネル（省略時は実行したチャンネル）')
    @app_commands.default_permissions(administrator=True)
    async def say(self, interaction: discord.Interaction, message: str, channel: discord.TextChannel = None):
        if not is_admin(interaction):
            await interaction.response.send_message('管理者のみ実行できます。', ephemeral=True)
            return

        target = channel or interaction.channel
        try:
            await target.send(message)
        except discord.Forbidden:
            await interaction.response.send_message('送信権限がありません。', ephemeral=True)
            return
        except Exception:
            print(f'[ERROR] say送信失敗 (guild={interaction.guild.id}, user={interaction.user.id})')
            await interaction.response.send_message('送信に失敗しました。', ephemeral=True)
            return

        await interaction.response.send_message(f'発言しました: {target.mention}', ephemeral=True)


async def setup(bot):
    await bot.add_cog(Say(bot))
