import asyncio
import os
from asyncio import QueueEmpty

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

from Yukki import MUSIC_BOT_NAME, app, db_mem
from Yukki.Core.PyTgCalls import Queues
from Yukki.Core.PyTgCalls.Converter import convert
from Yukki.Core.PyTgCalls.Downloader import download
from Yukki.Core.PyTgCalls.Yukki import (
    pause_stream,
    resume_stream,
    skip_stream,
    skip_video_stream,
    stop_stream,
)
from Yukki.Database import (
    is_active_chat,
    is_music_playing,
    music_off,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
)
from Yukki.Decorators.admins import AdminRightsCheck
from Yukki.Decorators.checker import checker
from Yukki.Inline import audio_markup, primary_markup, secondary_markup2
from Yukki.Utilities.changers import time_to_seconds
from Yukki.Utilities.chat import specialfont_to_normal
from Yukki.Utilities.theme import check_theme
from Yukki.Utilities.thumbnails import gen_thumb
from Yukki.Utilities.timer import start_timer
from Yukki.Utilities.youtube import get_m3u8, get_yt_info_id

loop = asyncio.get_event_loop()


__MODULE__ = "Sesli Sohbet"
__HELP__ = """


/durdur
- Sesli sohbette çalan müziği duraklatın.

/devam
- Sesli sohbette duraklatılmış müziği devam ettirin.

/atla
- Sesli sohbette çalmakta olan müziği atla.

/bitir veya /stop
- Akışı durdurun.

/sıra
- Sıra listesini kontrol edin.


**Not:**
Yalnızca Kurucular için

/aktifses
- Botta aktif sesli sohbetleri kontrol edin.

/aktifvideo
- Botta aktif görüntülü aramaları kontrol edin.
"""


@app.on_message(
    filters.command(["durdur", "atla", "devam", "stop", "bitir"]) & filters.group
)
@AdminRightsCheck
@checker
async def admins(_, message: Message):
    global get_queue
    if not len(message.command) == 1:
        return await message.reply_text("Hata! Komutun Yanlış Kullanımı.")
    if not await is_active_chat(message.chat.id):
        return await message.reply_text("Sesli sohbette hiçbir şey oynatılmıyor.")
    chat_id = message.chat.id
    if message.command[0][1] == "a":
        if not await is_music_playing(message.chat.id):
            return await message.reply_text("Müzik zaten Duraklatıldı.")
        await music_off(chat_id)
        await pause_stream(chat_id)
        await message.reply_text(f"🎧 Sesli sohbet {message.from_user.mention} tarafından duraklatıldı!")
    if message.command[0][1] == "e":
        if await is_music_playing(message.chat.id):
            return await message.reply_text("Müzik zaten Çalıyor.")
        await music_on(chat_id)
        await resume_stream(chat_id)
        await message.reply_text(f"🎧 Sesli sohbet {message.from_user.mention} tarafından devam ettirildi!")
    if message.command[0][1] == "t" or message.command[0][1] == "n":
        if message.chat.id not in db_mem:
            db_mem[message.chat.id] = {}
        wtfbro = db_mem[message.chat.id]
        wtfbro["live_check"] = False
        try:
            Queues.clear(message.chat.id)
        except QueueEmpty:
            pass
        await remove_active_chat(chat_id)
        await remove_active_video_chat(chat_id)
        await stop_stream(chat_id)
        await message.reply_text(
            f"🎧 Sesli sohbet {message.from_user.mention} tarafından bitirildi!"
        )
    if message.command[0][1] == "k":
        if message.chat.id not in db_mem:
            db_mem[message.chat.id] = {}
        wtfbro = db_mem[message.chat.id]
        wtfbro["live_check"] = False
        Queues.task_done(chat_id)
        if Queues.is_empty(chat_id):
            await remove_active_chat(chat_id)
            await remove_active_video_chat(chat_id)
            await message.reply_text(
               "**Kuyrukta artık müzik yok.** \n\n**Sesli Sohbetten Çıkılıyor**"
            )
            await stop_stream(chat_id)
            return
        else:
            videoid = Queues.get(chat_id)["file"]
            got_queue = get_queue.get(chat_id)
            if got_queue:
                got_queue.pop(0)
            finxx = f"{videoid[0]}{videoid[1]}{videoid[2]}"
            aud = 0
            if str(finxx) == "raw":
                await skip_stream(chat_id, videoid)
                afk = videoid
                title = db_mem[videoid]["title"]
                duration_min = db_mem[videoid]["duration"]
                duration_sec = int(time_to_seconds(duration_min))
                mention = db_mem[videoid]["username"]
                videoid = db_mem[videoid]["videoid"]
                if str(videoid) == "smex1":
                    buttons = buttons = audio_markup(
                        videoid,
                        message.from_user.id,
                        duration_min,
                        duration_min,
                    )
                    thumb = "Utils/Telegram.JPEG"
                    aud = 1
                else:
                    _path_ = _path_ = (
                        (str(afk))
                        .replace("_", "", 1)
                        .replace("/", "", 1)
                        .replace(".", "", 1)
                    )
                    thumb = f"cache/{_path_}final.png"
                    buttons = primary_markup(
                        videoid,
                        message.from_user.id,
                        duration_min,
                        duration_min,
                    )
                final_output = await message.reply_photo(
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=f"**Parça Atlandı**\n\n🎥 **Oynamaya başlayan parça**: {title} \n⏳ **Süre**: {duration_min} \n👤 **Talep Eden**: {mention}",
                )
                await start_timer(
                    videoid,
                    duration_min,
                    duration_sec,
                    final_output,
                    message.chat.id,
                    message.from_user.id,
                    aud,
                )
            elif str(finxx) == "s1s":
                mystic = await message.reply_text(
                    "Atlandı.. Sonraki Video Akışına geçiliyor."
                )
                afk = videoid
                read = (str(videoid)).replace("s1s_", "", 1)
                s = read.split("_+_")
                quality = s[0]
                videoid = s[1]
                if int(quality) == 1080:
                    try:
                        await skip_video_stream(chat_id, videoid, 720, mystic)
                    except Exception as e:
                        return await mystic.edit(
                            f"Video akışı değiştirilirken hata oluştu. \n\nSebep:- {e}"
                        )
                    buttons = secondary_markup2("Smex1", message.from_user.id)
                    mention = db_mem[afk]["username"]
                    await mystic.delete()
                    final_output = await message.reply_photo(
                        photo="Utils/Telegram.JPEG",
                        reply_markup=InlineKeyboardMarkup(buttons),
                        caption=(
                            f"**Görüntülü Sohbet Atlandı** \n\n👤**Talep Eden:** {mention}"
                        ),
                    )
                    await mystic.delete()
                else:
                    (
                        title,
                        duration_min,
                        duration_sec,
                        thumbnail,
                    ) = get_yt_info_id(videoid)
                    nrs, ytlink = await get_m3u8(videoid)
                    if nrs == 0:
                        return await mystic.edit(
                            "Video Biçimleri getirilemedi.",
                        )
                    try:
                        await skip_video_stream(chat_id, ytlink, quality, mystic)
                    except Exception as e:
                        return await mystic.edit(
                            f"Video akışı değiştirilirken hata oluştu. \n\nSebep:- {e}"
                        )
                    theme = await check_theme(chat_id)
                    c_title = message.chat.title
                    user_id = db_mem[afk]["user_id"]
                    chat_title = await specialfont_to_normal(c_title)
                    thumb = await gen_thumb(
                        thumbnail, title, user_id, theme, chat_title
                    )
                    buttons = primary_markup(
                        videoid, user_id, duration_min, duration_min
                    )
                    mention = db_mem[afk]["username"]
                    await mystic.delete()
                    final_output = await message.reply_photo(
                        photo=thumb,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        caption=(
                            f"**Video Akışı Atlandı** \n\n🎥 **Oynatılmaya Başlanan Video**: [{title[:25]}](https://www.youtube.com/watch?v={videoid}) \n👤**Talep Eden**: {mention}"
                        ),
                    )
                    await mystic.delete()
                    os.remove(thumb)
                    await start_timer(
                        videoid,
                        duration_min,
                        duration_sec,
                        final_output,
                        message.chat.id,
                        message.from_user.id,
                        aud,
                    )
            else:
                mystic = await message.reply_text(
                    f"**{MUSIC_BOT_NAME} Çalma Listesi İşlevi** \n\n**Çalma Listesinden Sonraki Müzikleri İndirme...**"
                )
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                ) = get_yt_info_id(videoid)
                await mystic.edit(
                    f"**{MUSIC_BOT_NAME} İndirici** \n\n**Başlık:** {title[:50]}\n\n0% ▓▓▓▓▓▓▓▓▓▓▓▓ 100%"
                )
                downloaded_file = await loop.run_in_executor(
                    None, download, videoid, mystic, title
                )
                raw_path = await convert(downloaded_file)
                await skip_stream(chat_id, raw_path)
                theme = await check_theme(chat_id)
                chat_title = await specialfont_to_normal(message.chat.title)
                thumb = await gen_thumb(
                    thumbnail, title, message.from_user.id, theme, chat_title
                )
                buttons = primary_markup(
                    videoid, message.from_user.id, duration_min, duration_min
                )
                await mystic.delete()
                mention = db_mem[videoid]["username"]
                final_output = await message.reply_photo(
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=(
                        f"**Müzik Akışı Atlandı** \n\n🎥 **Oynatılmaya Başlanan Parça**:[{title[:25]}](https://www.youtube.com/watch?v={videoid}) \n⏳ **Süre**: {duration_min} Dakika \n👤**Talep Eden**: {mention}"
                    ),
                )
                os.remove(thumb)
                await start_timer(
                    videoid,
                    duration_min,
                    duration_sec,
                    final_output,
                    message.chat.id,
                    message.from_user.id,
                    aud,
                )
