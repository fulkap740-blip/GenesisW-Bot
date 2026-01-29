#!/usr/bin/env python3
"""
GenesisW Bot - IMBA WORKING VERSION
РАБОЧИЙ ПОИСК • НЕТ ДУБЛИРОВАНИЯ • ВСЁ ВКЛЮЧЕНО
"""

import os
import asyncio
import time
from telethon import TelegramClient, events, functions, types

# ========== КОНФИГ ==========
API_ID = int(os.environ.get("API_ID", "22446695"))
API_HASH = os.environ.get("API_HASH", "64587d7e1431a0d7e1959387faa4958a")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8576112278:AAE35GWqoHpsQ9bdB069f__LDShXkNeHXro")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER", "+996706161234")
ADMIN_PASS = "Su54us"
CRYPTO_WALLET = "TKMBNpspKG6uQZi8J9siyChhX6BrZJnJr7"
SEARCH_LIMIT = 20
# ============================

print("\n" + "="*70)
print("🚀 GENESISW BOT - IMBA VERSION")
print("="*70)

# ========== ФИКС ДУБЛИРОВАНИЯ ==========
last_actions = {}
user_data = {}
admin_users = set()

def block_duplicate(user_id, action):
    """Блокирует дублирование"""
    key = f"{user_id}_{action}"
    now = time.time()
    
    if key in last_actions:
        if now - last_actions[key] < 2:  # 2 секунды задержки
            return True
    
    last_actions[key] = now
    return False

# ========== ТЕЛЕГРАМ КЛИЕНТ ==========
client = None

async def init_client():
    """Инициализация клиента"""
    global client
    
    # Проверяем файл сессии
    session_file = 'genesis_session.session'
    if not os.path.exists(session_file):
        print(f"❌ ФАЙЛ СЕССИИ НЕ НАЙДЕН: {session_file}")
        print("Создай: python -c \"from telethon import TelegramClient; import asyncio; async def f(): client=TelegramClient('genesis_session', {API_ID}, '{API_HASH}'); await client.start('{PHONE_NUMBER}'); print('✅ Сессия создана'); await client.disconnect(); asyncio.run(f())\"")
        return False
    
    try:
        client = TelegramClient(session_file, API_ID, API_HASH)
        await client.start(phone=PHONE_NUMBER)
        me = await client.get_me()
        print(f"✅ КЛИЕНТ ГОТОВ: @{me.username}")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

async def real_search(keyword):
    """РЕАЛЬНЫЙ ПОИСК КАНАЛОВ"""
    try:
        print(f"🔍 Ищу: '{keyword}'")
        
        # Telegram API поиск
        result = await client(functions.contacts.SearchRequest(
            q=keyword,
            limit=15
        ))
        
        channels = []
        for chat in result.chats:
            if hasattr(chat, 'title'):
                channels.append({
                    'title': chat.title[:40],
                    'username': getattr(chat, 'username', None),
                    'members': getattr(chat, 'participants_count', 0),
                    'id': chat.id
                })
        
        # Сортируем по количеству участников
        channels.sort(key=lambda x: x['members'], reverse=True)
        
        print(f"✅ Найдено: {len(channels)} каналов")
        return channels
        
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        return None

async def main():
    """Главная функция"""
    print("🎯 Запускаю бота...")
    
    # Инициализация клиента
    if not await init_client():
        print("❌ Не могу запустить")
        return
    
    print("✅ Всё готово к работе")
    
    # ========== КОМАНДЫ ==========
    
    @client.on(events.NewMessage(pattern='/start'))
    async def start_cmd(event):
        """Команда /start"""
        if event.is_group:
            return
        
        user_id = event.sender_id
        if block_duplicate(user_id, 'start'):
            return
        
        # Инициализация пользователя
        if user_id not in user_data:
            user_data[user_id] = {'searches': 0, 'state': None}
        
        text = f"""
🎯 GENESISW SEARCH BOT

🔍 Реальный поиск каналов в Telegram
📊 Поисков: {user_data[user_id]['searches']}/{SEARCH_LIMIT}

📋 КОМАНДЫ:
/search - найти каналы
/premium - безлимит
/admin - админка
/help - помощь

👑 Владелец: Gen Kai
💎 Бот: @genesisw_bot
"""
        await event.respond(text)
    
    @client.on(events.NewMessage(pattern='/search'))
    async def search_cmd(event):
        """Команда /search"""
        if event.is_group:
            return
        
        user_id = event.sender_id
        if block_duplicate(user_id, 'search'):
            return
        
        # Инициализация если нет
        if user_id not in user_data:
            user_data[user_id] = {'searches': 0, 'state': None}
        
        # Проверка лимита
        if user_id not in admin_users and user_data[user_id]['searches'] >= SEARCH_LIMIT:
            await event.respond(f"❌ Лимит! /premium")
            return
        
        user_data[user_id]['state'] = 'searching'
        await event.respond("🔍 Введите слово для поиска:")
    
    @client.on(events.NewMessage(pattern='/admin'))
    async def admin_cmd(event):
        """Команда /admin"""
        if event.is_group:
            return
        
        user_id = event.sender_id
        if block_duplicate(user_id, 'admin'):
            return
        
        if user_id not in user_data:
            user_data[user_id] = {'searches': 0, 'state': None}
        
        user_data[user_id]['state'] = 'admin_pass'
        await event.respond("Пиздуй нахуй 😎\nПароль админа:")
    
    @client.on(events.NewMessage(pattern='/premium'))
    async def premium_cmd(event):
        """Команда /premium"""
        if event.is_group:
            return
        
        user_id = event.sender_id
        if block_duplicate(user_id, 'premium'):
            return
        
        text = f"""
💰 ПРЕМИУМ ДОСТУП

💎 Тарифы (USDT):
🥉 BASIC - 10 USDT
🥈 ADVANCED - 25 USDT
🥇 PRO - 50 USDT
👑 ULTIMATE - 100 USDT

💳 Кошелёк:
{CRYPTO_WALLET}

📨 После оплаты отправьте хэш транзакции
"""
        await event.respond(text)
    
    @client.on(events.NewMessage(pattern='/help'))
    async def help_cmd(event):
        """Команда /help"""
        if event.is_group:
            return
        
        user_id = event.sender_id
        if block_duplicate(user_id, 'help'):
            return
        
        text = f"""
🆘 ПОМОЩЬ

📋 Команды:
/start - информация
/search - поиск
/premium - безлимит
/admin - админка
/help - справка

📊 Лимиты:
Бесплатно: {SEARCH_LIMIT} поисков
Премиум: безлимит

@genesisw_bot
"""
        await event.respond(text)
    
    @client.on(events.NewMessage(pattern='/test'))
    async def test_cmd(event):
        """Тестовая команда /test"""
        if event.is_group:
            return
        
        user_id = event.sender_id
        if block_duplicate(user_id, 'test'):
            return
        
        await event.respond("🔧 Тестирую поиск...")
        channels = await real_search("новости")
        
        if channels:
            await event.respond(f"✅ Тест пройден! Найдено: {len(channels)} каналов")
        else:
            await event.respond("❌ Тест не пройден")
    
    # ========== ОБРАБОТКА ТЕКСТА ==========
    
    @client.on(events.NewMessage)
    async def message_handler(event):
        """Обработчик всех сообщений"""
        if event.is_group:
            return
        
        user_id = event.sender_id
        text = event.text.strip() if event.text else ""
        
        if not text or text.startswith('/'):
            return
        
        # Блокировка дублирования текста
        if block_duplicate(user_id, f"text_{text[:10]}"):
            return
        
        # Проверка состояния пользователя
        if user_id not in user_data:
            return
        
        state = user_data[user_id].get('state')
        
        # Обработка пароля админа
        if state == 'admin_pass':
            if text == ADMIN_PASS:
                admin_users.add(user_id)
                user_data[user_id]['searches'] = 0
                await event.respond("✅ Админ доступ активирован!")
            else:
                await event.respond("❌ Неверный пароль!")
            user_data[user_id]['state'] = None
            return
        
        # Обработка поискового запроса
        if state == 'searching':
            keyword = text.lower().strip()
            
            if len(keyword) < 2:
                await event.respond("⚠️ Минимум 2 символа")
                user_data[user_id]['state'] = None
                return
            
            await event.respond(f"🔍 Ищу: '{keyword}'...")
            
            # ВЫПОЛНЯЕМ РЕАЛЬНЫЙ ПОИСК
            channels = await real_search(keyword)
            
            if channels is None:
                await event.respond("⚠️ Ошибка поиска")
            elif channels:
                # Увеличиваем счётчик
                if user_id not in admin_users:
                    user_data[user_id]['searches'] += 1
                
                # Формируем результат
                result = f"✅ Найдено {len(channels)} каналов:\n\n"
                for i, ch in enumerate(channels[:5], 1):
                    username = f"@{ch['username']}" if ch['username'] else "без @"
                    members = f"{ch['members']:,}" if ch['members'] > 0 else "?"
                    result += f"{i}. {ch['title']}\n"
                    result += f"   👥 {members} | {username}\n\n"
                
                if len(channels) > 5:
                    result += f"... и ещё {len(channels)-5} каналов"
                
                await event.respond(result)
            else:
                await event.respond(f"❌ По '{keyword}' ничего не найдено")
            
            user_data[user_id]['state'] = None
            return
    
    # ========== ЗАПУСК ==========
    
    print("\n" + "="*70)
    print("🤖 БОТ ЗАПУЩЕН И ГОТОВ!")
    print("✅ Дублирование: ЗАБЛОКИРОВАНО")
    print("✅ Поиск: АКТИВИРОВАН")
    print("📞 Отправь /start в Telegram")
    print("="*70)
    
    # Бесконечный цикл
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Остановлен")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")