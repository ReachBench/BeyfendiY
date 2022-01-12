from pyrogram import filters
from pyrogram.types import Message

from Yukki import app
from Yukki.Database import (
    delete_authuser,
    get_authuser,
    get_authuser_names,
    save_authuser,
)
from Yukki.Decorators.admins import AdminActual
from Yukki.Utilities.changers import int_to_alpha

__MODULE__ = "Auth Users"
__HELP__ = """

**Not:**
-Yetkilendirilen kullanıcılar, Yönetici Hakları olmadan bile Sesli sohbetteki müzikleri atlayabilir, duraklatabilir, durdurabilir, devam ettirebilir.


/yetkili [Kullanıcı Adı veya Bir Mesajı Yanıtla]
- Grubun YETKİ LİSTESİ'ne bir kullanıcı ekleyin.

/yetkisiz [Kullanıcı Adı veya Bir Mesajı Yanıtla]
- Grubun yetkilendirme listesinden bir kullanıcıyı kaldırın.

/yetkililer
- Grubun Yetkililer Listesini kontrol edin.
"""


@app.on_message(filters.command("yetkili") & filters.group)
@AdminActual
async def yetkili(_, message: Message):
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
        user_id = message.from_user.id
        token = await int_to_alpha(user.id)
        from_user_name = message.from_user.first_name
        from_user_id = message.from_user.id
        _check = await get_authuser_names(message.chat.id)
        count = 0
        for smex in _check:
            count += 1
        if int(count) == 20:
            return await message.reply_text(
               "Grup Yetkili Kullanıcılar Listenizde Yalnızca 20 Kullanıcınız Olabilir"
            )
        if token not in _check:
            assis = {
                "auth_user_id": user.id,
                "auth_name": user.first_name,
                "admin_id": from_user_id,
                "admin_name": from_user_name,
            }
            await save_authuser(message.chat.id, token, assis)
            await message.reply_text(f"Seçtiğiniz kullanıcı bu grubun Yetkili Kullanıcılar Listesine eklendi.")
            return
        else:
            await message.reply_text(f"Seçtiğiniz kullanıcı zaten Yetkili Kullanıcılar Listesinde.")
        return
    from_user_id = message.from_user.id
    user_id = message.reply_to_message.from_user.id
    user_name = message.reply_to_message.from_user.first_name
    token = await int_to_alpha(user_id)
    from_user_name = message.from_user.first_name
    _check = await get_authuser_names(message.chat.id)
    count = 0
    for smex in _check:
        count += 1
    if int(count) == 20:
        return await message.reply_text(
            "Grup Yetkili Kullanıcılar Listenizde Yalnızca 20 Kullanıcınız Olabilir"
        )
    if token not in _check:
        assis = {
            "auth_user_id": user_id,
            "auth_name": user_name,
            "admin_id": from_user_id,
            "admin_name": from_user_name,
        }
        await save_authuser(message.chat.id, token, assis)
        await message.reply_text(f"Seçtiğiniz kullanıcı bu grubun Yetkili Kullanıcılar Listesine eklendi.")
        return
    else:
        await message.reply_text(f"Seçtiğiniz kullanıcı zaten Yetkili Kullanıcılar Listesinde.")


@app.on_message(filters.command("yetkisiz") & filters.group)
@AdminActual
async def whitelist_chat_func(_, message: Message):
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
        token = await int_to_alpha(user.id)
        deleted = await delete_authuser(message.chat.id, token)
        if deleted:
            return await message.reply_text(
                f"Seçtiğiniz kullanıcı bu Grubun Yetkili Kullanıcılar Listesinden Kaldırılmıştır."
            )
        else:
            return await message.reply_text(f"Kullanıcı Yetkili Değil.")
    user_id = message.reply_to_message.from_user.id
    token = await int_to_alpha(user_id)
    deleted = await delete_authuser(message.chat.id, token)
    if deleted:
        return await message.reply_text(
            f"Seçtiğiniz Kişi bu Grubun Yetkili Kullanıcılar Listesinden Kaldırıldı."
        )
    else:
        return await message.reply_text(f"Kullanıcı Yetkili Değil.")


@app.on_message(filters.command("yetkililer") & filters.group)
async def yetkililer(_, message: Message):
    _playlist = await get_authuser_names(message.chat.id)
    if not _playlist:
        return await message.reply_text(
            f"Bu Grupta Yetkili Kullanıcı Yok. \n\nKullanıcıları /yetkili ile yetkilendirin ve /yetkisiz ile yetkisizleştirin."
        )
    else:
        j = 0
        m = await message.reply_text("Yetkili Kullanıcılar Alınıyor... Lütfen Bekleyin")
        msg = f"**Yetkili Kullanıcılar Listesi:**\n\n"
        for note in _playlist:
            _note = await get_yetkililer(message.chat.id, note)
            user_id = _note["auth_user_id"]
            _note["auth_name"]
            admin_id = _note["admin_id"]
            admin_name = _note["admin_name"]
            try:
                user = await app.get_users(user_id)
                user = user.first_name
                j += 1
            except Exception:
                continue
            msg += f"{j}➤ {user}[`{user_id}`]\n"
            msg += f"    ┗ Tarafından eklendi:- {admin_name}[`{admin_id}`]\n\n"
        await m.edit_text(msg)
