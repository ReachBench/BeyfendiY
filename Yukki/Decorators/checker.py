from Yukki import BOT_USERNAME, LOG_GROUP_ID, app
from Yukki.Database import blacklisted_chats, is_gbanned_user, is_on_off


def checker(mystic):
    async def wrapper(_, message):
        if message.sender_chat:
            return await message.reply_text(
                "Şu An Anonim Yöneticisiniz! \nLütfen Anonim Yetkinizi Kapatınız."
            )
        blacklisted_chats_list = await blacklisted_chats()
        if message.chat.id in blacklisted_chats_list:
            await message.reply_text(
                f"**Kara Listeye Alınmış Sohbet**\n\nSohbetiniz Botun Kurucuları tarafından kara listeye alındı. \nHerhangi Bir Kurucudan Sohbetinizin kara listeden kaldırılmasını isteyebilirsiniz. \nBotun Kurucu Listesine [Buradan](https://t.me/{BOT_USERNAME}?start=sudolist) Bakabilirsiniz."
            )
            return await app.leave_chat(message.chat.id)
        if await is_on_off(1):
            if int(message.chat.id) != int(LOG_GROUP_ID):
                return await message.reply_text(
                    f"Bot Şu Anda Bakımda. Rahatsızlıktan dolayı özür dileriz!"
                )
        if await is_gbanned_user(message.from_user.id):
            return await message.reply_text(
                f"**Küresel Yasaklı Kullanıcı**\n\nBot kullanman yasaklandı. \nHerhangi Bir Kurucudan Küresel Yasaklamanızı Kaldırmasını İsteyebilirsiniz. \nBotun Kurucu Listesine [Buradan](https://t.me/{BOT_USERNAME}?start=sudolist) Bakabilirsiniz."
            )
        return await mystic(_, message)

    return wrapper


def checkerCB(mystic):
    async def wrapper(_, CallbackQuery):
        blacklisted_chats_list = await blacklisted_chats()
        if CallbackQuery.message.chat.id in blacklisted_chats_list:
            return await CallbackQuery.answer("Sohbet Kara Listede", show_alert=True)
        if await is_on_off(1):
            if int(CallbackQuery.message.chat.id) != int(LOG_GROUP_ID):
                return await CallbackQuery.answer(
                    "Bot Bakımda. Verdiğimiz rahatsızlık için özür dileriz!",
                    show_alert=True,
                )
        if await is_gbanned_user(CallbackQuery.from_user.id):
            return await CallbackQuery.answer("Küresel Yasaklı Kullanıcısınız", show_alert=True)
        return await mystic(_, CallbackQuery)

    return wrapper
