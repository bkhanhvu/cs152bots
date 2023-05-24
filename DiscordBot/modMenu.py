import discord
from ticket import Ticket, tickets

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
    
    @discord.ui.button(label="Ban User", style=discord.ButtonStyle.red)
    # TODO: Add filler message since we are not actually implementing banning
    async def callbackBtn(self, interaction: Interaction, button:Button):
        await interaction.response.send_message("\n")
    
    # Temporarily revoke all permissions 
    @discord.ui.button(label="Mute User", style=discord.ButtonStyle.red)
    async def callback1Btn(self, interaction: Interaction, button:Button):
        # TODO: Implement button to revoke all channels permission for user
        # Use msg_user_id field of Ticket()

        await interaction.response.send_message("\n",
                                                view=None)
    
    @discord.ui.button(label="Kick User", style=discord.ButtonStyle.red)
    # TODO: Kick user from channel -- don't need to actually 
    async def callback2Btn(self, interaction: Interaction, button:Button):
        await interaction.response.send_message("\n",
                                                view=None)
        
    @discord.ui.button(label="Warn User", style=discord.ButtonStyle.red)
    # TODO: Implement sending user a warning message and (possibly) creating a strike counter to track previous infringement
    async def callback3Btn(self, interaction: Interaction, button:Button):
        await interaction.response.send_message("\n",
                                                view=None)
    

