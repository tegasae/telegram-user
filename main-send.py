from pyrogram import Client
#from decouple import config

#API_ID=28172272
#API_HASH='d06bd430d4b4ee0a6e9d08b2fd9d68e7'
#PHONE='+79204695225'
#LOGIN='Thisismeornotme'

API_ID=22055896
API_HASH='012b8eaca5a72fe8db2b69d9a1dcf3a5'
PHONE='+79003062066'
LOGIN='Angelinakis01'



bot = Client(name=LOGIN,
             api_id=API_ID,
             api_hash=API_HASH,
             phone_number=PHONE)


bot.start()
bot.send_message(chat_id='me', text='Нет, это не я набирал')
bot.stop()



