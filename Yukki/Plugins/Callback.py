import asyncio
import os
from asyncio import QueueEmpty

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup

from Yukki import BOT_USERNAME, MUSIC_BOT_NAME, app, db_mem
from Yukki.Core.PyTgCalls import Queues
from Yukki.Core.PyTgCalls.Converter import convert
from Yukki.Core.PyTgCalls.Downloader import download
from Yukki.Core.PyTgCalls.Yukki import (
    join_stream,
    pause_stream,
    resume_stream,
    skip_stream,
    skip_video_stream,
    stop_stream,
)
from Yukki.Database import (
    delete_playlist,
    get_playlist,
    get_playlist_names,
    is_active_chat,
    remove_active_video_chat,
    save_playlist,
)
from Yukki.Database.queue import (
    add_active_chat,
    is_active_chat,
    is_music_playing,
    music_off,
    music_on,
    remove_active_chat,
)
from Yukki.Decorators.admins import AdminRightsCheckCB
from Yukki.Decorators.checker import checkerCB
from Yukki.Inline import (
    audio_markup,
    audio_markup2,
    download_markup,
    fetch_playlist,
    paste_queue_markup,
    primary_markup,
    secondary_markup2,
)
from Yukki.Utilities.changers import time_to_seconds
from Yukki.Utilities.chat import specialfont_to_normal
from Yukki.Utilities.paste import isPreviewUp, paste_queue
from Yukki.Utilities.theme import check_theme
from Yukki.Utilities.thumbnails import gen_thumb
from Yukki.Utilities.timer import start_timer
from Yukki.Utilities.youtube import get_m3u8, get_yt_info_id

loop = asyncio.get_event_loop()


@app.on_callback_query(filters.regex("forceclose"))
async def forceclose(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    query, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "Bunu kapatmanıza izin verilmiyor!", show_alert=True
        )
    await CallbackQuery.message.delete()
    await CallbackQuery.answer()


@app.on_callback_query(filters.regex(pattern=r"^(pausecb|skipcb|stopcb|resumecb)$"))
@AdminRightsCheckCB
@checkerCB
async def admin_risghts(_, CallbackQuery):
    global get_queue
    command = CallbackQuery.matches[0].group(1)
    if not await is_active_chat(CallbackQuery.message.chat.id):
        return await CallbackQuery.answer(
            "Sesli sohbette hiçbir şey çalmıyor!", show_alert=True
        )
    chat_id = CallbackQuery.message.chat.id
    if command == "pausecb":
        if not await is_music_playing(chat_id):
            return await CallbackQuery.answer(
                "Müzik zaten Duraklatıldı.", show_alert=True
            )
        await music_off(chat_id)
        await pause_stream(chat_id)
        await CallbackQuery.message.reply_text(
            f"🎧 Sesli sohbet {CallbackQuery.from_user.mention} tarafından durduruldu!",
            reply_markup=audio_markup2,
        )
        await CallbackQuery.message.delete()
        await CallbackQuery.answer("Durduruldu", show_alert=True)
    if command == "resumecb":
        if await is_music_playing(chat_id):
            return await CallbackQuery.answer(
                "Müzik zaten devam ediyor.", show_alert=True
            )
        await music_on(chat_id)
        await resume_stream(chat_id)
        await CallbackQuery.message.reply_text(
            f"🎧 Sesli sohbet {CallbackQuery.from_user.mention} tarafından devam ettirildi!",
            reply_markup=audio_markup2,
        )
        await CallbackQuery.message.delete()
        await CallbackQuery.answer("Devam ettirildi", show_alert=True)
    if command == "stopcb":
        if CallbackQuery.message.chat.id not in db_mem:
            db_mem[CallbackQuery.message.chat.id] = {}
        wtfbro = db_mem[CallbackQuery.message.chat.id]
        wtfbro["live_check"] = False
        try:
            Queues.clear(chat_id)
        except QueueEmpty:
            pass
        await remove_active_chat(chat_id)
        await remove_active_video_chat(chat_id)
        await stop_stream(chat_id)
        await CallbackQuery.message.reply_text(
            f"🎧 Sesli sohbet {CallbackQuery.from_user.mention} tarafından bitirildi/sonlandırıldı!",
            reply_markup=audio_markup2,
        )
        await CallbackQuery.message.delete()
        await CallbackQuery.answer("Bitirildi", show_alert=True)
    if command == "skipcb":
        if CallbackQuery.message.chat.id not in db_mem:
            db_mem[CallbackQuery.message.chat.id] = {}
        wtfbro = db_mem[CallbackQuery.message.chat.id]
        wtfbro["live_check"] = False
        Queues.task_done(chat_id)
        if Queues.is_empty(chat_id):
            await remove_active_chat(chat_id)
            await remove_active_video_chat(chat_id)
            await CallbackQuery.message.reply_text(
                f"Kuyrukta daha fazla müzik yok. \n\nAsistan sesli sohbetten ayrılıyor...Butona basan kişi:- {CallbackQuery.from_user.mention}"
            )
            await stop_stream(chat_id)
            await CallbackQuery.message.delete()
            await CallbackQuery.answer(
                "Atlandı. Sırada artık müzik yok!", show_alert=True
            )
            return
        else:
            videoid = Queues.get(chat_id)["file"]
            got_queue = get_queue.get(CallbackQuery.message.chat.id)
            if got_queue:
                got_queue.pop(0)
            finxx = f"{videoid[0]}{videoid[1]}{videoid[2]}"
            aud = 0
            if str(finxx) == "raw":
                await CallbackQuery.message.delete()
                await CallbackQuery.answer("Atlandı!", show_alert=True)
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
                        CallbackQuery.from_user.id,
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
                        CallbackQuery.from_user.id,
                        duration_min,
                        duration_min,
                    )
                final_output = await CallbackQuery.message.reply_photo(
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=f"**Sesli Sohbet Atlandı** \n\n🎥 **Oynatılmaya Başlanan Parça**: {title} \n⏳ **Süre: {duration_min} \n👤 Talep Eden: {mention}",
                )
                await start_timer(
                    videoid,
                    duration_min,
                    duration_sec,
                    final_output,
                    CallbackQuery.message.chat.id,
                    CallbackQuery.message.from_user.id,
                    aud,
                )
            if str(finxx) == "s1s":
                afk = videoid
                await CallbackQuery.answer()
                mystic = await CallbackQuery.message.reply_text(
                    "Atlandı! Lütfen Video Akışının Değiştirilmesini Bekleyin..."
                )
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
                    buttons = secondary_markup2("Smex1", CallbackQuery.from_user.id)
                    mention = db_mem[afk]["username"]
                    await mystic.delete()
                    final_output = await CallbackQuery.message.reply_photo(
                        photo="Utils/Telegram.JPEG",
                        reply_markup=InlineKeyboardMarkup(buttons),
                        caption=(f"**Video Atlandı**\n\n👤**Talep Eden:** {mention}"),
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
                    c_title = CallbackQuery.message.chat.title
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
                    final_output = await CallbackQuery.message.reply_photo(
                        photo=thumb,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        caption=(
                            f"**Görüntülü Sohbet atlandı.** \n\n🎥 Video Oynatmaya Başlandı: [{title[:25]}](https://www.youtube.com/watch?v={videoid}) \n👤**Talep eden:** {mention}"
                        ),
                    )
                    os.remove(thumb)
                    await start_timer(
                        videoid,
                        duration_min,
                        duration_sec,
                        final_output,
                        CallbackQuery.message.chat.id,
                        CallbackQuery.message.from_user.id,
                        aud,
                    )
            else:
                await CallbackQuery.message.delete()
                await CallbackQuery.answer(
                    "Atlandı! Oynatma Listesi Oynatılıyor...", show_alert=True
                )
                mystic = await CallbackQuery.message.reply_text(
                    f"**{MUSIC_BOT_NAME} Çalma Listesi İşlevi** \n\nÇalma Listesinden Sonraki Müzik İndiriliyor...\n\nButonu Kullanan Kişi :- {CallbackQuery.from_user.mention}"
                )
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                ) = get_yt_info_id(videoid)
                await mystic.edit(
                    f"**{MUSIC_BOT_NAME} İndirici** \n\n**Başlık:** {title[:50]} \n\n0% ▓▓▓▓▓▓▓▓▓▓▓▓ 100%"
                )
                downloaded_file = await loop.run_in_executor(
                    None, download, videoid, mystic, title
                )
                raw_path = await convert(downloaded_file)
                await skip_stream(chat_id, raw_path)
                theme = await check_theme(chat_id)
                chat_title = await specialfont_to_normal(
                    CallbackQuery.message.chat.title
                )
                thumb = await gen_thumb(
                    thumbnail,
                    title,
                    CallbackQuery.from_user.id,
                    theme,
                    chat_title,
                )
                buttons = primary_markup(
                    videoid,
                    CallbackQuery.from_user.id,
                    duration_min,
                    duration_min,
                )
                await mystic.delete()
                mention = db_mem[videoid]["username"]
                final_output = await CallbackQuery.message.reply_photo(
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=(
                        f"**Video Atlandı** \n\n🎥 Başlatılan Oynatma: [{title[:25]}](https://www.youtube.com/watch?v={videoid}) \n⏳ **Süre**: {duration_min} Dakika \n👤**Talep Eden**: {mention}"
                    ),
                )
                os.remove(thumb)
                await start_timer(
                    videoid,
                    duration_min,
                    duration_sec,
                    final_output,
                    CallbackQuery.message.chat.id,
                    CallbackQuery.message.from_user.id,
                    aud,
                )


@app.on_callback_query(filters.regex("play_playlist"))
async def play_playlist(_, CallbackQuery):
    global get_queue
    loop = asyncio.get_event_loop()
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    callback_request = callback_data.split(None, 1)[1]
    user_id, smex, type = callback_request.split("|")
    chat_title = CallbackQuery.message.chat.title
    user_id = int(user_id)
    if chat_id not in db_mem:
        db_mem[chat_id] = {}
    if smex == "third":
        _playlist = await get_playlist_names(user_id, type)
        try:
            user = await app.get_users(user_id)
            third_name = user.first_name
        except:
            third_name = "Deleted Account"
    elif smex == "Personal":
        if CallbackQuery.from_user.id != int(user_id):
            return await CallbackQuery.answer(
                "Bu sana göre değil! Kendi çalma listeni çal", show_alert=True
            )
        _playlist = await get_playlist_names(user_id, type)
        third_name = CallbackQuery.from_user.first_name
    elif smex == "Group":
        _playlist = await get_playlist_names(CallbackQuery.message.chat.id, type)
        user_id = CallbackQuery.message.chat.id
        third_name = chat_title
    else:
        return await CallbackQuery.answer("Çalma Listesi Hatası")
    if CallbackQuery.message.chat.id not in db_mem:
        db_mem[CallbackQuery.message.chat.id] = {}
    try:
        read1 = db_mem[CallbackQuery.message.chat.id]["live_check"]
        if read1:
            return await CallbackQuery.answer(
                "Canlı Akış Oynatma... Çalma listesini oynatmak için durdurun",
                show_alert=True,
            )
        else:
            pass
    except:
        pass
    if not _playlist:
        return await CallbackQuery.answer(
            f"Bu Kullanıcının sunucularda oynatma listesi yok..", show_alert=True
        )
    else:
        await CallbackQuery.message.delete()
        mystic = await CallbackQuery.message.reply_text(
            f"{third_name} İsimli Çalma Listesi Başlatıldı. \n\nTalep Eden:- {CallbackQuery.from_user.first_name}"
        )
        msg = f"Sıraya Alınmış Oynatma Listesi:\n\n"
        j = 0
        for_t = 0
        for_p = 0
        for shikhar in _playlist:
            _note = await get_playlist(user_id, shikhar, type)
            title = _note["title"]
            videoid = _note["videoid"]
            url = f"https://www.youtube.com/watch?v={videoid}"
            duration = _note["duration"]
            if await is_active_chat(chat_id):
                position = await Queues.put(chat_id, file=videoid)
                j += 1
                for_p = 1
                msg += f"{j}- {title[:50]}\n"
                msg += f"Sıradaki Pozisyon- {position}\n\n"
                if videoid not in db_mem:
                    db_mem[videoid] = {}
                db_mem[videoid]["username"] = CallbackQuery.from_user.mention
                db_mem[videoid]["chat_title"] = chat_title
                db_mem[videoid]["user_id"] = user_id
                got_queue = get_queue.get(CallbackQuery.message.chat.id)
                title = title
                user = CallbackQuery.from_user.first_name
                duration = duration
                to_append = [title, user, duration]
                got_queue.append(to_append)
            else:
                loop = asyncio.get_event_loop()
                send_video = videoid
                for_t = 1
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                ) = get_yt_info_id(videoid)
                mystic = await mystic.edit(
                    f"**{MUSIC_BOT_NAME} İndirici** \n\n**Başlık:** {title[:50]} \n\n0% ▓▓▓▓▓▓▓▓▓▓▓▓ 100%"
                )
                downloaded_file = await loop.run_in_executor(
                    None, download, videoid, mystic, title
                )
                raw_path = await convert(downloaded_file)
                if not await join_stream(chat_id, raw_path):
                    return await mystic.edit(
                        "Sesli Sohbete Katılma Hatası. Sesli Sohbetin Açık olduğundan emin olun."
                    )
                theme = await check_theme(chat_id)
                chat_title = await specialfont_to_normal(chat_title)
                thumb = await gen_thumb(
                    thumbnail,
                    title,
                    CallbackQuery.from_user.id,
                    theme,
                    chat_title,
                )
                buttons = primary_markup(
                    videoid,
                    CallbackQuery.from_user.id,
                    duration_min,
                    duration_min,
                )
                await mystic.delete()
                get_queue[CallbackQuery.message.chat.id] = []
                got_queue = get_queue.get(CallbackQuery.message.chat.id)
                title = title
                user = CallbackQuery.from_user.first_name
                duration = duration_min
                to_append = [title, user, duration]
                got_queue.append(to_append)
                await music_on(chat_id)
                await add_active_chat(chat_id)
                cap = f"🎥 Oynatılıyor: [{title[:25]}](https://www.youtube.com/watch?v={videoid}) \n💡 Bilgi: [Ek Bilgi Alın](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n👤**Talep Eden**: {CallbackQuery.from_user.mention}"
                final_output = await CallbackQuery.message.reply_photo(
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=cap,
                )
                os.remove(thumb)
        await mystic.delete()
        if for_p == 1:
            m = await CallbackQuery.message.reply_text(
                "Sıraya alınmış çalma listesi yapıştırılıyor."
            )
            link = await paste_queue(msg)
            preview = link + "/preview.png"
            url = link + "/index.txt"
            buttons = paste_queue_markup(url)
            if await isPreviewUp(preview):
                await CallbackQuery.message.reply_photo(
                    photo=preview,
                    caption=f"Bu {third_name} için sıraya alınmış çalma listesi. \n\nOynatan :- {CallbackQuery.from_user.mention}",
                    quote=False,
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
                await m.delete()
            else:
                await CallbackQuery.message.reply_text(
                    text=msg, reply_markup=audio_markup2
                )
                await m.delete()
        else:
            await CallbackQuery.message.reply_text(
                "Çalma Listesinde Yalnızca 1 Müzik var.. Sıraya eklenecek başka müzik yok."
            )
        if for_t == 1:
            await start_timer(
                send_video,
                duration_min,
                duration_sec,
                final_output,
                CallbackQuery.message.chat.id,
                CallbackQuery.message.from_user.id,
                0,
            )


@app.on_callback_query(filters.regex("add_playlist"))
async def group_playlist(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    videoid, type, genre = callback_request.split("|")
    if type == "Personal":
        user_id = CallbackQuery.from_user.id
    elif type == "Group":
        a = await app.get_chat_member(
            CallbackQuery.message.chat.id, CallbackQuery.from_user.id
        )
        if not a.can_manage_voice_chats:
            return await CallbackQuery.answer(
                "Bu eylemi gerçekleştirmek için gerekli izne sahip değilsiniz. \nGereken Yetki: `Sesli Sohbeti Yönetme`",
                show_alert=True,
            )
        user_id = CallbackQuery.message.chat.id
    _count = await get_playlist_names(user_id, genre)
    if not _count:
        sex = await CallbackQuery.message.reply_text(
            f"{MUSIC_BOT_NAME} adlı kullanıcının Oynatma Listesi Özelliğine Hoş Geldiniz. \n\nVeritabanında Çalma Listeniz Oluşturuluyor. Lütfen bekleyin... \n\nTür:- {genre}"
        )
        await asyncio.sleep(2)
        await sex.delete()
        count = len(_count)
    else:
        count = len(_count)
    count = int(count)
    if count == 50:
        return await CallbackQuery.answer(
            "Üzgünüm! Bir çalma listesinde yalnızca 50 müzik olabilir.",
            show_alert=True,
        )
    asyncio.get_event_loop()
    await CallbackQuery.answer()
    title, duration_min, duration_sec, thumbnail = get_yt_info_id(videoid)
    _check = await get_playlist(user_id, videoid, genre)
    title = title[:50]
    if _check:
        return await CallbackQuery.message.reply_text(
            f"{CallbackQuery.from_user.mention}, Zaten Oynatma Listesinde!"
        )
    assis = {
        "videoid": videoid,
        "title": title,
        "duration": duration_min,
    }
    await save_playlist(user_id, videoid, assis, genre)
    CallbackQuery.from_user.first_name
    return await CallbackQuery.message.reply_text(
        f"{type}'ın {genre} Oynatma Listesine ekleyen: {CallbackQuery.from_user.mention}"
    )


@app.on_callback_query(filters.regex("check_playlist"))
async def check_playlist(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    type, genre = callback_request.split("|")
    if type == "Personal":
        user_id = CallbackQuery.from_user.id
        user_name = CallbackQuery.from_user.first_name
    elif type == "Group":
        user_id = CallbackQuery.message.chat.id
        user_name = CallbackQuery.message.chat.title
    _playlist = await get_playlist_names(user_id, genre)
    if not _playlist:
        return await CallbackQuery.answer(
            f"Sunucularda {genre} Oynatma Listesi yok. Çalma listesine müzik eklemeyi deneyin. ",
            show_alert=True,
        )
    else:
        j = 0
        await CallbackQuery.answer()
        await CallbackQuery.message.delete()
        msg = f"Getirilen Oynatma Listesi:\n\n"
        for shikhar in _playlist:
            j += 1
            _note = await get_playlist(user_id, shikhar, genre)
            title = _note["title"]
            duration = _note["duration"]
            msg += f"{j}- {title[:60]}\n"
            msg += f"    Süre- {duration} Dakika(lar)\n\n"
        m = await CallbackQuery.message.reply_text(
            "Sıraya alınmış çalma listesi yapıştırılıyor"
        )
        link = await paste_queue(msg)
        preview = link + "/preview.png"
        url = link + "/index.txt"
        buttons = fetch_playlist(
            user_name, type, genre, CallbackQuery.from_user.id, url
        )
        if await isPreviewUp(preview):
            await CallbackQuery.message.reply_photo(
                photo=preview,
                caption=f"Bu, {user_name} Oynatma Listesi.",
                quote=False,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
            await m.delete()
        else:
            await CallbackQuery.message.reply_text(text=msg, reply_markup=audio_markup2)
            await m.delete()


@app.on_callback_query(filters.regex("delete_playlist"))
async def del_playlist(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    type, genre = callback_request.split("|")
    if str(type) == "Personal":
        user_id = CallbackQuery.from_user.id
        CallbackQuery.from_user.first_name
    elif str(type) == "Group":
        a = await app.get_chat_member(
            CallbackQuery.message.chat.id, CallbackQuery.from_user.id
        )
        if not a.can_manage_voice_chats:
            return await CallbackQuery.answer(
                "Bu eylemi gerçekleştirmek için gerekli izne sahip değilsiniz. \nGereken Yetki: `Sesli Sohbeti Yönetme`",
                show_alert=True,
            )
        user_id = CallbackQuery.message.chat.id
        CallbackQuery.message.chat.title
    _playlist = await get_playlist_names(user_id, genre)
    if not _playlist:
        return await CallbackQuery.answer(
            "Grubun Bot Sunucusunda Oynatma Listesi yok", show_alert=True
        )
    else:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
        for shikhar in _playlist:
            await delete_playlist(user_id, shikhar, genre)
    await CallbackQuery.message.reply_text(
        f"{type} adlı kullanıcının {genre} oynatma listesinin tamamı {CallbackQuery.from_user.mention} tarafından başarıyla silindi."
    )


@app.on_callback_query(filters.regex("audio_video_download"))
async def down_playlisyts(_, CallbackQuery):
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    CallbackQuery.from_user.id
    videoid, user_id = callback_request.split("|")
    buttons = download_markup(videoid, user_id)
    await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex(pattern=r"good"))
async def good(_, CallbackQuery):
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    CallbackQuery.from_user.id
    videoid, user_id = callback_request.split("|")
    buttons = download_markup(videoid, user_id)
    await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )
