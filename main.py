#!/usr/bin/env python3
"""
GenesisW Bot - приватная версия
"""

import os
import asyncio
import logging
import time
from datetime import datetime
from telethon import TelegramClient, events, functions
from collections import defaultdict

# ========== ДАННЫЕ (скрыты) ==========
API_ID = 22446695
API_HASH = "64587d7e1431a0d7e1959387faa4958a"
PHONE = "+996706161234"  # Только в коде, не показывать!
BOT_TOKEN = "8576112278:AAE35GWqoHpsQ9bdB069f__LDShXkNeHXro"

OWNER = "Gen Kai"
BOT_USER = "genesisw_bot"
WALLET = "TKMBNpspKG6uQZi8J9siyChhX6BrZJnJr7"
ADMIN_PASS = "Su54us"
# =====================================

print("🦾 GenesisW Bot запускается...")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LIMIT = 20
user_counts = defaultdict(int)
admins = set()
last_cmd = {}

# Поисковый клиент
search_client = None

async def init_search():
    """Инициализация поиска"""
    global search_client
    
    try:
        if os.path.exists('user_session.session'):
            search_client = TelegramClient('user_session', API_ID, API_HASH)
            await search_client.start()
            logger.info("✅ Поиск инициализирован")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Поиск: {e}")
        return False

async def search_channels(query):
    """Поиск каналов"""
    if not search_client:
        return None
    
    try:
        result = await search_client(functions.contacts.SearchRequest(
            q=query,
            limit=12
        ))
        
        channels = []
        for chat in result.chats:
            if hasattr(chat, 'title'):
                channels.append({
                    'name': chat.title[:35],
                    'username': getattr(chat, 'username', None),
                    'members': getattr(chat, 'participants_count', 0),
                    'verified': getattr(chat, 'verified', False)
                })
        
        channels.sort(key=lambda x: x['members'], reverse=True)
        return channels
    except Exception as e:
        logger.error(f"Поиск: {e}")
        return None

async def send(event, text):
    """Отправка сообщения"""
    try:
        await event.respond(text)
        return True
    except:
        return False

async def main():
    try:
        # Запуск бота
        bot = TelegramClient('bot_main', API_ID, API_HASH)
        await bot.start(bot_token=BOT_TOKEN)
        bot_info = await bot.get_me()
        print(f"✅ Бот: @{bot_info.username}")
        
        # Инициализация поиска
        search_active = await init_search()
        
        user_state = {}
        
        @bot.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            user_id = event.sender_id
            if user_id not in user_counts:
                user_counts[user_id] = 0
            
            search_status = "✅ СИСТЕМА АКТИВНА" if search_active else "⚠️ ОБНОВЛЕНИЕ"
            
            await send(event, f"""
{search_status}

🎯 **GENESISW SEARCH SYSTEM**

🔐 **Приватный режим работы**
👑 **Владелец:** {OWNER}
🤖 **Бот:** @{BOT_USER}

📊 **Ваш статус:**
• Поисков: {user_counts[user_id]}/{LIMIT}
• Осталось: {LIMIT - user_counts[user_id]}
• Уровень: {'👑 АДМИН' if user_id in admins else '👤 ПОЛЬЗОВАТЕЛЬ'}

⚡ **ДОСТУПНЫЕ КОМАНДЫ:**
`/search` - поиск информации
`/premium` - премиум доступ
`/admin` - система управления
`/help` - инструкции

💎 **Система работает в защищенном режиме**
            """)
        
        @bot.on(events.NewMessage(pattern='/search'))
        async def search_handler(event):
            user_id = event.sender_id
            
            if not search_active:
                await send(event, "🔄 **СИСТЕМА НА ОБСЛУЖИВАНИИ**\n\nПопробуйте позже или используйте `/premium` для приоритета.")
                return
            
            if user_id not in admins and user_counts[user_id] >= LIMIT:
                await send(event, f"""
❌ **ЛИМИТ ДОСТУПА ИСЧЕРПАН**

📊 **Использовано:** {user_counts[user_id]}/{LIMIT}

💰 **ТРЕБУЕТСЯ ПРЕМИУМ ДОСТУП:**
• Безлимитный поиск
• Приоритетная обработка
• Расширенные функции

💳 **ОПЛАТА USDT TRC20:**
`{WALLET}`

📨 **После оплаты отправьте хэш транзакции**
                """)
                return
            
            user_state[user_id] = 'awaiting_query'
            await send(event, "🔍 **ВВЕДИТЕ КЛЮЧЕВОЕ СЛОВО ДЛЯ ПОИСКА:**")
        
        @bot.on(events.NewMessage(pattern='/admin'))
        async def admin_handler(event):
            user_id = event.sender_id
            user_state[user_id] = 'awaiting_auth'
            await send(event, "**🔒 СИСТЕМА ДОСТУПА**\n\nДля входа в панель управления введите код доступа:")
        
        @bot.on(events.NewMessage(pattern='/premium'))
        async def premium_handler(event):
            await send(event, f"""
💰 **ПРЕМИУМ ДОСТУП GENESISW**

**ТАРИФНЫЕ ПЛАНЫ:**

**🥉 BASIC** - 10 USDT (30 дней)
• Безлимитный поиск
• Базовая поддержка

**🥈 ADVANCED** - 25 USDT (90 дней)
• Расширенные фильтры
• Приоритетная очередь

**🥇 PRO** - 50 USDT (180 дней)
• Максимальная скорость
• Экспорт результатов

**👑 ULTIMATE** - 100 USDT (ПОЖИЗНЕННО)
• Полный доступ ко всем функциям
• Персональная поддержка

💳 **КОШЕЛЕК ДЛЯ ОПЛАТЫ:**
`{WALLET}`

📨 **После оплаты отправьте хэш транзакции для активации**
            """)
        
        @bot.on(events.NewMessage(pattern='/help'))
        async def help_handler(event):
            await send(event, f"""
🆘 **СПРАВОЧНАЯ ИНФОРМАЦИЯ**

**📋 ОСНОВНЫЕ КОМАНДЫ:**
• `/search` - поиск информации
• `/premium` - премиум доступ
• `/admin` - система управления
• `/help` - эта справка

**🔍 КАК ПОЛЬЗОВАТЬСЯ:**
1. Отправьте команду `/search`
2. Введите ключевое слово
3. Получите результаты

**🎯 ПРИМЕРЫ ЗАПРОСОВ:**
• Психология
• Криптовалюты
• Фитнес
• Новости
• Программирование

**📊 СИСТЕМНЫЕ ЛИМИТЫ:**
• Бесплатно: {LIMIT} поисков
• Премиум: безлимитный доступ

👤 **Владелец системы:** {OWNER}
🤖 **Технический бот:** @{BOT_USER}
            """)
        
        @bot.on(events.NewMessage(pattern='/stats'))
        async def stats_handler(event):
            user_id = event.sender_id
            if user_id in admins:
                total_users = len(user_counts)
                total_searches = sum(user_counts.values())
                
                await send(event, f"""
📊 **СИСТЕМНАЯ СТАТИСТИКА**

👥 **Пользователей:** {total_users}
🔍 **Поисков всего:** {total_searches}
👑 **Администраторов:** {len(admins)}
⚡ **Поиск активен:** {'✅' if search_active else '❌'}
🎫 **Базовый лимит:** {LIMIT}
⏰ **Время:** {datetime.now().strftime('%H:%M:%S')}
                """)
        
        @bot.on(events.NewMessage())
        async def message_handler(event):
            user_id = event.sender_id
            text = event.text.strip() if event.text else ""
            
            if not text or text.startswith('/'):
                return
            
            # Аутентификация админа
            if user_id in user_state and user_state[user_id] == 'awaiting_auth':
                if text == ADMIN_PASS:
                    admins.add(user_id)
                    user_counts[user_id] = 0
                    del user_state[user_id]
                    
                    await send(event, f"""
✅ **ДОСТУП ПРЕДОСТАВЛЕН**

👑 **Статус:** АДМИНИСТРАТОР СИСТЕМЫ
⚡ **Уровень доступа:** ПОЛНЫЙ
🔍 **Лимит поисков:** БЕЗЛИМИТ

**📋 ДОСТУПНЫЕ КОМАНДЫ:**
• `/stats` - системная статистика
• `/help` - справочная информация

🔐 **Код доступа:** `{ADMIN_PASS}`
                    """)
                else:
                    await send(event, "❌ **НЕВЕРНЫЙ КОД ДОСТУПА**\n\nПопытка несанкционированного доступа зафиксирована.")
                    del user_state[user_id]
                return
            
            # Обработка поискового запроса
            if user_id in user_state and user_state[user_id] == 'awaiting_query':
                query = text.lower().strip()
                
                if len(query) < 2:
                    await send(event, "⚠️ **ТРЕБУЕТСЯ МИНИМУМ 2 СИМВОЛА**")
                    del user_state[user_id]
                    return
                
                # Обновление счетчика
                if user_id not in admins:
                    user_counts[user_id] += 1
                
                del user_state[user_id]
                
                remaining = LIMIT - user_counts[user_id]
                if user_id in admins:
                    remaining = "∞"
                
                await send(event, f"🔍 **ВЫПОЛНЯЕТСЯ ПОИСК:** `{query}`")
                
                # Поиск
                channels = await search_channels(query)
                
                if channels is None:
                    await send(event, f"""
⚠️ **СИСТЕМНАЯ ОШИБКА**

По запросу `{query}` произошла ошибка обработки.

📊 **Ваш статус:**
• Поисков: {user_counts[user_id]}/{LIMIT}
• Осталось: {remaining}
• Уровень: {'👑 АДМИН' if user_id in admins else '👤 ОБЫЧНЫЙ'}
                    """)
                elif channels:
                    total = len(channels)
                    verified = sum(1 for c in channels if c['verified'])
                    
                    response = f"""
✅ **ПОИСК ВЫПОЛНЕН**

**Запрос:** `{query}`
**Найдено:** {total} источников
**Проверенных:** {verified}

📋 **РЕЗУЛЬТАТЫ ПОИСКА:**
"""
                    for i, ch in enumerate(channels[:5], 1):
                        username = f"@{ch['username']}" if ch['username'] else "🔒 Приватный"
                        verified_mark = " ✅" if ch['verified'] else ""
                        
                        response += f"\n**{i}. {ch['name']}**{verified_mark}"
                        response += f"\n   👥 {ch['members']:,} | {username}\n"
                    
                    if total > 5:
                        response += f"\n📈 **... и еще {total-5} источников**"
                    
                    # Информация о лимитах
                    if user_id not in admins:
                        used = user_counts[user_id]
                        response += f"\n\n📊 **ВАШИ ЛИМИТЫ:**"
                        response += f"\n• Использовано: {used}/{LIMIT}"
                        response += f"\n• Осталось: {remaining}"
                        
                        if used >= LIMIT:
                            response += f"\n\n❌ **ЛИМИТ ИСЧЕРПАН!**\nИспользуйте `/premium` для продолжения."
                        elif used >= LIMIT * 0.8:
                            response += f"\n\n⚠️ **ЛИМИТ ПОЧТИ ИСЧЕРПАН!**\nРекомендуем `/premium`"
                    
                    response += f"\n\n💎 **ПРЕМИУМ ДОСТУП:** `/premium`"
                    
                    await send(event, response)
                else:
                    await send(event, f"""
❌ **РЕЗУЛЬТАТЫ НЕ НАЙДЕНЫ**

По запросу `{query}` не найдено соответствующих источников.

💡 **РЕКОМЕНДАЦИИ:**
• Используйте другие ключевые слова
• Проверьте правильность запроса
• Попробуйте более общие запросы

📊 **Поисков использовано:** {user_counts[user_id]}/{LIMIT}
                    """)
                return
        
        print("\n" + "="*50)
        print("🦾 GENESISW BOT АКТИВИРОВАН")
        print("="*50)
        print(f"👑 Владелец: {OWNER}")
        print(f"🤖 Бот: @{BOT_USER}")
        print(f"🔍 Поиск: {'✅' if search_active else '❌'}")
        print(f"🔐 Админ код: {ADMIN_PASS}")
        print("="*50)
        print("\n🚀 ОТПРАВЬТЕ /start ДЛЯ НАЧАЛА")
        
        await bot.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")

if __name__ == "__main__":
    asyncio.run(main())