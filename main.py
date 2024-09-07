import random
import time
import requests
from highrise import BaseBot, Highrise, Position, AnchorPosition, Reaction
from highrise import __main__
from asyncio import run as arun
from emotes import Dance_Floor
import asyncio
from random import choice
import os
import json
from typing import List
from datetime import datetime, timedelta
from highrise.models import SessionMetadata
import re
from highrise.models import SessionMetadata,  GetMessagesRequest, User ,Item, Position, CurrencyItem, Reaction
from typing import Any, Dict, Union
from highrise.__main__ import *
import asyncio, random
from emotes import Emotes
from emotes import Dance_Floor
owners = ['alionardo_','enjoytech']
moderators = ['alionardo_','enjoytech']

class BotDefinition:
    
      
    def __init__(self, bot, room_id, api_token):
        self.bot = bot
        self.room_id = room_id
        self.api_token = api_token
        self.following_username = None

class Counter:
    bot_id = ""
    static_ctr = 0
    usernames = ['Alionardo_']

class Bot(BaseBot):
    continuous_emote_tasks: Dict[int, asyncio.Task[Any]] = {}  
    user_data: Dict[int, Dict[str, Any]] = {}
    continuous_emote_task = None
    cooldowns = {}  # Class-level variable to store cooldown timestamps
    emote_looping = False


    def __init__(self):
        super().__init__()
        self.load_membership()
        self.load_moderators()
        self.load_temporary_vips()
        self.following_username = None
        self.maze_players = {}
        self.user_points = {}  # Dictionary to store user points
        self.Emotes = Emotes
        self.should_stop = False
        self.announce_task = None
        #conversation id var
        self.convo_id_registry = []
       
     
      
    def load_temporary_vips(self):
        try:
            with open("temporary.json", "r") as file:
                self.temporary_vips = json.load(file)
        except FileNotFoundError:
            self.temporary_vips = {}
   
    def save_temporary_vips(self):
      with open("temporary.json", "w") as file:
          json.dump(self.temporary_vips, file)
    def load_moderators(self):
        try:
            with open("moderators.json", "r") as file:
                self.moderators = json.load(file)
        except FileNotFoundError:
            self.moderators = []

        # Add default moderators here
        default_moderators = ['alionardo_']
        for mod in default_moderators:
            if mod.lower() not in self.moderators:
                self.moderators.append(mod.lower())
       
    def load_membership(self):
     try:
        with open("membership.json", "r") as file:
            self.membership = json.load(file)
     except FileNotFoundError:
        self.membership = []
    def save_membership(self):
     with open("membership.json", "w") as file:
        json.dump(self.membership, file)

  
    def save_moderators(self):

      with open("moderators.json", "w") as file:
            json.dump(self.moderators, file)


    async def announce(self, user_input: str, message: str):
      while not self.should_stop:  
          await asyncio.sleep(6)
          await self.highrise.chat(user_input)
          await asyncio.sleep(60)
          await self.highrise.send_emote('emote-hello')

          if message.lower().startswith("-announce "):
              parts = message.split()
              if len(parts) >= 3:
                  user_input = message[len("-announce "):]
                  await self.announce(user_input, message)

    def stop_announce(self):
      self.should_stop = True
      if self.announce_task is not None:
          self.announce_task.cancel()

    async def start_announce(self, user_input: str, message: str):
      if self.announce_task is not None:
          return
      self.announce_task = asyncio.create_task(self.announce(user_input, message))

    async def on_start(self, session_metadata: SessionMetadata) -> None:
      try:
         Counter.bot_id = session_metadata.user_id
         print("Ali is booting ...")
       

         self.highrise.tg.create_task(self.highrise.walk_to(Position(3.5, 0,2.5, facing='FrontLeft')))
         self.load_temporary_vips()
         self.load_moderators()
         await asyncio.sleep(10)
         await self.highrise.chat(f"Deployed")
        
      except Exception as e:
          print(f"An exception occured: {e}")  
    async def on_emote(self, user: User ,emote_id : str , receiver: User | None )-> None:
      print (f"{user.username} , {emote_id}")
    async def on_user_leave(self, user: User) -> None:
        if user.id in self.dancer:
                self.dancer.remove(user.id)
    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:

      try:
            title = ""
            if user.username in self.membership:
                title = self.get_title(user.username, self.membership[user.username]["amount"])
                await self.highrise.send_whisper(user.id, f"\nThe {title} {user.username} in the house!\n Welcome to Club Genesis\n• !list or -list :To discover our room.")
                await self.highrise.send_emote('emote-salute')
            elif user.username in moderators:
                 title = "Owners member"
                 await self.highrise.send_whisper(user.id, f"\nThe {title} :{user.username} in the house!")
                 await self.highrise.send_emote('emote-salute')
            elif user.username in self.moderators:
                 title = "MOd member"
                 await self.highrise.send_whisper(user.id, f"\nThe {title} :{user.username} in the house!")
                 await self.highrise.send_emote('emote-salute')
            else :
                await self.highrise.send_whisper(user.id, f"\nHello {user.username},\nWelcome to  Club Genesis\n• !list or -list :To discover our room.")
          
      except Exception as e:
            print(f"An error on user_on_join: {e}")
    
    async def teleport_user_next_to(self, target_username: str, requester_user: User):
      room_users = await self.highrise.get_room_users()
      requester_position = None

      for user, position in room_users.content:
        if user.id == requester_user.id:
            requester_position = position
            break
      for user, position in room_users.content:
        if user.username.lower() == target_username.lower(): 
          z = requester_position.z 
          new_z = z + 1 

          user_dict = {
            "id": user.id,
            "position": Position(requester_position.x, requester_position.y, new_z, requester_position.facing)
          }
          await self.highrise.teleport(user_dict["id"], user_dict["position"])

   
  
    async def run(self, room_id, token):
        definitions = [BotDefinition(self, room_id, token)]
        await __main__.main(definitions) 
 
    def remaining_time(self, username):
        if username in self.temporary_vips:
            remaining_seconds = self.temporary_vips[username] - int(time.time())
            if remaining_seconds > 0:
                return str(timedelta(seconds=remaining_seconds))
        return "Not a temporary VIP."


    async def on_chat(self, user: User, message: str) -> None:
      try:
         user_input = None
         print(f"{user.username} said: {message}")     
         if message.lower().startswith("-announce ") and user.username.lower() in moderators:
           parts = message.split()
           self.should_stop = None
           if len(parts) >= 3:
               user_input =  message[len("-announce "):]
               await self.highrise.chat("Alright i will loop this message with intervals of 60 seconds.")
               await self.announce(user_input,message)
         if message.lower().startswith("-clear") :
            if user.username.lower() in moderators:
               await self.highrise.chat (f"Announcement message cleared")
               self.stop_announce()
               return
                
         if message.startswith("❤️ all"):
           if user.username.lower() in self.moderators:
             roomUsers = (await self.highrise.get_room_users()).content
             for roomUser, _ in roomUsers:
                await self.highrise.react("heart", roomUser.id)
         if message.startswith("!kick"):
            if user.username.lower() in self.moderators:
                parts = message.split()
                if len(parts) < 2:
                    await self.highrise.chat(user.id, "Usage: !kick @username")
                    return

                mention = parts[1]
                username_to_kick = mention.lstrip('@')  # Remove the '@' symbol from the mention
                response = await self.highrise.get_room_users()
                users = [content[0] for content in response.content]  # Extract the User objects
                user_ids = [user.id for user in users]  # Extract the user IDs

                if username_to_kick.lower() in [user.username.lower() for user in users]:
                    user_index = [user.username.lower() for user in users].index(username_to_kick.lower())
                    user_id_to_kick = user_ids[user_index]
                    await self.highrise.moderate_room(user_id_to_kick, "kick")
                    await self.highrise.chat( f"Kicked {mention}.")
                else:
                    await self.highrise.send_whisper(user.id, f"User {mention} is not in the room.")
            else:
                await self.highrise.send_whisper(user.id, "You can't use this command.")

         elif message.startswith("!mute"):
            if user.username.lower() in self.moderators:
                parts = message.split()
                if len(parts) < 2:
                    await self.highrise.chat(user.id, "Usage: !mute @username")
                    return

                mention = parts[1]
                username_to_mute = mention.lstrip('@')  # Remove the '@' symbol from the mention
                response = await self.highrise.get_room_users()
                users = [content[0] for content in response.content]  # Extract the User objects
                user_ids = [user.id for user in users]  # Extract the user IDs

                if username_to_mute.lower() in [user.username.lower() for user in users]:
                    user_index = [user.username.lower() for user in users].index(username_to_mute.lower())
                    user_id_to_mute = user_ids[user_index]
                    await self.highrise.moderate_room(user_id_to_mute, "mute",3600)  # Mute for 1 hour
                    await self.highrise.chat(f"Muted {mention} for 1 hour.")
                else:
                    await self.highrise.send_whisper(user.id, f"User {mention} is not in the room.")
            else:
                await self.highrise.send_whisper(user.id, "You can't use this command.")

         elif message.startswith("!unmute"):
            if user.username.lower() in self.moderators:
                parts = message.split()
                if len(parts) < 2:
                    await self.highrise.chat(user.id, "Usage: !mute @username")
                    return

                mention = parts[1]
                username_to_mute = mention.lstrip('@')  # Remove the '@' symbol from the mention
                response = await self.highrise.get_room_users()
                users = [content[0] for content in response.content]  # Extract the User objects
                user_ids = [user.id for user in users]  # Extract the user IDs

                if username_to_mute.lower() in [user.username.lower() for user in users]:
                    user_index = [user.username.lower() for user in users].index(username_to_mute.lower())
                    user_id_to_mute = user_ids[user_index]
                    await self.highrise.moderate_room(user_id_to_mute, "mute",1)  # Mute for 1 hour
                    await self.highrise.chat(f"{mention} Unmuted.")
                else:
                    await self.highrise.send_whisper(user.id, f"User {mention} is not in the room.")
            else:
                await self.highrise.send_whisper(user.id, "You can't use this command.")

         elif message.startswith("!ban"):
            if user.username.lower() in self.moderators:
                parts = message.split()
                if len(parts) < 2:
                    await self.highrise.chat(user.id, "Usage: !ban @username")
                    return

                mention = parts[1]
                username_to_ban = mention.lstrip('@')  # Remove the '@' symbol from the mention
                response = await self.highrise.get_room_users()
                users = [content[0] for content in response.content]  # Extract the User objects
                user_ids = [user.id for user in users]  # Extract the user IDs

                if username_to_ban.lower() in [user.username.lower() for user in users]:
                    user_index = [user.username.lower() for user in users].index(username_to_ban.lower())
                    user_id_to_ban = user_ids[user_index]
                    await self.highrise.moderate_room(user_id_to_ban, "ban", 3600)  # Ban for 1 hour
                    await self.highrise.chat(f"Banned {mention} for 1 hour.")
                else:
                    await self.highrise.send_whisper(user.id, f"User {mention} is not in the room.")
            else:
                await self.highrise.send_whisper(user.id, "You can't use this command.")

        
        
         if message == "-tip 5":
              if user.username.lower() in self.moderators:
                roomUsers = (await self.highrise.get_room_users()).content
                for roomUser, _ in roomUsers:
                  await self.highrise.tip_user(roomUser.id, "gold_bar_5")
              else: 
                await  self.highrise.send_whisper(user.id, f"Only Admins and mods can use tip!")

         if message == "-tip 1":
              if user.username.lower() in self.moderators:
                roomUsers = (await self.highrise.get_room_users()).content
                for roomUser, _ in roomUsers:
                  await self.highrise.tip_user(roomUser.id, "gold_bar_1")
              else: 
                await  self.highrise.send_whisper(user.id, f"Only Admins and mods are eligible to tip.")
         if message == "-tip 10":
              if user.username.lower() in self.moderators:
                roomUsers = (await self.highrise.get_room_users()).content
                for roomUser, _ in roomUsers:
                  await self.highrise.tip_user(roomUser.id, "gold_bar_10")
              else: 
                await  self.highrise.send_whisper(user.id, f"Only Admins and mods are eligible to tip.")
         if message.lower().lstrip().startswith(("-emotes", "!emotes")):
                await self.highrise.send_whisper(user.id, "\n• Emote can be used by NUMBERS")
                await self.highrise.send_whisper(user.id, "\n• For loops say -loop or !loop then the emote number.")         
         if message.lower().lstrip().startswith(("!admin","-admin")):
           if user.username.lower() in moderators :
             await self.highrise.send_whisper(user.id,"\n____________________________\n• Give mod & vip :\n-give @ mod \n-give @ mod 24h \n• Remove mod\vop\n-remove @ mod\vip\n• Advertising\n-announce + text\n-clear\n ____________________________")
             await self.highrise.send_whisper(user.id,"\n____________________________\n• Tipping  :\n-tip 1\n-tip 5 \n-tip 10 \n-wallet to veiw the bot wallet.\n____________________________\n")
           else:
              await self.highrise.send_whisper(user.id,"Only Admins are eligible to veiw.")  
             
         

         if message.lower().lstrip().startswith(("-list", "!list")):
                await self.highrise.chat("\\commands you can use:\n• !profile or -profile\n• -top tippers or !top tippers \n• !teleports or -teleports \n • !mod or -mod(Only mods)\n• !admin or -admin(Only admins) ")

    
         if message == "-teleports" or message =="!teleports" :
                    await self.highrise.chat(f"\n • Teleports\n ____________________________\n-g or -floor1: Ground floor \n-floor2 or -2 :Second floor  \n-dj : (Owners& mods only)\n-vip or -v : (vip only), make sure you have 🎫VIP Tickets 🎫 \n• type -buy or !buy for details ")
         if message.lower().lstrip().startswith(("!rules", "-rules")):
           await self.highrise.chat(f"\n\n        RULES\n ____________________________\n 1. NO UNDERAGE \n 2. No advertising\n 3. No hate speech \n 4. No begging (those trash will be immediately banned 🚫) \n 5. No spamming ")
         if message.lower().lstrip().startswith(("-feedback", "!feedback")):
                    await self.highrise.send_whisper(user.id, "• [ Submit Feedback ]\\Thank you for joining our room! \n We value your feedback,")
                    await self.highrise.send_whisper(user.id,"Please share your feedback/suggestions with @stonedzillia9 to improve our environment. Your contributions are valuable and will help us improve.")  

         if user.username.lower() in self.moderators:
            if message.lower().lstrip().startswith(("-mod","!mod")):
               await self.highrise.send_whisper(user.id,"\n  \n•Moderating :\n ____________________________\n !kick @ \n !ban @ \n !mute @ \n !unmute @ ")
               await self.highrise.send_whisper(user.id,"\n  \n•Teleporting :\n ____________________________\n-here @ :to summon\n -tele @ tele_key. : telepport to a certain teleport\nExample -tele @username vip1")
            
             
         if message.lstrip().startswith(("-give","-remove","-here","-tele")):
            response = await self.highrise.get_room_users()
            users = [content[0] for content in response.content]
            usernames = [user.username.lower() for user in users]
            parts = message[1:].split()
            args = parts[1:]

            if len(args) < 1:
                await self.highrise.send_whisper(user.id, f"Usage !{parçalar[0]} <@Alionardo_>")
                return
            elif args[0][0] != "@":
                await self.highrise.send_whisper(user.id, "Invalid user format. Please use '@username'.")
                return
            elif args[0][1:].lower() not in usernames:
                await self.highrise.send_whisper(user.id, f"{args[0][1:]} is not in the room.")
                return
            user_upg = next((u.username for u in users if u.username.lower() == args[0][1:].lower()), None)
            user_id = next((u.id for u in users if u.username.lower() == args[0][1:].lower()), None)
            user_name = next((u.username.lower() for u in users if u.username.lower() == args[0][1:].lower()), None)
            if not user_id:
                await self.highrise.send_whisper(user.id, f"User {args[0][1:]} not found")
                return                     
            try:
              
               

                if message.lower().startswith("-give") and message.lower().endswith("mod"):   
                  if user.username.lower() in moderators :
                     await self.highrise.chat(f"{user_name} is now a Permanent MOD, given by {user.username}")
                     if user_name.lower() not in self.moderators:
                           self.moderators.append(user_name)
                           self.save_moderators()
                elif message.lower().startswith("-give") and message.lower().endswith("mod 24h"):
                  if user.username.lower() in owners :
                     await self.highrise.chat(f"{user_name} is now a Temporary MOD, given by {user.username}")
                     if user_name not in self.temporary_vips:
                         self.temporary_vips[user_name] = int(time.time()) + 24 * 60 * 60  # MOD for 24 hours
                         self.save_temporary_vips()
                elif message.lower().startswith("-remove") and message.lower().endswith("mod"):
                  if user.username.lower() in owners :
                    if user_name in self.moderators:
                       self.moderators.remove(user_name)
                       self.save_moderators()
                       await self.highrise.chat(f"{user_name} is no longer a moderator.")
                elif message.lower().startswith("-here"):
                   if user.username.lower() in self.moderators:
                      target_username = user_name
                      if target_username not in owners :
                          await self.teleport_user_next_to(target_username, user)
                elif message.lower().startswith(('-tele')) and  message.lower().endswith(("vip")) :
                    if user.username.lower() in self.moderators :
                        await self.highrise.teleport(user_id, Position(15, 12.75,16.5))
                elif message.lower().startswith(('-tele')) and  message.lower().endswith(("icon")) :
                    if user.username.lower() in self.moderators :
                        await self.highrise.teleport(user_id, Position(15.5,19,16.5))
                elif message.lower().startswith(('-tele')) and  message.lower().endswith(("g","1","floor1","f1")) :
                    if user.username.lower() in self.moderators :
                        await self.highrise.teleport(user_id, Position(15.5,0.25,11.5))   
                elif message.lower().startswith(('-tele')) and  message.lower().endswith(("2","floor2", "f2")) :
                    if user.username.lower() in self.moderators :
                        await self.highrise.teleport(user_id, Position(14.5,6.5,17))   
               
            except Exception as e:
             print(f"An exception occurred[Due To {parts[0][1:]}]: {e}")

         if message.lstrip().startswith(("-upgrade")):
            response = await self.highrise.get_room_users()
            users = [content[0] for content in response.content]
            usernames = [user.username.lower() for user in users]
            parts = message[1:].split()
            args = parts[1:]

            if len(args) < 1:
                await self.highrise.send_whisper(user.id, f"Usage!{parts[0]} <@Alionardo_>")
                return
            elif args[0][0]!= "@":
                await self.highrise.send_whisper(user.id, "Invalid user format. Please use '@username'.")
                return
            elif args[0][1:].lower() not in usernames:
                await self.highrise.send_whisper(user.id, f"{args[0][1:]} is not in the room.")
                return

            user_id = next((u.id for u in users if u.username.lower() == args[0][1:].lower()), None)
            user_name = next((u.username.lower() for u in users if u.username.lower() == args[0][1:].lower()), None)
            user_upg = next((u.username for u in users if u.username.lower() == args[0][1:].lower()), None)
            if not user_id:
                await self.highrise.send_whisper(user.id, f"User {args[0][1:]} not found")
                return    
            try:    
               if message.lower().startswith(('-upgrade')):
                   if user.username.lower() in moderators :
                        if user_upg in self.membership:
                           current_rank = self.membership[user_upg]["rank"]
                           next_rank = self.get_next_rank(current_rank)
                           if next_rank:
                               self.membership[user_upg]["rank"] = next_rank
                               new_title = self.get_title(user_upg, self.get_amount_from_rank(next_rank))
                               self.membership[user_upg]["amount"] = self.get_amount_from_rank(next_rank)
                               self.save_membership()
                               await self.highrise.chat(f"Congratulations, {user_upg}! You've been upgraded to {new_title} for free!")
                           else:
                               await self.highrise.chat("You are already at the highest rank!")
                        else:
                               await self.highrise.chat(f"{user_upg} in the rank list should at least try tip a nugget to get a rank.")
            except Exception as e:
                print(f"An exception occurred[Due To {parts[0][1:]}]: {e}")
         if message.startswith("!time"):
            parts = message.split()
            if len(parts) == 2:
                target_mention = parts[1]

                # Remove the "@" symbol if present
                target_user = target_mention.lstrip('@')

                # Check if the target user has temporary VIP status
                remaining_time = self.remaining_time(target_user.lower())
                await self.highrise.send_whisper(user.id, f"Remaining time for {target_mention}'s temporary VIP status: {remaining_time}")
            else:
                await self.highrise.send_whisper(user.id, "Usage: !time @username")

         if message.lower().startswith(("-profile","!profile")):
               await self.show_profile(user)
         if message.lower().startswith(("-top tippers","!top tippers")):
               await self.top_tippers()
         if message.lower().startswith(('-2','f2','floor2')) : 
            if user.username.lower() in self.moderators  :  
                 await self.highrise.teleport(user.id, Position(14.5,6.5,17)) 
         if message.lower().startswith(('-vip')) : 
            if user.username.lower() in self.moderators or (user.username in self.membership and self.get_rank(self.membership[user.username]["amount"]) in ["VIP","Icon"]):
               await self.highrise.teleport(user.id, Position(15, 12.75,16.5)) 
            else:
               await self.highrise.send_whisper((user.id)," this is a privet place for VIP ranks, and ranks above.")
         if message.lower().startswith(('-icon')) :
            if user.username.lower() in self.moderators or (user.username in self.membership and self.get_rank(self.membership[user.username]["amount"]) in ["Icon"]):
               await self.highrise.teleport(user.id, Position(15.5,19,16.5)) 
            else:
               await self.highrise.send_whisper((user.id)," this is a privet place for Icon ranks VIPs and ranks above.")
        
         if message.startswith(('-floor1','-g','-1','f1')):
             parts = message.split()
             if len(parts) == 1:
                await self.highrise.teleport(f"{user.id}", Position(15.5,0.25,11.5))
           
         if message.lower().startswith("loop"):
           parts = message.split()
           E = parts[1]
           E = int(E)
           emote_text, emote_time = await self.get_emote_E(E)
           emote_time -= 1
           user_id = user.id  
           if user.id in self.continuous_emote_tasks and not self.continuous_emote_tasks[user.id].cancelled():
              await self.stop_continuous_emote(user.id)
              task = asyncio.create_task(self.send_continuous_emote(emote_text,user_id,emote_time))
              self.continuous_emote_tasks[user.id] = task
           else:
              task = asyncio.create_task(self.send_continuous_emote(emote_text,user_id,emote_time))
              self.continuous_emote_tasks[user.id] = task  

         elif message.lower().startswith("stop"):
            if user.id in self.continuous_emote_tasks and not self.continuous_emote_tasks[user.id].cancelled():
                await self.stop_continuous_emote(user.id)
                await self.highrise.chat("Continuous emote has been stopped.")
            else:
                await self.highrise.chat("You don't have an active loop_emote.")
         elif message.lower().startswith("users"):
            room_users = (await self.highrise.get_room_users()).content
            await self.highrise.chat(f"There are {len(room_users)} users in the room")
        
         if  message.isdigit() and 1 <= int(message) <= 91:
              parts = message.split()
              E = parts[0]
              E = int(E)
              emote_text, emote_time = await self.get_emote_E(E)    
              tasks = [asyncio.create_task(self.highrise.send_emote(emote_text, user.id))]
              await asyncio.wait(tasks)
         if message.startswith("/e1"):
                 await self.highrise.set_outfit(outfit=[
          Item(type='clothing', 
                    amount=1, 
                    id='body-flesh',
                    account_bound=False,
                    active_palette=5),
          Item(type='clothing',
                    amount=1,
                    id='shirt-n_starteritems2019raglanwhite',
                   account_bound=False,
                    active_palette=-1),
          Item(type='clothing', 
               amount=1, 
               id='pants-n_room12019blackacidwashjeans',
               account_bound=False,
               active_palette=-1),
          Item(type='clothing', 
               amount=1, 
               id='nose-n_01_b',
               account_bound=False,
               active_palette=-1),
         Item(type='clothing',
              amount=1, 
              id='watch-n_room32019blackwatch', 
              account_bound=False,
              active_palette=-1),
         Item(type='clothing', 
              amount=1, 
              id='watch-n_room32019blackwatch', 
              account_bound=False,
              active_palette=-1),
         Item(type='clothing', 
              amount=1, id='shoes-n_room22019tallsocks', 
              account_bound=False,
              active_palette=-1), 
         Item(type='clothing',
              amount=1, 
              id='shoes-n_converse_black',
              account_bound=False,
              active_palette=-1),       
         Item(type='clothing',
              amount=1, 
              id='freckle-n_basic2018freckle04', 
              account_bound=False,
              active_palette=-1),
         Item(type='clothing',
              amount=1,
              id='mouth-basic2018fullpeaked',
              account_bound=False,
              active_palette=1),
         Item(type='clothing',
              amount=1,
              id= 'hair_back-n_malenew21',
              account_bound=False, active_palette=2),
        Item(type='clothing',
              amount=1,
              id= 'hair_front-n_malenew21',
              account_bound=False, active_palette=2),  
         Item(type='clothing', 
              amount=1, 
              id='eye-n_basic2018maleroundsleepy',
              account_bound=False,
              active_palette=2),
        Item(type='clothing', 
             amount=1,
             id='eyebrow-n_06', 
             account_bound=False,
             active_palette=2)
      ])

         if  message.lower().startswith("-wallet"):
            if user.username.lower() in self.moderators :

                  wallet = (await self.highrise.get_wallet()).content
                  await self.highrise.send_whisper(user.id, f"The bot wallet contains {wallet[0].amount} {wallet[0].type}")

            else: 
                await  self.highrise.send_whisper(user.id, f"Only Moderators Can View the Wallet")

    
          
      except Exception as e:
        print(f"An exception occured: {e}")  

    async def send_continuous_emote(self, emote_text ,user_id,emote_time):
      try:
          while True:                    
                tasks = [asyncio.create_task(self.highrise.send_emote(emote_text, user_id))]
                await asyncio.wait(tasks)
                await asyncio.sleep(emote_time)
                await asyncio.sleep(1)
      except Exception as e:
                print(f"{e}")

  
    async def stop_continuous_emote(self, user_id: int):
      if user_id in self.continuous_emote_tasks and not self.continuous_emote_tasks[user_id].cancelled():
          task = self.continuous_emote_tasks[user_id]
          task.cancel()
          with contextlib.suppress(asyncio.CancelledError):
              await task
          del self.continuous_emote_tasks[user_id]

    async def follow_user(self, target_username: str):
      while self.following_username == target_username:

          response = await self.highrise.get_room_users()
          target_user_position = None
          for user_info in response.content:
              if user_info[0].username.lower() == target_username.lower():
                  target_user_position = user_info[1]
                  break

          if target_user_position:
              nearby_position = Position(target_user_position.x + 1.0, target_user_position.y, target_user_position.z)
              await self.highrise.walk_to(nearby_position)

              await asyncio.sleep(2)
    async def get_emote_E(self, target) -> None: 

     try:
        emote_info = self.Emotes.get(target)
        return emote_info
     except ValueError:
        pass
    async def on_whisper(self, user: User, message: str ) -> None:

        if message == "here":
            if user.username.lower() in self.moderators:
                response = await self.highrise.get_room_users()
                users = [content for content in response.content]
                for u in users:
                    if u[0].id == user.id:
                        try:
                            await self.highrise.teleport(Counter.bot_id,Position((u[1].x),(u[1].y),(u[1].z),"FrontRight"))


                            break
                        except:

                            pass
       
        if message.startswith("-say"):
            if user.username.lower() in self.moderators:
                text = message.replace("-say", "").strip()
                await self.highrise.chat(text)

   
         

        elif message.startswith("-come"):
            if user.username.lower() in self.moderators:
                response = await self.highrise.get_room_users()
                your_pos = None
                for content in response.content:
                    if content[0].id == user.id:
                        if isinstance(content[1], Position):
                            your_pos = content[1]
                            break
                if not your_pos:
                    await self.highrise.send_whisper(user.id, "Invalid coordinates!")
                    return
                await self.highrise.chat(f"@{user.username} I'm coming ..")
                await self.highrise.walk_to(your_pos)

        elif message.lower().startswith("-follow"):
         
            target_username = message.split("@")[1].strip()

            if target_username.lower() == self.following_username:
                await self.highrise.send_whisper(user.id,"I am already following.")
            elif message.startswith("-say"):
              if user.username.lower() in self.moderators:
                  text = message.replace("-say", "").strip()
                  await self.highrise.chat(text)
            else:
                self.following_username = target_username
                await self.highrise.chat(f"hey {target_username}.")
            
                await self.follow_user(target_username)
        elif message.lower() == "-stop following":
            self.following_username = None
   
            await self.highrise.walk_to(Position(13.5, 1,11.5,"FrontRight"))

  
  
    def get_rank(self, amount: int) -> str:
        if amount < 100:
            return "Guest"
        elif amount < 500:
            return "Regular"
        elif amount < 1250:
            return "VIP"
        elif amount > 1250:
            return "Icon"
        else:
            return "Icon"

    def get_title(self, username: str, amount: int) -> str:
        rank = self.get_rank(amount)
        if rank == "Guest":
            return "Guest"
        elif rank == "Regular":
            return "Regular"
        elif rank == "VIP":
            return "VIP"
        elif rank == "Icon":
            return "Icon"
        else:
            return "Icon"    
    async def top_tippers(self, limit: int = 10) -> None:
        top_tippers_list = []
        for username, info in self.membership.items():
            title = self.get_title(username, info["amount"])
            top_tippers_list.append((info["amount"], title, username))
        top_tippers_list.sort(reverse=True)
        top_tippers_list = top_tippers_list[:limit]
        message = "\nTop Tippers:\n"
        for i, (amount, title, username) in enumerate(top_tippers_list, start=1):
            medal = ""
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            message += f"{i}. {medal} {title} : {username} - {amount} 🪙\n"
        await self.highrise.chat(message)
    async def show_profile(self, user: User) -> None:
        username = user.username
        if username in self.membership:
            amount = self.membership[username]["amount"]
            current_title = self.get_title(username, amount)
            next_title_amount = self.get_next_title_amount(amount)
            next_title = self.get_rank(next_title_amount)
            progress = int((amount / next_title_amount) * 10)
            thread = f"\n•{username}'s Profile :\n"
            thread += f"•Total Gold Spent: {amount} gold\n"
            thread += f"•Current Title: {current_title}\n"
            thread += f"•Progress to {next_title}: "
            for _ in range(progress):
                thread += "█"  # filled block
            for _ in range(10 - progress):
                thread += "░"  # shaded block
            thread += f"\n**Next Title:** {next_title} ({next_title_amount} gold)"
            await self.highrise.chat(thread)
        else:
            await self.highrise.send_whisper(user.id, "You don't have a profile yet. Start tipping gold to earn titles!")

    def get_next_title_amount(self, amount: int) -> int:
        if amount < 100:
            return 100
        elif amount < 500:
            return 500
        elif amount < 1250:
            return 1250
        else:
            return 1259
 
    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        try:
            print(f"{sender.username} tipped {receiver.username} an amount of {tip.amount}")
            if receiver.id == Counter.bot_id:
                if sender.username not in self.membership:
                    self.membership[sender.username] = {"amount": tip.amount, "rank": self.get_rank(tip.amount)}
                    title = self.get_title(sender.username, tip.amount)
                    self.membership[sender.username]["amount"] += 0
                    await self.highrise.chat(f"\n{title} : {sender.username} has tipped {tip.amount} g! Thank you for your generosity!")
                    self.save_membership()
                else:
                    previous_amount = self.membership[sender.username]["amount"]
                    previous_title = self.get_title(sender.username, previous_amount)
                    self.membership[sender.username]["amount"] += tip.amount
                    self.membership[sender.username]["rank"] = self.get_rank(self.membership[sender.username]["amount"])
                    title = self.get_title(sender.username, self.membership[sender.username]["amount"])
                    # Sort players by tip amount in descending order
                    self.membership = dict(sorted(self.membership.items(), key=lambda item: item[1]["amount"], reverse=True))
                    self.save_membership()
                    await self.highrise.chat(f"\n{title}: {sender.username} has tipped {tip.amount} g! Thank you for your generosity!")
                    new_amount = self.membership[sender.username]["amount"]
                    new_title = self.get_title(sender.username, new_amount)
                    if new_title!= previous_title:
                        await self.highrise.send_whisper(sender.id, f"Congratulations, {sender.username}! You've upgraded to {new_title} with a total of {new_amount}g!")
        except Exception as e:
            print(f"Error: {e}")
    def get_next_rank(self, current_rank: str) -> str:
        ranks = ["Guest", "Regular", "VIP", "Icon"]
        current_index = ranks.index(current_rank)
        if current_index < len(ranks) - 1:
            return ranks[current_index + 1]
        else:
            return None
    def get_amount_from_rank(self, rank: str) -> int:
        if rank == "Guest":
            return 0
        elif rank == "Regular":
            return 500
        elif rank == "VIP":
            return 750
        elif rank == "Icon":
            return 1500
        else:
            return 1500

    def get_title(self, username: str, amount: int) -> str:
        rank = self.get_rank(amount)
        if rank == "Guest":
            return "Our Guest"
        elif rank == "Regular":
            return "Our Regular vip"
        elif rank == "VIP":
            return "Our VIP"
        elif rank == "Icon":
            return "The Icon"
        else:
            return "The Icon"
    async def on_user_move(self, user: User, pos: Position | AnchorPosition) -> None:
      if user.username == " Alionardo_":
         print(f"{user.username}: {pos}")
     
  
    

   




    
