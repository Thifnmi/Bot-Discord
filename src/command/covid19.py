import os
import pytz
import requests
from discord import Embed
from discord.ext import commands
from datetime import datetime
from conf import config


env = os.getenv("ENV", "production")
VN = pytz.timezone('Asia/Ho_Chi_Minh')



class Covid19(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="covid19", help="Search covid19 info")
    async def covid19(self, ctx, *args):
        request = requests.get(config[env].COVID19)
        data = request.json()
        messages = Embed(title="Thông tin về đại dịch SARS-CoV-2", description="-----------------------------------------------------------------", color=0x0099ff)
        messages.add_field(name='Số ca nhiễm tại Việt Nam ', value=data['total']['internal']['cases'], inline= True)
        messages.add_field(name='Tử vong', value=data['total']['internal']['death'], inline=True)
        messages.add_field(name='Phục hồi', value=data['total']['internal']['recovered'], inline= True )
        time = datetime.now(VN).strftime("%H:%M:%S")
        date = datetime.now(VN)
        messages.set_footer(text=f'Thifnmi  *  {date} {time}', icon_url='https://i.imgur.com/LoaZBG3.jpg')