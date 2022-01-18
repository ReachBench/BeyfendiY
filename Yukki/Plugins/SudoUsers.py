import asyncio
import os
import shutil

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from config import LOG_SESSION, OWNER_ID
from Yukki import BOT_ID, BOT_USERNAME, MUSIC_BOT_NAME, OWNER_ID, SUDOERS, app
from Yukki.Database import (
    add_gban_user,
    add_off,
    add_on,
    add_sudo,
    get_served_chats,
    get_sudoers,
    is_gbanned_user,
    remove_gban_user,
    remove_sudo,
    set_video_limit,
)

__MODULE__ = "Kurucular"
__HELP__ = """


/kuruculistesi
- Botun Kurucu Listesini Verir. 


**Not:**
Yalnızca Kurucular İçindir. 


/kurucuekle [Kullanıcı adı veya bir kullanıcıyı yanıtla]
- Botun Kurucu listesine kullanıcı ekler.

/kurucusil [Kullanıcı adı veya bir kullanıcıyı yanıtla]
- Botun Kurucu listesine eklenen kullanıcıyı siler.

/bakim [acik / kapali]
- Etkinleştirildiğinde Bot bakım moduna girer. Artık kimse Müzik çalamaz!

/logger [acik / kapali]
- Etkinleştirildiğinde Bot bakım moduna girer. Artık kimse Müzik çalamaz!

/clean
- Temp Dosyalarını ve Günlüklerini Temizleyin.
"""
# Add Sudo Users!


@app.on_message(filters.command("kurucuekle") & filters.user(OWNER_ID))
async def useradd(_, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(
                "Bir kullanıcının mesajını yanıtlayın veya Kullanıcı Adı/Kullanıcı ID verin."
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        if user.id in SUDOERS:
            return await message.reply_text(f"{user.mention} Zaten Kurucu Listesinde.")
        added = await add_sudo(user.id)
        if added:
            await message.reply_text(f"**{user.mention}** Kurucu Listesine Eklendi.")
            os.system(f"kill -9 {os.getpid()} && python3 -m Yukki")
        else:
            await message.reply_text("Başarısız!")
        return
    if message.reply_to_message.from_user.id in SUDOERS:
        return await message.reply_text(
            f"{message.reply_to_message.from_user.mention} Zaten Kurucu Listesinde."
        )
    added = await add_sudo(message.reply_to_message.from_user.id)
    if added:
        await message.reply_text(
            f"**{message.reply_to_message.from_user.mention}** Kurucu Listesine Eklendi"
        )
        os.system(f"kill -9 {os.getpid()} && python3 -m Yukki")
    else:
        await message.reply_text("Başarısız!")
    return


@app.on_message(filters.command("kurucusil") & filters.user(OWNER_ID))
async def userdel(_, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(
                "Bir kullanıcının mesajını yanıtlayın veya Kullanıcı Adı/Kullanıcı ID verin"
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        message.from_user
        if user.id not in SUDOERS:
            return await message.reply_text(
                f"Kullanıcı Zaten Botun Kurucularından Değil."
            )
        removed = await remove_sudo(user.id)
        if removed:
            await message.reply_text(
                f"**Botun Kurucularından Olan {user.mention}**, {MUSIC_BOT_NAME}'nin Kurucu Listesinden Silindi."
            )
            return os.system(f"kill -9 {os.getpid()} && python3 -m Yukki")
        await message.reply_text(f"Ters giden bir şeyler oldu.")
        return
    message.from_user.id
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    if user_id not in SUDOERS:
        return await message.reply_text(
            f"Kullanıcı {MUSIC_BOT_NAME}'nin Kurucularından Değil"
        )
    removed = await remove_sudo(user_id)
    if removed:
        await message.reply_text(
            f"Botun Kurucularından Olan **{mention}**, {MUSIC_BOT_NAME}'nin Kurucu Listesinden Silindi"
        )
        return os.system(f"kill -9 {os.getpid()} && python3 -m Yukki")
    await message.reply_text(f"Ters Giden Bir Şeyler Oldu")


@app.on_message(filters.command("kuruculistesi"))
async def sudoers_list(_, message: Message):
    sudoers = await get_sudoers()
    text = "⭐️<u> **Sahip:**</u>\n"
    sex = 0
    for x in OWNER_ID:
        try:
            user = await app.get_users(x)
            user = user.first_name if not user.mention else user.mention
            sex += 1
        except Exception:
            continue
        text += f"{sex}➤ {user}\n"
    smex = 0
    for count, user_id in enumerate(sudoers, 1):
        if user_id not in OWNER_ID:
            try:
                user = await app.get_users(user_id)
                user = user.first_name if not user.mention else user.mention
                if smex == 0:
                    smex += 1
                    text += "\n⭐️<u> **Kurucular:**</u>\n"
                sex += 1
                text += f"{sex}➤ {user}\n"
            except Exception:
                continue
    if not text:
        await message.reply_text("Kurucular Yok")
    else:
        await message.reply_text(text)


### Video Limit


@app.on_message(
    filters.command(["set_video_limit", f"set_video_limit@{BOT_USERNAME}"])
    & filters.user(SUDOERS)
)
async def set_video_limit_kid(_, message: Message):
    if len(message.command) != 2:
        usage = "**Kullanım:**\n/set_video_limit [İzin Verilen Sohbet Sayısı]"
        return await message.reply_text(usage)
    message.chat.id
    state = message.text.split(None, 1)[1].strip()
    try:
        limit = int(state)
    except:
        return await message.reply_text(
            "Limiti Ayarlamak için Lütfen Sayısal Veriler Kullanın."
        )
    await set_video_limit(141414, limit)
    await message.reply_text(
        f"Sesli Sohbetlerdeki İzlenebilir Videoların Maksimum Sınırı, {limit} Sohbet için Tanımlandı."
    )


## Maintenance Yukki


@app.on_message(filters.command("bakim") & filters.user(SUDOERS))
async def maintenance(_, message):
    usage = "**Kullanım:**\n/bakim [acik|kapali]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    message.chat.id
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "acik":
        user_id = 1
        await add_on(user_id)
        await message.reply_text("Bakım Modu Aktif!")
    elif state == "kapali":
        user_id = 1
        await add_off(user_id)
        await message.reply_text("Bakım Modu Devre Dışı!")
    else:
        await message.reply_text(usage)


## Logger


@app.on_message(filters.command("logger") & filters.user(SUDOERS))
async def logger(_, message):
    if LOG_SESSION == "None":
        return await message.reply_text(
            "Kaydedici Hesabı Tanımlanmadı. \n\nLütfen `LOG_SESSION` değişkenini ayarlayın ve ardından günlüğe kaydetmeyi deneyin."
        )
    usage = "**Kullanım:**\n/logger [acik|kapali]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    message.chat.id
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "acik":
        user_id = 5
        await add_on(user_id)
        await message.reply_text("Log Etkin")
    elif state == "kapali":
        user_id = 5
        await add_off(user_id)
        await message.reply_text("Log Devre Dışı")
    else:
        await message.reply_text(usage)


## Gban Module


@app.on_message(filters.command("gban") & filters.user(SUDOERS))
async def ban_globally(_, message):
    if not message.reply_to_message:
        if len(message.command) < 2:
            await message.reply_text(
                "**Kullanım:**\n/gban [Kullanıcı Adı | Kullanıcı ID]"
            )
            return
        user = message.text.split(None, 2)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        from_user = message.from_user
        if user.id == from_user.id:
            return await message.reply_text(
                "Kendini Küresel Olarak Yasaklayamazsın. Bu Çok Mantıksız Geliyor!"
            )
        elif user.id == BOT_ID:
            await message.reply_text("Kendimi Engellememi İsteyemezsin! Bu Çok Saçma.")
        elif user.id in SUDOERS:
            await message.reply_text(
                "Bir Kurucuyu Yasaklamak Mı? Kulağa Saçma Geliyor!"
            )
        else:
            await add_gban_user(user.id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            m = await message.reply_text(
                f"**{user.mention} Üzerinde Küresel Yasaklama başlatılıyor** \n\nBeklenen Zaman: {len(served_chats)}"
            )
            number_of_chats = 0
            for sex in served_chats:
                try:
                    await app.ban_chat_member(sex, user.id)
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except Exception:
                    pass
            ban_text = f"""
__**Yeni {MUSIC_BOT_NAME} Küresel Yasaklaması**__

**Menşei:** {message.chat.title} [`{message.chat.id}`]
**Kurucu:** {from_user.mention}
**Yasaklanan Kullanıcı:** {user.mention}
**Yasaklanan Kullanıcının ID'si:** `{user.id}`
**Sohbetler:** {number_of_chats}"""
            try:
                await m.delete()
            except Exception:
                pass
            await message.reply_text(
                f"{ban_text}",
                disable_web_page_preview=True,
            )
        return
    from_user_id = message.from_user.id
    from_user_mention = message.from_user.mention
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    sudoers = await get_sudoers()
    if user_id == from_user_id:
        await message.reply_text(
            "Kendini Küresel Olarak Yasaklayamazsın. Bu Çok Mantıksız Geliyor!"
        )
    elif user_id == BOT_ID:
        await message.reply_text("Kendimi Engellememi İsteyemezsin! Bu Çok Saçma.")
    elif user_id in sudoers:
        await message.reply_text("Bir Kurucuyu Yasaklamak Mı? Kulağa Saçma Geliyor!")
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if is_gbanned:
            await message.reply_text("Kullanıcı Zaten Küresel Olarak Banlandı.")
        else:
            await add_gban_user(user_id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            m = await message.reply_text(
                f"**{mention} Üzerinde Küresel Yasaklama başlatılıyor** \n\nBeklenen Zaman: {len(served_chats)}"
            )
            number_of_chats = 0
            for sex in served_chats:
                try:
                    await app.ban_chat_member(sex, user_id)
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except Exception:
                    pass
            ban_text = f"""
__**Yeni {MUSIC_BOT_NAME} Küresel Yasaklaması**__

**Menşei:** {message.chat.title} [`{message.chat.id}`]
**Kurucu:** {from_user_mention}
**Yasaklanan Kullanıcı:** {mention}
**Yasaklanan Kullanıcının ID'si:** `{user_id}`
**Sohbetler:** {number_of_chats}"""
            try:
                await m.delete()
            except Exception:
                pass
            await message.reply_text(
                f"{ban_text}",
                disable_web_page_preview=True,
            )
            return


@app.on_message(filters.command("ungban") & filters.user(SUDOERS))
async def unban_globally(_, message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(
                "**Kullanım:**\n/ungban [Kullanıcı Adı | Kullanıcı ID]"
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        from_user = message.from_user
        sudoers = await get_sudoers()
        if user.id == from_user.id:
            await message.reply_text("Bu İşlemi Kendin İçin Kullanamazsın!")
        elif user.id == BOT_ID:
            await message.reply_text(
                "Zaten Kendimi Yasaklamam Mümkün Değilken Yasağımı Kaldırmaya Çalışma."
            )
        elif user.id in sudoers:
            await message.reply_text(
                "Kurucuları Yasaklayamaz Veya Yasağını Kaldıramazsınız!"
            )
        else:
            is_gbanned = await is_gbanned_user(user.id)
            if not is_gbanned:
                await message.reply_text(
                    "Kullanıcı Zaten özgür, neden ona zorbalık ediyorsun?"
                )
            else:
                await remove_gban_user(user.id)
                await message.reply_text(f"Küresel Yasaklama Kaldırıldı!")
        return
    from_user_id = message.from_user.id
    user_id = message.reply_to_message.from_user.id
    message.reply_to_message.from_user.mention
    sudoers = await get_sudoers()
    if user_id == from_user_id:
        await message.reply_text("Bu İşlemi Kendin İçin Kullanamazsın.")
    elif user_id == BOT_ID:
        await message.reply_text(
            "Zaten Kendimi Yasaklamam Mümkün Değilken Yasağımı Kaldırmaya Çalışma."
        )
    elif user_id in sudoers:
        await message.reply_text(
            "Kurucuları Yasaklayamaz Veya Yasağını Kaldıramazsınız!"
        )
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if not is_gbanned:
            await message.reply_text(
                "Kullanıcı Zaten özgür, neden ona zorbalık ediyorsun?"
            )
        else:
            await remove_gban_user(user_id)
            await message.reply_text(f"Küresel Yasaklama Kaldırıldı!")


# Broadcast Message


@app.on_message(filters.command("broadcast_pin") & filters.user(SUDOERS))
async def broadcast_message_pin_silent(_, message):
    if not message.reply_to_message:
        pass
    else:
        x = message.reply_to_message.message_id
        y = message.chat.id
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = await app.forward_messages(i, y, x)
                try:
                    await m.pin(disable_notification=True)
                    pin += 1
                except Exception:
                    pass
                await asyncio.sleep(0.3)
                sent += 1
            except Exception:
                pass
        await message.reply_text(
            f"**{sent} sohbette {pin} sabitli mesaj ile yayınlandı.**"
        )
        return
    if len(message.command) < 2:
        await message.reply_text(
            "**Kullanım**:\n/broadcast [Mesaj] ya da [Bir Mesajı Yanıtlama]"
        )
        return
    text = message.text.split(None, 1)[1]
    sent = 0
    pin = 0
    chats = []
    schats = await get_served_chats()
    for chat in schats:
        chats.append(int(chat["chat_id"]))
    for i in chats:
        try:
            m = await app.send_message(i, text=text)
            try:
                await m.pin(disable_notification=True)
                pin += 1
            except Exception:
                pass
            await asyncio.sleep(0.3)
            sent += 1
        except Exception:
            pass
    await message.reply_text(f"**{sent} sohbette {pin} sabitli mesaj ile yayınlandı.**")


@app.on_message(filters.command("broadcast_pin_loud") & filters.user(SUDOERS))
async def broadcast_message_pin_loud(_, message):
    if not message.reply_to_message:
        pass
    else:
        x = message.reply_to_message.message_id
        y = message.chat.id
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = await app.forward_messages(i, y, x)
                try:
                    await m.pin(disable_notification=False)
                    pin += 1
                except Exception:
                    pass
                await asyncio.sleep(0.3)
                sent += 1
            except Exception:
                pass
        await message.reply_text(
            f"**{sent} sohbette {pin} sabitli mesaj ile yayınlandı.**"
        )
        return
    if len(message.command) < 2:
        await message.reply_text(
            "**Kullanım**:\n/broadcast [Mesaj] ya da [Bir Mesajı Yanıtlama]"
        )
        return
    text = message.text.split(None, 1)[1]
    sent = 0
    pin = 0
    chats = []
    schats = await get_served_chats()
    for chat in schats:
        chats.append(int(chat["chat_id"]))
    for i in chats:
        try:
            m = await app.send_message(i, text=text)
            try:
                await m.pin(disable_notification=False)
                pin += 1
            except Exception:
                pass
            await asyncio.sleep(0.3)
            sent += 1
        except Exception:
            pass
    await message.reply_text(f"**{sent} sohbette {pin} sabitli mesaj ile yayınlandı.**")


@app.on_message(filters.command("broadcast") & filters.user(SUDOERS))
async def broadcast(_, message):
    if not message.reply_to_message:
        pass
    else:
        x = message.reply_to_message.message_id
        y = message.chat.id
        sent = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = await app.forward_messages(i, y, x)
                await asyncio.sleep(0.3)
                sent += 1
            except Exception:
                pass
        await message.reply_text(f"**{sent} Sohbette Mesaj Yayınlandı.**")
        return
    if len(message.command) < 2:
        await message.reply_text(
            "**Kullanım**:\n/broadcast [Mesaj] ya da [Bir Mesajı Yanıtlama]"
        )
        return
    text = message.text.split(None, 1)[1]
    sent = 0
    chats = []
    schats = await get_served_chats()
    for chat in schats:
        chats.append(int(chat["chat_id"]))
    for i in chats:
        try:
            m = await app.send_message(i, text=text)
            await asyncio.sleep(0.3)
            sent += 1
        except Exception:
            pass
    await message.reply_text(f"**{sent} Sohbette Mesaj Yayınlandı.**")


# Clean


@app.on_message(filters.command("clean") & filters.user(SUDOERS))
async def clean(_, message):
    dir = "downloads"
    dir1 = "cache"
    shutil.rmtree(dir)
    shutil.rmtree(dir1)
    os.mkdir(dir)
    os.mkdir(dir1)
    await message.reply_text("Tüm **temp** dizin(ler)i başarıyla temizlendi!")
