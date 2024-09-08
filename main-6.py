from highrise import *
from highrise.models import *
from asyncio import run as arun
from flask import Flask
from threading import Thread
from highrise.__main__ import *
from emotes import*
from mesajlar import*
from oranlar import*
from kiy import*
import random
import asyncio
import time

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.emote_looping = False
        self.user_emote_loops = {}
        self.loop_task = None
        self.following_users = []

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        if self.loop_task is None or self.loop_task.done():
            self.loop_task = asyncio.create_task(self.emote_loop())
        print("hi im alive?")
        await self.highrise.tg.create_task(self.highrise.teleport(
            session_metadata.user_id, Position(10.5, 2.0, 9.5, "FrontLeft")))
        await self.send_periodic_messages()
    

    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        try:
            emote_name = random.choice(list(secili_emote.keys()))
            emote_info = secili_emote[emote_name]
            emote_to_send = emote_info["value"]
            await self.send_emote(emote_to_send, user.id)
        except Exception as e:
            print(f"Error sending emote to user {user.id}: {e}")
  
    async def on_user_leave(self, user: User):
    
        user_id = user.id
        if user_id in self.user_emote_loops:
            await self.stop_emote_loop(user_id)

    async def send_periodic_messages(self):
        message_list = [
            "Bugünki ruh haline uyan şarkı ne öğrenmek ister misin? Şarkı yaz ve öğren!",
            "Gelecekte seni neler bekliyor olabilir? Fal yazarak bahtını öğrenebilirsin!",
            "Eğer komik bir şey duyamaya ihtiyacın varsa espri yaz ve eğlenmene bak!",
            "Birilerini düşürmek için güzel sözlere ihtiyacın varsa sana yardımcı olabilirim! Tek yapman gereken rizz yazmak!",
            "Laf sokmada en  iyisi kim biliyor musun? Tabii ki de ben, inanmıyorsan laf yazman yeterli!",
            "Birisi ile arandaki aşk oranını öğrenmek için: aşk @kullanıcıadı",
            "Birisi ile arandaki dostluk oranını öğrenmek için: dostluk @kullanıcıadı",
            "Birisi ile arandaki nefret oranını öğrenmek için: nefret @kullanıcıadı",
            "Birisi ile arandaki güven oranını öğrenmek için: güven @kullanıcıadı"
        ]
        index = 0
        while True:
            try:
                message = message_list[index]
                index = (index + 1) % len(message_list)
                wait_time = 30
                await asyncio.sleep(wait_time)
                await self.highrise.chat(message)
            except Exception as e:
                print(f"Mesaj gönderme hatası: {e}")
                


    async def follow(self, user: User):
        self.following_users = [user]  # Takip edilen kullanıcıyı listeye ekle

        while user in self.following_users:
            room_users = (await self.highrise.get_room_users()).content
            user_position = None
            for room_user, position in room_users:
                if room_user.id == user.id:
                    user_position = position
                    break
            if user_position is not None and isinstance(user_position, Position):
                nearby_position = Position(user_position.x + 1.0, user_position.y, user_position.z)
                await self.highrise.walk_to(nearby_position)
            await asyncio.sleep(0.5)

    async def on_chat(self, user: User, message: str) -> None:
        if message.lower().startswith("takip2") and await self.is_user_allowed(user):
            target_username = message.split('@')[-1].strip()
            if target_username:
                room_users = (await self.highrise.get_room_users()).content
                target_user = None
                for room_user, _ in room_users:
                    if room_user.username == target_username:
                        target_user = room_user
                        break
                if target_user:
                    self.following_users = []  # Önceki takipleri durdur
                    await self.follow(target_user)  # Yeni kullanıcıyı takip et
                else:
                    await self.highrise.chat("Oyuncu odada değil!")
            else:
                await self.highrise.chat("Takip edilecek kişiyi belirtmediniz.")

        if message.lower() == "stay2" and await self.is_user_allowed(user):
            self.following_users = []
            await self.highrise.chat("Takip etmeyi bıraktım.")
        
        if message.lower().startswith("degis2") and await self.is_user_allowed(user):
            # Randomly select active color palettes
            hair_active_palette = random.randint(0, 82)
            skin_active_palette = random.randint(0, 88)
            eye_active_palette = random.randint(0, 49)
            lip_active_palette = random.randint(0, 58)
            
            # Set the outfit with randomly chosen items and color palettes
            outfit = [
                Item(type='clothing', amount=1, id='body-flesh', account_bound=False, active_palette=skin_active_palette),
                Item(type='clothing', amount=1, id=random.choice(item_shirt), account_bound=False, active_palette=-1),
                Item(type='clothing', amount=1, id=random.choice(item_bottom), account_bound=False, active_palette=-1),
                Item(type='clothing', amount=1, id=random.choice(item_accessory), account_bound=False, active_palette=-1),
                Item(type='clothing', amount=1, id=random.choice(item_shoes), account_bound=False, active_palette=-1),
                Item(type='clothing', amount=1, id=random.choice(item_freckle), account_bound=False, active_palette=-1),
                Item(type='clothing', amount=1, id=random.choice(item_eye), account_bound=False, active_palette=eye_active_palette),
                Item(type='clothing', amount=1, id=random.choice(item_mouth), account_bound=False, active_palette=lip_active_palette),
                Item(type='clothing', amount=1, id=random.choice(item_nose), account_bound=False, active_palette=-1),
                Item(type='clothing', amount=1, id=random.choice(item_hairback), account_bound=False, active_palette=hair_active_palette),
                Item(type='clothing', amount=1, id=random.choice(item_hairfront), account_bound=False, active_palette=hair_active_palette),
                Item(type='clothing', amount=1, id=random.choice(item_eyebrow), account_bound=False, active_palette=hair_active_palette)
            ]
            
            # Set the outfit for the character
            await self.highrise.set_outfit(outfit=outfit)

        
        if message.startswith("full"):
            emote_name = message.replace("full", "").strip()
            if user.id in self.user_emote_loops and self.user_emote_loops[user.id] == emote_name:
                await self.stop_emote_loop(user.id)
            else:
                await self.start_emote_loop(user.id, emote_name)

        if message in ["stop", "dur", "0"]:
            if user.id in self.user_emote_loops:
                await self.stop_emote_loop(user.id)
                    
        if message == "ulti":
            if user.id not in self.user_emote_loops:
                await self.start_random_emote_loop(user.id)

        if message in ["stop", "dur"]:
            if user.id in self.user_emote_loops:
                if self.user_emote_loops[user.id] == "ulti":
                    await self.stop_random_emote_loop(user.id)


        message = message.strip().lower()      
        if "@" in message:
            parts = message.split("@")
            if len(parts) < 2:
                return

            emote_name = parts[0].strip()
            target_username = parts[1].strip()

            if emote_name in emote_mapping:
                response = await self.highrise.get_room_users()
                users = [content[0] for content in response.content]
                usernames = [user.username.lower() for user in users]

                if target_username not in usernames:
                    return

                user_id = next((u.id for u in users if u.username.lower() == target_username), None)
                if not user_id:
                    return

                await self.handle_emote_command(user.id, emote_name)
                await self.handle_emote_command(user_id, emote_name)

        for emote_name, emote_info in emote_mapping.items():
            if message.lower() == emote_name.lower():
                try:
                    emote_to_send = emote_info["value"]
                    await self.highrise.send_emote(emote_to_send, user.id)
                except Exception as e:
                    print(f"Error sending emote: {e}")

        if message.lower().startswith("all ") and await self.is_user_allowed(user):
            emote_name = message.replace("all ", "").strip()
            if emote_name in emote_mapping:
                emote_to_send = emote_mapping[emote_name]["value"]
                room_users = (await self.highrise.get_room_users()).content
                tasks = []
                for room_user, _ in room_users:
                    tasks.append(self.highrise.send_emote(emote_to_send, room_user.id))
                try:
                    await asyncio.gather(*tasks)
                except Exception as e:
                    error_message = f"Error sending emotes: {e}"
                    await self.highrise.send_whisper(user.id, error_message)
            else:
                await self.highrise.send_whisper(user.id, f"Invalid emote name: {emote_name}")

        try:
            if message.lstrip().startswith(("cast")):
                response = await self.highrise.get_room_users()
                users = [content[0] for content in response.content]
                usernames = [user.username.lower() for user in users]
                parts = message[1:].split()
                args = parts[1:]

                if len(args) >= 1 and args[0][0] == "@" and args[0][1:].lower() in usernames:
                    user_id = next((u.id for u in users if u.username.lower() == args[0][1:].lower()), None)

                    if message.lower().startswith("cast"):
                        await self.highrise.send_emote("emote-telekinesis", user.id)
                        await self.highrise.send_emote("emote-gravity", user_id)
        except Exception as e:
            print(f"An error occurred: {e}")

        if message.startswith("dans") or message.startswith("dance"):
            try:
                emote_name = random.choice(list(secili_emote.keys()))
                emote_to_send = secili_emote[emote_name]["value"]
                await self.highrise.send_emote(emote_to_send, user.id)
            except:
                print("Dans emote gönderilirken bir hata oluştu.")

        message_lower = message.lower()
        parts = message_lower.split("@")

        if len(parts) > 1:
            target_username = parts[-1].strip()
            target_username_lower = target_username.lower()
            user_username = user.username
            user_username_lower = user_username.lower()

            message_type = message_lower.split()[0]
            response_generators = {
                "ask": get_love_message,
                "aşk": get_love_message,
                "dostluk": get_friendship_message,
                "nefret": get_hate_message,
                "güven": get_trust_message,
                "guven": get_trust_message
            }

            if message_type in response_generators:
                score = random.randint(0, 100)
                response_message = response_generators[message_type](user_username, target_username, score)

                if response_message:
                    await self.highrise.chat(response_message)

        command = message.lower().split()[0]  # Extract the first word from the message
        message_dict = {
            "rizz": rizz_mesaj,
            "naber": nbr_mesaj,
            "nasılsın": nasl_mesaj,
            "nasilsin": nasl_mesaj,
            "espiri": espiri_mesaj,
            "espri": espiri_mesaj,
            "laf": laf_mesaj,
            "sarki": sarki_mesaj,
            "şarki": sarki_mesaj,
            "şarkı": sarki_mesaj,
            "fal": fal_mesaj,
            "yemek": yemek_mesaj
        }

        if command == "help":
            commands = "rizz, naber, nasilsin, espri, laf, sarki,fal"
            await self.highrise.chat(commands)
            return

        message_list = message_dict.get(command)
        
        if message_list:
            random_message = random.choice(message_list)
            await self.highrise.chat(f"{random_message} -@{user.username}")
    
    
#Numaralı emotlar numaralı emotlar
  
    async def handle_emote_command(self, user_id: str, emote_name: str) -> None:
        if emote_name in emote_mapping:
            emote_info = emote_mapping[emote_name]
            emote_to_send = emote_info["value"]

            try:
                await self.highrise.send_emote(emote_to_send, user_id)
            except Exception as e:
                print(f"Error sending emote: {e}")


    async def start_emote_loop(self, user_id: str, emote_name: str) -> None:
        if emote_name in emote_mapping:
            self.user_emote_loops[user_id] = emote_name
            emote_info = emote_mapping[emote_name]
            emote_to_send = emote_info["value"]
            emote_time = emote_info["time"]

            while self.user_emote_loops.get(user_id) == emote_name:
                try:
                    await self.highrise.send_emote(emote_to_send, user_id)
                except Exception as e:
                    if "Target user not in room" in str(e):
                        print(f"{user_id} odada değil, emote gönderme durduruluyor.")
                        break
                await asyncio.sleep(emote_time)

    async def stop_emote_loop(self, user_id: str) -> None:
        if user_id in self.user_emote_loops:
            self.user_emote_loops.pop(user_id)


  
#paid emotes paid emotes paid emote
  
    async def emote_loop(self):
        while True:
            try:
                emote_name = random.choice(list(paid_emotes.keys()))
                emote_to_send = paid_emotes[emote_name]["value"]
                emote_time = paid_emotes[emote_name]["time"]
                
                await self.highrise.send_emote(emote_id=emote_to_send)
                await asyncio.sleep(emote_time)
            except Exception as e:
                print("Error sending emote:", e) 


  
#Ulti Ulti Ulti Ulti Ulti Ulti Ulti

    async def start_random_emote_loop(self, user_id: str) -> None:
        self.user_emote_loops[user_id] = "ulti"
        while self.user_emote_loops.get(user_id) == "ulti":
            try:
                emote_name = random.choice(list(secili_emote.keys()))
                emote_info = secili_emote[emote_name]
                emote_to_send = emote_info["value"]
                emote_time = emote_info["time"]
                await self.highrise.send_emote(emote_to_send, user_id)
                await asyncio.sleep(emote_time)
            except Exception as e:
                print(f"Error sending random emote: {e}")

    async def stop_random_emote_loop(self, user_id: str) -> None:
        if user_id in self.user_emote_loops:
            del self.user_emote_loops[user_id]



  #Genel Genel Genel Genel Genel

    async def send_emote(self, emote_to_send: str, user_id: str) -> None:
        await self.highrise.send_emote(emote_to_send, user_id)
      
    async def on_user_move(self, user: User, pos: Position) -> None:
        """On a user moving in the room."""
        print(f"{user.username} moved to {pos}")

    async def on_whisper(self, user: User, message: str) -> None:
        """On a received room whisper."""
        if await self.is_user_allowed(user) and message.startswith(''):
            try:
                xxx = message[0:]
                await self.highrise.chat(xxx)
            except:
                print("error 3")

    async def is_user_allowed(self, user: User) -> bool:
        user_privileges = await self.highrise.get_room_privilege(user.id)
        return user_privileges.moderator or user.username in ["kakainek", "The.Ciyo"]


  
    async def run(self, room_id, token) -> None:
        await __main__.main(self, room_id, token)
class WebServer():

  def __init__(self):
    self.app = Flask(__name__)

    @self.app.route('/')
    def index() -> str:
      return "Alive"

  def run(self) -> None:
    self.app.run(host='0.0.0.0', port=8080)

  def keep_alive(self):
    t = Thread(target=self.run)
    t.start()
    
class RunBot():
  room_id = "664378afba25e36590a025ca"
  bot_token = "88ce933235c858601f9385356797555a4e8204fe45ce2d70ef553bc17dbd467d"
  bot_file = "main"
  bot_class = "Bot"

  def __init__(self) -> None:
    self.definitions = [
        BotDefinition(
            getattr(import_module(self.bot_file), self.bot_class)(),
            self.room_id, self.bot_token)
    ] 

  def run_loop(self) -> None:
    while True:
      try:
        arun(main(self.definitions)) 
      except Exception as e:
        import traceback
        print("Caught an exception:")
        traceback.print_exc()
        time.sleep(1)
        continue


if __name__ == "__main__":
  WebServer().keep_alive()

  RunBot().run_loop()