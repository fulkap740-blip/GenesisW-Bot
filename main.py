#!/usr/bin/env python3
"""
GenesisW Bot - FULL WORKING VERSION
"""

import os
import asyncio
import logging
import time
from telethon import TelegramClient, events, functions, types
from collections import defaultdict

# ========== CONFIG ==========
# Получаем из Railway Variables
API_ID = int(os.environ.get("API_ID", "22446695"))
API_HASH = os.environ.get("API_HASH", "64587d7e1431a0d7e1959387faa4958a")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8576112278:AAE35GWqoHpsQ9bdB069f__LDShXkNeHXro"))
PHONE_NUMBER = os.environ.get("PHONE_NUMBER", "+996706161234")

ADMIN_PASS = "Su54us"
CRYPTO_WALLET = "TKMBNpspKG6uQZi8J9siyChhX6BrZJnJr7"
SEARCH_LIMIT = 20
# ============================

print(f"""
{'='*60}
🚀 GENESISW BOT STARTING
📞 Phone: {PHONE_NUMBER}
🤖 Token: {BOT_TOKEN[:15]}...
{'='*60}
""")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Storage
user_searches = defaultdict(int)
admin_users = set()
user_states = {}
last_action = {}

# Clients
bot_client = None
search_client = None

async def init_search_client():
    """Initialize search client with session file"""
    global search_client
    
    session_files = [
        'genesis_session.session',
        'session.session',
        'telethon.session'
    ]
    
    # Check for session file
    found_session = None
    for session_file in session_files:
        if os.path.exists(session_file):
            found_session = session_file
            print(f"✅ Found session file: {session_file}")
            break
    
    if not found_session:
        print("❌ NO SESSION FILE FOUND!")
        print("Upload genesis_session.session via Railway")
        return False
    
    try:
        # Initialize client
        search_client = TelegramClient(found_session, API_ID, API_HASH)
        
        # Connect
        await search_client.start()
        
        # Verify connection
        me = await search_client.get_me()
        print(f"✅ Search client connected: @{me.username} (ID: {me.id})")
        return True
        
    except Exception as e:
        print(f"❌ Search client failed: {e}")
        return False

async def perform_search(keyword, limit=15):
    """Perform actual Telegram search"""
    if not search_client:
        return None
    
    try:
        print(f"🔍 Searching for: '{keyword}'")
        
        # Telegram API search
        result = await search_client(functions.contacts.SearchRequest(
            q=keyword,
            limit=limit
        ))
        
        channels = []
        for chat in result.chats:
            if isinstance(chat, (types.Channel, types.Chat)):
                channels.append({
                    'id': chat.id,
                    'title': chat.title,
                    'username': getattr(chat, 'username', None),
                    'members': getattr(chat, 'participants_count', 0),
                    'verified': getattr(chat, 'verified', False)
                })
        
        print(f"✅ Found {len(channels)} channels")
        return channels
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        return None

async def send_message(event, text):
    """Send message with spam protection"""
    user_id = event.sender_id
    current_time = time.time()
    
    # Anti-spam
    if user_id in last_action:
        if current_time - last_action[user_id] < 2:
            return False
    
    last_action[user_id] = current_time
    
    try:
        await event.respond(text)
        return True
    except Exception as e:
        print(f"Send error: {e}")
        return False

async def main():
    global bot_client
    
    print("Initializing bot...")
    
    # Initialize search FIRST
    search_ready = await init_search_client()
    
    if not search_ready:
        print("⚠️ WARNING: Search disabled")
    
    # Initialize bot
    bot_client = TelegramClient('bot', API_ID, API_HASH)
    await bot_client.start(bot_token=BOT_TOKEN)
    
    bot_info = await bot_client.get_me()
    print(f"✅ Bot started: @{bot_info.username}")
    
    # ========== COMMAND HANDLERS ==========
    
    @bot_client.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        user_id = event.sender_id
        
        if user_id not in user_searches:
            user_searches[user_id] = 0
        
        status = "✅ ПОИСК АКТИВЕН" if search_ready else "⚠️ ПОИСК ОТКЛЮЧЕН"
        
        text = f"""
{status}

GenesisW Search Bot v2.0
Владелец: Gen Kai

📊 Ваш статус:
Поисков: {user_searches[user_id]}/{SEARCH_LIMIT}
Осталось: {SEARCH_LIMIT - user_searches[user_id]}

🔍 Команды:
/search - найти каналы
/premium - безлимит
/admin - админка
/help - справка

💎 @genesisw_bot
"""
        await send_message(event, text)
    
    @bot_client.on(events.NewMessage(pattern='/search'))
    async def search_handler(event):
        user_id = event.sender_id
        
        if not search_ready:
            await send_message(event, "⚠️ Поиск отключен. Нужна сессия.")
            return
        
        # Check limit
        if user_id not in admin_users and user_searches[user_id] >= SEARCH_LIMIT:
            await send_message(event, 
                f"❌ Лимит!\n"
                f"Использовано: {user_searches[user_id]}/{SEARCH_LIMIT}\n\n"
                f"💰 /premium - безлимит"
            )
            return
        
        user_states[user_id] = 'searching'
        await send_message(event, "🔍 Введите слово для поиска:")
    
    @bot_client.on(events.NewMessage(pattern='/admin'))
    async def admin_handler(event):
        user_id = event.sender_id
        user_states[user_id] = 'admin_auth'
        await send_message(event, "Пиздуй нахуй 😎\nПароль админа:")
    
    @bot_client.on(events.NewMessage(pattern='/premium'))
    async def premium_handler(event):
        text = f"""
💰 ПРЕМИУМ ДОСТУП

💎 Тарифы (USDT TRC20):
🥉 BASIC - 10 USDT (30 дней)
🥈 ADVANCED - 25 USDT (90 дней)
🥇 PRO - 50 USDT (180 дней)
👑 ULTIMATE - 100 USDT (НАВСЕГДА)

💳 Кошелёк:
{CRYPTO_WALLET}

📨 После оплаты отправьте хэш транзакции
"""
        await send_message(event, text)
    
    @bot_client.on(events.NewMessage(pattern='/help'))
    async def help_handler(event):
        text = f"""
🆘 ПОМОЩЬ

📋 Команды:
/start - информация
/search - поиск
/premium - безлимит
/admin - админка
/help - эта справка

🔍 Как искать:
1. /search
2. Ввести слово
3. Получить результат

📊 Лимиты:
Бесплатно: {SEARCH_LIMIT} поисков
Премиум: безлимит

@genesisw_bot
"""
        await send_message(event, text)
    
    # ========== MESSAGE HANDLER ==========
    
    @bot_client.on(events.NewMessage)
    async def message_handler(event):
        user_id = event.sender_id
        text = event.text.strip() if event.text else ""
        
        if not text or text.startswith('/'):
            return
        
        # Admin auth
        if user_states.get(user_id) == 'admin_auth':
            if text == ADMIN_PASS:
                admin_users.add(user_id)
                user_searches[user_id] = 0
                await send_message(event, "✅ Админ доступ активирован!")
            else:
                await send_message(event, "❌ Неверный пароль!")
            user_states.pop(user_id, None)
            return
        
        # Search query
        if user_states.get(user_id) == 'searching' and search_ready:
            keyword = text.lower().strip()
            
            if len(keyword) < 2:
                await send_message(event, "⚠️ Минимум 2 символа")
                user_states.pop(user_id, None)
                return
            
            # Update counter
            if user_id not in admin_users:
                user_searches[user_id] += 1
            
            user_states.pop(user_id, None)
            
            await send_message(event, f"🔍 Ищу: '{keyword}'...")
            
            # PERFORM ACTUAL SEARCH
            channels = await perform_search(keyword)
            
            if channels is None:
                await send_message(event, "⚠️ Ошибка поиска")
            elif channels:
                # Format results
                result_text = f"✅ Найдено {len(channels)} каналов:\n\n"
                
                for i, ch in enumerate(channels[:5], 1):
                    name = ch['title'][:35]
                    username = f"@{ch['username']}" if ch['username'] else "без @"
                    members = f"{ch['members']:,}" if ch['members'] > 0 else "?"
                    
                    result_text += f"{i}. {name}\n"
                    result_text += f"   👥 {members} | {username}\n\n"
                
                if len(channels) > 5:
                    result_text += f"... и ещё {len(channels)-5} каналов"
                
                await send_message(event, result_text)
            else:
                await send_message(event, f"❌ По '{keyword}' ничего не найдено")
            return
    
    # ========== RUN BOT ==========
    
    print(f"""
{'='*60}
🤖 БОТ ЗАПУЩЕН И ГОТОВ!
🔍 Поиск: {'✅' if search_ready else '❌'}
📞 Номер: {PHONE_NUMBER}
👑 Админ: {ADMIN_PASS}
💳 Кошелёк: {CRYPTO_WALLET[:15]}...
{'='*60}
    """)
    
    print("📞 Отправьте /start в Telegram")
    
    # Keep running
    await bot_client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
