import asyncio
import csv
import logging
import os
from datetime import datetime
from io import StringIO
from typing import List, Optional, Tuple

import discord
import dotenv
import requests
from discord.ext import tasks

dotenv.load_dotenv()

# Discord Botのトークン
TOKEN = os.getenv("TOKEN")

# 通知を送るチャンネルID
CHANNEL_ID = os.getenv("CHANNEL_ID")

# 監視するAPIのURL
API_URL = "https://kurisyushien.org/api"

# ロガーの設定
logger = logging.getLogger("discord")

intents = discord.Intents.default()
intents.message_content = True

# Discordクライアントの設定
client = discord.Client(intents=intents)

# 前回のAPIレスポンスを保存する変数
previous_response = None


def find(lst: List[List[str]], condition) -> Optional[List[str]]:
    """
    リスト内の要素を検索して、条件に一致する最初の要素を返す関数。

    :param lst: 検索対象のリスト
    :param condition: 検索条件を定義する関数
    :return: 条件に一致する最初の要素、またはNone
    """
    for element in lst:
        if condition(element):
            return element
    return None


def parse_tsv(tsv_text: str) -> list:
    """
    TSV形式のテキストをパースして、リストに変換する関数。

    :param tsv_text: TSV形式のテキスト
    :return: パースされたリスト
    """
    return [i.split(r"\t") for i in tsv_text.split(r"\n")]


def diff_row(
    previous: List[List[str]], current: List[List[str]]
) -> List[Tuple[Optional[List[str]], List[str]]]:
    """
    ２つのリストを比較して、差分を取得する関数。

    :param previous: 前回のリスト
    :param current: 現在のリスト
    :return: 差分のリスト
    """
    return [
        (find(previous, lambda x: x[0] == c[0]), c)
        for c in current
        if c not in previous
    ]


@client.event
async def on_ready():
    logger.info(f"Botがログインしました: {client.user}")
    check_api.start()


@tasks.loop(minutes=1)
async def check_api():
    global previous_response
    response = requests.get(API_URL)
    if response.status_code == 200:
        current_response = parse_tsv(response.text)[
            1:
        ]  # １行目はタイムスタンプなので除外
        if previous_response is not None and current_response != previous_response:
            diff_list = diff_row(previous_response, current_response)
            channel = client.get_channel(CHANNEL_ID)
            if isinstance(channel, discord.TextChannel):
                embed = discord.Embed(title="新着情報", color=0x00FF00)
                for p, c in diff_list:
                    if p is None:
                        embed.add_field(name=c[0], value=c[1], inline=False)
                    else:
                        logger.info(f"変更があった項目: {c}")
                        embed.add_field(
                            name=f"{p[2]}",
                            value=f"{p[6]} -> {c[6]}",
                            inline=False,
                        )
                        embed.add_field(
                            name="シラバス",
                            value=f"[リンク](https://eduweb.sta.kanazawa-u.ac.jp/Portal/Public/Syllabus/DetailMain.aspx?student=1&lct_year={datetime.now().year}&lct_cd={c[0]}&je_cd=1&ActingAccess=1)",
                        )
                await channel.send(embed=embed)
        elif previous_response is None:
            channel = client.get_channel(CHANNEL_ID)
        previous_response = current_response
    else:
        print(f"APIリクエストに失敗しました: {response.status_code}")


# Botを実行
client.run(TOKEN)
