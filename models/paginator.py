from collections import namedtuple
from typing import List

from discord import Embed
from discord.abc import Messageable
from discord.member import Member
from discord_components import DiscordComponents, Button, ButtonStyle, Interaction, Select, SelectOption

class Paginator:
    def __init__(self, client: DiscordComponents, channel: Messageable, contents: List[Embed], author: Member, id: int, values: List[List]):
        self.client = client
        self.channel = channel
        self.contents = contents
        self.index = 0
        self.id = str(id)
        self.author = author
        self.values = values
    
    def get_current(self):
        e = self.contents[self.index]
        v = self.values[self.index]
        print(v)
        return [{'label': e.fields[i].name, 'value': v[i]} for i in range(len(e.fields))]

    def get_components(self):
        current = self.get_current()
        return [[self.client.add_callback(Button(style=ButtonStyle.blue, emoji="◀️"), self.button_left_callback, ),
                Button(label=f"Page {self.index + 1}/{len(self.contents)}", disabled=True),
                self.client.add_callback(Button(style=ButtonStyle.blue, emoji="▶️"), self.button_right_callback)],
                [Select(
                    placeholder='Выберите товар',
                    options=[*[SelectOption(label=i['label'], value=i['value']) for i in current], SelectOption(label="Отменить", value='Отменить')]
                    ,custom_id=self.id)]
                ]


    async def start(self):
        self.msg = await self.channel.send(embed=self.contents[self.index], components=self.get_components())
        o = False
        while not o:
            interaction = await self.client.wait_for('select_option')
            if interaction.custom_id == self.id and interaction.user == self.author:
                o = True
        response = interaction.values[0]
        return response, interaction, self.msg

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