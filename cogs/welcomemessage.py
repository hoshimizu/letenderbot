import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import os

CONFIG_FILE = 'welcome_config.json'
_config_cache = {}
_is_dirty = False

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
        
        formatted_preview = raw_message.replace('{usermention}', interaction.user.mention).replace('{servername}', guild.name).replace('{membercount}', str(guild.member_count))
        
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

    @commands.Cog.listener()
    async def on_close(self):
        print('[SYSTEM] ボットが終了処理に入りました。RAMからディスクへ最終保存を行います...')
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
            
        if raw_message:
            formatted_message = raw_message.replace('{usermention}', member.mention).replace('{servername}', member.guild.name).replace('{membercount}', str(member.guild.member_count))
        else:
            formatted_message = member.guild.name

        try:
            await channel.send(formatted_message)
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

async def setup(bot):
    await bot.add_cog(Welcome(bot))
