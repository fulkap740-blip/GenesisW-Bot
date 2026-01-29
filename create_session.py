from telethon import TelegramClient
import asyncio

API_ID = 22446695
API_HASH = "64587d7e1431a0d7e1959387faa4958a"
PHONE = "+996706161234"

async def main():
    print("=== GenesisW Session Creator ===")
    print(f"Phone: {PHONE}")
    print("Creating session file...")
    
    try:
        # Создаем клиента
        client = TelegramClient('genesis_session', API_ID, API_HASH)
        
        # Запускаем с номером телефона
        await client.start(phone=PHONE)
        
        # Получаем информацию о себе
        me = await client.get_me()
        print(f"\n✅ SUCCESS!")
        print(f"Username: @{me.username}")
        print(f"Phone: {me.phone}")
        print(f"ID: {me.id}")
        
        # Отключаемся
        await client.disconnect()
        
        print(f"\n📁 Session file created: 'genesis_session.session'")
        print("Now upload this file to Railway!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Make sure:")
        print("1. Phone number is correct: +996706161234")
        print("2. You have internet connection")
        print("3. Telegram app is working")

# Запуск
if __name__ == "__main__":
    asyncio.run(main())