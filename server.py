import os
from conf import config
from discord.ext import commands
from src.command import Music, Covid19, Helper

env = os.getenv("ENV", "production")
bot = commands.Bot(command_prefix='!')


#remove the default help command so that we can write out own
bot.remove_command('help')

bot.add_cog(Helper(bot))
bot.add_cog(Music(bot))
bot.add_cog(Covid19(bot))

bot.run(config[env].TOKEN)