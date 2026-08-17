import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import os

CONFIG_FILE = 'welcome_config.json'
_config_cache = {}
_is_dirty = False

PLACEHOLDERS = ('{usermention}', '{servername}', '{membercount}')


def load_config_to_cache():
    global _config_cache
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                _config_cache = json.load(f)
            print(f'[SYSTEM] データをRAMにロードしました。合計: {len(_config_cache)} サーバー')
        except json.JSONDecodeError:
            _config_cache = {}
    else:
        _config_cache = {}


def force_save_to_disk():
    global _is_dirty
    if not _is_dirty:
        return
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(_config_cache, f, ensure_ascii=False, indent=4)
        _is_dirty = False
        print('[SYSTEM] 変更されたウェルカム設定をディスクに安全に同期しました。')
    except Exception as e:
        print(f'[ERROR] 定期保存に失敗しました: {e}')


def format_message(raw_message: str, user: discord.abc.User, guild: discord.Guild) -> str:
    return (raw_message
            .replace('{usermention}', user.mention)
            .replace('{servername}', guild.name)
            .replace('{membercount}', str(guild.member_count)))


class welcomemordal(discord.ui.Modal, title='ウェルカムメッセージ設定'):
    message_input = discord.ui.TextInput(
        label='メッセージ内容',
        style=discord.TextStyle.paragraph,
        placeholder='{usermention}、{servername}、{membercount}が使えます。',
        required=True,
        max_length=1000
    )

    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        global _is_dirty
        raw_message = self.message_input.value
        guild = interaction.guild

        _config_cache[str(guild.id)] = {'channel_id': self.channel.id, 'message': raw_message}
        _is_dirty = True

        formatted_preview = format_message(raw_message, interaction.user, guild)

        await interaction.response.send_message(
            f'設定を一時保存しました！\n\n**[プレビュー]**\n{formatted_preview}',
            ephemeral=True
        )


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_config_to_cache()
        self.daily_save_task.start()

    def cog_unload(self):
        self.daily_save_task.cancel()
        force_save_to_disk()

    @tasks.loop(hours=24)
    async def daily_save_task(self):
        force_save_to_disk()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id_str = str(member.guild.id)
        if guild_id_str not in _config_cache:
            return

        guild_config = _config_cache[guild_id_str]
        channel_id = guild_config.get('channel_id')
        raw_message = guild_config.get('message')

        channel = member.guild.get_channel(channel_id)
        if not channel:
            return

        try:
            formatted_message = format_message(raw_message, member, member.guild) if raw_message else member.guild.name
            await channel.send(formatted_message)
        except discord.Forbidden:
            print(f'[ERROR] メンバー参加メッセージの送信権限がありません (guild={member.guild.id})')
        except Exception as e:
            print(f'Failed to send greeting to new member: {e}')

    @app_commands.command(name='welcomemessage', description='ウェルカムメッセージを作ります。')
    @app_commands.describe(channel='入室メッセージを設定するチャンネル')
    @app_commands.default_permissions(administrator=True)
    async def welcomemessage(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.send_modal(welcomemordal(channel=channel))

    @app_commands.command(name='welcomeoff', description='ウェルカムメッセージを削除します。')
    @app_commands.default_permissions(administrator=True)
    async def welcomeoff(self, interaction: discord.Interaction):
        global _is_dirty
        guild_id_str = str(interaction.guild.id)
        if guild_id_str in _config_cache:
            del _config_cache[guild_id_str]
            _is_dirty = True
            await interaction.response.send_message('設定を削除しました。', ephemeral=True)
        else:
            await interaction.response.send_message('このサーバーにはウェルカムメッセージがまだ設定されていません。', ephemeral=True)

    @app_commands.command(name='welcomecheck', description='現在のウェルカムメッセージ設定を確認します。')
    @app_commands.default_permissions(administrator=True)
    async def welcomecheck(self, interaction: discord.Interaction):
        guild_id_str = str(interaction.guild.id)
        config = _config_cache.get(guild_id_str)
        if not config:
            await interaction.response.send_message('このサーバーにはウェルカムメッセージが設定されていません。', ephemeral=True)
            return

        channel = interaction.guild.get_channel(config.get('channel_id'))
        channel_name = f'<#{channel.id}>' if channel else '不明なチャンネル'
        preview = format_message(config.get('message', ''), interaction.user, interaction.guild)

        await interaction.response.send_message(
            f'**[設定内容]**\n'
            f'送信先: {channel_name}\n'
            f'メッセージ:\n{config.get("message", "")}\n\n'
            f'**[プレビュー]**\n{preview}',
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Welcome(bot))
