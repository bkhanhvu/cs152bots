import discord
from ticket import Ticket, tickets
from userStatus import UserStatus, userStatuses

blacklist = set()

ExplicitTicket = Ticket
NonExplicitTicket = Ticket 

# =========== TYPE ALIASES ==============
Interaction = discord.Interaction
Button = discord.ui.Button
# ========= END TYPE ALIASES ===========

# TODO: Implement functionality to Complete ticket, update status in ticket database and forward progress 
# to requester of ticket

class ModMenuButtons(discord.ui.View):
    def __init__(self, bot, tid):
        super().__init__()
        self.bot = bot
        self.tid = tid

    @discord.ui.button(label="Approve User Label", style=discord.ButtonStyle.red)
    async def approveBtn(self, interaction: Interaction, button:Button):

        action_embed = discord.Embed(title=f'Approved label for ticket: {self.tid}.',
                              description='Please proceed by choosing action toward reported user.')
        action_embed.add_field(name='Ban User', value='User and associated IP will be permanently removed from guild', inline=False)
        action_embed.add_field(name='Mute User', value='User will temporarily have all permissions revoked.', inline=False)
        action_embed.add_field(name='Kick User', value='User will be removed from guild/channel and can only rejoin by invite.', inline=False)
        action_embed.add_field(name='Warn User', value='User will be warned of their behavior. If this is a re-offense, the user will be kicked.', inline=False)

        await interaction.response.send_message(embed=action_embed, view=ConsequenceActionButtons(self.bot, self.tid))
        # await interaction.response.send_message(embed=embed,
        #                                         view=ConsequenceActionButtons(self.bot, self.tid))
    
    @discord.ui.button(label="Disapprove User Label", style=discord.ButtonStyle.red)
    async def disapproveBtn(self, interaction: Interaction, button:Button):
        #TODO: implement dismissal of ticket
        user = self.bot.get_user(tickets[self.tid].msg_user_id)
    
    @discord.ui.button(label="Escalate Ticket", style=discord.ButtonStyle.red)
    async def escalateBtn(self, interaction: Interaction, button:Button):
        #TODO: Change Progress of ticket to Escalated to Management     

        await interaction.response.send_message('')

# TODO: Implement consequence verdict message forwarding to the user who violated 
# Create embed/modal/etc. to allow user to appeal verdict

class ConsequenceActionButtons(discord.ui.View):
    def __init__(self, bot, tid):
        super().__init__()
        self.bot = bot
        self.tid = tid

    def getUserFromTicket(self, interaction: Interaction):
        guild_id = interaction.client.guilds[0].id
        guild = interaction.client.get_guild(guild_id)

        username = str(tickets[self.tid].msg_user_id)
        usernameParts = username.split('#')
        user = discord.utils.get(guild.members, name=usernameParts[0], discriminator=usernameParts[1])
        return user

    
    @discord.ui.button(label="Ban User", style=discord.ButtonStyle.red)
    async def callbackBtn(self, interaction: Interaction, button:Button):
        username = str(tickets[self.tid].msg_user_id)
        user = self.getUserFromTicket(interaction)
        if user is not None:
            if username not in userStatuses:
                userStatuses.update({username : UserStatus()})
            # Instead of actually banning the user, log that they've been banned...
            userStatuses[username].isBanned = True
            # ...and send them a message
            message = "This message being sent to you indicates that you've been banned."
            tickets[self.tid].status = 'Complete'
            await user.send(content=message, embed=AbuserSummaryEmbed(self.tid, button))
            await interaction.response.send_message(f"Banned {username} from server.\n Ticket {self.tid} is marked as: Complete.")
        else:
            await interaction.response.send_message("No User Specified.")
    
    # # Temporarily revoke all permissions 
    # @discord.ui.button(label="Mute User", style=discord.ButtonStyle.red)
    # async def callback1Btn(self, interaction: Interaction, button:Button):
    #     # TODO: Implement button to revoke all channels permission for user
    #     # Use msg_user_id field of Ticket()

    #     await interaction.response.send_message("\n",
    #                                             view=None)
    
    @discord.ui.button(label="Kick User", style=discord.ButtonStyle.red)
    # TODO: Kick user from channel -- don't need to actually 
    async def callback2Btn(self, interaction: Interaction, button:Button):
        username = str(tickets[self.tid].msg_user_id)
        user = self.getUserFromTicket(interaction)

        message = "[ATTENTION] You have been kicked from the channel for an inappropriate action/behavior."
        tickets[self.tid].status = 'Complete'
        await user.send(content=message, embed=AbuserSummaryEmbed(self.tid, button))

        if user is not None:
            if username not in userStatuses:
                status = UserStatus()
                status.prevKicked = True
                userStatuses.update({username : status})
        await interaction.response.send_message(f"{tickets[self.tid].msg_user_id} has been kicked from server.\n Ticket {self.tid} is marked as: Complete.")
        
        
    @discord.ui.button(label="Warn User", style=discord.ButtonStyle.red)
    async def callback3Btn(self, interaction: Interaction, button:Button):
        username = str(tickets[self.tid].msg_user_id)
        user = self.getUserFromTicket(interaction)

        if user is not None:
            if username not in userStatuses:
                userStatuses.update({username : UserStatus()})

            strikeCount = userStatuses[username].strikeCounter + 1

            # TODO: write real message
            message = "[WARNING] You have been reported for an inappropriate action/behavior. \nYou now have " + str(strikeCount) + " strikes."
            tickets[self.tid].status = 'Complete'
            await user.send(content=message, embed=AbuserSummaryEmbed(self.tid, button))
            userStatuses[username].strikeCounter = strikeCount
            await interaction.response.send_message(f"Warning message sent to {username}. \n Ticket {self.tid} is marked as: Complete. ")
            return

        await interaction.response.send_message("\n",
                                                view=None)
        
abuser_fields = ['reason', 'sextortion_content', 'message_link', 'post_explicit', 'message']
class AbuserSummaryEmbed(discord.Embed):
    def __init__(self, tid, button:discord.Button):
        super().__init__(title=f'Summary of Report Ticket {tid}', description=f"We have received a report about your engagement in a prohibited action/behavior. This message is serves as confirmation for the completion of investigation and verdict. \nPlease see the report summary below for more details. \n \
                         If you would like to petition this ticket, please contact one of our channel moderators for help.")
        self.add_field(name='Status', value=tickets[tid].status, inline=False)
        tickets[tid].verdict = button.label
        self.add_field(name='Verdict', value=tickets[tid].verdict, inline=False)
        for key, value in tickets[tid]:
            if key in abuser_fields:
                self.add_field(name=key, value=value)





    

