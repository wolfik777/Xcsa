# ⚡ Быстрый старт за 5 минут

## 🎯 Самый быстрый способ запустить бота

### Шаг 1: Получите токен бота (2 минуты)

1. Откройте Telegram
2. Найдите [@BotFather](https://t.me/BotFather)
3. Отправьте `/newbot`
4. Придумайте имя и username для бота
5. **Скопируйте токен** (выглядит так: `123456:ABC-DEF1234...`)

### Шаг 2: Узнайте свой ID (1 минута)

1. Откройте [@userinfobot](https://t.me/userinfobot)
2. Отправьте `/start`
3. **Скопируйте ваш ID** (например: `123456789`)

### Шаг 3: Настройте бота (1 минута)

Скопируйте `.env.example` в `.env` и заполните:

```bash
# Windows
copy .env.example .env
notepad .env

# Linux/Mac
cp .env.example .env
nano .env
```

Минимальная настройка:
```env
BOT_TOKEN=ваш_токен_от_botfather
ADMIN_ID=ваш_telegram_id
DATABASE_URL=sqlite+aiosqlite:///./bot.db
```

### Шаг 4: Запустите! (1 минута)

#### 🐍 Python (локально)

```bash
# Установите зависимости
pip install -r requirements.txt

# Запустите бота
python main.py
```

#### 🐳 Docker (на сервере)

```bash
# Автоматический запуск
chmod +x deploy.sh
./deploy.sh
```

---

## ✅ Готово!

Откройте Telegram и найдите вашего бота. Отправьте `/start`

---

## 🎁 Настройка реферальной системы

По умолчанию:
- **10 рефералов** = Бонусные функции
- **50 рефералов** = Premium навсегда

Измените в `.env`:
```env
REFERRAL_BONUS_COUNT=10
PREMIUM_REFERRAL_COUNT=50
```

---

## 📥 Поддерживаемые платформы

- ✅ YouTube (видео/аудио)
- ✅ TikTok (без водяных знаков)
- ✅ Instagram (посты/reels/stories)
- ✅ Twitter/X
- ✅ Facebook

---

## 🛠 Дополнительные инструменты

- 🌐 Переводчик
- 📊 Генератор QR-кодов
- 🔗 Сокращение ссылок
- (больше функций в разработке)

---

## 🚀 Продвинутая настройка

Смотрите [INSTALL.md](INSTALL.md) для:
- Развертывание на VDS/VPS
- PostgreSQL настройка
- Мониторинг и логи
- Решение проблем

## 🎯 Стратегия роста

Смотрите [REFERRAL_STRATEGY.md](REFERRAL_STRATEGY.md) для:
- Как привлекать пользователей
- Вирусный маркетинг
- Монетизация
- Метрики успеха

---

## ❓ Частые вопросы

**Q: Бот не отвечает**
- Проверьте токен в .env
- Убедитесь, что бот запущен (`python main.py`)
- Проверьте логи на ошибки

**Q: Не скачивается видео**
- Проверьте, что установлен ffmpeg
- Некоторые приватные аккаунты могут не работать
- Попробуйте другую ссылку

**Q: Как обновить бота?**
```bash
git pull
pip install -r requirements.txt
python main.py
```

---

## 🔥 Полезные команды

```bash
# Просмотр логов (Docker)
docker-compose logs -f bot

# Перезапуск бота (Docker)
docker-compose restart bot

# Остановка бота (Docker)
docker-compose stop

# Обновление (Docker)
git pull && docker-compose up -d --build
```

---

## 📞 Нужна помощь?

Создайте Issue на GitHub: https://github.com/wolfik777/Xcsa/issues

---

Удачи! 🎉

