import asyncio
import math
import os
import shutil
from datetime import datetime

import dotenv
import heroku3
import requests
import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import filters

from config import HEROKU_API_KEY, HEROKU_APP_NAME, UPSTREAM_BRANCH
from Yukki import LOG_GROUP_ID, MUSIC_BOT_NAME, SUDOERS, app
from Yukki.Database import (
    get_active_chats,
    remove_active_chat,
    remove_active_video_chat,
)
from Yukki.Utilities.heroku import is_heroku
from Yukki.Utilities.paste import paste_queue

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


__MODULE__ = "Server"
__HELP__ = f"""

**Not:**
**Yalnızca Kurucular İçindir**

/get_log
- Heroku'dan son 100 satırın günlüğünü alın.

/get_var
- Heroku veya .env'den bir yapılandırma değişkeni alın.

/del_var
- Heroku veya env'deki herhangi bir değişkeni silin.

/set_var [Var Name] [Value]
- Heroku veya .env'de bir Var ayarlayın veya Var'ı güncelleyin. Var ve Değerini bir boşlukla ayırın.

/usage
- Dyno Kullanımını Alın.

/update
- Botunuzu Güncelleyin.

/restart 
- Botu Yeniden Başlatın [Tüm indirmeler, önbellek, ham dosyalar da temizlenecektir].
"""


XCB = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "git",
    "heroku",
    "push",
    str(HEROKU_API_KEY),
    "https",
    str(HEROKU_APP_NAME),
    "HEAD",
    "main",
]


@app.on_message(filters.command("get_log") & filters.user(SUDOERS))
async def log_(client, message):
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU UYGULAMASI ALGILANDI! </b>\n\nUygulamanızı güncellemek için, sırasıyla HEROKU_API_KEY ve HEROKU_APP_NAME değişkenlerini ayarlamanız gerekir!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU UYGULAMASI ALGILANDI!</b> \n\n<b>Uzaktan güncelleme yapabilmek için her ikisini de</b> HEROKU_API_KEY **ve** HEROKU_APP_NAME <b>değişkenlerini doğru şekilde eklediğinizden emin olun!</b>"
            )
    else:
        return await message.reply_text("Yalnızca Heroku Uygulamaları için")
    try:
        Heroku = heroku3.from_key(HEROKU_API_KEY)
        happ = Heroku.app(HEROKU_APP_NAME)
    except BaseException:
        return await message.reply_text(
            " Lütfen Heroku API Anahtarınızın, Uygulama adınızın heroku'da doğru şekilde yapılandırıldığından emin olun"
        )
    data = happ.get_log()
    if len(data) > 1024:
        link = await paste_queue(data)
        url = link + "/index.txt"
        return await message.reply_text(
            f"İşte Sizin Uygulamanızın Günlüğü[{HEROKU_APP_NAME}] \n\n[Günlükleri kontrol etmek için burayı tıklayın]({url})"
        )
    else:
        return await message.reply_text(data)


@app.on_message(filters.command("get_var") & filters.user(SUDOERS))
async def varget_(client, message):
    usage = "**Kullanım:**\n/get_var [Değişken adı]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    check_var = message.text.split(None, 2)[1]
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU UYGULAMASI ALGILANDI!</b>\n\nUygulamanızı güncellemek için sırasıyla HEROKU_API_KEY ve HEROKU_APP_NAME değişkenlerini ayarlamanız gerekir!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU UYGULAMASI ALGILANDI! </b>Uygulamanızı güncellemek için sırasıyla HEROKU_API_KEY ve HEROKU_APP_NAME değişkenlerini ayarlamanız gerekir!"
            )
        try:
            Heroku = heroku3.from_key(HEROKU_API_KEY)
            happ = Heroku.app(HEROKU_APP_NAME)
        except BaseException:
            return await message.reply_text(
                "Lütfen Heroku API Anahtarınızın ve Uygulama adınızın heroku'da doğru yapılandırıldığından emin olun"
            )
        heroku_config = happ.config()
        if check_var in heroku_config:
            return await message.reply_text(
                f"**Heroku Yapılandırması( Heroku Config):** **{check_var}** {heroku_config [ check_var]}"
            )
        else:
            return await message.reply_text("Böyle Bir `Var` Yok")
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await message.reply_text(".env bulunamadı.")
        output = dotenv.get_key(path, check_var)
        if not output:
            return await message.reply_text("Böyle Bir `Var` Yok")
        else:
            return await message.reply_text(
                f".env:\n\n**{check_var}:** `{str(output)}`"
            )


@app.on_message(filters.command("del_var") & filters.user(SUDOERS))
async def vardel_(client, message):
    usage = "**Kullanım:**\n/del_var [Değişken İsmi]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    check_var = message.text.split(None, 2)[1]
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU UYGULAMASI ALGILANDI!</b> \n\nUygulamanızı güncellemek için sırasıyla HEROKU_API_KEY ve HEROKUAPP_NAME değişkenlerini ayarlamanız gerekir!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU UYGULAMASI ALGILANDI!</b> \n\n<b>İkisini de eklediğinizden emin olun: </b> HEROKU_API_KEY **ve** HEROKU_APP_NAME <b>, uzaktan güncelleme yapabilmek için doğru bir şekilde değişir! </b>"
            )
        try:
            Heroku = heroku3.from_key(HEROKU_API_KEY)
            happ = Heroku.app(HEROKU_APP_NAME)
        except BaseException:
            return await message.reply_text(
                "Lütfen Heroku API Anahtarınızın ve Uygulama adınızın heroku'da doğru şekilde yapılandırıldığından emin olun"
            )
        heroku_config = happ.config()
        if check_var in heroku_config:
            await message.reply_text(
                "**Heroku Değişken Silme ** \n\n{check_var} başarıyla silindi."
            )
            del heroku_config[check_var]
        else:
            return await message.reply_text(f"Böyle Bir `Değişken` Yok")
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await message.reply_text(".env bulunamadı.")
        output = dotenv.unset_key(path, check_var)
        if not output[0]:
            return await message.reply_text("Böyle Bir `Değişken` Yok")
        else:
            return await message.reply_text(
                f"{check_var} başarıyla silindi. \n\nBotu yeniden başlatmak için /restart komutunu kullanın."
            )


@app.on_message(filters.command("set_var") & filters.user(SUDOERS))
async def set_var(client, message):
    usage = "**Kullanım:**\n/set_var [Değişken İsmi] [Değişken Değeri]"
    if len(message.command) < 3:
        return await message.reply_text(usage)
    to_set = message.text.split(None, 2)[1].strip()
    value = message.text.split(None, 2)[2].strip()
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU UYGULAMASI ALGILANDI!</b> \n\nUygulamanızı güncellemek için sırasıyla HEROKU_API_KEY ve HEROKU_APP_NAME değişkenlerini ayarlamanız gerekir!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU UYGULAMASI ALGILANDI!</b> \n\n<b>İkisini de eklediğinizden emin olun: </b>HEROKU_API_KEY **ve** HEROKU_APP_NAME<b> \n\nUzaktan güncelleme yapabilmek için doğru şekilde değişir !</b>"
            )
        try:
            Heroku = heroku3.from_key(HEROKU_API_KEY)
            happ = Heroku.app(HEROKU_APP_NAME)
        except BaseException:
            return await message.reply_text(
                "Lütfen Heroku API Anahtarınızın ve Uygulama adınızın heroku'da doğru şekilde yapılandırıldığından emin olun."
            )
        heroku_config = happ.config()
        if to_set in heroku_config:
            await message.reply_text(
                f"**Heroku Değişken Güncellemesi** \n\n{to_set} başarıyla güncellendi. Bot Şimdi Yeniden Başlayacak."
            )
        else:
            await message.reply_text(
                f"{to_set} adlı Yeni değişken eklendi. \n\nBot Şimdi Yeniden Başlayacak."
            )
        heroku_config[to_set] = value
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await message.reply_text(".env Bulunamadı.")
        dotenv.set_key(path, to_set, value)
        if dotenv.get_key(path, to_set):
            return await message.reply_text(
                f"**.env Değişken Güncellemesi** \n\n{to_set}' başarıyla güncellendi. Botu yeniden başlatmak için /restart komutunu kullanın."
            )
        else:
            return await message.reply_text(
                f"**.env Değişkeni Eklemesi:** \n\n{to_set} başarıyla eklendi. Botu yeniden başlatmak için /restart komutunu kullanın."
            )


@app.on_message(filters.command("usage") & filters.user(SUDOERS))
async def usage_dynos(client, message):
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU UYGULAMASI ALGILANDI!</b> \n\nUygulamanızı güncellemek için, sırasıyla HEROKU_API_KEY ve HEROKU_APP_NAME değişkenlerini ayarlamanız gerekir!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU UYGULAMASI ALGILANDI!</b> \n\n<b>İkisini de eklediğinizden emin olun:</b> \nHEROKU_API_KEY **ve** HEROKU _APP_NAME<b> \n\nuzaktan güncelleme yapabilmek için doğru şekilde değişir!</b>"
            )
    else:
        return await message.reply_text("Yalnızca Heroku Uygulamaları için")
    try:
        Heroku = heroku3.from_key(HEROKU_API_KEY)
        Heroku.app(HEROKU_APP_NAME)
    except BaseException:
        return await message.reply_text(
            "Lütfen Heroku API Anahtarınızın ve Uygulama adınızın heroku'da doğru yapılandırıldığından emin olun"
        )
    dyno = await message.reply_text(
        "Heroku kullanımı kontrol ediliyor. Lütfen bekleyin..."
    )
    account_id = Heroku.account().id
    useragent = (
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/80.0.3987.149 Mobile Safari/537.36"
    )
    headers = {
        "User-Agent": useragent,
        "Authorization": f"Bearer {HEROKU_API_KEY}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    path = "/accounts/" + account_id + "/actions/get-quota"
    r = requests.get("https://api.heroku.com" + path, headers=headers)
    if r.status_code != 200:
        return await dyno.edit("Dyno kullanımı getirilemiyor.")
    result = r.json()
    quota = result["account_quota"]
    quota_used = result["quota_used"]
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)
    App = result["apps"]
    try:
        App[0]["quota_used"]
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]["quota_used"] / 60
        AppPercentage = math.floor(App[0]["quota_used"] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)
    await asyncio.sleep(1.5)
    text = f"""
**DYNO KULLANIMI**

<u>Kullanım:</u>
Toplam Kullanım: `{AppHours}`**Saat** `{AppMinutes}` **Dakika** **%**[`{AppPercentage}`]

<u>Kalan Kota:</u>
Toplam Kalan: `{hours}`**Saat** `{minutes}`**Dakika** **%**[`{percentage}`]"""
    return await dyno.edit(text)


@app.on_message(filters.command("update") & filters.user(SUDOERS))
async def update_(client, message):
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU UYGULAMASI ALGILANDI!</b> \n\nUygulamanızı güncellemek için sırasıyla HEROKU_API_KEY ve HEROKU_APP_NAME değişkenlerini ayarlamanız gerekir!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU UYGULAMASI ALGILANDI!</b> \n\n<b>Uzaktan güncelleme yapabilmek için, HEROKU_API_KEY **ve** HEROKU_APP_NAME <b>değişkenlerini doğru şekilde eklediğinizden emin olun!</b>"
            )
    response = await message.reply_text("Mevcut güncellemeler kontrol ediliyor...")
    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit("Git Komut Hatası")
    except InvalidGitRepositoryError:
        return await response.edit("Geçersiz Github Reposu")
    to_exc = f"git getirme kaynağı {UPSTREAM_BRANCH} &> /dev/null"
    os.system(to_exc)
    await asyncio.sleep(7)
    verification = ""
    REPO_ = repo.remotes.origin.url.split(".git")[0]  # main git repository
    for checks in repo.iter_commits(f"HEAD..origin/{UPSTREAM_BRANCH}"):
        verification = str(checks.count())
    if verification == "":
        return await response.edit("Bot güncel!")
    updates = ""
    ordinal = lambda format: "%d%s" % (
        format,
        "tsnrhtdd"[(format // 10 % 10 != 1) * (format % 10 < 4) * format % 10 :: 4],
    )
    for info in repo.iter_commits(f"HEAD..origin/{UPSTREAM_BRANCH}"):
        updates += f"<b>➣ #{info.count()}: [{info.summary}]({REPO_}/commit/{info}) by -> {info.author}</b>\n\t\t\t\t<b>➥ Commited on:</b> {ordinal(int(datetime.fromtimestamp(info.committed_date).strftime('%d')))} {datetime.fromtimestamp(info.committed_date).strftime('%b')}, {datetime.fromtimestamp(info.committed_date).strftime('%Y')}\n\n"
    _update_response_ = "Bot için yeni bir güncelleme mevcut! \n\n➣  </b>Güncellemeleri Şimdi Uygula! </code > \n\n**<u>Güncellemeler:</u>**"
    _final_updates_ = _update_response_ + updates
    if len(_final_updates_) > 4096:
        link = await paste_queue(updates)
        url = link + "/index.txt"
        nrs = await response.edit(
            f"Bot için yeni bir güncelleme mevcut! \n\n➣ **Güncellemeleri Şimdi Uygula!** \n\n**Güncellemeler:** [Güncellemeleri görmek için tıklayın]({url})"
        )
    else:
        nrs = await response.edit(_final_updates_, disable_web_page_preview=True)
    os.system("git stash &> /dev/null && git pull")
    if await is_heroku():
        try:
            await response.edit(
                f"{nrs.text} \n\nBot, Heroku'da başarıyla güncellendi! Şimdi, bot yeniden başlayana kadar (5 dakika kadar) bekleyin!"
            )
            os.system(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
            return
        except Exception as err:
            await response.edit(
                f"{nrs.text} \n\nBot yeniden başlatılırken bir şeyler ters gitti! Lütfen daha sonra tekrar deneyin veya daha fazla bilgi için Log'u kontrol edin."
            )
            return await app.send_message(
                LOG_GROUP_ID,
                f"#UPDATER 'DA `{err}` NEDENİYLE BİR İSTİSNA OLUŞTU",
            )
    else:
        await response.edit(
            f"{nrs.text} \n\nBot başarıyla güncellendi! Şimdi, bot yeniden başlayana kadar yaklaşık 5 dakika bekleyin!"
        )
        os.system("pip3 install -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && bash start")
        exit()
    return


@app.on_message(filters.command("restart") & filters.user(SUDOERS))
async def restart_(_, message):
    response = await message.reply_text("Yeniden Başlatılıyor...")
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU UYGULAMASI ALGILANDI!</b> \n\nUygulamanızı güncellemek için sırasıyla HEROKU_API_KEY ve HEROKU_APP_NAME değişkenlerini ayarlamanız gerekir!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU UYGULAMASI ALGILANDI!</b> \n\n<b>Uzaktan güncelleme yapabilmek için, HEROKU_API_KEY **ve** HEROKU_APP_NAME <b>değişkenlerini doğru şekilde eklediğinizden emin olun!</b>"
            )
        try:
            served_chats = []
            try:
                chats = await get_active_chats()
                for chat in chats:
                    served_chats.append(int(chat["chat_id"]))
            except Exception:
                pass
            for x in served_chats:
                try:
                    await app.send_message(
                        x,
                        f"{MUSIC_BOT_NAME} az önce kendini yeniden başlattı. Sorunlar için üzgünüm. \n\n10-15 saniye sonra tekrar oynatmaya başlayın.",
                    )
                    await remove_active_chat(x)
                    await remove_active_video_chat(x)
                except Exception:
                    pass
            heroku3.from_key(HEROKU_API_KEY).apps()[HEROKU_APP_NAME].restart()
            await response.edit(
                "**Heroku Yeniden Başlatma** \n\nYeniden başlatma başarılı! Bot yeniden başlayana kadar yaklaşık 5 dakika bekleyin."
            )
            return
        except Exception:
            await response.edit(
                "Bot yeniden başlatılırken bir şeyler ters gitti! Lütfen daha sonra tekrar deneyin veya daha fazla bilgi için Log'u kontrol edin."
            )
            return
    else:
        served_chats = []
        try:
            chats = await get_active_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
        except Exception:
            pass
        for x in served_chats:
            try:
                await app.send_message(
                    x,
                    f"{MUSIC_BOT_NAME} az önce kendini yeniden başlattı. Sorunlar için üzgünüm. \n\n10-15 saniye sonra tekrar oynatmaya başlayın.",
                )
                await remove_active_chat(x)
                await remove_active_video_chat(x)
            except Exception:
                pass
        A = "downloads"
        B = "raw_files"
        C = "cache"
        D = "search"
        try:
            shutil.rmtree(A)
            shutil.rmtree(B)
            shutil.rmtree(C)
            shutil.rmtree(D)
        except:
            pass
        await asyncio.sleep(2)
        try:
            os.mkdir(A)
        except:
            pass
        try:
            os.mkdir(B)
        except:
            pass
        try:
            os.mkdir(C)
        except:
            pass
        try:
            os.mkdir(D)
        except:
            pass
        await response.edit(
            "Yeniden başlatma başarılı! \nBot yeniden başlayana kadar yaklaşık 5 dakika bekleyin."
        )
        os.system(f"kill -9 {os.getpid()} && bash start")
