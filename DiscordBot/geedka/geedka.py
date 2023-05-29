import os
import discord
import typing

# TYPE ALIASES
File = typing.TextIO
Interaction = discord.Interaction
Button = discord.ui.Button
View = discord.ui.View
Embed = discord.Embed
# END TYPE ALIASES

def message_impl(bot, config : File, tokens : list[str]) -> Embed:
        class MessageImpl(Embed):
                def __init__(self):
                        super().__init__()
                        self.bot = bot
                        self.description = tokens[0].strip()
                        self.title = "Welcome to Geedka"

        return MessageImpl
        

def geedka_frontend(bot, config : File):
        tokens : list[str] = config.readline().split('|')
        match tokens[0]:
                case 'm':
                        return message_impl(bot, config, tokens[1:])
                case 's':
                        raise Exception("Not implemented")
                case 'w':
                        raise Exception("Not implemented")
                case 't':
                        raise Exception("Not implemented")
                case _:
                        raise Exception("Unknown node type passed")


def get_bot(bot, config_filename : str):
        if not os.path.isfile(config_filename):
                raise Exception(f"{config_filename} not found!")

        return geedka_frontend(bot, open(config_filename, 'r'))()

