#!/usr/bin/env python3
"""
GenesisW Bot - FINAL FIXED VERSION
"""

import os
import asyncio
import logging
import time
from telethon import TelegramClient, events, functions, types
from collections import defaultdict

# ========== CONFIG ==========
API_ID = int(os.environ.get("API_ID", "22446695"))
API_HASH = os.environ.get("API_HASH", "64587d7e1431a0d7e1959387faa4958a")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8576112278:AAE35GWqoHpsQ9bdB069f__LDShXkNeHXro")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER", "+996706161234")

ADMIN_PASS = "Su54us"
CRYPTO_WALLET = "TKMBNpspKG6uQZi8J9siyChhX6BrZJnJr7"
SEARCH_LIMIT = 20
# ============================

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Проверка файлов
print("=" * 60)
print("📁 FILE CHECK")
print(f"Dir: {os.getcwd()}")
files = os.listdir('.')
print(f"Files ({len(files)}): {', '.join(files[:10])}{'...' if len(files) > 10 else ''}")

# Ищем сессию
SESSION_FILES = ['genesis_session.session', 'session.session', 'telethon.session']
session_path = None
for sf in SESSION_FILES:
    if os.path.exists(sf):
        session_path = sf
        print(f"✅ Found: {sf} ({os.path.getsize(sf)} bytes)")
        break

if not session_path:
    print("❌ No session file found!")
    print("Upload genesis_session.session to Railway")

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
    
    if not session_path:
        logger.error("No session file for search")
        return False
    
    try:
        search_client = TelegramClient(session_path, API_ID, API_HASH)
        await search_client.start()
        me = await search_client.get_me()
        logger.info(f"Search client ready: @{me.username}")
        return True
    except Exception as e:
        logger.error(f"Search init failed: {e}")
        return False

async def safe_send(event, text):
    """Отправка сообщения без дублирования"""
    user_id = event.sender_id
    current_time = time.time()
    
    # Защита от дублирования (3 секунды)
    if user_id in last_command:
        if current_time - last_command[user_id] < 3:
            logger.warning(f"Cooldown for user {user_id}")
            return False
    
    last_command[user_id] = current_time
    
    try:
        await event.respond(text)
        logger.info(f"Sent to {user_id}")
        return True
    except Exception as e:
        logger.error(f"Send failed: {e}")
        return False

async def perform_search(keyword):
    """Выполнение поиска"""
    if not search_client:
        return None
    
    try:
        logger.info(f"Searching: {keyword}")
        
        result = await search_client(functions.contacts.SearchRequest(
            q=keyword,
            limit=12
        ))
        
        channels = []
        for chat in result.chats:
            if hasattr(chat, 'title'):
                channels.append({
                    'title': chat.title[:40],
                    'username': getattr(chat, 'username', None),
                    'members': getattr(chat, 'participants_count', 0),
                    'verified': getattr(chat, 'verified', False)
                })
        
        channels.sort(key=lambda x: x['members'], reverse=True)
        logger.info(f"Found {len(channels)} channels")
        return channels
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return None

async def main():
    global bot
    
    logger.info("Starting GenesisW Bot...")
    
    # Инициализация поиска
    search_ready = await init_search()
    search_status = "✅" if search_ready else "❌"
    
    # Инициализация бота
    try:
        bot = TelegramClient('bot', API_ID, API_HASH)
        await bot.start(bot_token=BOT_TOKEN)
        bot_info = await bot.get_me()
        logger.info(f"Bot started: @{bot_info.username}")
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")
        return
    
    # ========== HANDLERS ==========
    handlers_active = {}
    
    @bot.on(events.NewMessage(pattern=r'^/start$'))
    async def start_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        if user_id not in user_searches:
            user_searches[user_id] = 0
        
        # Проверяем активность обработчика
        handler_key = f"start_{user_id}"
        if handler_key in handlers_active:
            return
        handlers_active[handler_key] = True
        
        try:
            status = "✅ ПОИСК РАБОТАЕТ" if search_ready else "⚠️ ПОИСК ОТКЛЮЧЕН"
            
            text = f"""{status}

GenesisW Search Bot
Владелец: Gen Kai

📊 Ваш статус:
Поисков: {user_searches[user_id]}/{SEARCH_LIMIT}
Осталось: {SEARCH_LIMIT - user_searches[user_id]}

🔍 Команды:
/search - найти каналы
/premium - безлимит
/admin - админка
/help - справка

💎 @genesisw_bot"""
            
            await safe_send(event, text)
        finally:
            handlers_active.pop(handler_key, None)
    
    @bot.on(events.NewMessage(pattern=r'^/search$'))
    async def search_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        
        handler_key = f"search_{user_id}"
        if handler_key in handlers_active:
            return
        handlers_active[handler_key] = True
        
        try:
            if not search_ready:
                await safe_send(event, "⚠️ Поиск отключен")
                return
            
            if user_id not in admin_users and user_searches[user_id] >= SEARCH_LIMIT:
                await safe_send(event, 
                    f"❌ Лимит!\n"
                    f"Использовано: {user_searches[user_id]}/{SEARCH_LIMIT}\n\n"
                    f"💰 /premium - безлимит"
                )
                return
            
            user_states[user_id] = 'awaiting_keyword'
            await safe_send(event, "🔍 Введите слово для поиска:")
        finally:
            handlers_active.pop(handler_key, None)
    
    @bot.on(events.NewMessage(pattern=r'^/admin$'))
    async def admin_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        
        handler_key = f"admin_{user_id}"
        if handler_key in handlers_active:
            return
        handlers_active[handler_key] = True
        
        try:
            user_states[user_id] = 'awaiting_password'
            await safe_send(event, "Пиздуй нахуй 😎\nПароль админа:")
        finally:
            handlers_active.pop(handler_key, None)
    
    @bot.on(events.NewMessage(pattern=r'^/premium$'))
    async def premium_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        
        handler_key = f"premium_{user_id}"
        if handler_key in handlers_active:
            return
        handlers_active[handler_key] = True
        
        try:
            text = f"""💰 ПРЕМИУМ ДОСТУП

💎 Тарифы (USDT TRC20):
🥉 BASIC - 10 USDT (30 дней)
🥈 ADVANCED - 25 USDT (90 дней)
🥇 PRO - 50 USDT (180 дней)
👑 ULTIMATE - 100 USDT (НАВСЕГДА)

💳 Кошелёк:
{CRYPTO_WALLET}

📨 После оплаты отправьте хэш транзакции"""
            
            await safe_send(event, text)
        finally:
            handlers_active.pop(handler_key, None)
    
    @bot.on(events.NewMessage(pattern=r'^/help$'))
    async def help_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        
        handler_key = f"help_{user_id}"
        if handler_key in handlers_active:
            return
        handlers_active[handler_key] = True
        
        try:
            text = f"""🆘 ПОМОЩЬ

📋 Команды:
/start - информация
/search - поиск
/premium - безлимит
/admin - админка
/help - справка

🔍 Как искать:
1. /search
2. Ввести слово
3. Получить результат

📊 Лимиты:
Бесплатно: {SEARCH_LIMIT} поисков
Премиум: безлимит

@genesisw_bot"""
            
            await safe_send(event, text)
        finally:
            handlers_active.pop(handler_key, None)
    
    @bot.on(events.NewMessage(pattern=r'^/debug$'))
    async def debug_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        
        handler_key = f"debug_{user_id}"
        if handler_key in handlers_active:
            return
        handlers_active[handler_key] = True
        
        try:
            text = f"""🔧 DEBUG:
• User: {user_id}
• Searches: {user_searches.get(user_id, 0)}/{SEARCH_LIMIT}
• Admin: {user_id in admin_users}
• Search ready: {search_ready}
• Session: {session_path or 'None'}
• State: {user_states.get(user_id, 'None')}"""
            
            await safe_send(event, text)
        finally:
            handlers_active.pop(handler_key, None)
    
    # Основной обработчик сообщений
    @bot.on(events.NewMessage)
    async def message_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        text = event.text.strip() if event.text else ""
        
        if not text or text.startswith('/'):
            return
        
        handler_key = f"msg_{user_id}_{text[:20]}"
        if handler_key in handlers_active:
            return
        handlers_active[handler_key] = True
        
        try:
            # Админ пароль
            if user_states.get(user_id) == 'awaiting_password':
                if text == ADMIN_PASS:
                    admin_users.add(user_id)
                    user_searches[user_id] = 0
                    await safe_send(event, "✅ Админ доступ активирован!")
                else:
                    await safe_send(event, "❌ Неверный пароль!")
                user_states.pop(user_id, None)
                return
            
            # Поисковый запрос
            if user_states.get(user_id) == 'awaiting_keyword' and search_ready:
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
                    for i, ch in enumerate(channels[:5], 1):
                        username = f"@{ch['username']}" if ch['username'] else "без @"
                        members = f"{ch['members']:,}" if ch['members'] > 0 else "?"
                        response += f"{i}. {ch['title']}\n"
                        response += f"   👥 {members} | {username}\n\n"
                    
                    if len(channels) > 5:
                        response += f"... и ещё {len(channels)-5} каналов"
                    
                    await safe_send(event, response)
                else:
                    await safe_send(event, f"❌ По '{keyword}' ничего не найдено")
                return
        finally:
            handlers_active.pop(handler_key, None)
    
    print(f"""
{'='*60}
🤖 GENESIW BOT - READY
🔍 Search: {search_status}
📞 Phone: {PHONE_NUMBER}
💼 Wallet: {CRYPTO_WALLET[:15]}...
{'='*60}
    """)
    
    logger.info("Bot is running. Send /start in Telegram")
    
    try:
        await bot.run_until_disconnected()
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        logger.info("Bot stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"\n💀 FATAL: {e}")
        import traceback
        traceback.print_exc()
