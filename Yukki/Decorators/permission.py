from Yukki import BOT_ID, app


def PermissionCheck(mystic):
    async def wrapper(_, message):
        if message.chat.type == "private":
            return await mystic(_, message)
        a = await app.get_chat_member(message.chat.id, BOT_ID)
        if a.status != "administrator":
            return await message.reply_text(
                "Altta gösterilen bazı izinlere ihtiyacım var: \n- **Sesli sohbetleri yönetme**: Sesli sohbetleri yönetmek için \n- **Mesajları silme**: Botun arama yaptıktan sonra kendi mesajlarını silmesi için \n- **Bağlantı ile davet etme**: Asistan hesabın gruba gelebilmesi için."
            )
        if not a.can_manage_voice_chats:
            await message.reply_text(
                "Bu eylemi gerçekleştirmek için gerekli izne sahip değilim."
                + "\n**Gereken Yetki:** `Sesli sohbeti yönetme`"
            )
            return
        if not a.can_delete_messages:
            await message.reply_text(
                "Bu eylemi gerçekleştirmek için gerekli izne sahip değilim."
                + "\n**Gereken Yetki:** `Mesajları Silme`"
            )
            return
        if not a.can_invite_users:
            await message.reply_text(
                "Bu eylemi gerçekleştirmek için gerekli izne sahip değilim."
                + "\n**Gereken Yetki:** `Bağlantı ile davet etme`"
            )
            return
        return await mystic(_, message)

    return wrapper
