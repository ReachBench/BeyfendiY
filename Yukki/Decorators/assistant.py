import random

from pyrogram import filters
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Yukki import BOT_ID, app, random_assistant
from Yukki.Database import get_assistant, save_assistant
from Yukki.Utilities.assistant import get_assistant_details


@app.on_callback_query(filters.regex("unban_assistant"))
async def unban_assistant_(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    query, user_id = callback_request.split("|")
    a = await app.get_chat_member(CallbackQuery.message.chat.id, BOT_ID)
    if not a.can_restrict_members:
        return await CallbackQuery.answer(
            "Kullanıcıları Yasaklama/Yasağı kaldırma yetkim yok. \nHerhangi bir yöneticiden asistanın yasağını kaldırmasını isteyin. ",
            show_alert=True,
        )
    else:
        try:
            await app.unban_chat_member(CallbackQuery.message.chat.id, user_id)
        except:
            return await CallbackQuery.answer(
                "Yasak kaldırılamadı.",
                show_alert=True,
            )
        return await CallbackQuery.edit_message_text(
            "Asistanın Yasağı Kaldırıldı. Şimdi Oynatmayı Deneyin."
        )


def AssistantAdd(mystic):
    async def wrapper(_, message):
        _assistant = await get_assistant(message.chat.id, "assistant")
        if not _assistant:
            ran_ass = random.choice(random_assistant)
            assis = {
                "saveassistant": ran_ass,
            }
            await save_assistant(message.chat.id, "assistant", assis)
        else:
            ran_ass = _assistant["saveassistant"]
        if ran_ass not in random_assistant:
            ran_ass = random.choice(random_assistant)
            assis = {
                "saveassistant": ran_ass,
            }
            await save_assistant(message.chat.id, "assistant", assis)
        ASS_ID, ASS_NAME, ASS_USERNAME, ASS_ACC = await get_assistant_details(ran_ass)
        try:
            b = await app.get_chat_member(message.chat.id, ASS_ID)
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🗑 Asistan Yasağını Kaldır",
                            callback_data=f"unban_assistant a|{ASS_ID}",
                        )
                    ],
                ]
            )
            if b.status == "kicked":
                return await message.reply_text(
                    f"Asistan Hesabı[{ASS_ID}] Tekmelendi. \nMüzik Botunu kullanmaya Devam Etmek İçin Asistanı Gruba Geri Alabilirsiniz. \n\nAsistan Kullanıcı Adı: @{ASS_USERNAME}",
                    reply_markup=key,
                )
            if b.status == "banned":
                return await message.reply_text(
                    f"Asistan Hesabı[{ASS_ID}] Yasaklandı.\nMüzik Botunu kullanmaya Devam Etmek İçin Asistan Hesabın Yasağını Kaldırınız. \n\nAsistan Kullanıcı Adı: @{ASS_USERNAME}",
                    reply_markup=key,
                )
        except UserNotParticipant:
            if message.chat.username:
                try:
                    await ASS_ACC.join_chat(message.chat.username)
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    await message.reply_text(
                        f"__Asistan Katılamadı__\n\n**Sebep**: {e}"
                    )
                    return
            else:
                try:
                    invitelink = await app.export_chat_invite_link(message.chat.id)
                    if invitelink.startswith("https://t.me/+"):
                        invitelink = invitelink.replace(
                            "https://t.me/+", "https://t.me/joinchat/"
                        )
                    await ASS_ACC.join_chat(invitelink)
                    await message.reply(
                        f"{ASS_NAME} Başarıyla Katıldı",
                    )
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    await message.reply_text(
                        f"__Asistan Katılamadı__\n\n**Sebep**: {e}"
                    )
                    return
        return await mystic(_, message)

    return wrapper
