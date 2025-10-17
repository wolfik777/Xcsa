"""
Тестовый скрипт для проверки бота
"""
import asyncio
from bot.config import config, load_config

async def test_configuration():
    """Проверка конфигурации"""
    print("🔍 Проверка конфигурации бота...\n")
    
    cfg = load_config()
    
    # Проверка токена
    if cfg.token and cfg.token != "your_bot_token_from_@BotFather":
        print("✅ BOT_TOKEN настроен")
    else:
        print("❌ BOT_TOKEN не настроен! Отредактируйте .env файл")
        return False
    
    # Проверка Admin ID
    if cfg.admin_id and cfg.admin_id != 0:
        print(f"✅ ADMIN_ID настроен: {cfg.admin_id}")
    else:
        print("❌ ADMIN_ID не настроен! Отредактируйте .env файл")
        return False
    
    # Проверка базы данных
    if cfg.database_url:
        print(f"✅ DATABASE_URL: {cfg.database_url}")
    
    print("\n✅ Конфигурация корректна!")
    print("\n🚀 Можете запускать бота: python main.py")
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_configuration())
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("\n💡 Убедитесь что:")
        print("  1. Создан файл .env")
        print("  2. В .env указан BOT_TOKEN")
        print("  3. В .env указан ADMIN_ID")

