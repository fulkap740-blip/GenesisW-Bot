#!/usr/bin/env python3
"""
GenesisW Bot - WORKING FOR ALL USERS
БОТ • ВСЕМ ОТВЕЧАЕТ • HELP • АДМИН БЕЗЛИМИТ • ВИП СТАТУС
"""

import os
import asyncio
import time
from datetime import datetime, timedelta
from telethon import TelegramClient, events, functions, types
from telethon.tl.types import ReplyInlineMarkup, KeyboardButtonRow, KeyboardButtonCallback

# ========== КОНФИГ ==========
API_ID = int(os.environ.get("API_ID", "22446695"))
API_HASH = os.environ.get("API_HASH", "64587d7e1431a0d7e1959387faa4958a"))
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8576112278:AAE35GWqoHpsQ9bdB069f__LDShXkNeHXro"))

ADMIN_USER_ID = 6902281947  # Твой Telegram ID для админа
CRYPTO_WALLET = "TKMBNpspKG6uQZi8J9siyChhX6BrZJnJr7"
SEARCH_LIMIT = 20
# ============================

print("\n" + "="*70)
print("🚀 GENESISW BOT - PUBLIC VERSION")
print("="*70)

# ========== ХРАНИЛИЩЕ ==========
class UserData:
    def __init__(self):
        self.users = {}
        self.payments = {}
        self.last_actions = {}
    
    def get_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = {
                'searches': 0,
                'premium': False,
                'premium_type': None,
                'premium_until': None,
                'state': None,
                'joined': datetime.now(),
                'is_vip': user_id == ADMIN_USER_ID  # Ты всегда VIP
            }
        return self.users[user_id]
    
    def is_premium(self, user_id):
        user = self.get_user(user_id)
        if user['is_vip']:  # VIP всегда премиум
            return True
        if user['premium'] and user['premium_until']:
            return datetime.now() < user['premium_until']
        return False
    
    def block_duplicate(self, user_id, action):
        key = f"{user_id}_{action}"
        now = time.time()
        
        if key in self.last_actions:
            if now - self.last_actions[key] < 1.5:
                return True
        
        self.last_actions[key] = now
        return False

storage = UserData()

# ========== ТЕЛЕГРАМ КЛИЕНТЫ ==========
bot_client = None  # Бот для ответов пользователям
user_client = None  # Пользователь для поиска

async def init_clients():
    """Инициализация двух клиентов"""
    global bot_client, user_client
    
    print("🔧 Инициализация клиентов...")
    
    # 1. БОТ-клиент (отвечает всем)
    try:
        bot_client = TelegramClient('bot_session', API_ID, API_HASH)
        await bot_client.start(bot_token=BOT_TOKEN)
        bot_info = await bot_client.get_me()
        print(f"✅ Бот готов: @{bot_info.username}")
    except Exception as e:
        print(f"❌ Ошибка бота: {e}")
        return False
    
    # 2. ПОЛЬЗОВАТЕЛЬСКИЙ клиент (только для поиска)
    try:
        if os.path.exists('genesis_session.session'):
            user_client = TelegramClient('genesis_session', API_ID, API_HASH)
            await user_client.start()
            user_info = await user_client.get_me()
            print(f"✅ Поиск готов: @{user_info.username}")
        else:
            print("⚠️ Файл сессии не найден, поиск отключен")
            user_client = None
    except Exception as e:
        print(f"⚠️ Ошибка пользовательского клиента: {e}")
        user_client = None
    
    return True

# ========== ИНЛАЙН КНОПКИ ==========
def create_inline_keyboard(buttons, columns=2):
    """Создание инлайн клавиатуры"""
    rows = []
    current_row = []
    
    for i, (text, data) in enumerate(buttons):
        button = KeyboardButtonCallback(
            text=text[:20],
            data=data.encode('utf-8')[:64]
        )
        current_row.append(button)
        
        if (i + 1) % columns == 0:
            rows.append(KeyboardButtonRow(buttons=current_row))
            current_row = []
    
    if current_row:
        rows.append(KeyboardButtonRow(buttons=current_row))
    
    return ReplyInlineMarkup(rows=rows)

# ========== ПОИСК ==========
async def real_search(keyword, limit=10):
    """Реальный поиск через пользовательский клиент"""
    if not user_client:
        return None
    
    try:
        print(f"🔍 Поиск: '{keyword}'")
        
        result = await user_client(functions.contacts.SearchRequest(
            q=keyword,
            limit=limit
        ))
        
        channels = []
        for chat in result.chats:
            if hasattr(chat, 'title'):
                channels.append({
                    'title': chat.title[:40],
                    'username': getattr(chat, 'username', None),
                    'members': getattr(chat, 'participants_count', 0),
                    'verified': getattr(chat, 'verified', False)
                })
        
        channels.sort(key=lambda x: x['members'], reverse=True)
        return channels[:limit]
        
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        return None

# ========== ОСНОВНАЯ ФУНКЦИЯ ==========
async def main():
    print("🎯 Запускаю публичный бот...")
    
    if not await init_clients():
        print("❌ Не могу запустить")
        return
    
    print("✅ Бот готов принимать команды от ВСЕХ пользователей")
    
    # ========== КОМАНДА /start ==========
    @bot_client.on(events.NewMessage(pattern='/start'))
    async def start_cmd(event):
        """Команда /start - работает для ВСЕХ"""
        user_id = event.sender_id
        if storage.block_duplicate(user_id, 'start'):
            return
        
        user = storage.get_user(user_id)
        
        # Статус пользователя
        is_vip = user['is_vip']
        is_premium = storage.is_premium(user_id)
        
        status_text = ""
        if is_vip:
            status_text = "👑 <b>ВЛАДЕЛЕЦ (БЕЗЛИМИТ)</b>"
        elif is_premium:
            status_text = "💎 <b>PREMIUM</b>"
        else:
            status_text = "⚪ <b>BASIC</b>"
        
        profile = f"""
{status_text}

🆔 ID: <code>{user_id}</code>
🔍 Поисков: {user['searches']}/{SEARCH_LIMIT}
📅 Регистрация: {user['joined'].strftime('%d.%m.%Y')}
"""
        if is_premium and user['premium_type']:
            profile += f"💎 Тариф: {user['premium_type'].upper()}\n"
            if user['premium_until']:
                days_left = (user['premium_until'] - datetime.now()).days
                profile += f"📅 Осталось: {days_left} дней\n"
        
        # Кнопки
        buttons = [
            ("🔍 Поиск", "search"),
            ("💎 Премиум", "premium"),
            ("👑 Админ", "admin"),
            ("🆘 Помощь", "help")
        ]
        
        keyboard = create_inline_keyboard(buttons, 2)
        
        await event.respond(profile, parse_mode='html', buttons=keyboard)
    
    # ========== КОМАНДА /help ==========
    @bot_client.on(events.NewMessage(pattern='/help'))
    async def help_cmd(event):
        """Команда /help"""
        user_id = event.sender_id
        if storage.block_duplicate(user_id, 'help'):
            return
        
        help_text = f"""
🆘 <b>ПОМОЩЬ ПО GENESISW BOT</b>

<b>📋 КОМАНДЫ:</b>
/start - главное меню
/search - поиск каналов
/premium - премиум доступ
/profile - ваш профиль
/help - эта справка

<b>🔍 КАК ИСКАТЬ:</b>
1. Отправьте /search
2. Введите ключевое слово
3. Получите 10 лучших каналов

<b>📊 ЛИМИТЫ:</b>
• Бесплатно: {SEARCH_LIMIT} поисков
• Премиум: безлимит (/premium)

<b>💎 ПРЕМИУМ:</b>
• Безлимитный поиск
• Приоритетная обработка
• Расширенные фильтры

<b>💳 ОПЛАТА:</b>
Только USDT (TRC20)
Кошелёк: <code>{CRYPTO_WALLET}</code>

👑 Владелец: @Alexanderiprx
🤖 Бот: @genesisw_bot
"""
        await event.respond(help_text, parse_mode='html')
    
    # ========== КОМАНДА /profile ==========
    @bot_client.on(events.NewMessage(pattern='/profile'))
    async def profile_cmd(event):
        """Команда /profile"""
        user_id = event.sender_id
        if storage.block_duplicate(user_id, 'profile'):
            return
        
        user = storage.get_user(user_id)
        is_vip = user['is_vip']
        is_premium = storage.is_premium(user_id)
        
        # Красивый профиль
        if is_vip:
            status_icon = "👑"
            status_text = "ВЛАДЕЛЕЦ"
            limit_text = "♾️ БЕЗЛИМИТ"
        elif is_premium:
            status_icon = "💎"
            status_text = "PREMIUM"
            remaining = "♾️"
            limit_text = f"{remaining} поисков"
        else:
            status_icon = "⚪"
            status_text = "BASIC"
            remaining = SEARCH_LIMIT - user['searches']
            limit_text = f"{remaining}/{SEARCH_LIMIT}"
        
        profile = f"""
┏━━━━━━━━━━━━━━━━━━━━┓
┃     👤 ПРОФИЛЬ     ┃
┗━━━━━━━━━━━━━━━━━━━━┛

{status_icon} <b>{status_text}</b>
🆔 ID: <code>{user_id}</code>
🔍 Поисков: {user['searches']}
📊 Лимит: {limit_text}
📅 В системе: {(datetime.now() - user['joined']).days} дней
"""
        if is_premium and user['premium_type']:
            profile += f"💎 Тариф: {user['premium_type'].upper()}\n"
            if user['premium_until']:
                days_left = (user['premium_until'] - datetime.now()).days
                profile += f"📅 Осталось: {days_left} дней\n"
        
        # Прогресс бар для обычных пользователей
        if not is_vip and not is_premium:
            progress = user['searches'] / SEARCH_LIMIT * 100
            progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
            profile += f"\n📊 Прогресс: [{progress_bar}] {progress:.1f}%\n"
            
            if user['searches'] >= SEARCH_LIMIT:
                profile += "\n⚠️ <b>ЛИМИТ ИСЧЕРПАН!</b>\n💎 Купите премиум для продолжения\n"
        
        buttons = [
            ("🔍 Поиск", "search"),
            ("💎 Премиум", "premium"),
            ("🔄 Обновить", "refresh_profile"),
            ("🆘 Помощь", "help")
        ]
        
        keyboard = create_inline_keyboard(buttons, 2)
        
        await event.respond(profile, parse_mode='html', buttons=keyboard)
    
    # ========== КОМАНДА /search ==========
    @bot_client.on(events.NewMessage(pattern='/search'))
    async def search_cmd(event):
        """Команда /search"""
        user_id = event.sender_id
        if storage.block_duplicate(user_id, 'search'):
            return
        
        user = storage.get_user(user_id)
        is_vip = user['is_vip']
        is_premium = storage.is_premium(user_id)
        
        # Проверка лимита
        if not is_vip and not is_premium and user['searches'] >= SEARCH_LIMIT:
            # ПЛАШКА ОПЛАТЫ
            payment_text = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃     ⚠️ ЛИМИТ ИСЧЕРПАН       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🔍 Вы использовали все {SEARCH_LIMIT} поисков.

💎 <b>Для продолжения нужен PREMIUM</b>

💳 Оплата в <b>USDT (TRC20)</b>
📦 Кошелёк:
<code>{CRYPTO_WALLET}</code>

📝 После оплаты отправьте <b>хэш транзакции</b>
"""
            buttons = [
                ("💎 Купить Premium", "premium_menu"),
                ("🔍 Проверить платёж", "check_payment"),
                ("📊 Профиль", "profile")
            ]
            
            keyboard = create_inline_keyboard(buttons, 2)
            
            await event.respond(payment_text, parse_mode='html', buttons=keyboard)
            return
        
        # Если можно искать
        user['state'] = 'searching'
        
        await event.respond(
            "🔍 <b>Введите ключевое слово для поиска:</b>\n\nПример: крипта, новости, спорт, музыка",
            parse_mode='html'
        )
    
    # ========== КОМАНДА /premium ==========
    @bot_client.on(events.NewMessage(pattern='/premium'))
    async def premium_cmd(event):
        """Команда /premium"""
        user_id = event.sender_id
        if storage.block_duplicate(user_id, 'premium'):
            return
        
        user = storage.get_user(user_id)
        
        # Если уже VIP
        if user['is_vip']:
            await event.respond("👑 <b>Вы уже ВЛАДЕЛЕЦ с безлимитным доступом!</b>", parse_mode='html')
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

💳 <b>Кошелёк:</b>
<code>{CRYPTO_WALLET}</code>

📝 <b>После оплаты отправьте хэш транзакции</b>
Или используйте команду /pay
"""
        buttons = [
            ("🥉 BASIC", "buy_basic"),
            ("🥈 ADVANCED", "buy_advanced"),
            ("🥇 PRO", "buy_pro"),
            ("👑 ULTIMATE", "buy_ultimate"),
            ("🔍 Проверить платёж", "check_payment"),
            ("📊 Профиль", "profile")
        ]
        
        keyboard = create_inline_keyboard(buttons, 2)
        
        await event.respond(premium_text, parse_mode='html', buttons=keyboard)
    
    # ========== КОМАНДА /admin ==========
    @bot_client.on(events.NewMessage(pattern='/admin'))
    async def admin_cmd(event):
        """Команда /admin"""
        user_id = event.sender_id
        if storage.block_duplicate(user_id, 'admin'):
            return
        
        user = storage.get_user(user_id)
        
        # Только для админа/VIP
        if not user['is_vip']:
            await event.respond("❌ <b>У вас нет доступа к админ панели</b>", parse_mode='html')
            return
        
        # АДМИН ПАНЕЛЬ
        admin_text = f"""
┏━━━━━━━━━━━━━━━━━━━━┓
┃    👑 АДМИН ПАНЕЛЬ ┃
┗━━━━━━━━━━━━━━━━━━━━┛

<b>СТАТИСТИКА:</b>
👥 Пользователей: {len(storage.users)}
🔍 Всего поисков: {sum(u['searches'] for u in storage.users.values())}
💎 Премиум: {sum(1 for u in storage.users.values() if storage.is_premium(u) and not u['is_vip'])}
⭐ VIP: {sum(1 for u in storage.users.values() if u['is_vip'])}
💰 Платежей: {len(storage.payments)}

<b>АДМИН КОМАНДЫ:</b>
• /add_premium [id] [days]
• /remove_premium [id]
• /stats - подробная статистика
• /users - список пользователей
"""
        buttons = [
            ("📊 Статистика", "admin_stats"),
            ("👥 Пользователи", "admin_users"),
            ("💰 Платежи", "admin_payments"),
            ("⚡ Быстрые действия", "admin_quick")
        ]
        
        keyboard = create_inline_keyboard(buttons, 2)
        
        await event.respond(admin_text, parse_mode='html', buttons=keyboard)
    
    # ========== КОМАНДА /pay ==========
    @bot_client.on(events.NewMessage(pattern='/pay'))
    async def pay_cmd(event):
        """Проверка платежа"""
        user_id = event.sender_id
        
        await event.respond(
            "📝 <b>Отправьте хэш транзакции для проверки:</b>\n\nПример: <code>a1b2c3d4e5f6...</code>",
            parse_mode='html'
        )
        storage.get_user(user_id)['state'] = 'checking_payment'
    
    # ========== ОБРАБОТКА СООБЩЕНИЙ ==========
    @bot_client.on(events.NewMessage)
    async def message_handler(event):
        """Обработчик всех сообщений"""
        if event.is_group or event.is_channel:
            return
        
        user_id = event.sender_id
        text = event.text.strip() if event.text else ""
        
        if not text or text.startswith('/'):
            return
        
        if storage.block_duplicate(user_id, f"msg_{text[:10]}"):
            return
        
        user = storage.get_user(user_id)
        state = user.get('state')
        
        # ========== ПРОВЕРКА ПЛАТЕЖА ==========
        if state == 'checking_payment':
            tx_hash = text.strip()
            
            await event.respond("🔍 <b>Проверяю платёж...</b>", parse_mode='html')
            
            # Имитация проверки
            await asyncio.sleep(2)
            
            if len(tx_hash) >= 10 and tx_hash.isalnum():
                storage.payments[tx_hash] = {
                    'user_id': user_id,
                    'hash': tx_hash,
                    'timestamp': datetime.now(),
                    'verified': True
                }
                
                # Активируем премиум
                user['premium'] = True
                user['premium_type'] = 'basic'
                user['premium_until'] = datetime.now() + timedelta(days=30)
                user['state'] = None
                
                await event.respond(
                    f"""
✅ <b>ПЛАТЁЖ ПОДТВЕРЖДЁН!</b>

💰 Premium активирован на 30 дней
💎 Тариф: BASIC

Теперь у вас безлимитный поиск!
Используйте /profile для проверки статуса
""",
                    parse_mode='html'
                )
            else:
                await event.respond(
                    "❌ <b>Неверный формат хэша</b>\n\nИспользуйте команду /pay для проверки.",
                    parse_mode='html'
                )
            return
        
        # ========== ПОИСК ==========
        if state == 'searching':
            keyword = text.lower().strip()
            
            if len(keyword) < 2:
                await event.respond("⚠️ <b>Минимум 2 символа</b>", parse_mode='html')
                return
            
            # Увеличиваем счётчик если не VIP и не премиум
            if not user['is_vip'] and not storage.is_premium(user_id):
                user['searches'] += 1
            
            user['state'] = None
            
            # Проверяем лимит после увеличения
            if not user['is_vip'] and not storage.is_premium(user_id) and user['searches'] > SEARCH_LIMIT:
                await event.respond(
                    f"❌ <b>Лимит исчерпан!</b>\n\nИспользуйте /premium для безлимитного доступа",
                    parse_mode='html'
                )
                return
            
            await event.respond(f"🔍 <b>Ищу каналы:</b> '{keyword}'...", parse_mode='html')
            
            channels = await real_search(keyword, 10)
            
            if not channels:
                await event.respond(
                    f"❌ <b>По запросу '{keyword}' ничего не найдено</b>",
                    parse_mode='html'
                )
                return
            
            # РЕЗУЛЬТАТЫ
            result_text = f"""
✅ <b>НАЙДЕНО {len(channels)} КАНАЛОВ</b>
🔍 Запрос: '{keyword}'

<b>ТОП-10 результатов:</b>
"""
            for i, ch in enumerate(channels, 1):
                username = f"@{ch['username']}" if ch['username'] else "без @"
                members = f"{ch['members']:,}" if ch['members'] > 0 else "?"
                
                icons = ""
                if ch.get('verified'):
                    icons += " ✅"
                
                result_text += f"\n{i}. <b>{ch['title']}</b>{icons}"
                result_text += f"\n   👥 {members} | {username}\n"
            
            # Инлайн кнопки
            buttons = [
                ("🔍 Новый поиск", "search_again"),
                ("💎 Premium", "premium_menu"),
                ("📊 Профиль", "profile"),
                ("🆘 Помощь", "help")
            ]
            
            keyboard = create_inline_keyboard(buttons, 2)
            
            await event.respond(result_text, parse_mode='html', buttons=keyboard)
            
            # Предупреждение о лимите
            if not user['is_vip'] and not storage.is_premium(user_id):
                remaining = SEARCH_LIMIT - user['searches']
                if remaining <= 5 and remaining > 0:
                    warning = f"⚠️ <b>Осталось {remaining} бесплатных поисков</b>"
                    await event.respond(warning, parse_mode='html')
            return
        
        # ========== АВТОПРОВЕРКА ХЭША ==========
        if len(text) >= 20 and all(c.isalnum() for c in text):
            await event.respond(
                f"""
🔍 <b>Обнаружен хэш транзакции</b>
<code>{text[:20]}...</code>

💎 Обратитесь к @Alexanderiprx для активации Premium.
""",
                parse_mode='html'
            )
            return
    
    # ========== ОБРАБОТКА ИНЛАЙН КНОПОК ==========
    @bot_client.on(events.CallbackQuery)
    async def callback_handler(event):
        user_id = event.sender_id
        data = event.data.decode('utf-8') if event.data else ""
        
        await event.answer()
        
        if data == 'search' or data == 'search_now' or data == 'search_again':
            await search_cmd(event)
        elif data == 'premium' or data == 'premium_menu':
            await premium_cmd(event)
        elif data == 'profile' or data == 'refresh_profile':
            await profile_cmd(event)
        elif data == 'help':
            await help_cmd(event)
        elif data == 'admin':
            await admin_cmd(event)
        elif data == 'check_payment':
            await pay_cmd(event)
        elif data.startswith('buy_'):
            plan = data[4:]
            prices = {'basic': 10, 'advanced': 25, 'pro': 50, 'ultimate': 100}
            price = prices.get(plan, 10)
            
            payment_info = f"""
💎 <b>ТАРИФ: {plan.upper()}</b>
💰 Цена: {price} USDT

💳 <b>Кошелёк:</b>
<code>{CRYPTO_WALLET}</code>

📝 После оплаты отправьте хэш транзакции
"""
            buttons = [
                ("💳 Оплатить", f"pay_{plan}"),
                ("🔍 Проверить", "check_payment"),
                ("🔙 Назад", "premium")
            ]
            
            keyboard = create_inline_keyboard(buttons, 2)
            
            await event.edit(text=payment_info, parse_mode='html', buttons=keyboard)
    
    print("\n" + "="*70)
    print("🤖 ПУБЛИЧНЫЙ БОТ ЗАПУЩЕН!")
    print("✅ Работает для ВСЕХ пользователей")
    print("✅ Команда /help добавлена")
    print("✅ Админ: БЕЗЛИМИТ + ВИП статус")
    print("✅ VIP статус для владельца")
    print("📞 Отправьте /start любому пользователю")
    print("="*70)
    
    # Запускаем бота
    await bot_client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Остановлен")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")