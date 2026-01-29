#!/usr/bin/env python3
"""
GenesisW Bot - Fixed Version
"""

import os
import asyncio
import logging
from telethon import TelegramClient, events, functions

# ========== КОНФИГУРАЦИЯ ==========
API_ID = 22446695
API_HASH = "64587d7e1431a0d7e1959387faa4958a"
BOT_TOKEN = "8576112278:AAE35GWqoHpsQ9bdB069f__LDShXkNeHXro"
ADMIN_PASS = "Su54us"
# ==================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 GenesisW Bot запускается...")

# Хранилище данных
users = {}
admins = set()
states = {}

# Клиенты
bot = None
search_client = None

async def init_search():
    """Инициализация поискового клиента"""
    global search_client
    
    session_file = 'genesis_session.session'
    
    if not os.path.exists(session_file):
        print("❌ Файл сессии НЕ НАЙДЕН!")
        print(f"📞 Создай сессию для: +996706161234")
        return False
    
    try:
        search_client = TelegramClient(session_file, API_ID, API_HASH)
        await search_client.start()
        me = await search_client.get_me()
        print(f"✅ Поиск активен: @{me.username}")
        return True
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        return False

async def main():
    global bot
    
    # Инициализируем поиск
    search_ready = await init_search()
    
    # Запускаем бота
    bot = TelegramClient('genesis_bot', API_ID, API_HASH)
    await bot.start(bot_token=BOT_TOKEN)
    
    bot_me = await bot.get_me()
    print(f"🤖 Бот запущен: @{bot_me.username}")
    
    @bot.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        user_id = event.sender_id
        
        # Инициализируем пользователя
        if user_id not in users:
            users[user_id] = 0
        
        # Статус поиска
        if search_ready:
            search_status = "✅ ПОИСК РАБОТАЕТ"
        else:
            search_status = "⚠️ ПОИСК ОТКЛЮЧЕН"
        
        # Ответ
        text = f"""
{search_status}

GenesisW Search Bot
Владелец: Gen Kai

📊 Ваш статус:
Поисков: {users[user_id]}/20
Осталось: {20 - users[user_id]}

🔍 Команды:
/search - найти каналы
/admin - админка
/premium - безлимит
"""
        await event.respond(text)
    
    @bot.on(events.NewMessage(pattern='/search'))
    async def search_handler(event):
        user_id = event.sender_id
        
        if not search_ready:
            await event.respond("❌ Поиск не доступен!")
            return
        
        if user_id not in admins and users.get(user_id, 0) >= 20:
            await event.respond("❌ Лимит исчерпан! /premium")
            return
        
        states[user_id] = 'search'
        await event.respond("🔍 Введите ключевое слово:")
    
    @bot.on(events.NewMessage(pattern='/admin'))
    async def admin_handler(event):
        user_id = event.sender_id
        states[user_id] = 'admin'
        await event.respond("Пиздуй нахуй 😎\nПароль админа:")
    
    @bot.on(events.NewMessage(pattern='/premium'))
    async def premium_handler(event):
        text = """
💰 ПРЕМИУМ ДОСТУП

💎 Тарифы (USDT):
🥉 BASIC - 10 USDT
🥈 ADVANCED - 25 USDT
🥇 PRO - 50 USDT
👑 ULTIMATE - 100 USDT

💳 Кошелёк:
TKMBNpspKG6uQZi8J9siyChhX6BrZJnJr7
"""
        await event.respond(text)
    
    @bot.on(events.NewMessage)
    async def message_handler(event):
        user_id = event.sender_id
        text = event.text.strip() if event.text else ""
        
        if not text or text.startswith('/'):
            return
        
        # Обработка админ пароля
        if states.get(user_id) == 'admin':
            if text == ADMIN_PASS:
                admins.add(user_id)
                users[user_id] = 0
                await event.respond("✅ Админ доступ активирован!")
            else:
                await event.respond("❌ Неверный пароль!")
            states.pop(user_id, None)
            return
        
        # Обработка поискового запроса
        if states.get(user_id) == 'search' and search_ready:
            keyword = text.lower()
            
            if len(keyword) < 2:
                await event.respond("⚠️ Минимум 2 символа")
                states.pop(user_id, None)
                return
            
            # Обновляем счётчик
            if user_id not in admins:
                users[user_id] = users.get(user_id, 0) + 1
            
            states.pop(user_id, None)
            await event.respond(f"🔍 Ищу: '{keyword}'...")
            
            try:
                # Выполняем поиск
                result = await search_client(functions.contacts.SearchRequest(
                    q=keyword,
                    limit=10
                ))
                
                # Обрабатываем результаты
                channels = []
                for chat in result.chats:
                    if hasattr(chat, 'title'):
                        channels.append({
                            'title': chat.title[:40],
                            'username': getattr(chat, 'username', None),
                            'members': getattr(chat, 'participants_count', 0)
                        })
                
                if channels:
                    # Сортируем по количеству участников
                    channels.sort(key=lambda x: x['members'], reverse=True)
                    
                    response = f"✅ Найдено {len(channels)} каналов:\n\n"
                    for i, ch in enumerate(channels[:5], 1):
                        username = f"@{ch['username']}" if ch['username'] else "без @"
                        members = f"{ch['members']:,}" if ch['members'] > 0 else "?"
                        response += f"{i}. {ch['title']}\n"
                        response += f"   👥 {members} | {username}\n\n"
                    
                    await event.respond(response)
                else:
                    await event.respond(f"❌ По запросу '{keyword}' ничего не найдено")
                    
            except Exception as e:
                logger.error(f"Search error: {e}")
                await event.respond("⚠️ Ошибка при выполнении поиска")
            return
    
    print("\n" + "="*50)
    print("🤖 БОТ АКТИВЕН И ГОТОВ К РАБОТЕ!")
    print("🔍 Поиск:", "✅" if search_ready else "❌")
    print("📞 Отправь /start в Telegram")
    print("="*50)
    
    # Запускаем бота
    await bot.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")