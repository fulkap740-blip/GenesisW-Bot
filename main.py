#!/usr/bin/env python3
"""
GenesisW Bot - FULL SEARCH WORKING
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

print("=" * 70)
print("🚀 GENESISW BOT - FULL SEARCH ACTIVATION")
print("=" * 70)

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG для деталей
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Хранилище
user_searches = defaultdict(int)
admin_users = set()
user_states = {}
last_action = {}
active_handlers = set()

# ЕДИНЫЙ КЛИЕНТ для всего
client = None

async def init_client():
    """Инициализация единого клиента для бота и поиска"""
    global client
    
    try:
        # Проверяем файл сессии
        if not os.path.exists('genesis_session.session'):
            print("❌ ФАЙЛ СЕССИИ НЕ НАЙДЕН!")
            print("Загрузи genesis_session.session в Railway")
            return False
        
        print("🔧 Инициализация единого клиента...")
        
        # Создаём клиент с сессией пользователя
        client = TelegramClient('genesis_session', API_ID, API_HASH)
        
        # Запускаем как пользователь (не как бот)
        await client.start(phone=PHONE_NUMBER)
        
        # Получаем информацию о себе
        me = await client.get_me()
        print(f"✅ КЛИЕНТ ГОТОВ: @{me.username} (ID: {me.id})")
        print(f"📱 Телефон: {me.phone}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return False

async def real_search(keyword):
    """РЕАЛЬНЫЙ ПОИСК КАНАЛОВ"""
    try:
        print(f"🔍 ВЫПОЛНЯЮ ПОИСК: '{keyword}'")
        
        # Используем метод поиска контактов
        result = await client(functions.contacts.SearchRequest(
            q=keyword,
            limit=20  # Больше результатов
        ))
        
        print(f"📊 Получено чатов: {len(result.chats)}")
        
        channels = []
        for chat in result.chats:
            if hasattr(chat, 'title'):
                # Получаем полную информацию о канале
                try:
                    full_chat = await client(functions.channels.GetFullChannelRequest(
                        channel=chat
                    )) if hasattr(chat, 'broadcast') else None
                    
                    channels.append({
                        'id': chat.id,
                        'title': chat.title,
                        'username': getattr(chat, 'username', None),
                        'members': getattr(chat, 'participants_count', 0),
                        'description': getattr(full_chat, 'about', '')[:100] if full_chat else '',
                        'verified': getattr(chat, 'verified', False),
                        'scam': getattr(chat, 'scam', False)
                    })
                except:
                    channels.append({
                        'id': chat.id,
                        'title': chat.title,
                        'username': getattr(chat, 'username', None),
                        'members': getattr(chat, 'participants_count', 0),
                        'description': '',
                        'verified': False,
                        'scam': False
                    })
        
        # Сортируем по количеству участников
        channels.sort(key=lambda x: x['members'], reverse=True)
        
        print(f"✅ НАЙДЕНО КАНАЛОВ: {len(channels)}")
        return channels
        
    except Exception as e:
        print(f"❌ ОШИБКА ПОИСКА: {e}")
        import traceback
        traceback.print_exc()
        return None

async def send_as_bot(event, text):
    """Отправка сообщения от имени бота"""
    try:
        # Создаём временного бота для отправки
        bot_client = TelegramClient('temp_bot', API_ID, API_HASH)
        await bot_client.start(bot_token=BOT_TOKEN)
        
        await bot_client.send_message(event.chat_id, text)
        await bot_client.disconnect()
        
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False

async def main():
    print("🎯 ЗАПУСК GENESISW BOT...")
    
    # Инициализируем клиент
    if not await init_client():
        print("❌ Невозможно запустить. Проверь сессию.")
        return
    
    print("✅ КЛИЕНТ УСПЕШНО ИНИЦИАЛИЗИРОВАН")
    
    # ========== ОБРАБОТЧИКИ КОМАНД ==========
    
    @client.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        
        if user_id not in user_searches:
            user_searches[user_id] = 0
        
        text = f"""
🎯 GENESISW SEARCH BOT
🔍 Реальный поиск каналов в Telegram

📊 Ваш статус:
Поисков: {user_searches[user_id]}/{SEARCH_LIMIT}
Осталось: {SEARCH_LIMIT - user_searches[user_id]}

📋 КОМАНДЫ:
/search - найти каналы
/premium - безлимитный доступ
/admin - админ панель
/help - помощь

👑 Владелец: Gen Kai
💎 Бот: @genesisw_bot
"""
        await event.respond(text)
    
    @client.on(events.NewMessage(pattern='/search'))
    async def search_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        
        if user_id not in admin_users and user_searches[user_id] >= SEARCH_LIMIT:
            await event.respond("❌ Лимит исчерпан! /premium")
            return
        
        user_states[user_id] = 'searching'
        await event.respond("🔍 Введите ключевое слово для поиска:")
    
    @client.on(events.NewMessage(pattern='/admin'))
    async def admin_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        user_states[user_id] = 'admin_auth'
        await event.respond("Пиздуй нахуй 😎\nПароль админа:")
    
    @client.on(events.NewMessage(pattern='/premium'))
    async def premium_handler(event):
        text = f"""
💰 ПРЕМИУМ ДОСТУП

💎 Тарифы (USDT TRC20):
🥉 BASIC - 10 USDT (30 дней)
• Безлимитный поиск

🥈 ADVANCED - 25 USDT (90 дней)
• Безлимит + фильтры

🥇 PRO - 50 USDT (180 дней)
• Все функции + экспорт

👑 ULTIMATE - 100 USDT (НАВСЕГДА)
• Всё включено + API

💳 Кошелёк для оплаты:
{CRYPTO_WALLET}

📨 После оплаты отправьте хэш транзакции
"""
        await event.respond(text)
    
    @client.on(events.NewMessage(pattern='/help'))
    async def help_handler(event):
        text = f"""
🆘 ПОМОЩЬ

🔍 КАК ИСКАТЬ:
1. Отправьте /search
2. Введите ключевое слово
3. Получите реальные результаты

📋 КОМАНДЫ:
/start - информация
/search - поиск каналов
/premium - премиум доступ
/admin - админ панель
/help - эта справка

📊 ЛИМИТЫ:
• Бесплатно: {SEARCH_LIMIT} поисков
• Премиум: безлимит

@genesisw_bot
"""
        await event.respond(text)
    
    @client.on(events.NewMessage(pattern='/test'))
    async def test_handler(event):
        """Тестовая команда для проверки поиска"""
        await event.respond("🔧 Тестирую поиск...")
        
        # Тестовый поиск
        channels = await real_search("новости")
        
        if channels:
            await event.respond(f"✅ Тест пройден! Найдено: {len(channels)} каналов")
        else:
            await event.respond("❌ Тест не пройден")
    
    # ========== ОБРАБОТКА СООБЩЕНИЙ ==========
    
    @client.on(events.NewMessage)
    async def message_handler(event):
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        text = event.text.strip() if event.text else ""
        
        if not text or text.startswith('/'):
            return
        
        # Админ пароль
        if user_states.get(user_id) == 'admin_auth':
            if text == ADMIN_PASS:
                admin_users.add(user_id)
                user_searches[user_id] = 0
                await event.respond("✅ АДМИН ДОСТУП АКТИВИРОВАН! Безлимитный поиск.")
            else:
                await event.respond("❌ Неверный пароль!")
            user_states.pop(user_id, None)
            return
        
        # Поисковый запрос
        if user_states.get(user_id) == 'searching':
            keyword = text.lower().strip()
            
            if len(keyword) < 2:
                await event.respond("⚠️ Минимум 2 символа")
                user_states.pop(user_id, None)
                return
            
            # Обновляем счётчик
            if user_id not in admin_users:
                user_searches[user_id] += 1
            
            user_states.pop(user_id, None)
            
            await event.respond(f"🔍 ИЩУ КАНАЛЫ ПО ЗАПРОСУ: '{keyword}'...")
            
            # ВЫПОЛНЯЕМ РЕАЛЬНЫЙ ПОИСК
            channels = await real_search(keyword)
            
            if channels is None:
                await event.respond("⚠️ Ошибка при выполнении поиска")
            elif channels:
                # Формируем результат
                result_text = f"""
✅ ПОИСК ЗАВЕРШЕН

Запрос: '{keyword}'
Найдено каналов: {len(channels)}

📋 ТОП-РЕЗУЛЬТАТЫ:
"""
                for i, ch in enumerate(channels[:5], 1):
                    name = ch['title'][:40]
                    username = f"@{ch['username']}" if ch['username'] else "без @"
                    members = f"{ch['members']:,}" if ch['members'] > 0 else "?"
                    
                    # Метки
                    marks = []
                    if ch['verified']:
                        marks.append("✅")
                    if ch['scam']:
                        marks.append("⚠️")
                    
                    marks_str = " " + "".join(marks) if marks else ""
                    
                    result_text += f"\n{i}. {name}{marks_str}"
                    result_text += f"\n   👥 {members} | {username}"
                    
                    if ch['description']:
                        result_text += f"\n   📝 {ch['description'][:50]}...\n"
                    else:
                        result_text += "\n"
                
                if len(channels) > 5:
                    result_text += f"\n📈 ... и ещё {len(channels)-5} каналов"
                
                # Информация о лимитах
                if user_id not in admin_users:
                    used = user_searches[user_id]
                    result_text += f"\n\n📊 ВАШ ЛИМИТ: {used}/{SEARCH_LIMIT}"
                    
                    if used >= SEARCH_LIMIT:
                        result_text += "\n❌ ЛИМИТ ИСЧЕРПАН! /premium"
                    elif used >= SEARCH_LIMIT * 0.8:
                        result_text += "\n⚠️ Лимит почти исчерпан! /premium"
                
                await event.respond(result_text)
            else:
                await event.respond(f"❌ По запросу '{keyword}' ничего не найдено.")
            return
    
    print("\n" + "=" * 70)
    print("🤖 БОТ УСПЕШНО ЗАПУЩЕН!")
    print("🔍 РЕАЛЬНЫЙ ПОИСК АКТИВИРОВАН")
    print("📞 Отправьте /start в Telegram")
    print("🔧 Тестовая команда: /test")
    print("=" * 70)
    
    # Запускаем
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"\n💀 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
