import math
import discord
import validators
from discord.ext import commands
from youtube_dl import YoutubeDL

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.is_paused = False
        self.current = None
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio/best', 'yesplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = None

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                if validators.url(item):
                    info = ydl.extract_info(item, download=False)
                else:
                    info = ydl.extract_info("ytsearch:%s" % item, download=False)
            except Exception as e:
                return False
        return info

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            item = self.music_queue[0][0]
            m_url = item['formats'][0]['url']
            self.current = item["title"]
            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self, ctx, skip_to=None):
        self.start = 0
        if len(self.music_queue) > 0:
            if skip_to:
                if skip_to > len(self.music_queue):
                    await ctx.reply(f"Out if range, please select >= {len(self.music_queue) + 1}")
                else:
                    self.is_playing = True
                    m_url = self.music_queue[skip_to][0]['formats'][0]['url']
                    if self.vc == None or not self.vc.is_connected():
                        self.vc = await self.music_queue[0][1].connect()
                        if self.vc == None:
                            await ctx.send("Could not connect to the voice channel")
                            return
                    else:
                        await self.vc.move_to(self.music_queue[0][1])
                    self.current = self.music_queue[skip_to][0]
                    for _ in range(0, skip_to - 1):
                        self.music_queue.pop(0)
                    self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            self.is_playing = True
            m_url = self.music_queue[0][0]['formats'][0]['url']
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])
            self.current = self.music_queue[0][0]
            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False
            await ctx.reply("No song in queue. Please request to listen")

    @commands.command(name="play", aliases=["p"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Connect to a voice channel!")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.reply("Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.")
            else:
                try:
                    if song['entries'] and len(song['entries']) > 1:
                        for item in song['entries']:
                            self.music_queue.append([item, voice_channel])

                            if self.is_playing == False:
                                await self.play_music(ctx)
                        await ctx.reply(f"Add {len(song['entries'])} song in playlist {query} to queue")
                    else:
                        self.music_queue.append([song['entries'][0], voice_channel])
                        await ctx.reply(f"Song `{song['entries'][0]['title']}` added")
                        
                        if self.is_playing == False:
                            await self.play_music(ctx)
                except Exception as e:
                    self.music_queue.append([song, voice_channel])
                    await ctx.reply(f"Song `{song['title']}` added")
                    
                    if self.is_playing == False:
                        await self.play_music(ctx)

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="resume", help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="skip", help="Skips the current song being played")
    async def skip(self, ctx, *args):
        if args:
            if len(args) > 1:
                await ctx.reply("Skip to only receive one agrument. Example: `!skip 1`")
            if args[0].isnumeric():
                index = int(args[0])
                if index < 1:
                    await ctx.reply("Index must lager 1")
                if index > len(self.music_queue):
                    await ctx.reply("Index out of range queue")
                to = int(args[0])
                self.vc.stop()
                await self.play_music(ctx, (to - 1))
            else:
                await ctx.reply(
                    f"Skip only receive one agrument and must is number but\
                         received character `{args}`.Example: `!skip 1`\
                              will skip to the first song in queue")

        if self.vc != None and self.vc:
            self.vc.stop()
            await self.play_music(ctx)


    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    @commands.has_permissions(manage_guild=True)
    async def queue(self, ctx, page: int = 1, pages: int = 1):
        embed = False
        queue = ''
        if self.is_playing:
            embed = discord.Embed(description=(f"`Playing:` {self.current['title']}\
                \n -----------------------------------------------------------------\
                \n")
            )
        if len(self.music_queue) == 0:
            queue = 'No song in queue'
        else:
            items_per_page = 5
            pages = math.ceil(len(self.music_queue) / items_per_page)

            start = (page - 1) * items_per_page
            end = start + items_per_page
            for i in range(0, len(self.music_queue)):
                if (i > (items_per_page - 1)):
                    break
                queue += '`{}`. [`{}`]({}) {}\n'\
                        .format(
                            i+1,
                            self.music_queue[i][0]["title"],
                            self.music_queue[i][0]['webpage_url'],
                            parse_duration(self.music_queue[i][0]["duration"])
                        )
            embed.set_footer(text='Page {}/{}'.format(page, pages))
        embed.add_field(name="", value=queue)
        await ctx.reply(embed=embed)

    @commands.command(name="clear", help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        self.current = None
        await ctx.reply("Music queue cleared")

    @commands.command(name="remove", aliases=["rm"], help="Remove song in queue")
    async def remove(self, ctx, *args):
        if len(args) > 1:
            await ctx.reply("Remove only receive one agrument. Example: `!remove 1` to remove this first song in queue")
        if args[0].isnumeric():
            index = int(args[0])
            if index < 1:
                await ctx.reply("Index must lager 1")
            if index > len(self.music_queue):
                await ctx.reply("Index out of range queue")
            item = self.music_queue[index - 1]
            self.music_queue.pop(index - 1)
            await ctx.reply(f"Removed song `{item[0]['title']}`")
        else:
            await ctx.reply(f"Remove only receive one agrument and must is number but received character `{args}`. Example: `!remove 1` to remove this first song in queue")

    @commands.command(name="quit", help="Disconnect voice channel")
    async def quit(self, ctx):
        self.is_playing = False
        self.is_paused = False
        self.music_queue = []
        await ctx.reply(f"Disconnect ...")
        await self.vc.disconnect()


def parse_duration(duration: int):
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    duration = []
    if days > 0:
        duration.append('{} days'.format(days))
    if hours > 0:
        duration.append('{}'.format(hours))
    if minutes > 0:
        duration.append('{}'.format(minutes))
    if seconds > 0:
        duration.append('{}'.format(seconds))
    return ':'.join(duration)
