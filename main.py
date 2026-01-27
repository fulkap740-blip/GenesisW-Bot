#!/usr/bin/env python3
"""
GenesisW Bot - Complete
Phone: +996706161234
Bot: 8576112278:AAE35GWqoHpsQ9bdB069f__LDShXkNeHXro
API: 22446695 / 64587d7e1431a0d7e1959387faa4958a
"""

import os
import asyncio
import logging
import time
from datetime import datetime
from telethon import TelegramClient, events, functions
from collections import defaultdict

# ========== ВСЕ ДАННЫЕ ==========
API_ID = 22446695
API_HASH = "64587d7e1431a0d7e1959387faa4958a"
PHONE_NUMBER = "+996706161234"  # Твой номер
BOT_TOKEN = "8576112278:AAE35GWqoHpsQ9bdB069f__LDShXkNeHXro"

OWNER_NAME = "Gen Kai"
BOT_USERNAME = "genesisw_bot"
CRYPTO_WALLET = "TKMBNpspKG6uQZi8J9siyChhX6BrZJnJr7"
ADMIN_PASSWORD = "Su54us"
# ================================

print(f"""
╔══════════════════════════════════════╗
║        🦾 GENESISW BOT v3.0         ║
║        Phone: {PHONE_NUMBER}      ║
║        Bot: {BOT_TOKEN[:15]}...     ║
║        Owner: {OWNER_NAME}          ║
╚══════════════════════════════════════╝
""")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Лимиты
SEARCH_LIMIT = 20
user_searches = defaultdict(int)
admin_users = set()

# Защита от спама
last_action = {}
ACTION_DELAY = 3

# Клиент для поиска
search_client = None
bot_client = None

async def init_search():
    """Инициализация поискового клиента"""
    global search_client
    
    try:
        search_client = TelegramClient('search_session', API_ID, API_HASH)
        await search_client.start(phone=PHONE_NUMBER)
        me = await search_client.get_me()
        logger.info(f"✅ Search client ready: @{me.username}")
        return True
    except Exception as e:
        logger.error(f"❌ Search init failed: {e}")
        return False

async def find_channels(keyword, limit=15):
    """Поиск каналов"""
    if not search_client:
        return None
    
    try:
        result = await search_client(functions.contacts.SearchRequest(
            q=keyword,
            limit=limit
        ))
        
        channels = []
        for chat in result.chats:
            if hasattr(chat, 'title'):
                channels.append({
                    'title': chat.title,
                    'username': getattr(chat, 'username', None),
                    'members': getattr(chat, 'participants_count', 0),
                    'verified': getattr(chat, 'verified', False),
                    'scam': getattr(chat, 'scam', False)
                })
        
        channels.sort(key=lambda x: x['members'], reverse=True)
        return channels[:limit]
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return None

async def send_safe(event, text):
    """Безопасная отправка"""
    user_id = event.sender_id
    now = time.time()
    
    if user_id in last_action:
        if now - last_action[user_id] < ACTION_DELAY:
            return False
    
    last_action[user_id] = now
    
    try:
        await event.respond(text)
        return True
    except:
        return False

async def main():
    try:
        # Инициализация бота
        bot_client = TelegramClient('bot_session', API_ID, API_HASH)
        await bot_client.start(bot_token=BOT_TOKEN)
        bot_me = await bot_client.get_me()
        print(f"✅ Bot started: @{bot_me.username}")
        
        # Инициализация поиска
        search_ready = await init_search()
        
        # Состояния
        user_state = {}
        
        @bot_client.on(events.NewMessage(pattern='/start'))
        async def start_cmd(event):
            user_id = event.sender_id
            if user_id not in user_searches:
                user_searches[user_id] = 0
            
            search_status = "✅ РЕАЛЬНЫЙ ПОИСК АКТИВЕН" if search_ready else "⚠️ ПОИСК НЕДОСТУПЕН"
            
            await send_safe(event, f"""
{search_status}

🎯 GenesisW Search System
📞 Аккаунт: {PHONE_NUMBER}
👑 Владелец: {OWNER_NAME}

🔍 БЕСПЛАТНЫЙ ПОИСК:
• {SEARCH_LIMIT} запросов
• Реальные результаты
• Топ каналы

📊 Ваш статус:
Поисков использовано: {user_searches[user_id]}/{SEARCH_LIMIT}
Осталось: {SEARCH_LIMIT - user_searches[user_id]}

📋 КОМАНДЫ:
/search - найти каналы
/premium - безлимит
/admin - админка
/help - помощь

💎 @{BOT_USERNAME}
            """)
        
        @bot_client.on(events.NewMessage(pattern='/search'))
        async def search_cmd(event):
            user_id = event.sender_id
            
            if not search_ready:
                await send_safe(event, "⚠️ Поиск временно недоступен")
                return
            
            if user_id not in admin_users and user_searches[user_id] >= SEARCH_LIMIT:
                await send_safe(event, f"""
❌ ЛИМИТ ЗАВЕРШЕН

Использовано: {user_searches[user_id]}/{SEARCH_LIMIT}

💰 ПРЕМИУМ ДОСТУП:
• Безлимитный поиск
• Приоритетная обработка
• Расширенные фильтры

💳 USDT TRC20:
{CRYPTO_WALLET}

Команда: /premium
                """)
                return
            
            user_state[user_id] = 'awaiting_keyword'
            await send_safe(event, "🔍 ВВЕДИТЕ КЛЮЧЕВОЕ СЛОВО ДЛЯ ПОИСКА:")
        
        @bot_client.on(events.NewMessage(pattern='/admin'))
        async def admin_cmd(event):
            user_id = event.sender_id
            user_state[user_id] = 'awaiting_admin_pass'
            await send_safe(event, "Пиздуй нахуй 😎\n\n🔐 ВВЕДИ ПАРОЛЬ АДМИНА:")
        
        @bot_client.on(events.NewMessage(pattern='/premium'))
        async def premium_cmd(event):
            await send_safe(event, f"""
💰 ПРЕМИУМ СИСТЕМА GENESISW

ТАРИФЫ (USDT TRC20):
🥉 BASIC - 10 USDT (30 дней)
• Безлимитный поиск
• Базовые фильтры

🥈 ADVANCED - 25 USDT (90 дней)
• Verified фильтр
• Экспорт данных
• Приоритет

🥇 PRO - 50 USDT (180 дней)
• Excel экспорт
• Расширенный анализ
• Высокий приоритет

👑 ULTIMATE - 100 USDT (ПОЖИЗНЕННО)
• Все функции PRO
• API доступ
• Персональная поддержка

💳 КОШЕЛЕК ДЛЯ ОПЛАТЫ:
{CRYPTO_WALLET}

📨 После оплаты отправьте хэш транзакции
            """)
        
        @bot_client.on(events.NewMessage(pattern='/help'))
        async def help_cmd(event):
            await send_safe(event, f"""
🆘 СПРАВКА GENESISW

📋 ОСНОВНЫЕ КОМАНДЫ:
/search - поиск каналов
/start - информация о системе
/premium - премиум доступ
/admin - админ панель
/help - эта справка

🔍 КАК ИСКАТЬ:
1. Отправьте /search
2. Введите ключевое слово
3. Получите результаты

🎯 ПРИМЕРЫ ЗАПРОСОВ:
• психология
• криптовалюта
• фитнес
• новости
• программирование

📊 ЛИМИТЫ:
• Бесплатно: {SEARCH_LIMIT} поисков
• Премиум: безлимит

👤 {OWNER_NAME}
🤖 @{BOT_USERNAME}
            """)
        
        @bot_client.on(events.NewMessage(pattern='/stats'))
        async def stats_cmd(event):
            user_id = event.sender_id
            if user_id in admin_users:
                total_users = len(user_searches)
                total_searches = sum(user_searches.values())
                
                await send_safe(event, f"""
📊 СИСТЕМНАЯ СТАТИСТИКА:

👥 Пользователей: {total_users}
🔍 Всего поисков: {total_searches}
👑 Админов: {len(admin_users)}
🔧 Поиск: {'✅' if search_ready else '❌'}
📞 Номер: {PHONE_NUMBER}
⏰ Время: {datetime.now().strftime('%H:%M:%S')}
💎 Владелец: {OWNER_NAME}
                """)
        
        @bot_client.on(events.NewMessage())
        async def message_handler(event):
            user_id = event.sender_id
            text = event.text.strip() if event.text else ""
            
            if not text or text.startswith('/'):
                return
            
            # Обработка пароля админа
            if user_id in user_state and user_state[user_id] == 'awaiting_admin_pass':
                if text == ADMIN_PASSWORD:
                    admin_users.add(user_id)
                    user_searches[user_id] = 0
                    del user_state[user_id]
                    
                    await send_safe(event, f"""
✅ АДМИН ДОСТУП АКТИВИРОВАН!

Владелец: {OWNER_NAME}
Номер: {PHONE_NUMBER}
Статус: 👑 АДМИН
Лимит: ∞ (безлимит)

📋 Команды админа:
/stats - статистика
/help - справка

🔐 Пароль: {ADMIN_PASSWORD}
                    """)
                else:
                    await send_safe(event, "❌ НЕВЕРНЫЙ ПАРОЛЬ!")
                    del user_state[user_id]
                return
            
            # Обработка поискового запроса
            if user_id in user_state and user_state[user_id] == 'awaiting_keyword':
                keyword = text.lower().strip()
                
                if len(keyword) < 2:
                    await send_safe(event, "⚠️ Минимум 2 символа")
                    del user_state[user_id]
                    return
                
                # Обновляем счетчик
                if user_id not in admin_users:
                    user_searches[user_id] += 1
                
                del user_state[user_id]
                
                searches_left = SEARCH_LIMIT - user_searches[user_id]
                if user_id in admin_users:
                    searches_left = "∞"
                
                await send_safe(event, f"🔍 ПОИСК: '{keyword}'\n⏳ Обработка...")
                
                # Выполняем реальный поиск
                channels = await find_channels(keyword, 12)
                
                if channels is None:
                    await send_safe(event, f"""
⚠️ ОШИБКА ПОИСКА

По запросу '{keyword}' возникла ошибка.

📊 Статистика:
• Использовано: {user_searches[user_id]}/{SEARCH_LIMIT}
• Осталось: {searches_left}
• Статус: {'Админ' if user_id in admin_users else 'Обычный'}
                    """)
                elif channels:
                    total = len(channels)
                    verified = sum(1 for c in channels if c['verified'])
                    
                    response = f"""
✅ ПОИСК ЗАВЕРШЕН

Запрос: {keyword}
Найдено: {total} каналов
Verified: {verified}

📋 РЕЗУЛЬТАТЫ:
"""
                    for i, ch in enumerate(channels[:5], 1):
                        name = ch['title'][:35]
                        username = f"@{ch['username']}" if ch['username'] else "нет @"
                        members = f"{ch['members']:,}" if ch['members'] > 0 else "?"
                        marks = ""
                        if ch['verified']:
                            marks += " ✅"
                        if ch['scam']:
                            marks += " ⚠️"
                        
                        response += f"\n{i}. {name}{marks}"
                        response += f"\n   👥 {members} | {username}\n"
                    
                    if total > 5:
                        response += f"\n📈 ... и еще {total-5} каналов"
                    
                    # Информация о лимитах
                    if user_id not in admin_users:
                        used = user_searches[user_id]
                        limit = SEARCH_LIMIT
                        response += f"\n\n📊 ВАШ ЛИМИТ: {used}/{limit}"
                        
                        if used >= limit:
                            response += f"\n❌ ЛИМИТ ИСЧЕРПАН! /premium"
                        elif used >= limit * 0.8:
                            response += f"\n⚠️ Лимит почти закончен! /premium"
                    
                    response += f"\n\n💎 Премиум: /premium"
                    response += f"\n👑 Админ: /admin"
                    
                    await send_safe(event, response)
                else:
                    await send_safe(event, f"""
❌ РЕЗУЛЬТАТЫ ПОИСКА

По запросу '{keyword}' ничего не найдено.

💡 Попробуйте:
• психология
• крипта
• фитнес
• новости
• спорт
• музыка

📊 Поисков: {user_searches[user_id]}/{SEARCH_LIMIT}
                    """)
                return
        
        print("\n" + "="*60)
        print("🚀 GENESISW BOT ЗАПУЩЕН УСПЕШНО!")
        print("="*60)
        print(f"📞 Телефон: {PHONE_NUMBER}")
        print(f"🤖 Бот: @{bot_me.username}")
        print(f"🔍 Поиск: {'✅ ГОТОВ' if search_ready else '❌ ОШИБКА'}")
        print(f"👑 Админ пароль: {ADMIN_PASSWORD}")
        print(f"💳 Кошелек: {CRYPTO_WALLET}")
        print("="*60)
        print("\n🎯 ОТПРАВЬТЕ /start В ТЕЛЕГРАМ ДЛЯ НАЧАЛА")
        
        await bot_client.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
