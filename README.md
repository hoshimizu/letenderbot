# Letender Bot
ウェルカムメッセージ機能などを搭載したBotです。
サーバーはよくオフラインになります。

# 動かし方
`.env` ファイルを作成し、以下のコードを書き込みます。
```
DISCORD_TOKEN=あなたのDiscordボットトークン
```

ライブラリをインストールします。
```bash
pip install discord.py python-dotenv
```

起動します。
```bash
python3 bot.py
```

# コマンド
| コマンド | 説明 |
| --- | --- |
| `/welcomemessage <channel>` | ウェルカムメッセージを設定します（管理者のみ） |
| `/welcomecheck` | 現在のウェルカムメッセージ設定を確認します（管理者のみ） |
| `/welcomeoff` | ウェルカムメッセージを削除します（管理者のみ） |
| `/createinvite` | 招待リンクを作成します（管理者のみ） |
| `/help` | ヘルプを表示します |

ウェルカムメッセージには `{usermention}`（メンション）、`{servername}`（サーバー名）、`{membercount}`（メンバー数）のプレースホルダーが使えます。
