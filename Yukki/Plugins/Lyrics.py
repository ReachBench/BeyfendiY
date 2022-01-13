import os
import re

import lyricsgenius
from pyrogram import filters
from pyrogram.types import Message
from youtubesearchpython import VideosSearch

from Yukki import MUSIC_BOT_NAME, app

__MODULE__ = "Sözler"
__HELP__ = """

/Lyrics [Müzik İsmi]
- Web'de belirli bir Müzik için Şarkı Sözleri arar.

**Not**:
Sözler her zaman tam doğru olmayabilir! Sözlerde irili ufaklı birkaç hata olabilir bunun için özür dileriz.
"""


@app.on_callback_query(filters.regex(pattern=r"lyrics"))
async def lyricssex(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    try:
        id, user_id = callback_request.split("|")
    except Exception as e:
        return await CallbackQuery.message.edit(
            f"Hata oluştu\n**Olası hata şu olabilir**:{e}"
        )
    url = f"https://www.youtube.com/watch?v={id}"
    print(url)
    try:
        results = VideosSearch(url, limit=1)
        for result in results.result()["result"]:
            title = result["title"]
    except Exception:
        return await CallbackQuery.answer(
            "Ses bulunamadı. Youtube Kaynaklıdır!", show_alert=True
        )
    x = "OXaVabSRKQLqwpiYOn-E4Y7k3wj-TNdL5RfDPXlnXhCErbcqVvdCF-WnMR5TBctI"
    y = lyricsgenius.Genius(x)
    t = re.sub(r"[^\w]", " ", title)
    y.verbose = False
    S = y.search_song(t, get_full_info=False)
    if S is None:
        return await CallbackQuery.answer("Sözler bulunamadı 🙁", show_alert=True)
    await CallbackQuery.message.delete()
    userid = CallbackQuery.from_user.id
    usr = f"[{CallbackQuery.from_user.first_name}](tg://user?id={userid})"
    xxx = f"""
**Şarkı sözü {MUSIC_BOT_NAME} tarafından yüklendi**

**Talep Eden:-** {usr}
**Aranan Şarkı:-** __{title}__

**Bulunan Şarkı Sözleri:-** __{S.title}__
**Sanatçı:-** {S.artist}

**__Sözler:__**

{S.lyrics}"""
    if len(xxx) > 4096:
        filename = "lyrics.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(xxx.strip()))
        await CallbackQuery.message.reply_document(
            document=filename,
            caption=f"**Çıktı:**\n\n`Sözler`",
            quote=False,
        )
        os.remove(filename)
    else:
        await CallbackQuery.message.reply_text(xxx)


@app.on_message(filters.command("lyrics"))
async def lrsearch(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("**Kullanım:**\n\n/lyrics [ Müzik İsmi]")
    m = await message.reply_text("Sözler Aranıyor...")
    query = message.text.split(None, 1)[1]
    x = "OXaVabSRKQLqwpiYOn-E4Y7k3wj-TNdL5RfDPXlnXhCErbcqVvdCF-WnMR5TBctI"
    y = lyricsgenius.Genius(x)
    y.verbose = False
    S = y.search_song(query, get_full_info=False)
    if S is None:
        return await m.edit("Sözler Bulunamadı 🙁")
    xxx = f"""
**Şarkı sözü {MUSIC_BOT_NAME} tarafından yüklendi**

**Aranan Şarkı:-** __{query}__
**Bulunan Şarkı Sözleri:-** __{S.title}__
**Sanatçı:-** {S.artist}

**__Sözler:__**

{S.lyrics}"""
    if len(xxx) > 4096:
        await m.delete()
        filename = "lyrics.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(xxx.strip()))
        await message.reply_document(
            document=filename,
            caption=f"**Çıktı:**\n\n`Sözler`",
            quote=False,
        )
        os.remove(filename)
    else:
        await m.edit(xxx)
