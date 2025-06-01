
import os
import threading
from requests import get, post

try:
    from urllib.parse import urlencode
except ImportError:
    os.system('pip install urllib3')
    from urllib.parse import urlencode
try:
    import MedoSigner
except ImportError:
    os.system('pip install MedoSigner')
    import MedoSigner
from random import choice, randrange
import requests
import re
from time import sleep, time
from telebot import TeleBot
from uuid import uuid4
import random
import json
from datetime import datetime
import secrets
import uuid
import binascii
import sys
from requests import post
from random import choice, randrange
import re
from MedoSigner import Argus, Gorgon, md5, Ladon
import urllib.parse
import binascii
import uuid
import time

# Global Variables
KBS = '100'  # Password
checking_active = False
linked_emails = []
lock = threading.Lock()  # Lock for thread safety when appending to linked_emails
session = requests.Session()


# دالة تسجيل الدخول إلى TikTok API
def sign(params, payload: str = None, sec_device_id: str = "", cookie: str or None = None, aid: int = 1233,
         license_id: int = 1611921764, sdk_version_str: str = "2.3.1.i18n", sdk_version: int = 2, platform: int = 19,
         unix: int = None):
    x_ss_stub = md5(payload.encode('utf-8')).hexdigest() if payload != None else None
    data = payload
    if not unix: unix = int(time.time())
    return Gorgon(params, unix, payload, cookie).get_value() | {
        "x-ladon": Ladon.encrypt(unix, license_id, aid),
        "x-argus": Argus.get_sign(params, x_ss_stub, unix, platform=platform, aid=aid, license_id=license_id,
                                   sec_device_id=sec_device_id, sdk_version=sdk_version_str,
                                   sdk_version_int=sdk_version)
    }


secret = secrets.token_hex(16)


# دالة الحصول على البارامترات
def get_params():
    try:
        global secret, session
        cookies = {
            "passport_csrf_token": secret,
            "passport_csrf_token_default": secret,
            "sessionid": "71bde776f6f69faf6030936b74f22e61"
        }
        session.cookies.update(cookies)
        params = {
            'passport-sdk-version': "19",
            'iid': str(random.randint(1, 10 ** 19)),
            'device_id': str(random.randint(1, 10 ** 19)),
            'ac': "WIFI",
            'channel': "googleplay",
            'aid': "1233",
            'app_name': "musical_ly",
            'version_code': "310503",
            'version_name': "31.5.3",
            'device_platform': "android",
            'os': "android",
            'ab_version': "31.5.3",
            'ssmix': "a",
            'device_type': random.choice(["SM-S928B", "P40", "Mi 11", "iPhone12,1", "OnePlus9"]),
            'device_brand': random.choice(["samsung", "huawei", "xiaomi", "apple", "oneplus"]),
            'language': "en",
            'os_api': str(random.randint(28, 34)),
            'os_version': str(random.randint(10, 14)),
            'openudid': str(binascii.hexlify(os.urandom(8)).decode()),
            'manifest_version_code': "2023105030",
            'resolution': "1080*2232",
            'dpi': str(random.choice([420, 480, 532])),
            'update_version_code': "2023105030",
            '_rticket': str(round(random.uniform(1.2, 1.6) * 100000000)) + "4632",
            'is_pad': "0",
            'current_region': random.choice(["AE", "IQ", "US", "FR", "DE"]),
            'app_type': "normal",
            'sys_region': random.choice(["AE", "IQ", "US", "FR", "DE"]),
            'mcc_mnc': "41805",
            'timezone_name': "Asia/Baghdad",
            'carrier_region_v2': "418",
            'residence': random.choice(["AE", "IQ", "US", "FR", "DE"]),
            'app_language': random.choice(["ar", "en"]),
            'carrier_region': random.choice(["AE", "IQ", "US", "FR", "DE"]),
            'ac2': "wifi",
            'uoo': "0",
            'op_region': random.choice(["AE", "IQ", "US", "FR", "DE"]),
            'timezone_offset': "10800",
            'build_number': "31.5.3",
            'host_abi': "arm64-v8a",
            'locale': "ar",
            'region': random.choice(["AE", "IQ", "US", "FR", "DE"]),
            'content_language': "ar,",
            'ts': str(round(random.uniform(1.2, 1.6) * 100000000)),
            'cdid': str(uuid.uuid4()),
            'support_webview': "1",
            'cronet_version': "2fdb62f9_2023-09-06",
            'ttnet_version': "4.2.152.11-tiktok",
            'use_store_region_cookie': "1"
        }
        return params
    except:
        return None


# دالة الحصول على الهيدرات
def get_headers():
    try:
        global secret, session
        pa = get_params()
        if not pa:
            return None, None
        m = sign(params=urlencode(pa), payload="", cookie="")

        headers = {
            'User-Agent': "com.zhiliaoapp.musically/2023105030 (Linux; U; Android 14; ar_IQ; Infinix X6833B; Build/UP1A.231005.007; Cronet/TTNetVersion:2fdb62f9 2023-09-06 QuicVersion:bb24d47c 2023-07-19)",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'x-tt-passport-csrf-token': secret,
            'x-argus': m["x-argus"],
            'x-gorgon': m["x-gorgon"],
            'x-khronos': m["x-khronos"],
            'x-ladon': m["x-ladon"]
        }
        return headers, pa
    except:
        return None, None


# دالة فحص البريد على TikTok
def check_email_tiktok(email, bot, chat_id):
    global linked_emails, lock, session # Include session in globals
    try:
        headers, params = get_headers()
        if not headers or not params:
            bot.send_message(chat_id, "Failed to get headers or params.")
            return False

        url = "https://api22-normal-c-alisg.tiktokv.com/passport/email/bind_without_verify/"
        res = session.post(url, params=params, data=f"email={email}", headers=headers)  # Reuse session
        res.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        res_json = res.json()


        if '1023' in str(res_json):
            with lock:
                print(f"البريد {email} مرتبط بحساب TikTok!")
                linked_emails.append(email)
            bot.send_message(chat_id, f"البريد {email} مرتبط بحساب TikTok!")
            return True
        else:
            print(f"البريد {email} غير مرتبط بحساب TikTok.")
            bot.send_message(chat_id, f"البريد {email} غير مرتبط بحساب TikTok.")
            return False
    except requests.exceptions.RequestException as e:  # Catch specific request exceptions
        bot.send_message(chat_id, f"حدث خطأ في الاتصال أثناء الفحص: {e}")
        return False
    except Exception as e:
        bot.send_message(chat_id, f"حدث خطأ أثناء الفحص: {e}")
        return False


# Telegram Bot Handlers
def start_bot(bot_token):
    global bot
    bot = TeleBot(bot_token)

    @bot.message_handler(commands=['start'])
    def start(message):
        bot.reply_to(message, "مرحبا! أنا هنا لفحص بريدك على TikTok. أرسل /help لعرض الأوامر.")

    @bot.message_handler(commands=['help'])
    def help(message):
        help_text = """
الأوامر المتاحة:
/start - لبدء البوت
/check_file - لفحص قائمة بريدات من ملف (أرسل الملف بعد هذا الأمر)
/check_manual <email> - لفحص بريد واحد يدويًا
/stop - لإيقاف الفحص الحالي وحفظ النتائج
/help - لعرض هذه الرسالة
        """
        bot.reply_to(message, help_text)

    @bot.message_handler(commands=['check_manual'])
    def check_manual(message):
        global checking_active
        try:
            email = message.text.split(' ')[1]  # Get the email from the command
            if email:
                checking_active = True
                bot.reply_to(message, f"جاري فحص البريد {email}...")
                check_email_tiktok(email, bot, message.chat.id)
                checking_active = False  # Stop after checking one email
                bot.reply_to(message, f"تم فحص البريد {email}.")
            else:
                bot.reply_to(message, "الرجاء إدخال بريد إلكتروني صالح بعد الأمر /check_manual.")
        except IndexError:
            bot.reply_to(message, "الرجاء إدخال بريد إلكتروني بعد الأمر /check_manual.")

    @bot.message_handler(commands=['stop'])
    def stop_checking(message):
        global checking_active, linked_emails
        if checking_active:
            checking_active = False
            bot.reply_to(message, "تم إيقاف الفحص. جاري حفظ النتائج...")

            # Save linked emails to file
            try:
                with open("owo.txt", "w") as f:
                    for email in linked_emails:
                        f.write(email + "\n")
                bot.reply_to(message, f"تم حفظ {len(linked_emails)} بريد مرتبط في owo.txt.")
            except Exception as e:
                bot.reply_to(message, f"حدث خطأ أثناء حفظ الملف: {e}")
            finally:
                linked_emails = []  # Clear the list after saving
        else:
            bot.reply_to(message, "لا يوجد فحص قيد التشغيل حاليًا.")

    @bot.message_handler(commands=['check_file'])
    def handle_check_file(message):
        bot.reply_to(message, "الرجاء إرسال ملف قائمة البريد الإلكتروني الآن.")

    @bot.message_handler(content_types=['document'])
    def handle_document(message):
        global checking_active
        if checking_active:
            bot.reply_to(message, "يوجد فحص قيد التشغيل. الرجاء إيقافه أولاً.")
            return

        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            email_list = downloaded_file.decode('utf-8').splitlines()

            checking_active = True
            bot.reply_to(message, f"جاري فحص {len(email_list)} بريد إلكتروني...")

            def process_emails(chat_id):
                global checking_active, session
                for email in email_list:
                    if not checking_active:
                        bot.send_message(chat_id, "تم إيقاف الفحص.")
                        break  # Stop if checking is deactivated

                    email = email.strip()
                    if email:
                        bot.send_chat_action(chat_id, action='typing')  # Show "typing" indicator
                        bot.send_message(chat_id, f"جاري فحص البريد: {email}")  # Added here
                        check_email_tiktok(email, bot, chat_id)
                        time.sleep(0.1) # Small delay to prevent overwhelming the API and bot
                if checking_active:
                    bot.send_message(chat_id, "تم الانتهاء من فحص جميع البريدات.")
                else:
                    bot.send_message(chat_id, "تم إيقاف الفحص قبل الانتهاء.")
                stop_checking(message)  # Automatically save results
                checking_active = False

            threading.Thread(target=process_emails, args=(message.chat.id,)).start()


        except Exception as e:
            bot.reply_to(message, f"حدث خطأ أثناء معالجة الملف: {e}")
            checking_active = False

    print("البوت يعمل الآن. ابدأ المحادثة مع البوت على Telegram.")
    bot.infinity_polling()




   # Get bot token from environment variable
token = os.getenv("BOT_TOKEN")

os.system('clear')

try:
    start_bot(token)  # استخدم المتغير الصحيح اللي فيه التوكن
except Exception as e:
    print(f"Error initializing bot: {e}")
