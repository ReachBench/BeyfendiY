from Yukki import SUDOERS, app
from Yukki.Database import get_authuser_names, is_nonadmin_chat
from Yukki.Utilities.changers import int_to_alpha


def AdminRightsCheck(mystic):
    async def wrapper(_, message):
        if message.sender_chat:
            return await message.reply_text(
                "Şu an anonim yöneticisiniz. \nLütfen anonim yetkinizi kapatınız."
            )
        is_non_admin = await is_nonadmin_chat(message.chat.id)
        if not is_non_admin:
            member = await app.get_chat_member(message.chat.id, message.from_user.id)
            if not member.can_manage_voice_chats:
                if message.from_user.id not in SUDOERS:
                    token = await int_to_alpha(message.from_user.id)
                    _check = await get_authuser_names(message.chat.id)
                    if token not in _check:
                        return await message.reply(
                            "Bu eylemi gerçekleştirmek için gerekli izne sahip değilsiniz. \n\n**Sesli sohbeti yönetme yetkisine ihtiyacınız var.**"
                        )
        return await mystic(_, message)

    return wrapper


def AdminActual(mystic):
    async def wrapper(_, message):
        if message.sender_chat:
            return await message.reply_text(
                "Şu an anonim yöneticisiniz. \nLütfen anonim yetkinizi kapatınız."
            )
        member = await app.get_chat_member(message.chat.id, message.from_user.id)
        if not member.can_manage_voice_chats:
            return await message.reply(
                "Bu eylemi gerçekleştirmek için gerekli izne sahip değilsiniz. \n\n**Sesli sohbeti yönetme yetkisine ihtiyacınız var.**"
            )
        return await mystic(_, message)

    return wrapper


def AdminRightsCheckCB(mystic):
    async def wrapper(_, CallbackQuery):
        is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
        if not is_non_admin:
            a = await app.get_chat_member(
                CallbackQuery.message.chat.id, CallbackQuery.from_user.id
            )
            if not a.can_manage_voice_chats:
                if CallbackQuery.from_user.id not in SUDOERS:
                    token = await int_to_alpha(CallbackQuery.from_user.id)
                    _check = await get_authuser_names(CallbackQuery.from_user.id)
                    if token not in _check:
                        return await CallbackQuery.answer(
                            "Bu eylemi gerçekleştirmek için gerekli izne sahip değilsiniz. \nGereken Yetki: **Sesli sohbeti yönetme**",
                            show_alert=True,
                        )
        return await mystic(_, CallbackQuery)

    return wrapper


def ActualAdminCB(mystic):
    async def wrapper(_, CallbackQuery):
        a = await app.get_chat_member(
            CallbackQuery.message.chat.id, CallbackQuery.from_user.id
        )
        if not a.can_manage_voice_chats:
            return await CallbackQuery.answer(
                "Bu eylemi gerçekleştirmek için gerekli izne sahip değilsiniz. \nGereken Yetki: **Sesli sohbeti yönetme**",
                show_alert=True,
            )
        return await mystic(_, CallbackQuery)

    return wrapper
