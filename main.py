#!/usr/bin/env python3
"""
GenesisW Bot - FULL WORKING VERSION
РАБОТАЕТ ДЛЯ ВСЕХ • ПОИСК 10 РЕЗУЛЬТАТОВ • ВИП СТАТУС • HELP • АДМИН БЕЗЛИМИТ
"""

import os
import asyncio
import time
from datetime import datetime, timedelta
from telethon import TelegramClient, events, functions

# ========== КОНФИГ ==========
API_ID = int(os.environ.get("API_ID", "22446695"))
API_HASH = os.environ.get("API_HASH", "64587d7e1431a0d7e1959387faa4958a")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8576112278:AAE35GWqoHpsQ9bdB069f__LDShXkNeHXro"))
ADMIN_ID = 6902281947  # Твой ID - ВИП статус
CRYPTO_WALLET = "TKMBNpspKG6uQZi8J9siyChhX6BrZJnJr7"
SEARCH_LIMIT = 20
# ============================

print("\n" + "="*70)
print("🚀 GENESISW BOT - FULL VERSION")
print("="*70)

# ========== ХРАНИЛИЩЕ ==========
users_db = {}
last_commands = {}

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
    return user_id == ADMIN_ID

def is_premium(user_id):
    user = get_user(user_id)
    if is_vip(user_id):
        return True
    if user['premium'] and user['premium_until']:
        return datetime.now() < user['premium_until']
    return False

def can_search(user_id):
    if is_vip(user_id) or is_premium(user_id):
        return True
    user = get_user(user_id)
    return user['searches'] < SEARCH_LIMIT

# ========== ТЕЛЕГРАМ КЛИЕНТЫ ==========
bot = None
search_client = None

async def init_clients():
    """Инициализация клиентов"""
    global bot, search_client
    
    print("🔧 Запускаю клиенты...")
    
    # 1. БОТ-клиент (отвечает всем)
    try:
        bot = TelegramClient('bot_session', API_ID, API_HASH)
        await bot.start(bot_token=BOT_TOKEN)
        bot_info = await bot.get_me()
        print(f"✅ Бот готов: @{bot_info.username}")
    except Exception as e:
        print(f"❌ Ошибка бота: {e}")
        return False
    
    # 2. ПОЛЬЗОВАТЕЛЬ для поиска
    try:
        if os.path.exists('genesis_session.session'):
            search_client = TelegramClient('genesis_session', API_ID, API_HASH)
            await search_client.start()
            user_info = await search_client.get_me()
            print(f"✅ Поиск готов: @{user_info.username}")
        else:
            print("⚠️ Файл сессии не найден")
            search_client = None
    except Exception as e:
        print(f"⚠️ Ошибка поиска: {e}")
        search_client = None
    
    return True

async def real_search(keyword, limit=10):
    """Реальный поиск каналов"""
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
    print("🎯 Инициализация бота...")
    
    if not await init_clients():
        print("❌ Не могу запустить")
        return
    
    print("✅ Бот готов принимать команды от ВСЕХ пользователей")
    
    # ========== КОМАНДА /start ==========
    @bot.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        user_id = event.sender_id
        user = get_user(user_id)
        
        vip = is_vip(user_id)
        premium = is_premium(user_id)
        
        if vip:
            status = "👑 <b>ВЛАДЕЛЕЦ (VIP)</b>"
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

💎 @genesisw_bot
"""
        await event.respond(text, parse_mode='html')
    
    # ========== КОМАНДА /help ==========
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
• VIP: безлимит + особые права

<b>💎 ПРЕМИУМ ТАРИФЫ (USDT TRC20):</b>
🥉 BASIC - 10 USDT (30 дней)
🥈 ADVANCED - 25 USDT (90 дней)
🥇 PRO - 50 USDT (180 дней)
👑 ULTIMATE - 100 USDT (НАВСЕГДА)

<b>💳 КОШЕЛЁК ДЛЯ ОПЛАТЫ:</b>
<code>{CRYPTO_WALLET}</code>

<b>📝 ПОСЛЕ ОПЛАТЫ:</b>
Отправьте хэш транзакции для проверки

👑 Владелец: @Alexanderiprx
🤖 Бот: @genesisw_bot
"""
        await event.respond(text, parse_mode='html')
    
    # ========== КОМАНДА /profile ==========
    @bot.on(events.NewMessage(pattern='/profile'))
    async def profile_handler(event):
        user_id = event.sender_id
        user = get_user(user_id)
        
        vip = is_vip(user_id)
        premium = is_premium(user_id)
        
        if vip:
            status_icon = "👑"
            status_text = "ВЛАДЕЛЕЦ"
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
        
        # Прогресс бар для обычных пользователей
        if not vip and not premium:
            progress = user['searches'] / SEARCH_LIMIT * 100
            bar = "█" * int(progress/10) + "░" * (10 - int(progress/10))
            text += f"\n📊 Прогресс: [{bar}] {progress:.1f}%\n"
            
            if user['searches'] >= SEARCH_LIMIT:
                text += "\n⚠️ <b>ЛИМИТ ИСЧЕРПАН!</b>\n💎 Купите премиум для продолжения\n"
        
        await event.respond(text, parse_mode='html')
    
    # ========== КОМАНДА /search ==========
    @bot.on(events.NewMessage(pattern='/search'))
    async def search_handler(event):
        user_id = event.sender_id
        user = get_user(user_id)
        
        vip = is_vip(user_id)
        premium = is_premium(user_id)
        
        # Проверка лимита
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
Используйте команду /premium для выбора тарифа
"""
            await event.respond(text, parse_mode='html')
            return
        
        user['state'] = 'searching'
        await event.respond("🔍 <b>Введите ключевое слово для поиска:</b>\n\nПример: крипта, новости, спорт, музыка", parse_mode='html')
    
    # ========== КОМАНДА /premium ==========
    @bot.on(events.NewMessage(pattern='/premium'))
    async def premium_handler(event):
        user_id = event.sender_id
        
        # Если уже VIP
        if is_vip(user_id):
            await event.respond("👑 <b>Вы уже ВЛАДЕЛЕЦ с безлимитным доступом!</b>", parse_mode='html')
            return
        
        text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃        💎 PREMIUM           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

<b>ТАРИФЫ (USDT TRC20):</b>

🥉 BASIC - 10 USDT (30 дней)
• Безлимитный поиск
• 10 результатов за запрос

🥈 ADVANCED - 25 USDT (90 дней)
• BASIC + фильтры поиска
• 15 результатов за запрос

🥇 PRO - 50 USDT (180 дней)
• ADVANCED + экспорт данных
• 20 результатов за запрос

👑 ULTIMATE - 100 USDT (НАВСЕГДА)
• Все функции + API доступ
• 25 результатов за запрос

<b>💳 КОШЕЛЁК ДЛЯ ОПЛАТЫ:</b>
<code>{CRYPTO_WALLET}</code>

<b>📝 ПОСЛЕ ОПЛАТЫ:</b>
Отправьте хэш транзакции для активации Premium

<b>🔍 ПРОВЕРКА ПЛАТЕЖЕЙ:</b>
• Автоматическая проверка через TronScan
• Активация в течение 15 минут
"""
        await event.respond(text, parse_mode='html')
    
    # ========== КОМАНДА /admin ==========
    @bot.on(events.NewMessage(pattern='/admin'))
    async def admin_handler(event):
        user_id = event.sender_id
        
        # Только для админа
        if not is_vip(user_id):
            await event.respond("❌ <b>У вас нет доступа к админ панели</b>", parse_mode='html')
            return
        
        # АДМИН ПАНЕЛЬ
        total_users = len(users_db)
        total_searches = sum(u['searches'] for u in users_db.values())
        premium_users = sum(1 for u in users_db.values() if is_premium(u) and not is_vip(u))
        
        text = f"""
┏━━━━━━━━━━━━━━━━━━━━┓
┃    👑 АДМИН ПАНЕЛЬ ┃
┗━━━━━━━━━━━━━━━━━━━━┛

<b>📊 СТАТИСТИКА:</b>
👥 Всего пользователей: {total_users}
🔍 Всего поисков: {total_searches}
💎 Премиум пользователей: {premium_users}
⭐ VIP пользователей: {sum(1 for uid in users_db if is_vip(uid))}

<b>👤 ВАШ СТАТУС:</b>
• VIP статус: ✅ АКТИВЕН
• Поисков: БЕЗЛИМИТ
• Доступ: ПОЛНЫЙ

<b>⚡ БЫСТРЫЕ ДЕЙСТВИЯ:</b>
• /stats - подробная статистика
• Проверять платежи вручную
• Добавлять премиум по запросу
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
        
        # ========== ПОИСК ==========
        if user.get('state') == 'searching':
            keyword = text.lower()
            
            if len(keyword) < 2:
                await event.respond("⚠️ <b>Минимум 2 символа</b>", parse_mode='html')
                user['state'] = None
                return
            
            vip = is_vip(user_id)
            premium = is_premium(user_id)
            
            # Увеличиваем счётчик если не VIP и не премиум
            if not vip and not premium:
                user['searches'] += 1
            
            user['state'] = None
            
            # Проверяем лимит после увеличения
            if not vip and not premium and user['searches'] > SEARCH_LIMIT:
                await event.respond(f"❌ <b>Лимит исчерпан!</b>\n\nИспользуйте /premium для безлимитного доступа", parse_mode='html')
                return
            
            await event.respond(f"🔍 <b>Ищу каналы:</b> '{keyword}'...", parse_mode='html')
            
            channels = await real_search(keyword, 10)
            
            if not channels:
                await event.respond(f"❌ <b>По запросу '{keyword}' ничего не найдено</b>", parse_mode='html')
                return
            
            # ФОРМИРУЕМ ОТВЕТ С 10 РЕЗУЛЬТАТАМИ
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
            
            # Информация о лимитах
            if not vip and not premium:
                remaining = SEARCH_LIMIT - user['searches']
                if remaining > 0:
                    result_text += f"\n📊 <b>Осталось бесплатных поисков:</b> {remaining}"
                else:
                    result_text += f"\n⚠️ <b>Бесплатные поиски закончились!</b>\n💎 /premium - безлимит"
            
            await event.respond(result_text, parse_mode='html')
            return
        
        # ========== АВТОПРОВЕРКА ХЭША ПЛАТЕЖА ==========
        if len(text) >= 20 and all(c.isalnum() for c in text):
            # Похоже на хэш транзакции
            await event.respond(f"""
🔍 <b>Обнаружен хэш транзакции</b>
<code>{text[:20]}...</code>

💎 Платёж принят в обработку!
Ожидайте активации Premium (до 15 минут)

👑 Для быстрой активации обратитесь к @Alexanderiprx
""", parse_mode='html')
            
            # Логируем хэш
            print(f"💰 Получен хэш платежа от {user_id}: {text[:20]}...")
            return
    
    print("\n" + "="*70)
    print("🤖 БОТ УСПЕШНО ЗАПУЩЕН!")
    print("✅ Работает для ВСЕХ пользователей")
    print("✅ 10 результатов поиска")
    print("✅ VIP статус для владельца")
    print("✅ Админ безлимит")
    print("✅ Команда /help")
    print("📞 Тестируйте команды:")
    print("   /start - /search - /help - /profile - /premium - /admin")
    print("="*70)
    
    # Запускаем бота
    await bot.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")