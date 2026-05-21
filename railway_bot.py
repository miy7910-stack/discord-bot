import discord
from discord.ext import commands
import asyncio
import os
import traceback

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=".", intents=intents)

running = False
attack_tasks = []

@bot.event
async def on_ready():
    await bot.user.edit(username="GU1DE")
    print(f"{bot.user} 실행 완료!")

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"오류 발생 ({event}):\n{traceback.format_exc()}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"커맨드 오류: {error}")

async def send_loop(ctx, message):
    while running:
        try:
            await ctx.send(message)
        except discord.HTTPException:
            await asyncio.sleep(1)
        except Exception:
            await asyncio.sleep(1)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content == ".tp":
        await start_attack(message, "# 안녕하세요")
        return

    if message.content.startswith(".tp") and not message.content.startswith(".tp "):
        name = message.content[3:]
        await start_attack(message, f"# @{name}")
        return

    await bot.process_commands(message)

async def start_attack(message, text):
    global running, attack_tasks
    if running:
        return
    running = True
    ctx = await bot.get_context(message)
    for _ in range(5):
        attack_tasks.append(asyncio.create_task(send_loop(ctx, text)))

@bot.command(name="그만")
async def stop(ctx):
    global running, attack_tasks
    running = False
    for t in attack_tasks:
        t.cancel()
    attack_tasks = []

@bot.command(name="들어가")
async def join(ctx):
    voice_channels = ctx.guild.voice_channels
    if not voice_channels:
        return
    channel = voice_channels[0]
    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()

@bot.command(name="나와")
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@bot.command(name="끄기")
async def mute(ctx):
    if ctx.voice_client and ctx.voice_client.channel:
        await ctx.guild.change_voice_state(channel=ctx.voice_client.channel, self_mute=True, self_deaf=False)

@bot.command(name="켜기")
async def unmute(ctx):
    if ctx.voice_client and ctx.voice_client.channel:
        await ctx.guild.change_voice_state(channel=ctx.voice_client.channel, self_mute=False, self_deaf=False)

async def main():
    while True:
        try:
            await bot.start(TOKEN)
        except discord.LoginFailure:
            print("토큰 오류 - 봇을 종료합니다.")
            break
        except Exception as e:
            print(f"봇 오류: {e} — 5초 후 재시작...")
            await asyncio.sleep(5)
            await bot.close()
            bot.clear()

asyncio.run(main())
