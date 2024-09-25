# rishu-bot

このプロジェクトは大学の履修登録状況が変化したときにサーバーの指定チャンネルにメッセージを送るDiscord Botです。`discord.py`と`docker`を用いて実装しています。

## 特徴

- 履修登録状況の自動監視
- 変更があった場合にDiscordチャンネルに通知
- 簡単にデプロイ可能なDockerサポート

## 必要条件

- Python 3.8+
- Docker
- Discord Bot Token

## インストール

1. リポジトリをクローンします。

  ```bash
  git clone https://github.com/ToYama170402/rishu-bot.git
  cd rishu-bot
  ```

2. `.env`ファイルを作成し、`sample.env`を参考に設定します。

  ```env
  TOKEN=ボットのトークン
  CHANNEL_ID=チャンネルのID
  ```

## 使用方法

1. Dockerを使用してBotを起動します。

  ```bash
  docker-compose up --build
  ```

2. Botが指定されたチャンネルにメッセージを送信することを確認します。

## 貢献

貢献は大歓迎です。バグ報告やプルリクエストをお待ちしています。

大急ぎで突貫工事したので、コードが汚いです。ご了承ください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
