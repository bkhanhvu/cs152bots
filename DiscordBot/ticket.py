from __future__ import annotations
import dataclasses
import discord

# =========== TYPE ALIASES ==============
Interaction = discord.Interaction
Button = discord.ui.Button
# ========= END TYPE ALIASES ===========

# TODO: some of these fields can be changed to enums
# TODO: determine if all of these fields are truly necessary. I have just copied
# the keys used but this is much redundancy, at least judging from field names.
@dataclasses.dataclass

class Ticket:
        harassment_type    : str = "" # Type of harassment
        image_owner        : str = "" # "Are these images of you or someone else?""
        know_image         : str = "" # "Do you know what images this user has?"
        know_other         : str = "" # "Do you know this other person?"
        know_responsible   : str = "" # "Do you know the user responsible?""
        message_link       : str = "" # Link of message reported
        other_username     : str = "" # "Do you know this other person?" > "Yes" > "Enter Username"
        post_explicit      : str = "" # "Did the user post an explicit image?"
        reason             : str = "" # "Please select reason for reporting this content"
        sextortion_content : str = "" # "Sextortion - Select Type of Content
        shared_explicit    : str = "" # "Have you shared explicit images with this user?"
        status             : str = "" # Status of ticket: In Progress, Complete, Elevated
        user_id_requester  : str = "" # user_id of individual who initiated and sent ticket
        msg_user_id        : str = "" # user_id of user who sent message being reported
        message            : str = "" # message being reported
        type               : str = "Manual" # Automated or Manual
        bot_msg            : discord.Message = None # Message sent by bot after message has been flagged
        hash_attachment    : str = "" # contain attachments?

        def __iter__(self):
                return iter([(f.name, getattr(self, f.name)) \
                        for f in dataclasses.fields(self) \
                        if getattr(self, f.name) != ""])
                
        def __getitem__(self, key):
                return getattr(self, key)

        def __setitem__(self, key, value):
                setattr(self, key, value)
                

tickets : dict[int, Ticket] = {}