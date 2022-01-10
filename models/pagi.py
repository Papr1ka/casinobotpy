from typing import List

from discord import Embed
from discord.abc import Messageable
from discord.member import Member
from discord_components import DiscordComponents, Button, ButtonStyle, Interaction
from discord.errors import NotFound

class Paginator:
    def __init__(self, client: DiscordComponents, channel: Messageable, contents: List[Embed], author: Member, id: int, values: List, guild):
        self.client = client
        self.channel = channel
        self.contents = contents
        self.index = 0
        self.id = str(id)
        self.author = author
        self.prosessed = []
        self.values = values
        self.l = len(self.values)
        self.guild = guild
        self.force = 10
    
    async def get_current(self):
        if len(self.prosessed) - 1 >= self.index:
            return self.prosessed[self.index]
        else:
            embed = self.contents[self.index]
            embed.set_thumbnail(url=self.guild.icon_url)
            for i in range(self.index * self.force, min(self.l, self.index * self.force + self.force)):
                try:
                    m = await self.guild.fetch_member(int(self.values[i]['_id']))
                    m = m.display_name
                except NotFound:
                    m = 'неизвестный'
                embed.add_field(name=f"`{i + 1}` | " + m + " | " + self.values[i]['custom'], value=f"Уровень: `{self.values[i]['level']}`, опыта `{self.values[i]['exp']}`", inline=False)
            self.prosessed.append(embed)
            return embed

    def get_components(self):
        return [[self.client.add_callback(Button(style=ButtonStyle.blue, emoji="◀️"), self.button_left_callback, ),
                Button(label=f"Page {self.index + 1}/{len(self.contents)}", disabled=True),
                self.client.add_callback(Button(style=ButtonStyle.blue, emoji="▶️"), self.button_right_callback)]
                ]

    async def start(self):
        return await self.channel.send(embed=await self.get_current(), components=self.get_components())

    async def button_left_callback(self, inter: Interaction):
        if self.index == 0:
            self.index = len(self.contents) - 1
        else:
            self.index -= 1

        await self.button_callback(inter)

    async def button_right_callback(self, inter: Interaction):
        if self.index == len(self.contents) - 1:
            self.index = 0
        else:
            self.index += 1
        await self.button_callback(inter)

    async def button_callback(self, inter: Interaction):
        await inter.edit_origin(embed=await self.get_current(), components=self.get_components())