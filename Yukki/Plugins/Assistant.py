import random

from pyrogram import filters
from pyrogram.types import Message

from Yukki import ASSISTANT_PREFIX, SUDOERS, app, random_assistant
from Yukki.Database import get_assistant, save_assistant

__MODULE__ = "Asistan"
__HELP__ = f"""


/asistankontrol
- Sohbetinizde kullanılan asistanı kontrol edin


**Not:**
- Sadece Kurucular İçin

{ASSISTANT_PREFIX[0]} Engelle [Bir Kullanıcı Mesajını Yanıtla]
- Kullanıcıyı Asistan Hesabından Engeller.

{ASSISTANT_PREFIX[0]} Engeli Kaldır [Bir Kullanıcı Mesajına yanıt verme]
- Kullanıcının Asistan Hesabındaki engellemesini kaldırır.

{ASSISTANT_PREFIX[0]} Onayla [Bir Kullanıcı Mesajını Yanıtla]
- Kullanıcıyı DM için onaylar.

{ASSISTANT_PREFIX[0]} Onaylama [Bir Kullanıcı Mesajına Cevap Ver]
- Kullanıcıyı DM için onaylamaz.

{ASSISTANT_PREFIX[0]} Profil Fotoğrafı [ Bir Fotoğrafa Yanıt Ver]
- Asistan hesabı Profil Fotoğrafını değiştirir.

{ASSISTANT_PREFIX[0]} bio [Bio Mesajı] 
- Asistan Hesabın Bio Yazısını Değiştirir.

/asistandegistir [1 den 5 e kadar olan numara]
- Asistan Hesabın Hangisi olduğunu gösterir.

/asistanayarla [bu komutu tek başına kullanırsanız rastgele bir asistan seçer veya 1 den 5 e kadar olan bir numara girerek istediğiniz asistanı ayarlayabilirsiniz]
- Sohbet için bir asistan hesabı ayarlayın.
"""


ass_num_list = ["1", "2", "3", "4", "5"]


@app.on_message(filters.command("asistandegistir") & filters.user(SUDOERS))
async def assis_change(_, message: Message):
    usage = f"**Kullanım:** \n/asistandegistir [Asistan Numarası] \n\nAralarından seçim yapın \n{' | '.join(ass_num_list)}"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    num = message.text.split(None, 1)[1].strip()
    if num not in ass_num_list:
        return await message.reply_text(usage)
    ass_num = int(message.text.strip().split()[1])
    _assistant = await get_assistant(message.chat.id, "assistant")
    if not _assistant:
        return await message.reply_text(
            "Önceden Kaydedilmiş Asistan Bulunamadı. \n\nAsistanı /asistanayarla komutu ile ayarlayabilirsiniz"
        )
    else:
        ass = _assistant["saveassistant"]
    assis = {
        "saveassistant": ass_num,
    }
    await save_assistant(message.chat.id, "assistant", assis)
    await message.reply_text(
        f"**Asistan Değiştirildi**\n\nAsistan hesabı şundan **{ass}** Şuna değiştirildi **{ass_num}**"
    )


ass_num_list2 = ["1", "2", "3", "4", "5", "Random"]


@app.on_message(filters.command("asistanayarla") & filters.user(SUDOERS))
async def assis_change(_, message: Message):
    usage = f"**Kullanım:**\n/asistanayarla [Asistan Numarası Veya Tek başına Komut Kullanımı] \n\nAralarından Seçim Yapın \n{' | '.join(ass_num_list2)} \n\nRastgele Asistan Ayarlamak İçin Komutu Tek Başına Kullanın"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    query = message.text.split(None, 1)[1].strip()
    if query not in ass_num_list2:
        return await message.reply_text(usage)
    if str(query) == "Random":
        ran_ass = random.choice(random_assistant)
    else:
        ran_ass = int(message.text.strip().split()[1])
    _assistant = await get_assistant(message.chat.id, "assistant")
    if not _assistant:
        await message.reply_text(
            f"**Her Telden Müzik Botu Asistanı Atandı** \n\nAsistan Numarası: **{ran_ass}**"
        )
        assis = {
            "saveassistant": ran_ass,
        }
        await save_assistant(message.chat.id, "assistant", assis)
    else:
        ass = _assistant["saveassistant"]
        return await message.reply_text(
            f"Önceden Kaydedilmiş Asistan Numarası {ass} Bulundu. \n\nAsistan Değiştirmek İçin Komut: /asistandegistir"
        )


@app.on_message(filters.command("asistankontrol") & filters.group)
async def check_ass(_, message: Message):
    _assistant = await get_assistant(message.chat.id, "assistant")
    if not _assistant:
        return await message.reply_text(
            "Önceden Kaydedilmiş Asistan Bulunamadı. \n\nAsistanı ayarlamak için komut: /asistanayarla"
        )
    else:
        ass = _assistant["saveassistant"]
        return await message.reply_text(
            f"Önceden Kaydedilmiş Asistan Bulundu. \n\nAsistan Numarası: {ass} "
        )
