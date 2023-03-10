from discord.ext import commands

class Helper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = """
```
Bot music by @Thifnmi is running 👀👀

Mucsic commands:
!help or !h - displays all the available commands
!play <keywords> or !p <keywords> - finds the song on youtube and plays it in your current channel. Will resume playing the current song if it was paused
!queue or !q - displays the current music queue
!skip - skips the current song being played
!skip <index> - next to the song number in queue and play
!clear - Stops the music and clears the queue
!quit - Disconnected the bot from the voice channel
!pause - pauses the current song being played or resumes if already paused
!resume - resumes playing the current song
!remove <index> - remove song in queue with index

Covid 19 commands:
!covid19 - display infe about covid19 in VN
```
"""
        self.text_channel_list = []
 
    # @commands.Cog.listener()
    # async def on_ready(self):
    #     # print((f'{self.bot.user.name} has connected to Discord!'))
    #     for guild in self.bot.guilds:
    #         for channel in guild.text_channels:
    #             self.text_channel_list.append(channel)

    #     await self.send_to_config_channel("test", self.help_message)

    @commands.command(name="help", aliases=["h"], help="Displays all the available commands")
    async def help(self, ctx):
        await ctx.send(self.help_message)

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_list:
            await text_channel.send(msg)
    
    async def send_to_config_channel(self, channel, msg):
        for text_channel in self.text_channel_list:
            if text_channel.name == channel:
                await text_channel.send(msg)