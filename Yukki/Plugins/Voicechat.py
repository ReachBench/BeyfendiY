import asyncio
import os

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

from Yukki import SUDOERS, app, db_mem
from Yukki.Database import (
    get_active_chats,
    get_active_video_chats,
    get_assistant,
    is_active_chat,
)
from Yukki.Inline import primary_markup
from Yukki.Utilities.assistant import get_assistant_details

loop = asyncio.get_event_loop()

__MODULE__ = "Katıl/Ayrıl"
__HELP__ = """

**Not:**
Yalnızca Kurucular ve Grup Yetkilileri İçindir


/katil [Sohbet Kullanıcı Adı veya Sohbet Kimliği]
- Asistanı Botun Olduğu Bir Gruba Ekler.


/ayril [Sohbet Kullanıcı Adı veya Sohbet Kimliği]
- Asistan belirli bir gruptan ayrılacaktır.


/botayril [Sohbet Kullanıcı Adı veya Sohbet Kimliği]
- Bot belirli sohbeti terk eder.
"""


@app.on_callback_query(filters.regex("pr_go_back_timer"))
async def pr_go_back_timer(_, CallbackQuery):
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    videoid, user_id = callback_request.split("|")
    if await is_active_chat(CallbackQuery.message.chat.id):
        if db_mem[CallbackQuery.message.chat.id]["videoid"] == videoid:
            dur_left = db_mem[CallbackQuery.message.chat.id]["left"]
            duration_min = db_mem[CallbackQuery.message.chat.id]["total"]
            buttons = primary_markup(videoid, user_id, dur_left, duration_min)
            await CallbackQuery.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(buttons)
            )


@app.on_callback_query(filters.regex("timer_checkup_markup"))
async def timer_checkup_markup(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    videoid, user_id = callback_request.split("|")
    if await is_active_chat(CallbackQuery.message.chat.id):
        if db_mem[CallbackQuery.message.chat.id]["videoid"] == videoid:
            dur_left = db_mem[CallbackQuery.message.chat.id]["left"]
            duration_min = db_mem[CallbackQuery.message.chat.id]["total"]
            return await CallbackQuery.answer(
                f"{duration_min} Dakikadan kalan {dur_left}.",
                show_alert=True,
            )
        return await CallbackQuery.answer(f"Oynatılan Bir Şey Yok.", show_alert=True)
    else:
        return await CallbackQuery.answer(f"Sesli Sohbet Açık Değil", show_alert=True)


@app.on_message(filters.command("queue"))
async def activevc(_, message: Message):
    global get_queue
    if await is_active_chat(message.chat.id):
        mystic = await message.reply_text("Lütfen Bekleyiniz... Sıraya Alınıyor...")
        dur_left = db_mem[message.chat.id]["left"]
        db_mem[message.chat.id]["total"]
        got_queue = get_queue.get(message.chat.id)
        if not got_queue:
            await mystic.edit(f"Sıra Boş")
        fetched = []
        for get in got_queue:
            fetched.append(get)

        ### Results
        current_playing = fetched[0][0]
        user_name = fetched[0][1]

        msg = "**Sıra Listesi**\n\n"
        msg += "**Çalmakta Olan:**"
        msg += "\n▶️" + current_playing[:30]
        msg += f"\n   ╚Talep Eden:- {user_name}"
        msg += f"\n   ╚Süre:- {duration_limit} sürenin dışında kalan {dur_left}"
        fetched.pop(0)
        if fetched:
            msg += "\n\n"
            msg += "**Sıradaki Kuyruk:**"
            for song in fetched:
                name = song[0][:30]
                usr = song[1]
                dur = song[2]
                msg += f"\n⏸️{name}"
                msg += f"\n   ╠Süre : {dur}"
                msg += f"\n   ╚Talep Eden : {usr}\n"
        if len(msg) > 4096:
            await mystic.delete()
            filename = "queue.txt"
            with open(filename, "w+", encoding="utf8") as out_file:
                out_file.write(str(msg.strip()))
            await message.reply_document(
                document=filename,
                caption=f"**Çıktı:**\n\n`Sıradakiler Listesi`",
                quote=False,
            )
            os.remove(filename)
        else:
            await mystic.edit(msg)
    else:
        await message.reply_text(f"Sıra yok")


@app.on_message(filters.command("activevc") & filters.user(SUDOERS))
async def activevc(_, message: Message):
    served_chats = []
    try:
        chats = await get_active_chats()
        for chat in chats:
            served_chats.append(int(chat["chat_id"]))
    except Exception as e:
        await message.reply_text(f"**Hata:-** {e}")
    text = ""
    j = 0
    for x in served_chats:
        try:
            title = (await app.get_chat(x)).title
        except Exception:
            title = "Private Group"
        if (await app.get_chat(x)).username:
            user = (await app.get_chat(x)).username
            text += f"<b>{j + 1}.</b>  [{title}](https://t.me/{user})[`{x}`]\n"
        else:
            text += f"<b>{j + 1}. {title}</b> [`{x}`]\n"
        j += 1
    if not text:
        await message.reply_text("Sesli Sohbet Açık Değil ")
    else:
        await message.reply_text(
            f"**Sesli Sohbette Müzik Aktif:-**\n\n{text}",
            disable_web_page_preview=True,
        )


@app.on_message(filters.command("activevideo") & filters.user(SUDOERS))
async def activevi_(_, message: Message):
    served_chats = []
    try:
        chats = await get_active_video_chats()
        for chat in chats:
            served_chats.append(int(chat["chat_id"]))
    except Exception as e:
        await message.reply_text(f"**Hata:-** {e}")
    text = ""
    j = 0
    for x in served_chats:
        try:
            title = (await app.get_chat(x)).title
        except Exception:
            title = "Private Group"
        if (await app.get_chat(x)).username:
            user = (await app.get_chat(x)).username
            text += f"<b>{j + 1}.</b>  [{title}](https://t.me/{user})[`{x}`]\n"
        else:
            text += f"<b>{j + 1}. {title}</b> [`{x}`]\n"
        j += 1
    if not text:
        await message.reply_text("Sesli Sohbet Açık Değil")
    else:
        await message.reply_text(
            f"**Sesli Sohbette Video Aktif:-**\n\n{text}",
            disable_web_page_preview=True,
        )


@app.on_message(filters.command("katil") & filters.user(SUDOERS))
async def basffy(_, message):
    if len(message.command) != 2:
        await message.reply_text(
            "**Kullanım:**\n/katil [Sohbet Kullanıcı Adı Veya Sohbet ID'si]"
        )
        return
    chat = message.text.split(None, 2)[1]
    try:
        chat_id = (await app.get_chat(chat)).id
    except:
        return await message.reply_text(
            "Önce bu Sohbete Botu Ekle.. Bot Bu Sohbeti Tanımıyor."
        )
    _assistant = await get_assistant(chat_id, "assistant")
    if not _assistant:
        return await message.reply_text(
            "Bu Grupta Kaydedilmiş Asistan Bulunamadı\n\n/asistanayarla komutu ile asistan ayarlayabilirsiniz."
        )
    else:
        ran_ass = _assistant["saveassistant"]
    ASS_ID, ASS_NAME, ASS_USERNAME, ASS_ACC = await get_assistant_details(ran_ass)
    try:
        await ASS_ACC.join_chat(chat_id)
    except Exception as e:
        await message.reply_text(f"Başarısız\n**Sebebi Şu Olabilir**:{e}")
        return
    await message.reply_text("Asistan Sohbete Katıldı.")


@app.on_message(filters.command("botayril") & filters.user(SUDOERS))
async def baaaf(_, message):
    if len(message.command) != 2:
        await message.reply_text(
            "**Kullanım:**\n/botayril [Sohbet Kullanıcı Adı Veya Sohbet ID'si]"
        )
        return
    chat = message.text.split(None, 2)[1]
    try:
        await app.leave_chat(chat)
    except Exception as e:
        await message.reply_text(f"Başarısız\n**Sebebi Şu Olabilir**:{e}")
        print(e)
        return
    await message.reply_text("Bot Sohbetten Başarıyla Ayrıldı")


@app.on_message(filters.command("ayril") & filters.user(SUDOERS))
async def baujaf(_, message):
    if len(message.command) != 2:
        await message.reply_text(
            "**Kullanım:**\n/ayril [Sohbet Kullanıcı Adı Veya Sohbet ID'si]"
        )
        return
    chat = message.text.split(None, 2)[1]
    try:
        chat_id = (await app.get_chat(chat)).id
    except:
        return await message.reply_text(
            "Önce Botu Gruba Ekleyin... Bot Bu Sohbeti Tanımıyor."
        )
    _assistant = await get_assistant(chat, "assistant")
    if not _assistant:
        return await message.reply_text(
            "Bu Grupta Kaydedilmiş Asistan Bulunamadı\n\n/asistanayarla komutu ile asistan ayarlayabilirsiniz."
        )
    else:
        ran_ass = _assistant["saveassistant"]
    ASS_ID, ASS_NAME, ASS_USERNAME, ASS_ACC = await get_assistant_details(ran_ass)
    try:
        await ASS_ACC.leave_chat(chat_id)
    except Exception as e:
        await message.reply_text(f"Başarısız\n**Sebebi Şu Olabilir**:{e}")
        return
    await message.reply_text("Asistan Başarıyla Ayrıldı.")
