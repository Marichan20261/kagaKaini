import discord
from discord.ext import commands, tasks
import asyncio
import datetime
import os
import json

from scheduler import TaskScheduler

TOKEN = os.getenv("DISCORD_TOKEN")  # Render 環境変数に登録推奨
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# スケジューラ初期化
scheduler = TaskScheduler("tasks.json")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    check_tasks.start()  # タスク監視開始

# === 各コマンド ===

@bot.command(name="add_todo")
async def add_todo(ctx, time: str, *, content: str):
    """
    /add_todo 2025/09/19/16:30 テスト内容
    """
    try:
        run_time = datetime.datetime.strptime(time, "%Y/%m/%d/%H:%M")
        scheduler.add_task("To-do", run_time, content)
        await ctx.send(f"To-doを追加しました: {time} {content}")
    except ValueError:
        await ctx.send("時刻の形式が正しくありません。例: 2025/09/19/16:30")

@bot.command(name="repair_End")
async def repair_end(ctx, minutes: int, ship_name: str):
    run_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    scheduler.add_task("入渠終了", run_time, f"{ship_name}")
    await ctx.send(f"{ship_name} の入渠終了を {run_time} に設定しました。")

@bot.command(name="expedition_End")
async def expedition_end(ctx, minutes: int, expedition_name: str):
    run_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    scheduler.add_task("遠征帰投", run_time, expedition_name)
    await ctx.send(f"{expedition_name} の遠征帰投を {run_time} に設定しました。")

@tasks.loop(seconds=30)
async def check_tasks():
    """30秒ごとにタスクを確認"""
    now = datetime.datetime.now()
    due_tasks = scheduler.get_due_tasks(now)

    if not due_tasks:
        return

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("通知先チャンネルが見つかりません。CHANNEL_IDを確認してください。")
        return

    for task in due_tasks:
        msg = scheduler.format_message(task)
        await channel.send(msg)

    scheduler.save()  # JSON更新

bot.run(TOKEN)
