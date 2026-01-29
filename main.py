#!/usr/bin/env python3
"""
GenesisW Bot - FINAL WORKING VERSION
"""

import os
import asyncio
import logging
import time
from telethon import TelegramClient, events, functions, types
from collections import defaultdict

# ========== CONFIG ==========
API_ID = int(os.environ.get("API_ID", "22446695"))
API_HASH = os.environ.get("API_HASH", "64587d7e1431a0d7e1959387faa4958a"))
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8576112278:AAE35GWqoHpsQ9bdB069f__LDShXkNeHXro")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER", "+996706161234")

ADMIN_PASS = "Su54us"
CRYPTO_WALLET = "TKMBNpspKG6uQZi8J9siyChhX6BrZJnJr7"
SEARCH_LIMIT = 20
# ============================

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

print("=" * 60)
print("🚀 GenesisW Bot - STARTING")
print(f"📁 Session: {'genesis_session.session' if os.path.exists('genesis_session.session') else 'NOT FOUND'}")
print("=" * 60)

# Хранилище
user_searches = defaultdict(int)
admin_users = set()
user_states = {}
last_command = {}

# Клиенты
bot = None
search_client = None

async def init_search():
    """Инициализация поиска"""
    global search_client
    
    try:
        if not os.path.exists('genesis_session.session'):
            logger.error("❌ No session file")
            return False
        
        search_client = TelegramClient('genesis_session', API_ID, API_HASH)
        await search_client.start()
        me = await search_client.get_me()
        logger.info(f"✅ Search: @{me.username}")
        return True
    except Exception as e:
        logger.error(f"❌ Search init: {e}")
        return False

async def init_bot():
    """Инициализация бота с задержкой"""
    global bot
    
    try:
        # Ждём 5 секунд между клиентами
        logger.info("⏳ Waiting 5s before bot init...")
        await asyncio.sleep(5)
        
        bot = TelegramClient('bot_session', API_ID, API_HASH)
        
        # Настройки для избежания флуд контроля
        bot.session.set_dc(2, '149.154.167.51', 443)
        
        await bot.start(bot_token=BOT_TOKEN)
        
        bot_info = await bot.get_me()
        logger.info(f"✅ Bot: @{bot_info.username}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Bot init failed: {e}")
        
        # Пробуем альтернативный метод
        try:
            logger.info("🔄 Trying alternative method...")
            await asyncio.sleep(10)  # Ждём 10 секунд
            
            # Создаём нового клиента
            bot = TelegramClient('bot_session_alt', API_ID, API_HASH)
            await bot.start(bot_token=BOT_TOKEN)
            
            bot_info = await bot.get_me()
            logger.info(f"✅ Bot (alt): @{bot_info.username}")
            return True
        except Exception as e2:
            logger.error(f"❌ Alt method also failed: {e2}")
            return False

async def safe_send(event, text):
    """Отправка сообщения с защитой"""
    user_id = event.sender_id
    current_time = time.time()
    
    # Защита от дублирования
    if user_id in last_command:
        if current_time - last_command[user_id] < 2:
            return False
    
    last_command[user_id] = current_time
    
    try:
        await event.respond(text)
        return True
    except:
        return False

async def perform_search(keyword):
    """Выполнение поиска"""
    if not search_client:
        return None
    
    try:
        result = await search_client(functions.contacts.SearchRequest(
            q=keyword,
            limit=10
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
        return channels
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return None

async def main():
    logger.info("Initializing...")
    
    # Инициализируем поиск
    search_ready = await init_search()
    
    # Инициализируем бота с задержкой
    bot_ready = await init_bot()
    
    if not bot_ready:
        logger.error("❌ Bot failed to start. Check token or wait.")
        return
    
    # ========== ОБРАБОТЧИКИ ==========
    active_handlers = set()
    
    @bot.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        key = f"start_{user_id}"
        
        if key in active_handlers:
            return
        active_handlers.add(key)
        
        try:
            if user_id not in user_searches:
                user_searches[user_id] = 0
            
            status = "✅ ПОИСК РАБОТАЕТ" if search_ready else "⚠️ ПОИСК ОТКЛЮЧЕН"
            
            text = f"""{status}

GenesisW Search Bot
Поисков: {user_searches[user_id]}/{SEARCH_LIMIT}

Команды:
/search - найти каналы
/admin - админка
/premium - безлимит
/help - справка"""
            
            await safe_send(event, text)
        finally:
            active_handlers.discard(key)
    
    @bot.on(events.NewMessage(pattern='/search'))
    async def search_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        key = f"search_{user_id}"
        
        if key in active_handlers:
            return
        active_handlers.add(key)
        
        try:
            if not search_ready:
                await safe_send(event, "⚠️ Поиск отключен")
                return
            
            if user_id not in admin_users and user_searches[user_id] >= SEARCH_LIMIT:
                await safe_send(event, "❌ Лимит! /premium")
                return
            
            user_states[user_id] = 'search'
            await safe_send(event, "🔍 Введите слово:")
        finally:
            active_handlers.discard(key)
    
    @bot.on(events.NewMessage(pattern='/admin'))
    async def admin_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        key = f"admin_{user_id}"
        
        if key in active_handlers:
            return
        active_handlers.add(key)
        
        try:
            user_states[user_id] = 'admin'
            await safe_send(event, "Пиздуй нахуй 😎\nПароль админа:")
        finally:
            active_handlers.discard(key)
    
    @bot.on(events.NewMessage(pattern='/premium'))
    async def premium_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        key = f"premium_{user_id}"
        
        if key in active_handlers:
            return
        active_handlers.add(key)
        
        try:
            text = f"""💰 ПРЕМИУМ ДОСТУП

💳 Кошелёк:
{CRYPTO_WALLET}"""
            await safe_send(event, text)
        finally:
            active_handlers.discard(key)
    
    @bot.on(events.NewMessage)
    async def message_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        text = event.text.strip() if event.text else ""
        
        if not text or text.startswith('/'):
            return
        
        key = f"msg_{user_id}"
        if key in active_handlers:
            return
        active_handlers.add(key)
        
        try:
            # Админ пароль
            if user_states.get(user_id) == 'admin':
                if text == ADMIN_PASS:
                    admin_users.add(user_id)
                    user_searches[user_id] = 0
                    await safe_send(event, "✅ Админ доступ активирован!")
                else:
                    await safe_send(event, "❌ Неверный пароль!")
                user_states.pop(user_id, None)
                return
            
            # Поисковый запрос
            if user_states.get(user_id) == 'search' and search_ready:
                keyword = text.lower().strip()
                
                if len(keyword) < 2:
                    await safe_send(event, "⚠️ Минимум 2 символа")
                    user_states.pop(user_id, None)
                    return
                
                if user_id not in admin_users:
                    user_searches[user_id] += 1
                
                user_states.pop(user_id, None)
                
                await safe_send(event, f"🔍 Ищу: '{keyword}'...")
                
                channels = await perform_search(keyword)
                
                if channels is None:
                    await safe_send(event, "⚠️ Ошибка поиска")
                elif channels:
                    response = f"✅ Найдено {len(channels)} каналов:\n\n"
                    for i, ch in enumerate(channels[:3], 1):
                        username = f"@{ch['username']}" if ch['username'] else "без @"
                        response += f"{i}. {ch['title']}\n{username}\n\n"
                    
                    await safe_send(event, response)
                else:
                    await safe_send(event, f"❌ По '{keyword}' ничего")
                return
        finally:
            active_handlers.discard(key)
    
    print("\n" + "=" * 60)
    print("🤖 БОТ ЗАПУЩЕН!")
    print(f"🔍 Поиск: {'✅' if search_ready else '❌'}")
    print("📞 Отправь /start в Telegram")
    print("=" * 60)
    
    # Запускаем
    await bot.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Остановлен")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
