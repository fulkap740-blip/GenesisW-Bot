#!/usr/bin/env python3
"""
GenesisW Search - Professional Version
"""

import asyncio
import logging
import time
from datetime import datetime
from telethon import TelegramClient, events, functions
from collections import defaultdict

# ========== НАСТРОЙКИ ==========
API_ID = 22446695
API_HASH = "64587d7e1431a0d7e1959387faa4958a"
BOT_TOKEN = "8576112278:AAE35GWqoHpsQ9bdB069f__LDShXkNeHXro"

ADMIN_PASSWORD = "Su54us"
CRYPTO_WALLET = "TKMBNpspKG6uQZi8J9siyChhX6BrZJnJr7"
# ==============================

print("🚀 GenesisW Search запускается...")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Система
SEARCH_LIMIT = 20
user_searches = defaultdict(int)
admin_users = set()
search_engine = None
last_command = {}

# Инициализация поиска
async def init_engine():
    global search_engine
    try:
        if os.path.exists('session.auth'):
            search_engine = TelegramClient('session.auth', API_ID, API_HASH)
            await search_engine.start()
            return True
        return False
    except:
        return False

# Поиск каналов
async def search_channels(query):
    if not search_engine:
        return None
    
    try:
        result = await search_engine(functions.contacts.SearchRequest(
            q=query,
            limit=12
        ))
        
        results = []
        for chat in result.chats:
            if hasattr(chat, 'title'):
                results.append({
                    'name': chat.title[:35],
                    'username': getattr(chat, 'username', None),
                    'members': getattr(chat, 'participants_count', 0),
                    'verified': getattr(chat, 'verified', False)
                })
        
        results.sort(key=lambda x: x['members'], reverse=True)
        return results
    except:
        return None

# Запуск бота
async def main():
    try:
        bot = TelegramClient('genesis.bot', API_ID, API_HASH)
        await bot.start(bot_token=BOT_TOKEN)
        
        me = await bot.get_me()
        print(f"✅ Бот запущен: @{me.username}")
        
        # Состояния
        user_mode = {}
        
        @bot.on(events.NewMessage(pattern='/start'))
        async def start_cmd(event):
            user_id = event.sender_id
            if user_id not in user_searches:
                user_searches[user_id] = 0
            
            await event.respond(f"""
🔍 **GENESISW CHANNEL SEARCH**

Мощный поиск телеграм каналов по ключевым словам

🎯 **Ваш статус:**
• Поисков использовано: `{user_searches[user_id]}/{SEARCH_LIMIT}`
• Осталось: `{SEARCH_LIMIT - user_searches[user_id]}`

⚡ **Команды:**
`/search` - поиск каналов
`/premium` - премиум доступ
`/help` - помощь

💎 **Система GenesisW v3.0**
            """)
        
        @bot.on(events.NewMessage(pattern='/search'))
        async def search_cmd(event):
            user_id = event.sender_id
            
            if user_id not in admin_users:
                if user_searches[user_id] >= SEARCH_LIMIT:
                    await event.respond(f"""
❌ **ЛИМИТ ИСЧЕРПАН**

Вы использовали {SEARCH_LIMIT} бесплатных поисков.

💰 **ПРЕМИУМ ДОСТУП:**
• Безлимитный поиск
• Приоритетная обработка
• Расширенные фильтры

💳 **Оплата USDT TRC20:**
`{CRYPTO_WALLET}`

📨 Отправьте `/premium` для выбора тарифа
                    """)
                    return
            
            user_mode[user_id] = 'awaiting_query'
            await event.respond("🔍 **Введите ключевое слово для поиска:**")
        
        @bot.on(events.NewMessage(pattern='/premium'))
        async def premium_cmd(event):
            await event.respond(f"""
💰 **ПРЕМИУМ ДОСТУП GENESISW**

**ТАРИФЫ (USDT TRC20):**
• **BASIC** - 10 USDT (30 дней)
• **ADVANCED** - 25 USDT (90 дней)  
• **PRO** - 50 USDT (180 дней)
• **ULTIMATE** - 100 USDT (пожизненно)

💳 **Кошелек для оплаты:**
`{CRYPTO_WALLET}`

📋 **После оплаты:**
1. Сохраните хэш транзакции
2. Отправьте хэш боту
3. Получите премиум доступ
            """)
        
        @bot.on(events.NewMessage(pattern='/admin'))
        async def admin_cmd(event):
            user_id = event.sender_id
            user_mode[user_id] = 'admin_auth'
            await event.respond("🔐 **Введите пароль доступа:**")
        
        @bot.on(events.NewMessage(pattern='/help'))
        async def help_cmd(event):
            await event.respond("""
🆘 **ПОМОЩЬ ПО ИСПОЛЬЗОВАНИЮ**

**Как использовать:**
1. Отправьте команду `/search`
2. Введите ключевое слово
3. Получите результаты поиска

**Примеры запросов:**
• психология
• криптовалюта
• фитнес
• программирование
• новости

**Лимиты:**
• Бесплатно: 20 поисков
• Премиум: безлимит

**Команды:**
`/start` - информация
`/search` - поиск каналов
`/premium` - премиум доступ
`/help` - помощь
            """)
        
        @bot.on(events.NewMessage())
        async def message_handler(event):
            user_id = event.sender_id
            text = event.text.strip() if event.text else ""
            
            if not text or text.startswith('/'):
                return
            
            # Аутентификация админа
            if user_id in user_mode and user_mode[user_id] == 'admin_auth':
                if text == ADMIN_PASSWORD:
                    admin_users.add(user_id)
                    user_searches[user_id] = 0
                    del user_mode[user_id]
                    await event.respond("✅ **АДМИН ДОСТУП АКТИВИРОВАН**")
                else:
                    await event.respond("❌ Неверный пароль")
                    del user_mode[user_id]
                return
            
            # Обработка поискового запроса
            if user_id in user_mode and user_mode[user_id] == 'awaiting_query':
                query = text.lower().strip()
                
                if len(query) < 2:
                    await event.respond("⚠️ Введите минимум 2 символа")
                    del user_mode[user_id]
                    return
                
                # Обновляем счетчик
                if user_id not in admin_users:
                    user_searches[user_id] += 1
                
                del user_mode[user_id]
                
                await event.respond(f"🔍 **Поиск:** `{query}`\n⏳ Обработка...")
                
                # Выполняем поиск
                results = await search_channels(query)
                
                if results:
                    total = len(results)
                    verified = sum(1 for r in results if r['verified'])
                    
                    response = f"""
✅ **ПОИСК ЗАВЕРШЕН**

**Запрос:** `{query}`
**Найдено каналов:** {total}
**Верифицированных:** {verified}

📋 **Результаты:**
"""
                    for i, item in enumerate(results[:5], 1):
                        marks = " ✅" if item['verified'] else ""
                        username = f"`@{item['username']}`" if item['username'] else "🔒 Приватный"
                        response += f"\n{i}. **{item['name']}**{marks}"
                        response += f"\n   👥 {item['members']:,} | {username}\n"
                    
                    if total > 5:
                        response += f"\n📈 *... и еще {total-5} каналов*"
                    
                    # Статистика пользователя
                    if user_id not in admin_users:
                        used = user_searches[user_id]
                        left = SEARCH_LIMIT - used
                        response += f"\n\n📊 **Ваш лимит:** {used}/{SEARCH_LIMIT}"
                        
                        if left <= 5:
                            response += f"\n⚠️ *Лимит почти исчерпан!*"
                    
                    response += f"\n\n💎 **Премиум доступ:** /premium"
                    
                    await event.respond(response)
                else:
                    await event.respond(f"""
❌ **РЕЗУЛЬТАТЫ ПОИСКА**

По запросу `{query}` ничего не найдено.

💡 **Попробуйте:**
• Более общие слова
• Английские термины
• Популярные темы

📊 **Поисков использовано:** {user_searches[user_id]}/{SEARCH_LIMIT}
                    """)
                return
        
        print("\n" + "="*50)
        print("🚀 GENESISW SEARCH SYSTEM ACTIVATED")
        print("="*50)
        print("🔍 Professional Telegram Channel Search")
        print("💰 Premium: USDT TRC20 payments")
        print("👑 Admin access: /admin")
        print("="*50)
        
        await bot.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ System error: {e}")

if __name__ == "__main__":
    asyncio.run(main())