import os

import speedtest
import wget
from pyrogram import filters

from Yukki import app

__MODULE__ = "Hız Testi"
__HELP__ = """

/hiztest
- Sunucu Gecikmesini ve Hızını Kontrol Edin.

"""


@app.on_message(filters.command("hiztest") & ~filters.edited)
async def statsguwid(_, message):
    m = await message.reply_text("Hız Testi Başlatılıyor...")
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        m = await m.edit("İndirme Hızı Alınıyor...")
        test.download()
        m = await m.edit("Yükleme Hızı Alınıyor...")
        test.upload()
        test.results.share()
        result = test.results.dict()
    except Exception as e:
        return await m.edit(e)
    m = await m.edit("Hız Testi Sonuçları Gönderiliyor...")
    path = wget.download(result["share"])

    output = f"""**Hız Testi Sonuçları**
    
<u>**Site Sunucusu:**</u>
**__ISP:__** {result['client']['isp']}
**__Ülke:__** {result['client']['country']}
  
<u>**Bot Sunucusu:**</u>
**__İsim:__** {result['server']['name']}
**__Ülke:__** {result['server']['country']}, {result['server']['cc']}
**__Sponsor:__** {result['server']['sponsor']}
**__Gecikme:__** {result['server']['latency']}  
**__Ping:__** {result['ping']}"""
    msg = await app.send_photo(chat_id=message.chat.id, photo=path, caption=output)
    os.remove(path)
    await m.delete()
