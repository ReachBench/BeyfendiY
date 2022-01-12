from pyrogram import filters
from pyrogram.types import Message

from Yukki import SUDOERS, app
from Yukki.Database import blacklist_chat, blacklisted_chats, whitelist_chat

__MODULE__ = "Kara Liste"
__HELP__ = """


/karalistedekigruplar
- Bot'un Kara Listeye Alınmış Sohbetlerini Kontrol Edin.


**Not:**
Sadece Kurucular İçin.


/karalisteyeal [Grup ID] 
- Müzik Botunu kullanarak herhangi bir sohbeti kara listeye alın


/beyazlisteyeal [Grup ID] 
- Müzik Botunu kullanarak kara listeye alınmış herhangi bir sohbeti beyaz listeye alın

"""


@app.on_message(filters.command("karalisteyeal") & filters.user(SUDOERS))
async def blacklist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("**Kullanım:**\n/karalisteyeal [Grup ID]")
    chat_id = int(message.text.strip().split()[1])
    if chat_id in await blacklisted_chats():
        return await message.reply_text("Grup zaten kara listede.")
    blacklisted = await blacklist_chat(chat_id)
    if blacklisted:
        return await message.reply_text("Grup Başarıyla Kara Listeye Alındı")
    await message.reply_text("Yanlış bir şey oldu, log'u kontrol edin.")


@app.on_message(filters.command("beyazlisteyeal") & filters.user(SUDOERS))
async def whitelist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("**Kullanım:**\n/beyazlisteyeal [Grup ID]")
    chat_id = int(message.text.strip().split()[1])
    if chat_id not in await blacklisted_chats():
        return await message.reply_text("Grup zaten beyaz listede.")
    whitelisted = await whitelist_chat(chat_id)
    if whitelisted:
        return await message.reply_text("Grup Başarıyla Beyaz Listeye Alındı")
    await message.reply_text("Yanlış bir şey oldu, Log'u kontrol edin.")


@app.on_message(filters.command("karalistedekigruplar"))
async def blacklisted_chats_func(_, message: Message):
    text = "**Kara Listedeki Gruplar:**\n\n"
    j = 0
    for count, chat_id in enumerate(await blacklisted_chats(), 1):
        try:
            title = (await app.get_chat(chat_id)).title
        except Exception:
            title = "Private"
        j = 1
        text += f"**{count}. {title}** [`{chat_id}`]\n"
    if j == 0:
        await message.reply_text("Kara Listeye Alınmış Grup Yok")
    else:
        await message.reply_text(text)
