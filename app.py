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
if "TOKEN" not in os.environ:
    raise ValueError("No token provided.")
TOKEN = str(os.getenv("TOKEN"))

# 通知を送るチャンネルID
if "CHANNEL_ID" not in os.environ:
    raise ValueError("No channel id provided.")
CHANNEL_ID = int(str(os.getenv("CHANNEL_ID")))

# 監視するAPIのURL
API_URL = "https://kurisyushien.org/api"


intents = discord.Intents.default()
intents.message_content = True

# Discordクライアントの設定
client = discord.Client(intents=intents)

# ロガーの設定
logger = logging.getLogger("discord")

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


def split_list(lst, chunk_size):
    """
    リストを指定されたサイズで分割する関数。
    params:lst: 分割するリスト
    params:chunk_size: 分割するサイズ
    return: 分割されたリスト
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


@client.event
async def on_ready():
    logger.info(f"Logged in as {client.user}")
    check_api.start()


@tasks.loop(minutes=1)
async def check_api():
    global previous_response
    logger.info("Fetching API...")
    response = requests.get(API_URL)
    logger.info(f"Status code: {response.status_code}")
    if response.status_code == 200:
        current_response = parse_tsv(response.text)[
            1:
        ]  # １行目はタイムスタンプなので除外
        if previous_response is not None and current_response != previous_response:
            diff_list = diff_row(previous_response, current_response)
            logger.info(f"Changed: {len(diff_list)}")
            channel = client.get_channel(CHANNEL_ID)
            if isinstance(channel, discord.TextChannel):
                for chunk in split_list(diff_list, 10):  # 例として10個ずつ分割
                    embed = discord.Embed(title="新着｜履修登録状況", color=0x00FF00)
                    for p, c in chunk:
                        if p is None:
                            embed.add_field(name=c[0], value=c[1], inline=False)
                        else:
                            embed.add_field(
                                name=f"{p[2]}",
                                value=f"""
                                適正人数：{p[-3]}
                                登録数：{p[-2]} -> {c[-2]}
                                登録残数：{p[-1]} -> {c[-1]}
                                [シラバス](https://eduweb.sta.kanazawa-u.ac.jp/Portal/Public/Syllabus/DetailMain.aspx?student=1&lct_year={datetime.now().year}&lct_cd={c[0]}&je_cd=1&ActingAccess=1)
                                """,
                                inline=False,
                            )
                    await channel.send(embed=embed)
            else:
                logger.error("Not found channel.")
        previous_response = current_response
    else:
        logger.error(f"Failed to fetch API: {response.status_code}")


# Botを実行
client.run(TOKEN)
