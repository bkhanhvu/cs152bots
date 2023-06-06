import os
import discord
import typing
from typing import Optional
from label_provider import LabelProvider
from dataclasses import dataclass

# TYPE ALIASES
File    : typing.TypeAlias = typing.TextIO
# END TYPE ALIASES
lp = LabelProvider()

def classname_from_label(label : int) -> str:
        return f'geedka_impl_class{label}'

def class_and_filename(label : int) -> tuple[str, str]:
        return [classname_from_label(label), f'{classname_from_label(label)}.py']

def write_class_def_to_file(filename : str, content : str) -> None:
        with open(filename, 'w') as writer:
                writer.write(content)

def get_embed_addfield(key : str, val : str) -> str:
        return f"""
                impl_embed.add_field(name = \"{key}\", value = \"{val}\")
        """

def get_embed_gen(description : str) -> str:
        embed_elements : list[str] = [elem.strip() for elem in description.split("\\")]
        embed_specific : list[list[str]] = []
        for elem in embed_elements:
                inner_list : list[str] = [x for x in elem.strip().split('^')]
                embed_specific += [inner_list]

        embed_addfields : str = '\n'.join([get_embed_addfield(l[0], l[1]) for l in embed_specific])
        return f"""
                impl_embed = discord.Embed()

{embed_addfields}
        """

# TODO: make this not shit
def terminal_gen(label : int) -> None:
        classname, filename = class_and_filename(label)

        write_class_def_to_file(filename, \
        f"""
import discord
import asyncio

class {classname}(discord.ui.View):
        @classmethod
        async def create(cls, i : discord.Interaction, ticket : dict[str, str]):
                resulting_ticket = discord.Embed()
                [resulting_ticket.add_field(name=key, value=val) for key, val in ticket.items()]
                resulting_ticket.title = \"Your Report\"
                resulting_ticket.set_author(name=\"Geedka\")
                # This isn't necessary but it makes me happy.
                resulting_ticket.set_thumbnail(url=\"https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Adansonia_grandidieri04.jpg/1200px-Adansonia_grandidieri04.jpg\")
                await i.channel.send(embed = resulting_ticket)
                return None

        def __init__(self):
                super().__init__()
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

class {classname}(discord.ui.View):
        @classmethod
        async def create(cls, i : discord.Interaction, ticket : dict[str, str] = {{}}):
{get_embed_gen(tokens[0])}
                await i.channel.send(embed=impl_embed)
                child = await {child_classname}.create(i, ticket)
                
                return child


        def __init__(self):
                super().__init__()
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

def get_button_def(tag : str, text : str, label : int) -> str:
        return f"""
        @discord.ui.button(label=\"{text}\", style=discord.ButtonStyle.red)
        async def callback{text.replace(" ", "_")}{label}(self, interaction : discord.Interaction, button):
                self.ticket[\"{tag}\"] = \"{text}\"
                await interaction.channel.send(\"You selected {text}\")
                child = await {classname_from_label(label)}.create(interaction, self.ticket)

                if child != None:
                        await interaction.channel.send(view = child)
                try:
                        if not interaction.response.is_done():
                                await interaction.response.defer()
                except:
                        return
        """

def switch_gen(config : File, tokens : list[str], label : int) -> None:
        child_names : list[str] = get_child_names(config)
        button_impl(config, tokens, label, child_names)

def yn_gen(config : File, tokens : list[str], label : int) -> None:
        button_impl(config, tokens, label, ["Yes", "No"])

def button_impl(config : File, tokens : list[str], label : int, \
        child_names : list[str]) -> None:

        response_tag : str = tokens[0]
        message_spec : str = tokens[2]
        data_collect : bool = tokens[1] == 'd'

        classname, filename = class_and_filename(label)

        child_labels : list[int] =  [lp.get_label()] * len(child_names) \
                if data_collect else [lp.get_label() for _ in child_names]

        child_buttons : list[str] = [get_button_def(response_tag, n, l) for n, l \
                in zip(child_names, child_labels)]

        import_statement : str = get_import_statement(child_labels[0]) \
                if data_collect else ''.join(get_imports(child_labels)) 

        write_class_def_to_file(filename, \
        f"""
import discord 
import asyncio 
{import_statement} 

class {classname}(discord.ui.View):
        @classmethod
        async def create(cls, i : discord.Interaction, ticket : dict[str, str] = {{}}): 
{get_embed_gen(message_spec)}
                await i.channel.send(embed=impl_embed)
                self = {classname}(ticket)
                return self

        def __init__(self, ticket):
                super().__init__()
                self.ticket = ticket

{''.join(child_buttons)} 
""")

        if data_collect:
                geedka_frontend(config, child_labels[0])
        else:
                [geedka_frontend(config, l) for l in child_labels]

        
def get_case(name : str, label : int) -> str:
        return f"""
                        case \"{name}\":
                                child = await geedka_impl_class{label}.create(interaction, self.ticket)
                                if (child != None):
                                        await interaction.channel.send(view=child)
        """

def get_cases(child_names : list[str], child_labels : list[int]) -> str:
        return "\n".join([get_case(n, l) for n, l in \
                zip(child_names, child_labels)])

def select_gen(config : File, tokens : list[str], label : int) -> None:
        
        response_tag : str = tokens[0]
        message_spec : str = tokens[2]
        data_collect : bool = tokens[1] == 'd'

        classname, filename = class_and_filename(label)
        child_names : list[str] = get_child_names(config)
        child_labels : list[int] = [lp.get_label()] * len(child_names) \
                if data_collect else [lp.get_label() for _ in child_names]

        child_case_handling : str = f"""
                child = await geedka_impl_class{child_labels[0]}.create(interaction, self.ticket)
                if (child != None):
                        await interaction.channel.send(view=child)
        """ \
        if data_collect else \
        f"""
                match selection.values[0]:
{get_cases(child_names, child_labels)}
        """

        imports : str = get_import_statement(child_labels[0]) \
                if data_collect else ''.join(get_imports(child_labels)) 
        # TODO: get better ticket labeling
        
        write_class_def_to_file(filename, \
        f"""
import discord 
import asyncio 
{imports}

def get_dropdown_options(elems : list[str]) -> list[discord.SelectOption]:
        return [discord.SelectOption(label=l, description="Description") \\
                for l in elems]

class {classname}(discord.ui.View):
        @classmethod
        async def create(cls, i : discord.Interaction, ticket : dict[str, str] = {{}}): 
{get_embed_gen(message_spec)}
                await i.channel.send(embed=impl_embed)
                self = {classname}(ticket)
                return self

        def __init__(self, ticket : dict[str, str]):
                super().__init__()
                self.ticket = ticket
        
        @discord.ui.select(placeholder=\"Select one\", \\
                options=get_dropdown_options({child_names}))
        async def select_callback(self, interaction : discord.Interaction,
                selection : discord.ui.Select):
                self.ticket[\"{response_tag}\"] = selection.values[0]
                await interaction.channel.send( \\
                        f\"You selected {{selection.values[0]}}\")
{child_case_handling}

                try:
                        if not interaction.response.is_done():
                                await interaction.response.defer()
                except:
                        return
                        
        """)

        if data_collect:
                geedka_frontend(config, child_labels[0])
        else:
                [geedka_frontend(config, l) for l in child_labels]

def get_input_label(name : str) -> str:
        return f"""
                self.add_item(discord.ui.TextInput(label=\"{name}\"))
        """

def get_input_labels(options : list[str]) -> str:
        return "\n".join([get_input_label(o) for o in options])

def get_modal_ticket_saves(names : list[str]) -> str:
        return "\n".join([f"""
                self.ticket[\"{name}\"] = self.children[{index}].value
        """ for index, name in enumerate(names)])

def modal_gen(config : File, tokens : list[str], label) -> None:
        options : list[str] = get_child_names(config)
        classname, filename = class_and_filename(label)
        child_label : int = lp.get_label()
        child_classname : str = classname_from_label(child_label)
        
        geedka_frontend(config, child_label)

        write_class_def_to_file(filename, \
        f"""
import discord 
import asyncio 
from {child_classname} import {child_classname}

class ModalImpl(discord.ui.Modal):
        def __init__(self, ticket : dict[str, str]):
                super().__init__(title = \"{tokens[0]}\")
                self.ticket = ticket
{get_input_labels(options)}

        async def on_submit(self, interaction : discord.Interaction):
                {get_modal_ticket_saves(options)}
                child = await {child_classname}.create(interaction, self.ticket)
                if child != None:
                        await interaction.channel.send(view = child)
                self.stop()
                
class {classname}(discord.ui.View):
        @classmethod
        async def create(cls, i : discord.Interaction, ticket : dict[str, str]): 
                child = ModalImpl(ticket)
                await i.response.send_modal(child)
                await child.wait()
                return None

        def __init__(self):
                super().__init__()

""")


def geedka_frontend(config : File, label : int = -1):
# TODO: figure out a way to render multiple elements that aren't directly connected
        if (label == -1):
                label = lp.get_label()
        tokens : list[str] = config.readline().strip().split('|')
        match tokens[0]:
                case 'm':
                        return message_gen(config, tokens[1:], label)
                case 's':
                        return select_gen(config, tokens[1:], label)
                case 'w':
                        return switch_gen(config, tokens[1:], label)
                case 'y':
                        return yn_gen(config, tokens[1:], label)
                case 'i':
                        return modal_gen(config, tokens[1:], label)
                case 't':
                        return terminal_gen(label)
                case _:
                        error_message = f"Unknown node type {tokens[0]} passed"
                        raise Exception(error_message)

def main():
        print("Hello world")
        config_filename : str = 'config.geedka'
        if not os.path.isfile(config_filename):
                raise Exception(f"{config_filename} not found!")

        return geedka_frontend(open(config_filename, 'r'))

if __name__=='__main__':
        main()

