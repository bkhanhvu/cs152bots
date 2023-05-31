import os
import discord
import typing
from typing import Optional
from label_provider import LabelProvider

# TYPE ALIASES
File            : typing.TypeAlias = typing.TextIO
Interaction     : typing.TypeAlias = discord.Interaction
Embed           : typing.TypeAlias = discord.Embed
Selection       : typing.TypeAlias = discord.SelectOption
# END TYPE ALIASES

lp = LabelProvider()

def class_and_filename(label : int) -> tuple[str, str]:
        return [f'geedka_impl_class{label}', \
                f'geedka_impl_class{label}.py']

def write_class_def_to_file(filename : str, content : str) -> None:
        with open(filename, 'w') as writer:
                writer.write(content)

# TODO: make this not shit
def terminal_gen(label : int) -> None:
        classname, filename = class_and_filename(label)

        write_class_def_to_file(filename, \
        f"\
import discord\n\
\n\
class {classname}(discord.ui.View):\n\
        def __init__(self):\n\
                super().__init__()\n\
                self.description = \"This Geedka moderation flow has been completed\"\
")

def message_gen(config : File, tokens : list[str], label : int) \
        -> None:

        classname, filename = class_and_filename(label)
        child_label : int = lp.get_label()
        child_classname, child_filename = \
                class_and_filename(child_label)

        write_class_def_to_file(filename, \
        f"\
import discord\n\
from {child_classname} import {child_classname} \n\
\n\
class {classname}(discord.ui.View):\n\
        def __init__(self):\n\
                super().__init__()\n\
                self.description = \"{tokens[0]}\"\n\
\n\
        @discord.ui.button(label=\"Continue\", \\\n\
                style = discord.ButtonStyle.red) \n\
        async def callback(self, interaction : discord.Interaction, button): \n\
                await interaction.response.send_message(\"Continuing\", \\\n\
                view={child_classname}())\
        ")

        geedka_frontend(config, child_label)
        
def get_dropdown_options(elems : list[str]) -> list[Selection]:
        return [Selection(label=l) for l in elems]

def geedka_frontend(config : File, label : int = lp.get_label()):
        # This is some sorcery I found on stack overflow
# https://stackoverflow.com/questions/10140281/how-to-find-out-whether-a-file-is-at-its-eof
#        while config.tell() != os.fstat(config.fileno()).st_size:
# TODO: figure out a way to render multiple elements that aren't directly connected
        tokens : list[str] = config.readline().strip().split('|')
        match tokens[0]:
                case 'm':
                        return message_gen(config, tokens[1:], \
                                label)
                case 's':
                        raise Exception("Not implemented")
                case 'w':
                        raise Exception("Not implemented")
                case 't':
                        return terminal_gen(label)
                case _:
                        raise Exception("Unknown node type passed")


def main():
        print("Hello world")
        config_filename : str = 'hello.geedka'
        if not os.path.isfile(config_filename):
                raise Exception(f"{config_filename} not found!")

        return geedka_frontend(open(config_filename, 'r'))

if __name__=='__main__':
        main()

