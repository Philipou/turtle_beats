import discord
from discord.ext import commands
import time
import youtube_dl
import asyncio
from requests import get
import datetime
import random
import openai

start_time = time.time()
default_intents = discord.Intents.all()
activity = discord.Activity(type=discord.ActivityType.listening, name="Philipou#6977")
bot = commands.Bot(command_prefix=".", intents=default_intents, activity=activity, status=discord.Status.online)
musics = {}
ytdl = youtube_dl.YoutubeDL()
queue = []
next_number_survivamod = "1"
last_person_survivamod = "0"
openai.api_key = "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"


async def is_counting_channel(ctx):
    return ctx.channel.id == 1072618962547908658


@bot.event
async def on_ready():
    print("The bot is ready !")


@bot.listen()
async def on_message(message):
    global next_number_survivamod
    global last_person_survivamod
    if message.channel.id == 1072618962547908658:  # survivamod
        if message.author.bot:
            return
        if message.content == next_number_survivamod and not message.author.id == last_person_survivamod:
            await message.add_reaction("✅")
            last_person_survivamod = message.author.id
            next_number_survivamod = int(next_number_survivamod)
            next_number_survivamod += 1
            next_number_survivamod = str(next_number_survivamod)
        elif not message.content == next_number_survivamod:
            await message.channel.send(
                f"{message.author.mention} s'est trompé ! Le nombre étais {next_number_survivamod} ! "
                f"Retour à la case départ !")
            last_person_survivamod = "0"
            next_number_survivamod = "1"
        elif message.author.id == last_person_survivamod:
            await message.channel.send(f"{message.author.mention} s'est trompé ! La même personne ne peut pas compter "
                                       f"deux fois de suite ! Retour à la case départ !")
            last_person_survivamod = "0"
            next_number_survivamod = "1"


class Video:
    def __init__(self, arg):
        try:
            get(arg)
        except:
            video = ytdl.extract_info(f"ytsearch:{arg}", download=False)["entries"][0]
        else:
            video = ytdl.extract_info(arg, download=False)
        video_format = video["formats"][0]
        self.url = video["webpage_url"]
        self.stream_url = video_format["url"]


@bot.command(name="stop", help="Stops the current track.", )
async def stop(ctx):
    global queue
    client = ctx.guild.voice_client
    musics[ctx.guild] = []
    if client:
        await client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel !")


@bot.command(name="resume", help="Resume the current paused track.")
async def resume(ctx):
    client = ctx.guild.voice_client
    if client.is_paused():
        client.resume()
        await ctx.send("Resuming the current track.")
    else:
        await ctx.send("I'm not paused !")


@bot.command(name="pause", help="Pause the current playing track.")
async def pause(ctx):
    client = ctx.guild.voice_client
    if not client.is_paused():
        client.pause()
        await ctx.send("Pausing the current playing track.")
    else:
        await ctx.send("I'm already paused !")


async def play_song(client, queue, song):
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url,
                                                                 before_options="-reconnect 1 -reconnect_streamed 1 "
                                                                                "-reconnect_delay_max 5 "))

    # noinspection PyTypeChecker
    def next(_):
        global queue
        if "loop" in queue:
            asyncio.run_coroutine_threadsafe(play_song(client, queue, song), bot.loop)
        elif len(queue) > 0:
            new_song = queue[0]
            del queue
            queue = [0]
            asyncio.run_coroutine_threadsafe(play_song(client, queue, new_song), bot.loop)
        else:
            asyncio.run_coroutine_threadsafe(client.disconnect(), bot.loop)

    client.play(source, after=next)


@bot.command(name="play", help="Play a song from a search query or url.")
async def play(ctx, *, url):
    client = ctx.guild.voice_client
    video = Video(url)
    musics[ctx.guild] = []
    channel = ctx.author.voice.channel

    if random.randint(1, 100) == 100:
        video = Video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    if client and client.channel:
        await client.disconnect()
        time.sleep(1)
        client = await channel.connect()
        await ctx.send(f"Playing : {video.url}")
        await play_song(client, musics[ctx.guild], video)
    else:
        await ctx.send(f"Playing : {video.url}")
        client = await channel.connect()
        await play_song(client, musics[ctx.guild], video)


@bot.command(name="ping", help="Check the bot's ping/latency.")
async def bot_ping(ctx):
    await ctx.channel.send(f"Bot have {round(bot.latency * 1000)} ms of ping")


@bot.command(name="uptime", help="Check the bot's uptime")
async def bot_uptime(ctx):
    current_time = time.time()
    difference = int(round(current_time - start_time))
    text = str(datetime.timedelta(seconds=difference))
    await ctx.channel.send("Bot have " + text + " of uptime")


@bot.command(name="about", help="Give information about the bot.")
async def about(ctx):
    await ctx.send("Hey ! I'm a nice bot made to listen to music from youtube (and i also have some other "
                   "funtionalities), for help type `.help`, for support contact `Philipou#6977`")


@bot.command(name="loop", help="Toggle loop for the current track.")
async def loop(ctx):
    client = ctx.guild.voice_client
    try:
        if not client.is_playing():
            return
    except AttributeError:
        await ctx.send("I'm not playing anything !")
        return

    if "loop" in queue:
        queue.remove("loop")
        await ctx.send("Looping disabled for the current track.")
    else:
        queue.append("loop")
        await ctx.send("Looping enabled for the current track.")


@bot.command(name="ask", help="Ask a question to the GPT-3 language model.")
async def ask(ctx, *, prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=512,
        n=1,
        stop=None,
        temperature=0.5,
    )
    await ctx.send(response["choices"][0]["text"])


bot.run("MTA0NDY1Nzc5Njc1NjUzNzUyOA.GqdCfU.7QSaCYFPDndGfQo4ugFkhOVQ1AExoq0ILCbsr0")
