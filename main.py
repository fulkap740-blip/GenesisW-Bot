#!/usr/bin/env python3
"""
GenesisW Bot - FINAL VERSION
ВАШ ID: 7870118249 • СКРЫТЫЕ АДМИН ФУНКЦИИ • ПАРОЛЬНЫЙ ДОСТУП
"""

import os
import asyncio
import time
from datetime import datetime, timedelta
from telethon import TelegramClient, events, functions

# ========== КОНФИГ ==========
API_ID = int(os.environ.get("API_ID", "22446695")
API_HASH = os.environ.get("API_HASH", "64587d7e1431a0d7e1959387faa4958a"))
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8576112278:AAE35GWqoHpsQ9bdB069f__LDShXkNeHXro"))

# СКРЫТЫЕ КЛЮЧИ ДОСТУПА (ТВОИ)
ADMIN_PASSWORD = "Su54us"        # Пароль для админ панели
BEZLIM_PASSWORD = "X9p!vR7z"     # Пароль для безлимита
VIP_USER_ID = 7870118249         # ТВОЙ ПРАВИЛЬНЫЙ ID 👑

CRYPTO_WALLET = "TKMBNpspKG6uQZi8J9siyChhX6BrZJnJr7"
SEARCH_LIMIT = 20
# ============================

print("\n" + "="*70)
print("🚀 GENESISW BOT - FINAL VERSION")
print(f"👑 Владелец ID: {VIP_USER_ID}")
print("="*70)

# ========== ХРАНИЛИЩЕ ==========
users_db = {}
admin_users = set()  # Пользователи с доступом к админке
bezlim_users = set() # Пользователи с безлимитом

def get_user(user_id):
    if user_id not in users_db:
        users_db[user_id] = {
            'searches': 0,
            'premium': False,
            'premium_until': None,
            'state': None,
            'joined': datetime.now()
        }
    return users_db[user_id]

def is_vip(user_id):
    # Ты (VIP) или админ или безлимит
    return (user_id == VIP_USER_ID or 
            user_id in admin_users or 
            user_id in bezlim_users)

def is_premium(user_id):
    user = get_user(user_id)
    if is_vip(user_id):
        return True
    if user['premium'] and user['premium_until']:
        return datetime.now() < user['premium_until']
    return False

# ========== ТЕЛЕГРАМ КЛИЕНТЫ ==========
bot = None
search_client = None

async def init_clients():
    global bot, search_client
    
    print("🔧 Запускаю бота...")
    
    try:
        bot = TelegramClient('bot_session', API_ID, API_HASH)
        await bot.start(bot_token=BOT_TOKEN)
        bot_info = await bot.get_me()
        print(f"✅ Бот запущен: @{bot_info.username}")
    except Exception as e:
        print(f"❌ Ошибка бота: {e}")
        return False
    
    try:
        if os.path.exists('genesis_session.session'):
            search_client = TelegramClient('genesis_session', API_ID, API_HASH)
            await search_client.start()
            print("✅ Поиск активирован")
        else:
            print("⚠️ Файл сессии не найден")
            search_client = None
    except Exception as e:
        print(f"⚠️ Ошибка поиска: {e}")
        search_client = None
    
    return True

async def real_search(keyword, limit=10):
    if not search_client:
        return None
    
    try:
        print(f"🔍 Поиск: '{keyword}'")
        
        result = await search_client(functions.contacts.SearchRequest(
            q=keyword,
            limit=limit
        ))
        
        channels = []
        for chat in result.chats:
            if hasattr(chat, 'title'):
                channels.append({
                    'title': chat.title[:40],
                    'username': getattr(chat, 'username', None),
                    'members': getattr(chat, 'participants_count', 0)
                })
        
        channels.sort(key=lambda x: x['members'], reverse=True)
        return channels[:limit]
        
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        return None

# ========== ОСНОВНАЯ ФУНКЦИЯ ==========
async def main():
    print("🎯 Инициализация...")
    
    if not await init_clients():
        print("❌ Не могу запустить")
        return
    
    print("✅ Бот готов к работе")
    
    # ========== /start ==========
    @bot.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        user_id = event.sender_id
        user = get_user(user_id)
        
        vip = is_vip(user_id)
        premium = is_premium(user_id)
        
        if vip:
            status = "👑 <b>VIP ДОСТУП</b>"
            limit_text = "♾️ БЕЗЛИМИТ"
        elif premium:
            status = "💎 <b>PREMIUM</b>"
            limit_text = "♾️ БЕЗЛИМИТ"
        else:
            status = "⚪ <b>BASIC</b>"
            remaining = SEARCH_LIMIT - user['searches']
            limit_text = f"{remaining}/{SEARCH_LIMIT}"
        
        text = f"""
{status}

🆔 ID: <code>{user_id}</code>
🔍 Поисков: {user['searches']}
📊 Лимит: {limit_text}

<b>📋 КОМАНДЫ:</b>
/search - найти каналы (10 результатов)
/premium - премиум доступ
/help - полная справка
/profile - ваш профиль
"""
        await event.respond(text, parse_mode='html')
    
    # ========== /help ==========
    @bot.on(events.NewMessage(pattern='/help'))
    async def help_handler(event):
        text = f"""
🆘 <b>ПОМОЩЬ ПО GENESISW BOT</b>

<b>📋 ОСНОВНЫЕ КОМАНДЫ:</b>
/start - главное меню
/search - поиск каналов (10 результатов)
/premium - премиум доступ
/profile - ваш профиль
/help - эта справка

<b>🔍 КАК ИСКАТЬ:</b>
1. Отправьте /search
2. Введите ключевое слово
3. Получите 10 лучших каналов

<b>📊 ЛИМИТЫ:</b>
• Бесплатно: {SEARCH_LIMIT} поисков
• Премиум: безлимитный поиск
• VIP: безлимит

<b>💎 ПРЕМИУМ ТАРИФЫ (USDT TRC20):</b>
🥉 BASIC - 10 USDT (30 дней)
🥈 ADVANCED - 25 USDT (90 дней)
🥇 PRO - 50 USDT (180 дней)
👑 ULTIMATE - 100 USDT (НАВСЕГДА)

<b>💳 КОШЕЛЁК ДЛЯ ОПЛАТЫ:</b>
<code>{CRYPTO_WALLET}</code>

<b>📝 ПОСЛЕ ОПЛАТЫ:</b>
Отправьте хэш транзакции
"""
        await event.respond(text, parse_mode='html')
    
    # ========== /profile ==========
    @bot.on(events.NewMessage(pattern='/profile'))
    async def profile_handler(event):
        user_id = event.sender_id
        user = get_user(user_id)
        
        vip = is_vip(user_id)
        premium = is_premium(user_id)
        
        if vip:
            status_icon = "👑"
            status_text = "VIP ДОСТУП"
            limit_text = "♾️ БЕЗЛИМИТ"
        elif premium:
            status_icon = "💎"
            status_text = "PREMIUM"
            limit_text = "♾️ БЕЗЛИМИТ"
        else:
            status_icon = "⚪"
            status_text = "BASIC"
            remaining = SEARCH_LIMIT - user['searches']
            limit_text = f"{remaining}/{SEARCH_LIMIT}"
        
        text = f"""
┏━━━━━━━━━━━━━━━━━━━━┓
┃     👤 ПРОФИЛЬ     ┃
┗━━━━━━━━━━━━━━━━━━━━┛

{status_icon} <b>{status_text}</b>
🆔 ID: <code>{user_id}</code>
🔍 Поисков использовано: {user['searches']}
📊 Доступно поисков: {limit_text}
📅 В системе: {(datetime.now() - user['joined']).days} дней
"""
        if premium and user['premium_until']:
            days_left = (user['premium_until'] - datetime.now()).days
            text += f"📅 Премиум истекает через: {days_left} дней\n"
        
        if not vip and not premium:
            progress = user['searches'] / SEARCH_LIMIT * 100
            bar = "█" * int(progress/10) + "░" * (10 - int(progress/10))
            text += f"\n📊 Прогресс: [{bar}] {progress:.1f}%\n"
            
            if user['searches'] >= SEARCH_LIMIT:
                text += "\n⚠️ <b>ЛИМИТ ИСЧЕРПАН!</b>\n💎 Купите премиум для продолжения\n"
        
        await event.respond(text, parse_mode='html')
    
    # ========== /search ==========
    @bot.on(events.NewMessage(pattern='/search'))
    async def search_handler(event):
        user_id = event.sender_id
        user = get_user(user_id)
        
        vip = is_vip(user_id)
        premium = is_premium(user_id)
        
        if not vip and not premium and user['searches'] >= SEARCH_LIMIT:
            text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃     ⚠️ ЛИМИТ ИСЧЕРПАН       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🔍 Вы использовали все {SEARCH_LIMIT} поисков.

💎 <b>Для продолжения нужен PREMIUM</b>

💳 Оплата в <b>USDT (TRC20)</b>
📦 Кошелёк:
<code>{CRYPTO_WALLET}</code>

📝 После оплаты отправьте <b>хэш транзакции</b>
"""
            await event.respond(text, parse_mode='html')
            return
        
        user['state'] = 'searching'
        await event.respond("🔍 <b>Введите ключевое слово для поиска:</b>\n\nПример: крипта, новости, спорт, музыка", parse_mode='html')
    
    # ========== /premium ==========
    @bot.on(events.NewMessage(pattern='/premium'))
    async def premium_handler(event):
        user_id = event.sender_id
        
        if is_vip(user_id):
            await event.respond("👑 <b>У вас уже VIP доступ с безлимитом!</b>", parse_mode='html')
            return
        
        text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃        💎 PREMIUM           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

<b>ТАРИФЫ (USDT TRC20):</b>

🥉 BASIC - 10 USDT (30 дней)
🥈 ADVANCED - 25 USDT (90 дней)
🥇 PRO - 50 USDT (180 дней)
👑 ULTIMATE - 100 USDT (НАВСЕГДА)

<b>💳 КОШЕЛЁК:</b>
<code>{CRYPTO_WALLET}</code>
"""
        await event.respond(text, parse_mode='html')
    
    # ========== /admin ========== (СКРЫТАЯ)
    @bot.on(events.NewMessage(pattern='/admin'))
    async def admin_handler(event):
        user_id = event.sender_id
        
        if user_id in admin_users:
            await show_admin_panel(event, user_id)
            return
        
        user = get_user(user_id)
        user['state'] = 'admin_auth'
        await event.respond("🔐 <b>Введите пароль админа:</b>", parse_mode='html')
    
    # ========== /bezlim ========== (СКРЫТАЯ)
    @bot.on(events.NewMessage(pattern='/bezlim'))
    async def bezlim_handler(event):
        user_id = event.sender_id
        
        if is_vip(user_id):
            await event.respond("✅ <b>У вас уже есть безлимит!</b>", parse_mode='html')
            return
        
        user = get_user(user_id)
        user['state'] = 'bezlim_auth'
        await event.respond("🔑 <b>Введите код для безлимита:</b>", parse_mode='html')
    
    # ========== /vip ========== (ТОЛЬКО ДЛЯ ТЕБЯ)
    @bot.on(events.NewMessage(pattern='/vip'))
    async def vip_handler(event):
        user_id = event.sender_id
        
        if user_id != VIP_USER_ID:
            await event.respond("❌ <b>Команда недоступна</b>", parse_mode='html')
            return
        
        text = f"""
🔒 <b>СЕКРЕТНАЯ ПАНЕЛЬ</b>

👑 Ваш ID: <code>{VIP_USER_ID}</code>
🔑 Админ пароль: {ADMIN_PASSWORD}
🔑 Безлимит код: {BEZLIM_PASSWORD}

<b>👥 СТАТУСЫ:</b>
• Админов: {len(admin_users)}
• Безлимит: {len(bezlim_users)}
• Всего юзеров: {len(users_db)}

<b>⚡ КОМАНДЫ:</b>
• /admin → {ADMIN_PASSWORD}
• /bezlim → {BEZLIM_PASSWORD}
"""
        await event.respond(text, parse_mode='html')
    
    # ========== ОБРАБОТКА СООБЩЕНИЙ ==========
    @bot.on(events.NewMessage)
    async def message_handler(event):
        user_id = event.sender_id
        text = event.text.strip() if event.text else ""
        
        if not text or text.startswith('/'):
            return
        
        user = get_user(user_id)
        state = user.get('state')
        
        # ========== АДМИН АВТОРИЗАЦИЯ ==========
        if state == 'admin_auth':
            if text == ADMIN_PASSWORD:
                admin_users.add(user_id)
                user['state'] = None
                await event.respond("✅ <b>АДМИН ДОСТУП АКТИВИРОВАН!</b>", parse_mode='html')
                await show_admin_panel(event, user_id)
            else:
                await event.respond("❌ <b>НЕВЕРНЫЙ ПАРОЛЬ</b>", parse_mode='html')
                user['state'] = None
            return
        
        # ========== БЕЗЛИМИТ АКТИВАЦИЯ ==========
        elif state == 'bezlim_auth':
            if text == BEZLIM_PASSWORD:
                bezlim_users.add(user_id)
                user['state'] = None
                await event.respond("""
🎉 <b>БЕЗЛИМИТ АКТИВИРОВАН!</b>

Теперь у вас:
• ♾️ Безлимитный поиск
• 👑 VIP статус
• 🔍 Неограниченные запросы
""", parse_mode='html')
            else:
                await event.respond("❌ <b>НЕВЕРНЫЙ КОД</b>", parse_mode='html')
                user['state'] = None
            return
        
        # ========== ПОИСК ==========
        elif state == 'searching':
            keyword = text.lower()
            
            if len(keyword) < 2:
                await event.respond("⚠️ <b>Минимум 2 символа</b>", parse_mode='html')
                user['state'] = None
                return
            
            vip = is_vip(user_id)
            premium = is_premium(user_id)
            
            if not vip and not premium:
                user['searches'] += 1
            
            user['state'] = None
            
            if not vip and not premium and user['searches'] > SEARCH_LIMIT:
                await event.respond(f"❌ <b>Лимит исчерпан!</b>\n\nИспользуйте /premium", parse_mode='html')
                return
            
            await event.respond(f"🔍 <b>Ищу каналы:</b> '{keyword}'...", parse_mode='html')
            
            channels = await real_search(keyword, 10)
            
            if not channels:
                await event.respond(f"❌ <b>По запросу '{keyword}' ничего не найдено</b>", parse_mode='html')
                return
            
            result_text = f"""
✅ <b>НАЙДЕНО {len(channels)} КАНАЛОВ</b>
🔍 Запрос: '{keyword}'

<b>ТОП-{len(channels)} результатов:</b>
"""
            for i, ch in enumerate(channels, 1):
                username = f"@{ch['username']}" if ch['username'] else "без @"
                members = f"{ch['members']:,}" if ch['members'] > 0 else "?"
                result_text += f"\n{i}. <b>{ch['title']}</b>"
                result_text += f"\n   👥 {members} | {username}\n"
            
            if not vip and not premium:
                remaining = SEARCH_LIMIT - user['searches']
                if remaining > 0:
                    result_text += f"\n📊 <b>Осталось поисков:</b> {remaining}"
                else:
                    result_text += f"\n⚠️ <b>Лимит исчерпан!</b>\n💎 /premium"
            
            await event.respond(result_text, parse_mode='html')
            return
        
        # ========== ХЭШ ПЛАТЕЖА ==========
        if len(text) >= 20 and all(c.isalnum() for c in text):
            await event.respond(f"""
🔍 <b>Обнаружен хэш транзакции</b>
<code>{text[:20]}...</code>

💎 Платёж принят в обработку!
""", parse_mode='html')
            return
    
    # ========== АДМИН ПАНЕЛЬ ==========
    async def show_admin_panel(event, user_id):
        total_users = len(users_db)
        total_searches = sum(u['searches'] for u in users_db.values())
        
        text = f"""
┏━━━━━━━━━━━━━━━━━━━━┓
┃    👑 АДМИН ПАНЕЛЬ ┃
┗━━━━━━━━━━━━━━━━━━━━┛

<b>📊 СТАТИСТИКА:</b>
👥 Всего пользователей: {total_users}
🔍 Всего поисков: {total_searches}
⭐ Админов: {len(admin_users)}
♾️ Безлимит: {len(bezlim_users)}

<b>🔑 ПАРОЛИ:</b>
• Админ: <code>{ADMIN_PASSWORD}</code>
• Безлимит: <code>{BEZLIM_PASSWORD}</code>

<b>⚡ ДЕЙСТВИЯ:</b>
1. Дать безлимит: Отправь код <code>{BEZLIM_PASSWORD}</code>
2. Дать админку: Отправь пароль <code>{ADMIN_PASSWORD}</code>
"""
        await event.respond(text, parse_mode='html')
    
    print("\n" + "="*70)
    print("🤖 БОТ ЗАПУЩЕН!")
    print(f"👑 Владелец ID: {VIP_USER_ID}")
    print("🔒 Скрытые команды:")
    print("   /admin - админ панель")
    print("   /bezlim - безлимит навсегда")
    print("   /vip - только для владельца")
    print("="*70)
    
    await bot.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")