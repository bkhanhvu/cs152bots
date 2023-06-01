import os
import discord
import typing
from typing import Optional
from label_provider import LabelProvider
from dataclasses import dataclass

# TYPE ALIASES
File            : typing.TypeAlias = typing.TextIO
Interaction     : typing.TypeAlias = discord.Interaction
Embed           : typing.TypeAlias = discord.Embed
Selection       : typing.TypeAlias = discord.SelectOption
# END TYPE ALIASES

lp = LabelProvider()

def classname_from_label(label : int) -> str:
        return f'geedka_impl_class{label}'

def class_and_filename(label : int) -> tuple[str, str]:
        return [classname_from_label(label), f'{classname_from_label(label)}.py']

def write_class_def_to_file(filename : str, content : str) -> None:
        with open(filename, 'w') as writer:
                writer.write(content)

# TODO: make this not shit
def terminal_gen(label : int) -> None:
        classname, filename = class_and_filename(label)

        write_class_def_to_file(filename, \
        f"""
import discord
import asyncio

async def send_message(tc : discord.TextChannel):
        await tc.send(\"`This Geedka moderation flow has been completed`\")

class {classname}(discord.ui.View):
        def __init__(self, tc : discord.TextChannel):
                super().__init__()
                t : Task = asyncio.create_task(send_message(tc))
""")

def message_gen(config : File, tokens : list[str], label : int) -> None:
        classname, filename = class_and_filename(label)
        child_label : int = lp.get_label()
        child_classname, child_filename = \
                class_and_filename(child_label)

        write_class_def_to_file(filename, \
        f"""
import discord
import asyncio
from {child_classname} import {child_classname}

async def send_message_impl(tc : discord.TextChannel):
        await tc.send(\"{tokens[0]}\")

class {classname}(discord.ui.View):
        def __init__(self, tc : discord.TextChannel):
                super().__init__()
                t : Task = asyncio.create_task(send_message_impl(tc)) 
                asyncio.wait_for(t, None)

        @discord.ui.button(label=\"Continue reporting\", style = discord.ButtonStyle.red)
        async def callback(self, interaction : discord.Interaction, button):
                await interaction.response.send_message(\"Continuing moderation.\", \\
                view={child_classname}(interaction.channel))
        """)

        # Continue recursion
        geedka_frontend(config, child_label)

def get_child_names(config : File) -> list[str]:
        return [label.strip() for label in config.readline().strip().split('|')]

def get_import_statement(label : int) -> str:
        classname, _ = class_and_filename(label)
        return f"from {classname} import {classname}"
        
def get_imports(children : list[int]) -> list[str]:
        return [f"{get_import_statement(i)}\n" for i in children]

def get_button_def(text : str, label : int) -> str:
        return f"""
        @discord.ui.button(label=\"{text}\", style=discord.ButtonStyle.red)
        async def callback{label}(self, interaction : discord.Interaction, button):
                await interaction.response.send_message(\"You selected {text}\",
                        view={classname_from_label(label)}(interaction.channel))\n\n"""

def switch_gen(config : File, tokens : list[str], label : int) -> None:
        classname, filename = class_and_filename(label)
        child_names : list[str] = get_child_names(config)
        child_labels : list[int] = [lp.get_label() for _ in child_names]
        child_buttons : list[str] = [get_button_def(n, l) for n, l \
                in zip(child_names, child_labels)]
        
        write_class_def_to_file(filename, \
        f"""
import discord 
import asyncio 
{''.join(get_imports(child_labels))} 

async def send_message_impl(tc : discord.TextChannel):
        await tc.send(\"{tokens[1]}\")

class {classname}(discord.ui.View):
        def __init__(self, tc : discord.TextChannel): 
                super().__init__() 
                t : Task = asyncio.create_task(send_message_impl(tc)) 
                asyncio.wait_for(t, None)

{''.join(child_buttons)} 
""")

        for l in child_labels:
                geedka_frontend(config, l)
        
def get_dropdown_options(elems : list[str]) -> list[Selection]:
        return [Selection(label=l) for l in elems]

def geedka_frontend(config : File, label : int = -1):
# TODO: figure out a way to render multiple elements that aren't directly connected
        if (label == -1):
                label = lp.get_label()
        tokens : list[str] = config.readline().strip().split('|')
        match tokens[0]:
                case 'm':
                        return message_gen(config, tokens[1:], label)
                case 's':
                        raise Exception("Not implemented")
                case 'w':
                        return switch_gen(config, tokens[1:], label)
                case 't':
                        return terminal_gen(label)
                case _:
                        raise Exception("Unknown node type passed")


def main():
        print("Hello world")
        config_filename : str = 'config.geedka'
        if not os.path.isfile(config_filename):
                raise Exception(f"{config_filename} not found!")

        return geedka_frontend(open(config_filename, 'r'))

if __name__=='__main__':
        main()

