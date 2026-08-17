import discord
from discord import app_commands
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='serverinfo', description='サーバーの情報を表示します。')
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=f'{guild.name} の情報', color=discord.Color.blue())
        embed.add_field(name='サーバーID:', value=guild.id, inline=False)
        embed.add_field(name='オーナー:', value=guild.owner.mention if guild.owner else '不明', inline=False)
        embed.add_field(name='メンバー数:', value=f'{guild.member_count}人', inline=False)
        embed.add_field(name='ロール数:', value=f'{len(guild.roles)}個', inline=False)
        embed.add_field(name='チャンネル数:', value=f'{len(guild.channels)}個', inline=False)
        embed.add_field(name='作成日:', value=guild.created_at.strftime('%Y/%m/%d'), inline=False)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='userinfo', description='ユーザーの情報を表示します。')
    @app_commands.describe(user='情報を見たいユーザー（省略時は自分）')
    async def userinfo(self, interaction: discord.Interaction, user: discord.User = None):
        target = user or interaction.user
        member = interaction.guild.get_member(target.id)
        embed = discord.Embed(title=f'{target.display_name} の情報', color=discord.Color.blue())
        embed.add_field(name='ユーザーID:', value=target.id, inline=False)
        embed.add_field(name='アカウント作成日:', value=target.created_at.strftime('%Y/%m/%d'), inline=False)
        if member:
            embed.add_field(name='サーバー参加日:', value=member.joined_at.strftime('%Y/%m/%d') if member.joined_at else '不明', inline=False)
            roles = ', '.join(r.mention for r in member.roles[1:]) or 'なし'
            embed.add_field(name='ロール:', value=roles, inline=False)
        embed.set_thumbnail(url=target.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Info(bot))
