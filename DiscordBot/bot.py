# bot.py
import discord
import uuid
# import imagehash
from PIL import Image
from discord.ext import commands
import os
import time
import json
import logging
import asyncio
import re
import requests
from report import Report
import pdb
import mainMenu
from myModal import MyModal
from reportButton import ReportButton
import os
import openai
import requests
import json
from ticket import Ticket, tickets, Interaction, Button
from apikeys import TISANE_KEY, OPENAI_KEY
# from apikeys import OPENAI_ORGANIZATION
from googleapi_detection import detect_label_safe_search_uri 

# const { EmbedBuilder } = require.('discord.js')
# Set up logging to the console
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# There should be a file called 'tokens.json' inside the same folder as this file
token_path = 'tokens.json'
if not os.path.isfile(token_path):
    raise Exception(f"{token_path} not found!")
with open(token_path) as f:
    # If you get an error here, it means your token is formatted incorrectly. Did you put it in quotes?
    tokens = json.load(f)
    discord_token = tokens['discord']

class ModBot(commands.Bot):
    def __init__(self): 
        intents = discord.Intents.default()
        intents.members = True # Need this to be able to send DMs to users in the guild
        intents.message_content = True
        super().__init__(command_prefix='.', intents=intents)
        self.group_num = None
        self.mod_channels = {} # Map from guild to the mod channel id for that guild
        self.non_mod_text_channels = {}
        self.reports = {} # Map from user IDs to the state of their report
    
    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord! It is these guilds:')
        for guild in self.guilds:
            
            print(f' - {guild.name}')
        print('Press Ctrl-C to quit.')   
        

        # Parse the group number out of the bot's name
        match = re.search('[gG]roup (\d+) [bB]ot', self.user.name)
        if match:
            self.group_num = match.group(1)
        else:
            raise Exception("Group number not found in bot's name. Name format should be \"Group # Bot\".")

        # Find the mod channel in each guild that this bot should report to
        for guild in self.guilds:
            for channel in guild.text_channels:
                if channel.name == f'group-{self.group_num}-mod':
                    self.mod_channels[guild.id] = channel
                if channel.name == f'group-{self.group_num}':
                    self.non_mod_text_channels[guild.id] = channel
                
        
        # print(self.guilds[0].id)
        # print(f"mod channels = {self.mod_channels}")
        

    async def on_message(self, message):
        '''
        This function is called whenever a message is sent in a channel that the bot can see (including DMs). 
        Currently the bot is configured to only handle messages that are sent over DMs or in your group's "group-#" channel. 
        '''

        # Need to check whether message contains an image and compare to anything stored in hash database - Emily
        # if message.attachments: # TODO: @Emily I was getting errors about this line and False and'ed it out -- Matthew
        #     attach = message.attachments[0]
        #     hash = imagehash.average_hash(Image.open(attach.fp))

        # Ignore messages from the bot 
        if message.content.startswith('.'):
            await self.process_commands(message)

        # Ignore any messages that start with !
        # if message.content[0] == "!":
        #     return

        if message.author.id == self.user.id:
            return

        # Check if this message was sent in a server ("guild") or if it's a DM
        if message.guild:
            await self.handle_channel_message(message)
        else:
            await self.handle_dm(message)

    async def handle_dm(self, message):
        # Handle a help message
        # if message.content == Report.HELP_KEYWORD:
        #     view = SelectMenu()

        #     await message.channel.send(view=view)

            # reply =  "Use the `report` command to begin the reporting process.\n"
            # reply += "Use the `cancel` command to cancel the report process.\n"
            # await message.channel.send(reply)
            # return

        author_id = message.author.id
        responses = []

        # Only respond to messages if they're part of a reporting flow
        if author_id not in self.reports and not message.content.startswith(Report.START_KEYWORD):
            return

        # If we don't currently have an active report for this user, add one
        if author_id not in self.reports:
            self.reports[author_id] = Report(self)

        # Let the report class handle this message; forward all the messages it returns to uss
        responses = await self.reports[author_id].handle_message(message)
        for r in responses:
            await message.channel.send(r)

        # If the report is complete or cancelled, remove it from our map
        if self.reports[author_id].report_complete():
            self.reports.pop(author_id)

    async def handle_channel_message(self, message: discord.Message):
        # Only handle messages sent in the "group-#" channel
        if not message.channel.name == f'group-{self.group_num}':
            return

        if message.attachments:
            url = message.attachments[0].url
            print(f"url={url}")
            embed = discord.Embed(title = ' __Image Abuse Detection__', description='*### Reporting image labels and abuse detection.*')

            safe_search, labels = await detect_label_safe_search_uri(url)
            print(f"url={url}")
            print('Labels:')
            label_str = ''
            for label in labels:
                label_str += f'> description = {label.description}, score = {label.score}\n'
                print(label.description)

            safe_search_str = ''
            flagged = False
            print('Safe search:')
            for key, value in safe_search.items():
                if value not in ['UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY'] and not flagged:
                    embed.color = discord.Color.red() 
                    flagged = True
                    safe_search_str += f'> content = __{key}__, likelihood = **{value}**\n'
                else:
                    safe_search_str += f'> content = {key}, likelihood = {value}\n'

                print(f"{key}: {value}")
                
            if not flagged:
                embed.color = discord.Color.green()
            else:
                file_spoiler = f"||{url}||"
                time.sleep(1)
                message_str = "*This message has been flagged for abused and has been removed.* \n"
                await message.reply(message_str)
                await message.delete()
            
                embed.set_thumbnail(url='https://community.appinventor.mit.edu/uploads/default/2ad031bc25a55c4d3f55ff5ead8b2de63cdf28bf')

                embed.add_field(name='username', value=str(f'`{message.author.name}`'), inline=True)
                embed.add_field(name='flagged', value=str(f'`{flagged}`'), inline=False)
                embed.add_field(name='Labels', value=label_str)
                embed.add_field(name='Safe Search', value=safe_search_str)
                embed.add_field(name='Image URL', value=url, inline=False)
            
                await self.process_automatic_ticket(message, None, True, [embed])
                
            return
                # await mainMenu.send_completionEmbed(None, self, tid, embed=embed)

            
        if message.content == "trigger":
            print("Tripped the message detector!")
            view = mainMenu.MainMenuButtons(self, self.mod_channels[message.guild.id])
            embed = mainMenu.MainMenuEmbed()

            # await message.channel.send("Click this button to report the message above", view=ReportButton())
            await message.channel.send(embed=embed, view=view)
            return
            # await interaction.response.send_modal(MyModal())
        # Forward the message to the mod channel
        mod_channel = self.mod_channels[message.guild.id]
        # await mod_channel.send(f'Forwarded message:\n{message.author.name}: "{message.content}"')
        # response = self.process_text_tisane(message.content) if 'tisane' in message.content else self.eval_text(message.content)
        # print(response)
        
        # openaiCheck = message.content[0:6]
        flags = {'tisane_flagged': False, 'openaimod_flagged': False, 'chatgpt_flagged': False}
        responses = {'tisane': None, 'openaimod': None, 'chatgpt': None}
        embeds = []
        tisane_response = self.process_text_tisane(message.content)
        responses['tisane'] = tisane_response
        if 'abuse' in tisane_response:
            for abuse in tisane_response['abuse']:
                    if abuse['severity'] in ['medium', 'high', 'extreme']:
                        flags['tisane_flagged'] = True
                        embeds.append(await self.code_format(tisane_response, message, tisane=True, openAiChatCompletion=False, openAiModerator=False))
                        break
        
        # if 'tisane' in message.content:
        #     response = self.process_text_tisane(message.content)
        #     await self.code_format(response, message, tisane=True, openAiChatCompletion=False)
        
        # openai_mod evaluation
        openaimod_response = self.eval_text(message.content)
        responses['openaimod'] = openaimod_response

        # openaimod_flagged = False
        for category, score  in openaimod_response['category_scores'].items():
            if score > 0.05:
                flags['openaimod_flagged'] = True
                embeds.append(await self.code_format(openaimod_response, message, tisane=False, openAiChatCompletion=False, openAiModerator=True))
                break
        
        #chatgpt sextortion check
        chatgpt_response = int(self.openai_completion_eval_text(message.content))
        responses['chatgpt'] = chatgpt_response
        autoBanned = False
        autoKicked = False
        if chatgpt_response > 19 and chatgpt_response != 101:
            flags['chatgpt_flagged'] = True
            if chatgpt_response > 80:
                await message.author.send('*** ALERT: __You have been banned from the server.__ ***')
                autoBanned = True
            else:
                await message.author.send('*** ALERT: __You have been kicked from the server.__ ***')
                autoKicked = True
            
            embeds.append(await self.code_format(chatgpt_response, message, tisane=False, openAiChatCompletion=True, openAiModerator=False))
        
        if True in flags.values():
            message_str = "*This message has been flagged for abuse* \n" + f"**{message.author.name}**:" + "||" + str('```') + \
                f'{message.content}\n' + str('```') + "||"
            
            bot_message = await message.reply(message_str)
            await message.delete()
            await message.author.send(embeds=embeds)
            
            # time.sleep(1)
            # await bot_message.delete()

        # if chatgpt_flagged or openaimod_flagged or tisane_flagged:
        #     await self.process_automatic_ticket(message)
        
        # elif openaiCheck == 'openai':
        #     # Misleading -- this is chatgpt, not the openai API
        #     realMessage = message.content[7:]
        #     response = self.openai_completion_eval_text(realMessage)
        #     await self.code_format(response, message, tisane=False, openAiChatCompletion=True)
        # else:
        #     # self.eval_text(message.content)
        #     response = self.eval_text(message.content)
        #     await self.code_format(response, message, tisane=False, openAiChatCompletion=False)
        # print(response_formatted)
        # await message.channel.send(response_formatted['verdict'], embed=response_formatted['embed'])
            await self.process_automatic_ticket(message, bot_message, autoBanned=autoBanned, autoKicked=autoKicked)
    
    async def process_automatic_ticket(self, message:discord.Message, bot_message, image=False, embeds=None, autoBanned=False, autoKicked=False):
        embeds = embeds if embeds else []
        tid = uuid.uuid4()
        ticket = Ticket()
        tickets[tid] = ticket
        ticket.message = message.attachments[0].url if image else '||' + message.content + '||'
        ticket.msg_user_id = message.author
        ticket.status = 'Pending'
        ticket.type = 'Automated'
        ticket.bot_msg = bot_message
        
        embed=await mainMenu.create_completionEmbed(self, tid)
        embed.color = discord.Color.red()

        explicit_warning = str("""```css\n**[Explicit Warning!]** \nWe've detected content that could be harmful or disturbing! Please act with caution.```""")
        embed.description = explicit_warning
        # for key, value in tickets[tid]:
        #     print(key, value)
        #     if key == 'status' or 'type':
        #         continue
        
            # embed.add_field(name=key, value=value)
        embeds.append(embed)
        await mainMenu.send_completionEmbed(None, self, tid, embeds=embeds, autoBanned=autoBanned, autoKicked=autoKicked)
        # await mod_channel.send('Message has been flagged and is awaiting review.', embed=embed, )
        
        
        
    def process_text_tisane(self, message):
        url = "https://api.tisane.ai/parse"
        msg_content = message[(message).find('tisane') + len('tisane') + 1:]
        # print(msg_content)
        payload = json.dumps({
        "language": "en",
        "content": msg_content,
        "settings": {'abuse': True, 'snippets': True, 'tags': True, 'explain': True}
        })
        headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': TISANE_KEY
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        response_dict = json.loads(response.text)
        # for key, value in response_dict.items():
        #     print(f"key={key}\nvalue={value}")

        return response_dict
    
    def openai_completion_eval_text(self, message):
        # Misleading -- this is chatgpt
        # openai.organization = OPENAI_ORGANIZATION
        openai.api_key = OPENAI_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a content moderation system tasked with moderating sextortion. Classify each input as either being a risk for sextortion or benign. Inputs tagged as being a sextortion risk will be forwarded to a human moderator team. Please respond only with a number: 0 if you are certain the content is benign, 100 if you are certain it is a risk, and numbers between scaling linearly with riskiness. Be sure not to flag conversations that only talk about sextortion, and only to flag conversations that indicate that the user sending the message is likely to be sextorting its recipient"},
                {"role": "user", "content": message}
            ]
        )
        output = response["choices"][0]["message"]["content"]
        # ChatGPT can't be trusted to always give an answer that only has a number, so find the number
        listNums = re.findall(r'\d+', output)
        if len(listNums) == 0:
            print("Couldn't find a number...")
            return 101 # For now just assume it's bad 
        else:
            print(listNums[0])
            return listNums[0]

    def eval_text(self, message):
        ''''
        TODO: Once you know how you want to evaluate messages in your channel, 
        insert your code here! This will primarily be used in Milestone 3. 
        '''
        # openai.organization = OPENAI_ORGANIZATION
        openai.api_key = OPENAI_KEY

        response = openai.Moderation.create(
            input=message,
        )
        output = response["results"][0]
        return output

    
    async def code_format(self, response, message:discord.Message, tisane:bool, openAiChatCompletion:bool, openAiModerator:bool):
        ''''
        TODO: Once you know how you want to show that a message has been 
        evaluated, insert your code here for formatting the string to be 
        shown in the mod channel. 
        '''
        flagged = False
        if tisane or openAiChatCompletion or openAiModerator:
            flagged = True
        title = 'Tisane Abuse Report' if tisane else 'OpenAI Abuse Report'
        embed = discord.Embed(title=title)

        if tisane:
            # flagged = True if 'abuse' in response else False
            embed.set_thumbnail(url='https://pbs.twimg.com/profile_images/926300904399220737/JXJgzUm5_400x400.jpg')
        elif openAiChatCompletion:
            # flagged = True if int(response) > 20 else False
            embed.set_thumbnail(url='https://static.thenounproject.com/png/2486994-200.png')
        else:
            # flagged = True if response['flagged'] else False
            embed.set_thumbnail(url='https://static.thenounproject.com/png/2486994-200.png')

        if flagged:
            embed.color = discord.Color.red()
            embed.description = str("```diff\n- This message has been flagged for abuse.```")
        else:
            embed.color = discord.Color.green()
            embed.description = str("```diff\n+ No abuse detected.```")

        embed.add_field(name='username', value=str(f'`{message.author.name}`'), inline=False)

        if tisane == False:
            if openAiChatCompletion == False:
                embed.add_field(name='message_content', value=str(f'`{message.content}`'), inline=False)
                for category, score  in response['category_scores'].items():

                    # temporary threshold of 0.5
                    score_str = str(f'__**{str(score)}**__') if (score > 0.03) else str(score)
                    
                    embed.add_field(name=category, value=score_str)
            else:
                embed.add_field(name='message_content', value=str(f'`{message.content}`'), inline=False)
                embed.add_field(name="Sextortion", value=response)
                
        else:
            embed.add_field(name='message_content', value=str(f"`{response['text']}`"), inline=False)
    

                    # print(f"type={abuse['type']}, severity={abuse['severity']}, text={abuse['text']}, explanation={abuse['text'] if 'text' in abuse else ''}")
            if 'tags' in response:
                # print(f"tags= {response['tags']}")
                embed.add_field(name='tags', value=response['tags'].join(', '))

            expi = 1
            if 'sentiment_expressions' in response:
                for sentiment_expression in response['sentiment_expressions']:
                    explanation = sentiment_expression['explanation'] if 'explanation' in sentiment_expression else ''
                    embed.add_field(name=f"expression_{expi}, sentiment = {sentiment_expression['polarity']}", \
                                    value=str(f"> text_fragment = *{sentiment_expression['text']}* \n> reason: {explanation}"), inline=False)

            if flagged:
                for abuse in response['abuse']:
                    abuse_type = abuse['type']
                    abuse_tags = ', '.join(abuse['tags']) if 'tags' in abuse else 'None'
                    abuse_explanation= abuse['explanation'] if 'explanation' in abuse else 'None'
                    abuse_value = str(f"```\nseverity={abuse['severity']}\ntext={abuse['text']}\nexplanation={abuse_explanation}\ntags={abuse_tags}```")
                    embed.add_field(name=abuse_type, value=abuse_value, inline=False)
        
        return embed
        # await message.channel.send("Abuse Detected:" "'" + str(flagged) + "'", embed=embed)
        # return {'verdict': "Abuse Detected:" "'" + str(flagged) + "'", 'embed': embed}

    

client = ModBot()

@client.command()
async def hello(ctx):
    await ctx.reply("Hello!!!")

client.run(discord_token)


