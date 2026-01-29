#!/usr/bin/env python3
"""
GenesisW Bot - Railway Version (Fixed Double Message Issue)
"""

import os
import asyncio
import logging
from telethon import TelegramClient, events, functions
from collections import defaultdict

# ========== CONFIGURATION FROM RAILWAY ENV VARS ==========
API_ID = int(os.environ.get("API_ID", "22446695"))
API_HASH = os.environ.get("API_HASH", "64587d7e1431a0d7e1959387faa4958a")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8576112278:AAE35GWqoHpsQ9bdB069f__LDShXkNeHXro")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER", "+996706161234")
# ========================================================

ADMIN_PASS = "Su54us"
CRYPTO_WALLET = "TKMBNpspKG6uQZi8J9siyChhX6BrZJnJr7"
SEARCH_LIMIT = 20

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data storage
user_searches = defaultdict(int)
admin_users = set()
user_states = {}
last_command_time = {}
COMMAND_COOLDOWN = 2  # seconds

# Clients
bot = None
search_client = None

async def init_search():
    """Initialize search client with session file"""
    global search_client
    
    session_file = 'genesis_session.session'
    
    if not os.path.exists(session_file):
        logger.error(f"Session file not found: {session_file}")
        logger.info("Upload genesis_session.session via Railway Files interface")
        return False
    
    try:
        search_client = TelegramClient(session_file, API_ID, API_HASH)
        await search_client.start()
        me = await search_client.get_me()
        logger.info(f"Search client ready: @{me.username}")
        return True
    except Exception as e:
        logger.error(f"Failed to init search client: {e}")
        return False

async def safe_send_message(event, text):
    """Send message with cooldown check to prevent duplicates"""
    user_id = event.sender_id
    current_time = asyncio.get_event_loop().time()
    
    # Check cooldown
    if user_id in last_command_time:
        time_passed = current_time - last_command_time[user_id]
        if time_passed < COMMAND_COOLDOWN:
            logger.warning(f"Cooldown active for user {user_id}, skipping duplicate")
            return False
    
    last_command_time[user_id] = current_time
    
    try:
        await event.respond(text)
        return True
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return False

async def main():
    global bot
    
    print("=" * 60)
    print("🚀 GenesisW Bot Starting...")
    print(f"📞 Phone: {PHONE_NUMBER}")
    print("=" * 60)
    
    # Initialize search client
    search_ready = await init_search()
    
    # Initialize bot
    bot = TelegramClient('genesis_bot', API_ID, API_HASH)
    await bot.start(bot_token=BOT_TOKEN)
    bot_me = await bot.get_me()
    print(f"🤖 Bot: @{bot_me.username}")
    print(f"🔍 Search: {'✅ READY' if search_ready else '❌ DISABLED'}")
    print("=" * 60)
    
    # Event handler for /start
    @bot.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        user_id = event.sender_id
        
        # Initialize user if not exists
        if user_id not in user_searches:
            user_searches[user_id] = 0
        
        search_status = "✅ РЕАЛЬНЫЙ ПОИСК" if search_ready else "⚠️ ПОИСК ОТКЛЮЧЕН"
        
        response = f"""
{search_status}

GenesisW Search Bot
Владелец: Gen Kai

📊 Ваш статус:
Поисков использовано: {user_searches[user_id]}/{SEARCH_LIMIT}
Осталось: {SEARCH_LIMIT - user_searches[user_id]}

📋 Команды:
/search - найти каналы
/admin - админ панель
/premium - премиум доступ
/help - справка
"""
        await safe_send_message(event, response)
    
    # Event handler for /search
    @bot.on(events.NewMessage(pattern='/search'))
    async def search_handler(event):
        user_id = event.sender_id
        
        if not search_ready:
            await safe_send_message(event, "⚠️ Поиск временно недоступен")
            return
        
        if user_id not in admin_users and user_searches[user_id] >= SEARCH_LIMIT:
            await safe_send_message(event, 
                f"❌ Лимит исчерпан!\n"
                f"Использовано: {user_searches[user_id]}/{SEARCH_LIMIT}\n\n"
                f"💰 Для безлимита: /premium"
            )
            return
        
        user_states[user_id] = 'awaiting_keyword'
        await safe_send_message(event, "🔍 Введите ключевое слово для поиска:")
    
    # Event handler for /admin
    @bot.on(events.NewMessage(pattern='/admin'))
    async def admin_handler(event):
        user_id = event.sender_id
        user_states[user_id] = 'awaiting_password'
        await safe_send_message(event, "Пиздуй нахуй 😎\n\n🔐 Введите пароль админа:")
    
    # Event handler for /premium
    @bot.on(events.NewMessage(pattern='/premium'))
    async def premium_handler(event):
        response = f"""
💰 ПРЕМИУМ ДОСТУП

ТАРИФЫ (USDT TRC20):
🥉 BASIC - 10 USDT (30 дней)
• Безлимитный поиск

🥈 ADVANCED - 25 USDT (90 дней)
• Безлимит + фильтры

🥇 PRO - 50 USDT (180 дней)
• Все функции + экспорт

👑 ULTIMATE - 100 USDT (ПОЖИЗНЕННО)
• Всё включено + API доступ

💳 КОШЕЛЁК ДЛЯ ОПЛАТЫ:
{CRYPTO_WALLET}

📨 После оплаты отправьте хэш транзакции
"""
        await safe_send_message(event, response)
    
    # Event handler for /help
    @bot.on(events.NewMessage(pattern='/help'))
    async def help_handler(event):
        response = f"""
🆘 СПРАВКА

📋 КОМАНДЫ:
/start - информация о боте
/search - поиск каналов
/premium - премиум доступ
/admin - админ панель
/help - эта справка

🔍 КАК ИСКАТЬ:
1. Отправьте /search
2. Введите ключевое слово
3. Получите результаты

📊 ЛИМИТЫ:
• Бесплатно: {SEARCH_LIMIT} поисков
• Премиум: безлимит (/premium)

👤 Владелец: Gen Kai
🤖 Бот: @genesisw_bot
"""
        await safe_send_message(event, response)
    
    # Main message handler for text input (keywords, admin password)
    @bot.on(events.NewMessage)
    async def message_handler(event):
        user_id = event.sender_id
        text = event.text.strip() if event.text else ""
        
        # Ignore empty messages or commands
        if not text or text.startswith('/'):
            return
        
        # Handle admin password input
        if user_id in user_states and user_states[user_id] == 'awaiting_password':
            if text == ADMIN_PASS:
                admin_users.add(user_id)
                user_searches[user_id] = 0
                await safe_send_message(event, 
                    f"✅ АДМИН ДОСТУП АКТИВИРОВАН!\n"
                    f"Теперь у вас безлимитный поиск."
                )
            else:
                await safe_send_message(event, "❌ Неверный пароль!")
            user_states.pop(user_id, None)
            return
        
        # Handle search keyword input
        if user_id in user_states and user_states[user_id] == 'awaiting_keyword':
            keyword = text.lower().strip()
            
            if len(keyword) < 2:
                await safe_send_message(event, "⚠️ Минимум 2 символа")
                user_states.pop(user_id, None)
                return
            
            # Update search counter for non-admin users
            if user_id not in admin_users:
                user_searches[user_id] += 1
            
            user_states.pop(user_id, None)
            
            await safe_send_message(event, f"🔍 Ищу каналы по запросу: '{keyword}'...")
            
            try:
                # Perform actual search
                channels = await search_client(functions.contacts.SearchRequest(
                    q=keyword,
                    limit=15
                ))
                
                results = []
                for chat in channels.chats:
                    if hasattr(chat, 'title'):
                        results.append({
                            'title': chat.title[:40],
                            'username': getattr(chat, 'username', None),
                            'members': getattr(chat, 'participants_count', 0)
                        })
                
                if results:
                    # Sort by member count
                    results.sort(key=lambda x: x['members'], reverse=True)
                    
                    response = f"✅ Найдено {len(results)} каналов:\n\n"
                    for i, ch in enumerate(results[:5], 1):
                        username = f"@{ch['username']}" if ch['username'] else "без @"
                        members = f"{ch['members']:,}" if ch['members'] > 0 else "?"
                        response += f"{i}. {ch['title']}\n"
                        response += f"   👥 {members} | {username}\n\n"
                    
                    if len(results) > 5:
                        response += f"📈 ... и ещё {len(results)-5} каналов"
                    
                    # Add limit info for regular users
                    if user_id not in admin_users:
                        used = user_searches[user_id]
                        response += f"\n\n📊 Ваш лимит: {used}/{SEARCH_LIMIT}"
                        if used >= SEARCH_LIMIT:
                            response += f"\n❌ ЛИМИТ ИСЧЕРПАН! /premium"
                    
                else:
                    response = f"❌ По запросу '{keyword}' ничего не найдено."
                
                await safe_send_message(event, response)
                
            except Exception as e:
                logger.error(f"Search error: {e}")
                await safe_send_message(event, "⚠️ Произошла ошибка при поиске.")
            return
    
    print("\n" + "=" * 60)
    print("🤖 Бот успешно запущен и готов к работе!")
    print("📞 Отправьте /start в Telegram для начала")
    print("=" * 60 + "\n")
    
    # Keep the bot running
    await bot.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем.")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
