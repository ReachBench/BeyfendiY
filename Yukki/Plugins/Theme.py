from pyrogram import filters

from Yukki import BOT_USERNAME, MUSIC_BOT_NAME, app
from Yukki.Database import get_theme, save_theme
from Yukki.Decorators.permission import PermissionCheck

themes = [
    "blue",
    "black",
    "red",
    "green",
    "grey",
    "orange",
    "pink",
    "yellow",
    "Random",
]

themes2 = [
    "blue",
    "black",
    "red",
    "green",
    "grey",
    "orange",
    "pink",
    "yellow",
]

__MODULE__ = "Tema"
__HELP__ = """


/settheme
- Küçük resimler için bir tema belirleyin.

/theme
- Sohbetiniz için Temayı kontrol edin.
"""


@app.on_message(
    filters.command(["settheme", f"settheme@{BOT_USERNAME}"]) & filters.group
)
async def settheme(_, message):
    usage = f"Bu bir tema değil. \nKullanım temasından seçin. \n{' | '.join(themes)} Rastgele tema seçimi elde etmek için Randomu kullanın"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    theme = message.text.split(None, 1)[1].strip()
    if theme not in themes:
        return await message.reply_text(usage)
    note = {
        "theme": theme,
    }
    await save_theme(message.chat.id, "theme", note)
    await message.reply_text(f"Küçük resim teması {theme} olarak değiştirildi")


@app.on_message(filters.command("theme"))
@PermissionCheck
async def theme_func(_, message):
    await message.delete()
    _note = await get_theme(message.chat.id, "theme")
    if not _note:
        theme = "Random"
    else:
        theme = _note["theme"]
    await message.reply_text(
        f"****{MUSIC_BOT_NAME} Küçük Resimler Teması** \n\n**Mevcut Tema : -** {theme} \n\n**Kullanılabilir Temalar:-** {' | '.join(theme 2)} \n\nTemayı değiştirmek için /settheme komutunu kullanın."
    )
