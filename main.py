#!/usr/bin/env python3
"""
GenesisW Bot - ULTIMATE WORKING VERSION
NO DUPLICATES | REAL SEARCH
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

print("\n" + "="*70)
print("🚀 GENESISW BOT - ULTIMATE VERSION")
print("="*70)

# Минимальное логирование
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# ========== ФИКС ДУБЛИРОВАНИЯ ==========
# Глобальный словарь для отслеживания последних команд
LAST_COMMANDS = {}
COMMAND_TIMEOUT = 3  # секунды

# Хранилище данных
user_data = {}
admin_users = set()

# Один клиент для всего
client = None

def check_duplicate(user_id: int, command: str) -> bool:
    """Проверяет дублирование команд"""
    key = f"{user_id}_{command}"
    current_time = time.time()
    
    if key in LAST_COMMANDS:
        if current_time - LAST_COMMANDS[key] < COMMAND_TIMEOUT:
            print(f"⚠️ Duplicate blocked: {key}")
            return True
    
    LAST_COMMANDS[key] = current_time
    return False

async def init_telegram():
    """Инициализация Telegram клиента"""
    global client
    
    try:
        # Проверяем сессию
        if not os.path.exists('genesis_session.session'):
            print("❌ NO SESSION FILE!")
            return False
        
        print("🔗 Подключаюсь к Telegram...")
        
        # Создаём клиент
        client = TelegramClient('genesis_session', API_ID, API_HASH)
        
        # Запускаем как пользователь
        await client.start(phone=PHONE_NUMBER)
        
        # Проверяем подключение
        me = await client.get_me()
        print(f"✅ Connected as: @{me.username}")
        print(f"📱 Phone: {me.phone}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def search_channels(keyword: str, limit: int = 15):
    """РЕАЛЬНЫЙ ПОИСК КАНАЛОВ"""
    try:
        print(f"🔍 REAL SEARCH: '{keyword}'")
        
        # Telegram API поиск
        result = await client(functions.contacts.SearchRequest(
            q=keyword,
            limit=limit
        ))
        
        if not hasattr(result, 'chats'):
            print("⚠️ No chats in result")
            return []
        
        channels = []
        for chat in result.chats:
            # Проверяем что это канал/группа
            if not hasattr(chat, 'title'):
                continue
            
            # Получаем информацию
            channels.append({
                'title': chat.title,
                'username': getattr(chat, 'username', None),
                'members': getattr(chat, 'participants_count', 0),
                'id': chat.id,
                'verified': getattr(chat, 'verified', False),
                'type': 'channel' if getattr(chat, 'broadcast', False) else 'group'
            })
        
        print(f"✅ Found {len(channels)} channels")
        return channels[:limit]  # Ограничиваем
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        return None

async def send_response(event, text: str):
    """Отправка ответа без дублирования"""
    try:
        # Простая отправка
        await event.respond(text)
        print(f"📤 Sent to {event.sender_id}")
        return True
    except Exception as e:
        print(f"❌ Send failed: {e}")
        return False

async def main():
    """Основная функция"""
    print("\n🎯 ИНИЦИАЛИЗАЦИЯ...")
    
    # Инициализируем клиент
    if not await init_telegram():
        print("❌ Не могу подключиться к Telegram")
        return
    
    print("✅ Telegram client ready")
    
    # ========== ОБРАБОТЧИКИ ==========
    
    @client.on(events.NewMessage(pattern='/start'))
    async def handle_start(event):
        """Обработчик /start"""
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        
        # Проверка дублирования
        if check_duplicate(user_id, 'start'):
            return
        
        # Инициализируем пользователя
        if user_id not in user_data:
            user_data[user_id] = {'searches': 0}
        
        text = f"""
🎯 GENESISW SEARCH BOT

🔍 Реальный поиск каналов в Telegram
📊 Поисков использовано: {user_data[user_id]['searches']}/{SEARCH_LIMIT}

📋 КОМАНДЫ:
/search - найти каналы
/premium - безлимит
/admin - админка
/help - помощь

👑 Владелец: Gen Kai
💎 Бот: @genesisw_bot
"""
        await send_response(event, text)
    
    @client.on(events.NewMessage(pattern='/search'))
    async def handle_search(event):
        """Обработчик /search"""
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        
        # Проверка дублирования
        if check_duplicate(user_id, 'search'):
            return
        
        # Инициализируем если нет
        if user_id not in user_data:
            user_data[user_id] = {'searches': 0}
        
        # Проверяем лимит
        if user_id not in admin_users and user_data[user_id]['searches'] >= SEARCH_LIMIT:
            await send_response(event, 
                f"❌ ЛИМИТ ИСЧЕРПАН!\n"
                f"Использовано: {user_data[user_id]['searches']}/{SEARCH_LIMIT}\n\n"
                f"💰 /premium - безлимитный доступ"
            )
            return
        
        # Устанавливаем состояние
        user_data[user_id]['state'] = 'awaiting_keyword'
        
        await send_response(event, "🔍 Введите ключевое слово для поиска:")
    
    @client.on(events.NewMessage(pattern='/admin'))
    async def handle_admin(event):
        """Обработчик /admin"""
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        
        # Проверка дублирования
        if check_duplicate(user_id, 'admin'):
            return
        
        # Устанавливаем состояние
        if user_id not in user_data:
            user_data[user_id] = {'searches': 0}
        
        user_data[user_id]['state'] = 'awaiting_password'
        
        await send_response(event, "Пиздуй нахуй 😎\n\n🔐 Введите пароль админа:")
    
    @client.on(events.NewMessage(pattern='/premium'))
    async def handle_premium(event):
        """Обработчик /premium"""
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        
        # Проверка дублирования
        if check_duplicate(user_id, 'premium'):
            return
        
        text = f"""
💰 ПРЕМИУМ ДОСТУП

💎 Тарифы (USDT TRC20):
🥉 BASIC - 10 USDT (30 дней)
🥈 ADVANCED - 25 USDT (90 дней)
🥇 PRO - 50 USDT (180 дней)
👑 ULTIMATE - 100 USDT (ПОЖИЗНЕННО)

💳 Кошелёк для оплаты:
{CRYPTO_WALLET}

📨 После оплаты отправьте хэш транзакции
"""
        await send_response(event, text)
    
    @client.on(events.NewMessage(pattern='/help'))
    async def handle_help(event):
        """Обработчик /help"""
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        
        # Проверка дублирования
        if check_duplicate(user_id, 'help'):
            return
        
        text = f"""
🆘 ПОМОЩЬ

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

@genesisw_bot
"""
        await send_response(event, text)
    
    @client.on(events.NewMessage(pattern='/test'))
    async def handle_test(event):
        """Тестовая команда"""
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        
        if check_duplicate(user_id, 'test'):
            return
        
        await send_response(event, "🔧 Тестирую поиск...")
        
        # Тестовый поиск
        channels = await search_channels("новости", 5)
        
        if channels:
            result = f"✅ ТЕСТ ПРОЙДЕН!\nНайдено: {len(channels)} каналов\n"
            for ch in channels[:3]:
                result += f"\n• {ch['title'][:30]}"
            await send_response(event, result)
        else:
            await send_response(event, "❌ ТЕСТ НЕ ПРОЙДЕН")
    
    # ========== ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ==========
    
    @client.on(events.NewMessage)
    async def handle_message(event):
        """Обработчик всех сообщений"""
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        text = event.text.strip() if event.text else ""
        
        # Пропускаем команды и пустые сообщения
        if not text or text.startswith('/'):
            return
        
        # Проверяем дублирование для текстовых сообщений
        msg_key = f"{user_id}_msg_{text[:10]}"
        if msg_key in LAST_COMMANDS:
            if time.time() - LAST_COMMANDS[msg_key] < 2:
                return
        
        LAST_COMMANDS[msg_key] = time.time()
        
        # Проверяем состояние пользователя
        if user_id not in user_data:
            return
        
        user_state = user_data[user_id].get('state')
        
        # Обработка пароля админа
        if user_state == 'awaiting_password':
            if text == ADMIN_PASS:
                admin_users.add(user_id)
                user_data[user_id]['searches'] = 0
                await send_response(event, "✅ АДМИН ДОСТУП АКТИВИРОВАН!")
            else:
                await send_response(event, "❌ НЕВЕРНЫЙ ПАРОЛЬ!")
            
            user_data[user_id]['state'] = None
            return
        
        # Обработка поискового запроса
        if user_state == 'awaiting_keyword':
            keyword = text.lower().strip()
            
            if len(keyword) < 2:
                await send_response(event, "⚠️ Минимум 2 символа")
                user_data[user_id]['state'] = None
                return
            
            await send_response(event, f"🔍 ИЩУ: '{keyword}'...")
            
            # ВЫПОЛНЯЕМ РЕАЛЬНЫЙ ПОИСК
            channels = await search_channels(keyword, 10)
            
            if channels is None:
                await send_response(event, "⚠️ Ошибка при поиске")
            elif channels:
                # Увеличиваем счётчик поисков
                if user_id not in admin_users:
                    user_data[user_id]['searches'] += 1
                
                # Формируем результат
                result_text = f"✅ НАЙДЕНО: {len(channels)} каналов\n\n"
                
                for i, ch in enumerate(channels[:5], 1):
                    name = ch['title'][:35]
                    username = f"@{ch['username']}" if ch['username'] else "без @"
                    members = f"{ch['members']:,}" if ch['members'] > 0 else "?"
                    
                    result_text += f"{i}. {name}\n"
                    result_text += f"   👥 {members} | {username}\n\n"
                
                if len(channels) > 5:
                    result_text += f"📊 ... и ещё {len(channels)-5} каналов"
                
                # Добавляем информацию о лимитах
                if user_id not in admin_users:
                    used = user_data[user_id]['searches']
                    result_text += f"\n\n📈 Ваш лимит: {used}/{SEARCH_LIMIT}"
                
                await send_response(event, result_text)
            else:
                await send_response(event, f"❌ По запросу '{keyword}' ничего не найдено")
            
            # Сбрасываем состояние
            user_data[user_id]['state'] = None
            return
    
    print("\n" + "="*70)
    print("🤖 БОТ УСПЕШНО ЗАПУЩЕН И ГОТОВ К РАБОТЕ!")
    print("✅ Дублирование сообщений: ЗАБЛОКИРОВАНО")
    print("✅ Реальный поиск: АКТИВИРОВАН")
    print("📞 Отправьте /start в Telegram")
    print("🔧 Тест: /test")
    print("="*70 + "\n")
    
    # Запускаем
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Остановлен пользователем")
    except Exception as e:
        print(f"\n💀 КРИТИЧЕСКАЯ ОШИБКА: {e}")