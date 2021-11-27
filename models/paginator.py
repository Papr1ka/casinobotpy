from typing import List

from discord import Embed
from discord.abc import Messageable
from discord_components import DiscordComponents, Button, ButtonStyle, Interaction


class Paginator:
    def __init__(self, client: DiscordComponents, channel: Messageable, contents: List[Embed]):
        self.client = client
        self.channel = channel
        self.contents = contents
        self.index = 0

    def get_components(self):
        return [[self.client.add_callback(Button(style=ButtonStyle.blue, emoji="◀️"), self.button_left_callback, ),
                Button(label=f"Page {self.index + 1}/{len(self.contents)}", disabled=True),
                self.client.add_callback(Button(style=ButtonStyle.blue, emoji="▶️"), self.button_right_callback)]]

    async def start(self):
        self.msg = await self.channel.send(embed=self.contents[self.index], components=self.get_components())

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
        await inter.edit_origin(embed=self.contents[self.index], components=self.get_components())