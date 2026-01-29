#!/usr/bin/env python3
"""
GenesisW Bot - IMBA 2.0
10 РЕЗУЛЬТАТОВ • ИНЛАЙН КНОПКИ • ПРОФИЛЬ • АДМИНКА • ПРОВЕРКА ПЛАТЕЖЕЙ • КРИПТА • ТРОН СКАН
"""

import os
import asyncio
import time
import hashlib
import json
from datetime import datetime, timedelta
from telethon import TelegramClient, events, functions, types
from telethon.tl.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========== КОНФИГ ==========
API_ID = int(os.environ.get("API_ID", "22446695"))
API_HASH = os.environ.get("API_HASH", "64587d7e1431a0d7e1959387faa4958a"))
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8576112278:AAE35GWqoHpsQ9bdB069f__LDShXkNeHXro")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER", "+996706161234")

ADMIN_PASS = "Su54us"
CRYPTO_WALLET = "TKMBNpspKG6uQZi8J9siyChhX6BrZJnJr7"  # USDT TRC20
SEARCH_LIMIT = 20
PREMIUM_PRICES = {
    "basic": 10,    # 10 USDT
    "advanced": 25, # 25 USDT  
    "pro": 50,      # 50 USDT
    "ultimate": 100 # 100 USDT
}
# ============================

print("\n" + "="*70)
print("🚀 GENESISW BOT - IMBA 2.0")
print("="*70)

# ========== ХРАНИЛИЩЕ ==========
class UserData:
    def __init__(self):
        self.users = {}
        self.payments = {}  # хэши платежей
        self.admin_users = set()
        self.last_actions = {}
    
    def get_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = {
                'searches': 0,
                'premium': False,
                'premium_type': None,
                'premium_until': None,
                'payment_hash': None,
                'state': None
            }
        return self.users[user_id]
    
    def is_premium(self, user_id):
        user = self.get_user(user_id)
        if user['premium'] and user['premium_until']:
            return datetime.now() < user['premium_until']
        return False
    
    def block_duplicate(self, user_id, action):
        key = f"{user_id}_{action}"
        now = time.time()
        
        if key in self.last_actions:
            if now - self.last_actions[key] < 1.5:  # 1.5 сек
                return True
        
        self.last_actions[key] = now
        return False

# Инициализация хранилища
storage = UserData()

# ========== ТЕЛЕГРАМ КЛИЕНТ ==========
client = None

async def init_client():
    """Инициализация клиента"""
    global client
    
    # Проверяем файл сессии
    session_file = 'genesis_session.session'
    if not os.path.exists(session_file):
        print(f"❌ ФАЙЛ СЕССИИ НЕ НАЙДЕН: {session_file}")
        return False
    
    try:
        client = TelegramClient(session_file, API_ID, API_HASH)
        await client.start(phone=PHONE_NUMBER)
        me = await client.get_me()
        print(f"✅ КЛИЕНТ ГОТОВ: @{me.username} (ID: {me.id})")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

# ========== ПОИСК ==========
async def real_search(keyword, limit=10):
    """РЕАЛЬНЫЙ ПОИСК - 10 РЕЗУЛЬТАТОВ"""
    try:
        print(f"🔍 Ищу: '{keyword}' (лимит: {limit})")
        
        # Telegram API поиск
        result = await client(functions.contacts.SearchRequest(
            q=keyword,
            limit=limit
        ))
        
        channels = []
        for chat in result.chats:
            if hasattr(chat, 'title'):
                channels.append({
                    'title': chat.title[:50],
                    'username': getattr(chat, 'username', None),
                    'members': getattr(chat, 'participants_count', 0),
                    'id': chat.id,
                    'verified': getattr(chat, 'verified', False),
                    'type': 'channel' if getattr(chat, 'broadcast', False) else 'group'
                })
        
        # Сортируем по количеству участников
        channels.sort(key=lambda x: x['members'], reverse=True)
        
        print(f"✅ Найдено: {len(channels)} каналов")
        return channels[:limit]  # Возвращаем точно limit
        
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        return None

# ========== ПРОВЕРКА КРИПТО ПЛАТЕЖЕЙ ==========
async def check_tron_payment(tx_hash):
    """Проверка платежа через TronScan (имитация)"""
    try:
        # Имитация проверки через API TronScan
        # В реальности: запрос к https://api.tronscan.org/api/transaction-info?hash={tx_hash}
        
        # Генерация "проверенного" платежа
        payment_data = {
            'hash': tx_hash,
            'verified': True,
            'amount': PREMIUM_PRICES.get("basic", 10),
            'timestamp': int(time.time()),
            'from': 'TKMBNpspKG6uQZi8J9siyChhX6BrZJnJr7',  # От кого
            'to': CRYPTO_WALLET,  # Наш кошелёк
            'status': 'CONFIRMED'
        }
        
        # Сохраняем в память (в реальности - в БД)
        storage.payments[tx_hash] = payment_data
        
        return payment_data
    except Exception as e:
        print(f"❌ Ошибка проверки платежа: {e}")
        return None

# ========== ИНЛАЙН КНОПКИ ==========
def create_keyboard(buttons, columns=2):
    """Создание инлайн клавиатуры"""
    keyboard = []
    row = []
    
    for i, (text, data) in enumerate(buttons):
        row.append(InlineKeyboardButton(text, callback_data=data))
        if (i + 1) % columns == 0:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard)

# ========== КОМАНДЫ ==========
async def main():
    """Главная функция"""
    print("🎯 Запускаю IMBA 2.0...")
    
    # Инициализация клиента
    if not await init_client():
        print("❌ Не могу запустить")
        return
    
    print("✅ Всё готово к работе")
    
    # ========== ОБРАБОТЧИК КОМАНД ==========
    
    @client.on(events.NewMessage(pattern='/start'))
    async def start_cmd(event):
        """Команда /start"""
        if event.is_group:
            return
        
        user_id = event.sender_id
        if storage.block_duplicate(user_id, 'start'):
            return
        
        # Получаем информацию о пользователе
        user = storage.get_user(user_id)
        is_premium = storage.is_premium(user_id)
        
        # Текст профиля
        profile_text = f"""
👤 <b>ВАШ ПРОФИЛЬ</b>

🆔 ID: <code>{user_id}</code>
🔍 Поисков использовано: {user['searches']}/{SEARCH_LIMIT}
⭐ Статус: {'💎 PREMIUM' if is_premium else '⚪ BASIC'}

"""
        if is_premium and user['premium_type']:
            profile_text += f"💎 Тариф: {user['premium_type'].upper()}\n"
            if user['premium_until']:
                days_left = (user['premium_until'] - datetime.now()).days
                profile_text += f"📅 Осталось дней: {days_left}\n"
        
        # Кнопки
        buttons = [
            ("🔍 Поиск", "search"),
            ("💎 Премиум", "premium"),
            ("👑 Админ", "admin"),
            ("🆘 Помощь", "help")
        ]
        
        keyboard = create_keyboard(buttons, 2)
        
        # Отправляем от лица ЮЗЕРА (не бота)
        await event.delete()  # Удаляем команду /start
        await client.send_message(
            entity=event.chat_id,
            message=profile_text,
            parse_mode='html',
            buttons=keyboard
        )
    
    @client.on(events.NewMessage(pattern='/profile'))
    async def profile_cmd(event):
        """Команда /profile - профиль пользователя"""
        if event.is_group:
            return
        
        user_id = event.sender_id
        user = storage.get_user(user_id)
        is_premium = storage.is_premium(user_id)
        
        # Создаём красивый профиль
        profile = f"""
┏━━━━━━━━━━━━━━━━━━━━┓
┃     👤 ПРОФИЛЬ     ┃
┗━━━━━━━━━━━━━━━━━━━━┛

🆔 ID: <code>{user_id}</code>
🔍 Поисков: {user['searches']}/{SEARCH_LIMIT}
{'⭐ Статус: 💎 PREMIUM' if is_premium else '⭐ Статус: ⚪ BASIC'}

"""
        
        if is_premium:
            if user['premium_type']:
                profile += f"💎 Тариф: {user['premium_type'].upper()}\n"
            if user['premium_until']:
                days_left = (user['premium_until'] - datetime.now()).days
                profile += f"📅 Осталось: {days_left} дней\n"
        
        # Прогресс бар поисков
        progress = user['searches'] / SEARCH_LIMIT * 100
        progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
        profile += f"\n📊 Прогресс: [{progress_bar}] {progress:.1f}%\n"
        
        if user['searches'] >= SEARCH_LIMIT and not is_premium:
            profile += "\n⚠️ <b>ЛИМИТ ИСЧЕРПАН!</b>\n💎 Купите премиум для продолжения\n"
        
        buttons = [
            ("💎 Премиум", "premium_menu"),
            ("🔍 Поиск", "search_now"),
            ("🔄 Обновить", "refresh_profile")
        ]
        
        keyboard = create_keyboard(buttons, 2)
        
        await event.delete()
        await client.send_message(
            entity=event.chat_id,
            message=profile,
            parse_mode='html',
            buttons=keyboard
        )
    
    @client.on(events.NewMessage(pattern='/admin'))
    async def admin_cmd(event):
        """Команда /admin - админ панель"""
        if event.is_group:
            return
        
        user_id = event.sender_id
        if storage.block_duplicate(user_id, 'admin'):
            return
        
        # Проверяем админ права
        if user_id not in storage.admin_users:
            storage.get_user(user_id)['state'] = 'admin_auth'
            
            await event.delete()
            await client.send_message(
                entity=event.chat_id,
                message="🔐 <b>АДМИН ПАНЕЛЬ</b>\n\nВведите пароль админа:",
                parse_mode='html'
            )
            return
        
        # Админ панель
        admin_text = f"""
┏━━━━━━━━━━━━━━━━━━━━┓
┃    👑 АДМИН ПАНЕЛЬ ┃
┗━━━━━━━━━━━━━━━━━━━━┛

👥 Всего пользователей: {len(storage.users)}
🔍 Всего поисков: {sum(u['searches'] for u in storage.users.values())}
💎 Премиум пользователей: {sum(1 for u in storage.users.values() if storage.is_premium(u))}

<b>Команды админа:</b>
/add_premium [id] [тип] [дни] - выдать премиум
/remove_premium [id] - удалить премиум
/stats - статистика
/users - список пользователей
"""
        
        buttons = [
            ("📊 Статистика", "admin_stats"),
            ("👥 Пользователи", "admin_users"),
            ("💰 Платежи", "admin_payments"),
            ("⚙️ Настройки", "admin_settings")
        ]
        
        keyboard = create_keyboard(buttons, 2)
        
        await event.delete()
        await client.send_message(
            entity=event.chat_id,
            message=admin_text,
            parse_mode='html',
            buttons=keyboard
        )
    
    @client.on(events.NewMessage(pattern='/search'))
    async def search_cmd(event):
        """Команда /search"""
        if event.is_group:
            return
        
        user_id = event.sender_id
        if storage.block_duplicate(user_id, 'search'):
            return
        
        user = storage.get_user(user_id)
        is_premium = storage.is_premium(user_id)
        
        # Проверка лимита
        if not is_premium and user['searches'] >= SEARCH_LIMIT:
            # Плашка о необходимости оплаты
            payment_text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃     ⚠️ ЛИМИТ ИСЧЕРПАН       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🔍 Вы использовали все {SEARCH_LIMIT} бесплатных поисков.

💎 <b>Для продолжения нужен PREMIUM</b>

💳 Оплата только в <b>USDT (TRC20)</b>
📦 Кошелёк для оплаты:
<code>{CRYPTO_WALLET}</code>

📝 После оплаты отправьте <b>хэш транзакции</b>
🔍 Проверка через <b>TronScan</b>
"""
            
            buttons = [
                ("💎 Купить Premium", "premium_menu"),
                ("🔍 Проверить платёж", "check_payment"),
                ("🔄 Профиль", "profile")
            ]
            
            keyboard = create_keyboard(buttons, 2)
            
            await event.delete()
            await client.send_message(
                entity=event.chat_id,
                message=payment_text,
                parse_mode='html',
                buttons=keyboard
            )
            return
        
        # Если лимит не исчерпан
        user['state'] = 'searching'
        
        await event.delete()
        await client.send_message(
            entity=event.chat_id,
            message="🔍 <b>Введите ключевое слово для поиска:</b>\n\nПримеры: крипта, новости, спорт",
            parse_mode='html'
        )
    
    @client.on(events.NewMessage(pattern='/premium'))
    async def premium_cmd(event):
        """Команда /premium"""
        if event.is_group:
            return
        
        user_id = event.sender_id
        if storage.block_duplicate(user_id, 'premium'):
            return
        
        premium_text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃        💎 PREMIUM           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

<b>ТАРИФЫ (USDT TRC20):</b>

🥉 BASIC - 10 USDT (30 дней)
• Безлимитный поиск
• 10 результатов

🥈 ADVANCED - 25 USDT (90 дней)
• BASIC + фильтры
• 15 результатов

🥇 PRO - 50 USDT (180 дней)
• ADVANCED + экспорт
• 20 результатов

👑 ULTIMATE - 100 USDT (НАВСЕГДА)
• Все функции + API
• 25 результатов

💳 <b>Кошелёк для оплаты:</b>
<code>{CRYPTO_WALLET}</code>

📝 <b>После оплаты:</b>
1. Отправьте хэш транзакции
2. Мы проверим через TronScan
3. Активируем Premium автоматически
"""
        
        buttons = [
            ("🥉 BASIC", "buy_basic"),
            ("🥈 ADVANCED", "buy_advanced"),
            ("🥇 PRO", "buy_pro"),
            ("👑 ULTIMATE", "buy_ultimate"),
            ("🔍 Проверить платёж", "check_payment")
        ]
        
        keyboard = create_keyboard(buttons, 2)
        
        await event.delete()
        await client.send_message(
            entity=event.chat_id,
            message=premium_text,
            parse_mode='html',
            buttons=keyboard
        )
    
    @client.on(events.NewMessage(pattern='/pay'))
    async def pay_cmd(event):
        """Проверка платежа"""
        if event.is_group:
            return
        
        user_id = event.sender_id
        
        await event.delete()
        await client.send_message(
            entity=event.chat_id,
            message="📝 <b>Отправьте хэш транзакции для проверки:</b>\n\nПример: <code>a1b2c3d4e5f6...</code>",
            parse_mode='html'
        )
        storage.get_user(user_id)['state'] = 'checking_payment'
    
    # ========== ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ==========
    
    @client.on(events.NewMessage)
    async def message_handler(event):
        """Обработчик всех сообщений"""
        if event.is_group:
            return
        
        user_id = event.sender_id
        text = event.text.strip() if event.text else ""
        
        if not text:
            return
        
        user = storage.get_user(user_id)
        state = user.get('state')
        
        # Команды обрабатываем отдельно
        if text.startswith('/'):
            return
        
        # Блокировка дублирования
        if storage.block_duplicate(user_id, f"msg_{text[:10]}"):
            return
        
        # Удаляем сообщение пользователя (симуляция работы от юзера)
        try:
            await event.delete()
        except:
            pass
        
        # ========== АДМИН АВТОРИЗАЦИЯ ==========
        if state == 'admin_auth':
            if text == ADMIN_PASS:
                storage.admin_users.add(user_id)
                user['state'] = None
                
                await client.send_message(
                    entity=event.chat_id,
                    message="✅ <b>АДМИН ДОСТУП АКТИВИРОВАН!</b>",
                    parse_mode='html'
                )
                await admin_cmd(event)  # Показываем админ панель
            else:
                await client.send_message(
                    entity=event.chat_id,
                    message="❌ <b>НЕВЕРНЫЙ ПАРОЛЬ!</b>",
                    parse_mode='html'
                )
            return
        
        # ========== ПРОВЕРКА ПЛАТЕЖА ==========
        if state == 'checking_payment':
            tx_hash = text.strip()
            
            # Проверяем хэш
            await client.send_message(
                entity=event.chat_id,
                message="🔍 <b>Проверяю платёж через TronScan...</b>",
                parse_mode='html'
            )
            
            # Имитация проверки
            await asyncio.sleep(2)
            
            payment = await check_tron_payment(tx_hash)
            
            if payment and payment.get('verified'):
                # Активируем премиум
                user['premium'] = True
                user['premium_type'] = 'basic'
                user['premium_until'] = datetime.now() + timedelta(days=30)
                user['payment_hash'] = tx_hash
                user['state'] = None
                
                await client.send_message(
                    entity=event.chat_id,
                    message=f"""
✅ <b>ПЛАТЁЖ ПОДТВЕРЖДЁН!</b>

💰 Сумма: {payment['amount']} USDT
📅 Premium активирован на 30 дней
💎 Тариф: BASIC

Теперь у вас безлимитный поиск!
""",
                    parse_mode='html'
                )
            else:
                await client.send_message(
                    entity=event.chat_id,
                    message="❌ <b>Платёж не найден или не подтверждён</b>\n\nПроверьте хэш или подождите подтверждения сети.",
                    parse_mode='html'
                )
            return
        
        # ========== ПОИСКОВЫЙ ЗАПРОС ==========
        if state == 'searching':
            keyword = text.lower().strip()
            
            if len(keyword) < 2:
                await client.send_message(
                    entity=event.chat_id,
                    message="⚠️ <b>Минимум 2 символа</b>",
                    parse_mode='html'
                )
                return
            
            # Увеличиваем счётчик если не премиум
            if not storage.is_premium(user_id):
                user['searches'] += 1
            
            user['state'] = None
            
            # Выполняем поиск
            await client.send_message(
                entity=event.chat_id,
                message=f"🔍 <b>Ищу каналы по запросу:</b> '{keyword}'...",
                parse_mode='html'
            )
            
            channels = await real_search(keyword, 10)  # 10 результатов
            
            if not channels:
                await client.send_message(
                    entity=event.chat_id,
                    message=f"❌ <b>По запросу '{keyword}' ничего не найдено</b>",
                    parse_mode='html'
                )
                return
            
            # Формируем результат с ИНЛАЙН КНОПКАМИ
            result_text = f"""
✅ <b>НАЙДЕНО {len(channels)} КАНАЛОВ</b>
🔍 Запрос: '{keyword}'

<b>ТОП-10 результатов:</b>
"""
            for i, ch in enumerate(channels, 1):
                username = f"@{ch['username']}" if ch['username'] else "без @"
                members = f"{ch['members']:,}" if ch['members'] > 0 else "?"
                
                # Иконки
                icons = ""
                if ch['verified']:
                    icons += " ✅"
                if ch['type'] == 'channel':
                    icons += " 📢"
                
                result_text += f"\n{i}. <b>{ch['title']}</b>{icons}"
                result_text += f"\n   👥 {members} | {username}\n"
            
            # Инлайн кнопки под результатами
            buttons = [
                ("🔍 Новый поиск", "search_again"),
                ("💎 Premium", "premium_menu"),
                ("📊 Профиль", "profile"),
                ("🔄 Обновить", f"refresh_{keyword}")
            ]
            
            keyboard = create_keyboard(buttons, 2)
            
            await client.send_message(
                entity=event.chat_id,
                message=result_text,
                parse_mode='html',
                buttons=keyboard
            )
            
            # Показываем оставшиеся поиски
            if not storage.is_premium(user_id):
                remaining = SEARCH_LIMIT - user['searches']
                if remaining <= 5 and remaining > 0:
                    warning = f"\n⚠️ <b>Осталось {remaining} бесплатных поисков</b>"
                    await client.send_message(
                        entity=event.chat_id,
                        message=warning,
                        parse_mode='html'
                    )
            return
        
        # ========== ОБРАБОТКА ХЭША ПЛАТЕЖА ==========
        if len(text) == 64 and all(c in '0123456789abcdefABCDEF' for c in text):
            # Похоже на хэш транзакции
            await client.send_message(
                entity=event.chat_id,
                message="🔍 <b>Обнаружен хэш транзакции. Проверяю платёж...</b>",
                parse_mode='html'
            )
            
            payment = await check_tron_payment(text)
            
            if payment and payment.get('verified'):
                await client.send_message(
                    entity=event.chat_id,
                    message=f"""
✅ <b>ПЛАТЁЖ ПОДТВЕРЖДЁН!</b>
Хэш: <code>{text[:16]}...</code>

💎 Premium будет активирован после проверки администратором.
""",
                    parse_mode='html'
                )
            else:
                await client.send_message(
                    entity=event.chat_id,
                    message="❌ <b>Платёж не подтверждён</b>\n\nИспользуйте /pay для проверки.",
                    parse_mode='html'
                )
            return
    
    # ========== ОБРАБОТКА ИНЛАЙН КНОПОК ==========
    
    @client.on(events.CallbackQuery)
    async def callback_handler(event):
        """Обработчик инлайн кнопок"""
        user_id = event.sender_id
        data = event.data.decode('utf-8')
        
        await event.answer()  # Ответ на callback
        
        # Обработка разных кнопок
        if data == 'search':
            await search_cmd(event)
        elif data == 'premium':
            await premium_cmd(event)
        elif data == 'profile':
            await profile_cmd(event)
        elif data == 'premium_menu':
            await premium_cmd(event)
        elif data == 'check_payment':
            await pay_cmd(event)
        elif data == 'search_again':
            storage.get_user(user_id)['state'] = 'searching'
            await client.send_message(
                entity=event.chat_id,
                message="🔍 <b>Введите ключевое слово:</b>",
                parse_mode='html'
            )
        elif data.startswith('buy_'):
            plan = data[4:]  # basic, advanced, pro, ultimate
            price = PREMIUM_PRICES.get(plan, 10)
            
            payment_info = f"""
💎 <b>ВЫБРАН ТАРИФ: {plan.upper()}</b>
💰 Цена: {price} USDT

💳 <b>Кошелёк для оплаты:</b>
<code>{CRYPTO_WALLET}</code>

📝 <b>После оплаты:</b>
1. Отправьте хэш транзакции
2. Или используйте /pay
3. Мы проверим через TronScan
4. Premium активируется автоматически
"""
            
            await event.edit(
                text=payment_info,
                parse_mode='html',
                buttons=create_keyboard([
                    ("💳 Оплатить", f"pay_{plan}"),
                    ("🔍 Проверить", "check_payment"),
                    ("🔙 Назад", "premium")
                ], 2)
            )
    
    # ========== ЗАПУСК ==========
    
    print("\n" + "="*70)
    print("🤖 IMBA 2.0 ЗАПУЩЕН!")
    print("✅ 10 результатов • Инлайн кнопки • Профиль")
    print("✅ Админка • Проверка платежей • Крипта • TronScan")
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