import os
import requests
import re
import base64
import time
import socket
import json
import random
from datetime import datetime
import pytz

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@NexGozar")

HISTORY_FILE = "history.txt"
MAX_HISTORY_LINES = 1000

SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/vless/base64",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/oslook/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/Alireza0491/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/w1770946466/Auto_Proxy/main/Long_Term_Proxy_Sub",
    "https://raw.githubusercontent.com/coor-net/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/shif6/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/SamanGhaffarzadeh/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/mftf0/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/vfarid/v2ray-auto-config/master/v2ray-sub-with-vless.txt"
]

TITLE_VARIATIONS = [
    "🔥 کانفیگ جدید رسید!", "⚡️ اتصال جدید برقرار شد", "🚀 سرور پرسرعت اختصاصی",
    "🛸 شکار جدید از سرورهای زنده", "🛡 فیلترشکن دور‌زننده محدودیت", "💎 کانفیگ تست‌شده و پایدار",
    "🎯 دسترسی بدون سانسور و روان", "👑 سرور VIP و خط اختصاصی", "✨ فرکانس جدید اتصال آزاد",
    "🔮 کانفیگ بدون قطعی و پرقدرت"
]

SUPPORT_VARIATIONS = [
    "❤️ وصل شدی حمایت یادت نره", "✨ با دوستانت به اشتراک بگذار",
    "🚀 حمایت شما باعث انرژی ماست"
]

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()

def save_to_history(config_hash):
    with open(HISTORY_FILE, "a") as f:
        f.write(config_hash + "\n")
    try:
        with open(HISTORY_FILE, "r") as f:
            lines = f.read().splitlines()
        if len(lines) > MAX_HISTORY_LINES:
            with open(HISTORY_FILE, "w") as f:
                f.write("\n".join(lines[-MAX_HISTORY_LINES:]) + "\n")
    except:
        pass

def get_protocol(config):
    for p in ["vless", "vmess", "trojan", "ss", "ssr"]:
        if config.lower().startswith(p):
            return p.upper()
    return "VLESS"

def extract_host_and_port(config):
    try:
        config = config.strip()
        if config.startswith("vmess://"):
            b64_data = config.replace("vmess://", "")
            b64_data += "=" * ((4 - len(b64_data) % 4) % 4)
            decoded = base64.b64decode(b64_data).decode('utf-8', errors='ignore')
            data = json.loads(decoded)
            return data.get("add"), int(data.get("port", 443))
        else:
            clean_target = re.sub(r'^(vless|trojan|ss|ssr)://', '', config)
            server_part = clean_target.split('@')[-1].split('?')[0].split('#')[0]
            host = server_part.split(':')[0]
            port = int(server_part.split(':')[1]) if ':' in server_part else 443
            return host, port
    except:
        return None, None

def check_live_ping(host, port):
    if not host or not port:
        return False, 0
    try:
        start_time = time.time()
        s = socket.create_connection((host, port), timeout=1.5)
        s.close()
        ping_ms = int((time.time() - start_time) * 1000)
        return True, ping_ms
    except:
        return False, 0

def get_server_location(host):
    if not host:
        return "🌐 Global"
    try:
        response = requests.get(f"http://ip-api.com/json/{host}", timeout=2).json()
        if response.get("status") == "success":
            country_name = response.get("country", "Global")
            country_code = response.get("countryCode", "")
            if country_code:
                flag_emoji = "".join(chr(127397 + ord(c)) for c in country_code.upper())
                return f"{flag_emoji} {country_name}"
            return f"🌐 {country_name}"
    except:
        pass
    return "🌐 Global"

def rename_config(config, new_name):
    try:
        config = config.strip()
        if config.startswith("vmess://"):
            b64_data = config.replace("vmess://", "")
            b64_data += "=" * ((4 - len(b64_data) % 4) % 4)
            decoded = base64.b64decode(b64_data).decode('utf-8', errors='ignore')
            data = json.loads(decoded)
            data["ps"] = new_name
            new_json = json.dumps(data).encode('utf-8')
            return "vmess://" + base64.b64encode(new_json).decode('utf-8')
        if "#" in config:
            base_config = config.split("#")[0]
            return f"{base_config}#{new_name}"
        else:
            return f"{config}#{new_name}"
    except:
        return config

def fetch_configs():
    all_configs = []
    pattern = re.compile(r'((?:vless|vmess|trojan|ss|ssr)://[^\s]+)')
    history = load_history()
    
    shuffled_sources = SOURCES.copy()
    random.shuffle(shuffled_sources)
    
    for url in shuffled_sources[:3]:
        try:
            print(f"Fetching from: {url}")
            response = requests.get(url, timeout=2.5)
            if response.status_code == 200:
                text_content = response.text
                if "://" not in text_content and len(text_content.strip()) > 20:
                    try:
                        text_content = base64.b64decode(text_content.strip()).decode('utf-8')
                    except:
                        pass
                matches = pattern.findall(text_content)
                for match in matches:
                    config_base = match.split("#")[0]
                    if config_base not in history:
                        all_configs.append(match)
        except:
            print("سورس کند بود، رد شد.")
            
    return list(set(all_configs))

def send_to_telegram(config_data, host=None, ping_ms=0):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    real_location = get_server_location(host)
    proto = get_protocol(config_data)
    config_text = f"<code>{config_data}</code>"
    title = random.choice(TITLE_VARIATIONS)
    random_support = random.choice(SUPPORT_VARIATIONS)
    
    # ⏱ گرفتن ساعت دقیق ایران به صورت زنده
    tehran_tz = pytz.timezone('Asia/Tehran')
    current_time = datetime.now(tehran_tz).strftime("%H:%M")
    
    dynamic_hashtags = f"#کانفیگ_رایگان #ویتوری #v2ray #فیلترشکن #پروکسی #{proto.lower()}"
    
    text = (
        f"<blockquote>{title}</blockquote>\n"
        f"<blockquote>📍 لوکیشن: {real_location}</blockquote>\n"
        f"<blockquote>🔐 پروتکل: {proto}</blockquote>\n"
        f"<blockquote>⚡️ وضعیت: 🟢 ۱۰۰٪ زنده (تست شده در {current_time})</blockquote>\n"
        f"<blockquote>📊 تأخیر سرور: ⚡️ {ping_ms} میلی‌ثانیه (عالی)</blockquote>\n\n"
        f"{config_text}\n\n"
        f"<blockquote>{random_support}</blockquote>\n"
        f"<blockquote>🆔 {CHANNEL_ID}</blockquote>\n"
        f"<blockquote>{dynamic_hashtags}</blockquote>"
    )
    
    payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML"}
    try:
        res = requests.post(url, json=payload, timeout=5)
        if res.status_code == 200:
            print("ارسال به تلگرام موفقیت‌آمیز بود.")
            save_to_history(config_data.split("#")[0])
        else:
            print(f"خطای تلگرام: {res.text}")
    except Exception as e:
        print(f"خطا در ارسال: {e}")

def run_one_cycle():
    configs = fetch_configs()
    print(f"تعداد جدیدها: {len(configs)}")
    if configs:
        config_name = "NexGozar"
        live_configs = []
        
        for cfg in configs:
            host, port = extract_host_and_port(cfg)
            if host and port:
                is_live, ping_ms = check_live_ping(host, port)
                if is_live:
                    renamed = rename_config(cfg, config_name)
                    live_configs.append((renamed, host, ping_ms))
                    if len(live_configs) >= 1:
                        break
        
        if live_configs:
            for cfg, host_ip, ping_ms in live_configs:
                send_to_telegram(cfg, host=host_ip, ping_ms=ping_ms)
        else:
            print("کانفیگ زنده جدیدی یافت نشد.")
    else:
        print("هیچ کانفیگ جدیدی در منابع نبود.")

if __name__ == "__main__":
    for i in range(3):
        print(f"--- پارت {i+1} ---")
        run_one_cycle()
        if i < 2:
            time.sleep(45)
