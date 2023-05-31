import os
import discord
import typing
from typing import Optional

# TYPE ALIASES
File            : typing.TypeAlias = typing.TextIO
Interaction     : typing.TypeAlias = discord.Interaction
Button          : typing.TypeAlias = discord.ui.Button
View            : typing.TypeAlias = discord.ui.View
Embed           : typing.TypeAlias = discord.Embed
Selection       : typing.TypeAlias = discord.SelectOption
# END TYPE ALIASES

def message_impl(bot, config : File, tokens : list[str]):
        class MessageImpl(Embed):
                def __init__(self):
                        super().__init__()
                        self.bot = bot
                        self.description = tokens[0].strip()
                        self.title = "Welcome to Geedka"

        return MessageImpl
        
def get_dropdown_options(elems : list[str]) -> list[Selection]:
        return [Selection(label=l) for l in elems]

def select_impl(bot, config : File, tokens : list[str]):
        options_count : int = int(tokens[0])
        my_description : str = tokens[1]

        # FIXME: this is awkward, switch to a dict
        option_names : list[str] = config.readline().strip().split('|')

        option_outcomes : list = [geedka_frontend(bot, config) for i in \
                range(options_count)]

        print("Creating class")

        class SelectImpl(View):
                def __init__(self):
                        super().__init__()
                        self.bot = bot
                        self.description = my_description
                        self.option_names : list[str] = option_names
                        self.option_outcomes : list = option_outcomes
                        self.add_item(self.selection_callback)

                @discord.ui.select(placeholder="Choose one", \
                        options=get_dropdown_options(option_names))
                async def selection_callback(self, i : Interaction, \
                        s : discord.ui.Select):
                        await i.followup.send(self.option_outcomes[ \
                                self.option_names.index(s.label)]())

        print("Created class")

        return SelectImpl

def geedka_frontend(bot, config : File):
        # This is some sorcery I found on stack overflow
# https://stackoverflow.com/questions/10140281/how-to-find-out-whether-a-file-is-at-its-eof
#        while config.tell() != os.fstat(config.fileno()).st_size:
# TODO: figure out a way to render multiple elements that aren't directly connected
        tokens : list[str] = config.readline().strip().split('|')
        match tokens[0]:
                case 'm':
                        return message_impl(bot, config, tokens[1:])
                case 's':
                        return select_impl(bot, config, tokens[1:])
                case 'w':
                        raise Exception("Not implemented")
                case 't':
                        raise Exception("Not implemented")
                case _:
                        raise Exception("Unknown node type passed")


def geedka_init(bot, config_filename : str):
        if not os.path.isfile(config_filename):
                raise Exception(f"{config_filename} not found!")

        return geedka_frontend(bot, open(config_filename, 'r'))

class Init(View):
        def __init__(self, bot):
                super().__init__()
                self.bot = bot
                # self.geedka_type = geedka_type

        @discord.ui.button(label="Begin Report", style=discord.ButtonStyle.red)
        async def callback(self, i : Interaction, item):
                await i.response.send_message("Hello")

async def get_bot(bot, message):
        # geedka_type = geedka_init(bot, "config.geedka")
        return await message.channel.send(content="Welcome to Geedka", \
                view=Init(bot))

