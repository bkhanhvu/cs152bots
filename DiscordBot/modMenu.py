import discord
from ticket import Ticket, tickets
from userStatus import UserStatus, userStatuses
# from bot import ModBot

blacklist = set()

ExplicitTicket = Ticket
NonExplicitTicket = Ticket 

abuser_summary_description="We have received a report about your engagement in a prohibited action/behavior. This message is serves as confirmation for the completion of investigation and verdict. Please see the report summary below for more details. \n\n \
                         If you would like to petition this ticket, please contact one of our channel moderators for help."
reporter_summary_description="We have reviewed your report request. This message is serves as confirmation for the completion of investigation and verdict. Please see the report summary below for more details. \n\n \
                         If you would like to petition this ticket, please contact one of our channel moderators for help."
# =========== TYPE ALIASES ==============
Interaction = discord.Interaction
Button = discord.ui.Button
# ========= END TYPE ALIASES ===========

# TODO: Implement functionality to Complete ticket, update status in ticket database and forward progress 
# to requester of ticket

# DEPRECATED -- Do not use
# class ModMenuButtons(discord.ui.View):
#     def __init__(self, bot, tid):
#         super().__init__()
#         self.bot = bot
#         self.tid = tid

#     @discord.ui.button(label="Approve User Label", style=discord.ButtonStyle.red)
#     async def approveBtn(self, interaction: Interaction, button:Button):

#         action_embed = discord.Embed(title=f'Approved label for ticket: {self.tid}.',
#                               description='Please proceed by choosing action toward reported user.')
#         action_embed.add_field(name='Ban User', value='User and associated IP will be permanently removed from guild', inline=False)
#         # action_embed.add_field(name='Mute User', value='User will temporarily have all permissions revoked.', inline=False)
#         action_embed.add_field(name='Kick User', value='User will be removed from guild/channel and can only rejoin by invite.', inline=False)
#         action_embed.add_field(name='Warn User', value='User will be warned of their behavior. If this is a re-offense, the user will be kicked.', inline=False)

#         await interaction.response.send_message(embed=action_embed, view=ConsequenceActionButtons(self.bot, self.tid))
#         # await interaction.response.send_message(embed=embed,
#         #                                         view=ConsequenceActionButtons(self.bot, self.tid))
    
#     @discord.ui.button(label="Disapprove User Label", style=discord.ButtonStyle.red)
#     async def disapproveBtn(self, interaction: Interaction, button:Button):
#         #TODO: implement dismissal of ticket
#         user = self.bot.get_user(tickets[self.tid].msg_user_id)
    
#     @discord.ui.button(label="Escalate Ticket", style=discord.ButtonStyle.red)
#     async def escalateBtn(self, interaction: Interaction, button:Button):
#         #TODO: Change Progress of ticket to Escalated to Management     

#         await interaction.response.send_message('')

# TODO: Implement consequence verdict message forwarding to the user who violated 
# Create embed/modal/etc. to allow user to appeal verdict

class ConsequenceActionButtons(discord.ui.View):
    def __init__(self, bot, tid):
        super().__init__()
        self.bot = bot
        self.tid = tid

    async def notifyReporterCallback(self, interaction, button):
        user = self.getUserFromTicket(interaction, reporter=True)
        await user.send("We've finished processing your report ticket.", embed=SummaryEmbed(self.tid, button, description=reporter_summary_description))

    def getUserFromTicket(self, interaction: Interaction, reporter=False):
        guild_id = interaction.client.guilds[0].id
        guild = interaction.client.get_guild(guild_id)

        if reporter is True:
            username = str(tickets[self.tid].user_id_requester)
        else:
            username = str(tickets[self.tid].msg_user_id)

        usernameParts = username.split('#')
        user = discord.utils.get(guild.members, name=usernameParts[0], discriminator=usernameParts[1])
        return user

    @discord.ui.button(label="Disapprove User Label", style=discord.ButtonStyle.gray)
    async def disapproveBtn(self, interaction: Interaction, button:Button):
        currentStatus = tickets[self.tid].status
        if currentStatus == 'Complete':
            await interaction.response.send_message(f"\nTicket {self.tid} is already marked as complete.")
        else:
            tickets[self.tid].status = 'Complete'
            await interaction.response.send_message(f"\nTicket {self.tid} dismissed, marked as: Complete.")
            await self.notifyReporterCallback(interaction, button)
    
    @discord.ui.button(label="Ban User", style=discord.ButtonStyle.red)
    async def callbackBtn(self, interaction: Interaction, button:Button):
        username = str(tickets[self.tid].msg_user_id)
        user = self.getUserFromTicket(interaction)
        if user is not None:
            alreadyComplete = (tickets[self.tid].status == 'Complete')
            if username not in userStatuses:
                userStatuses.update({username : UserStatus()})
            elif userStatuses[username].isBanned == True:
                # Relevant in case multiple reports come in about the same user
                tickets[self.tid].status = 'Complete'
                message = f"User {username} is already banned."
                if not alreadyComplete:
                    message += f"\nTicket {self.tid} is marked as: Complete."
                await interaction.response.send_message(message)
                return
            # Instead of actually banning the user, log that they've been banned...
            userStatuses[username].isBanned = True
            # ...and send them a message
            message = "This message being sent to you indicates that you've been banned."
            tickets[self.tid].status = 'Complete'
            await user.send(content=message, embed=SummaryEmbed(self.tid, button, description=abuser_summary_description))
            await self.notifyReporterCallback(interaction, button)
            message = f"Banned {username} from server."
            if not alreadyComplete:
                message += f"\nTicket {self.tid} is marked as: Complete."
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message("No User Specified.")
    
    @discord.ui.button(label="Kick User", style=discord.ButtonStyle.red)
    # TODO: Kick user from channel -- don't need to actually 
    async def callback2Btn(self, interaction: Interaction, button:Button):
        username = str(tickets[self.tid].msg_user_id)
        user = self.getUserFromTicket(interaction)

        alreadyComplete = (tickets[self.tid].status == 'Complete')
        message = "[ATTENTION] You have been kicked from the channel for an inappropriate action/behavior."
        tickets[self.tid].status = 'Complete'
        await user.send(content=message, embed=SummaryEmbed(self.tid, button, description=abuser_summary_description))
        await self.notifyReporterCallback(interaction, button)

        if user is not None:
            if username not in userStatuses:
                status = UserStatus()
            else:
                status = userStatuses[username]
            status.prevKicked = True
            userStatuses.update({username : status})
            message = f"{tickets[self.tid].msg_user_id} has been kicked from server."
            if not alreadyComplete:
                message += f"\n Ticket {self.tid} is marked as: Complete."
            await interaction.response.send_message(message)
        else:
            message = f"{tickets[self.tid].msg_user_id} not found in server. Were they kicked previously?"
            if not alreadyComplete:
                message += f"\n Ticket {self.tid} is marked as: Complete."
            await interaction.response.send_message(message)
        
    @discord.ui.button(label="Warn User", style=discord.ButtonStyle.red)
    async def callback3Btn(self, interaction: Interaction, button:Button):
        username = str(tickets[self.tid].msg_user_id)
        user = self.getUserFromTicket(interaction)

        alreadyComplete = (tickets[self.tid].status == 'Complete')

        if user is not None:
            if username not in userStatuses:
                userStatuses.update({username : UserStatus()})

            strikeCount = userStatuses[username].strikeCounter + 1

            # TODO: write real message
            message = "[WARNING] You have been reported for an inappropriate action/behavior. \nYou now have " + str(strikeCount) + " strikes."
            tickets[self.tid].status = 'Complete'
            await user.send(content=message, embed=SummaryEmbed(self.tid, button, abuser_summary_description))
            await self.notifyReporterCallback(interaction, button)

            userStatuses[username].strikeCounter = strikeCount
            message = f"Warning message sent to {username}."
            if not alreadyComplete:
                message += f"\nTicket {self.tid} is marked as: Complete."
            await interaction.response.send_message(message)
            return

        await interaction.response.send_message("\n",
                                                view=None)
        
abuser_fields = ['reason', 'sextortion_content', 'message_link', 'post_explicit', 'message']
class SummaryEmbed(discord.Embed):
    def __init__(self, tid, button:discord.Button, description):
        super().__init__(title=f'Summary of Report Ticket {tid}', description=description)
        self.add_field(name='Status', value=tickets[tid].status, inline=False)
        tickets[tid].verdict = button.label
        self.add_field(name='Verdict', value=tickets[tid].verdict, inline=False)
        for key, value in tickets[tid]:
            if key in abuser_fields:
                self.add_field(name=key, value=value)







    

