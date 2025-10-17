# 📦 Инструкция по установке и развертыванию

## 🖥️ Локальная установка (для разработки)

### 1. Установите зависимости

```bash
# Python 3.9 или выше
python --version

# Создайте виртуальное окружение
python -m venv venv

# Активируйте виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### 2. Настройте бота

```bash
# Скопируйте пример конфигурации
cp .env.example .env

# Отредактируйте .env файл
# Windows:
notepad .env
# Linux/Mac:
nano .env
```

**Минимальная конфигурация для .env:**
```env
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_ID=your_telegram_user_id
DATABASE_URL=sqlite+aiosqlite:///./bot.db
```

### 3. Получите токен бота

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен и добавьте в `.env`

### 4. Узнайте свой Telegram ID

1. Откройте [@userinfobot](https://t.me/userinfobot)
2. Отправьте `/start`
3. Скопируйте ID и добавьте в `.env` как `ADMIN_ID`

### 5. Запустите бота

```bash
python main.py
```

---

## 🐳 Развертывание на VDS/VPS с Docker (рекомендуется)

### Требования
- VDS/VPS с Ubuntu 20.04+ (или другой Linux)
- Минимум 1GB RAM
- 10GB свободного места

### 1. Подключитесь к серверу

```bash
ssh root@your_server_ip
```

### 2. Клонируйте репозиторий

```bash
git clone https://github.com/wolfik777/Xcsa.git
cd Xcsa
```

### 3. Настройте конфигурацию

```bash
cp .env.example .env
nano .env
```

**Рекомендуемая конфигурация для продакшена:**
```env
BOT_TOKEN=your_bot_token
ADMIN_ID=your_telegram_id

# PostgreSQL (уже настроен в docker-compose)
DATABASE_URL=postgresql+asyncpg://botuser:changeme@db:5432/telegram_bot
REDIS_URL=redis://redis:6379/0

# Измените пароль БД
DB_PASSWORD=your_secure_password
```

### 4. Запустите автоматическое развертывание

```bash
chmod +x deploy.sh
./deploy.sh
```

Скрипт автоматически:
- Установит Docker (если не установлен)
- Установит Docker Compose
- Создаст и запустит все контейнеры
- Покажет логи

### 5. Управление ботом

```bash
# Просмотр логов
docker-compose logs -f bot

# Остановка бота
docker-compose stop

# Запуск бота
docker-compose start

# Перезапуск бота
docker-compose restart bot

# Полная остановка и удаление
docker-compose down

# Обновление и перезапуск
git pull
docker-compose up -d --build
```

---

## 🔄 Обновление бота

### Локальное обновление

```bash
git pull
pip install -r requirements.txt
python main.py
```

### Обновление на сервере

```bash
cd Xcsa
git pull
docker-compose up -d --build
```

---

## 🗄️ База данных

### SQLite (для разработки)
Используется по умолчанию, файл `bot.db` создается автоматически.

### PostgreSQL (для продакшена)
Автоматически настраивается в Docker Compose.

**Доступ к БД через Adminer:**
1. Откройте в браузере: `http://your_server_ip:8080`
2. Введите данные:
   - Система: PostgreSQL
   - Сервер: db
   - Пользователь: botuser
   - Пароль: (из .env)
   - База данных: telegram_bot

---

## 🔥 Firewall настройка (для VDS)

```bash
# Разрешите SSH
sudo ufw allow 22

# Разрешите Adminer (опционально)
sudo ufw allow 8080

# Включите firewall
sudo ufw enable
```

---

## 📊 Мониторинг

### Просмотр статистики

```bash
# Использование ресурсов
docker stats

# Логи в реальном времени
docker-compose logs -f bot

# Размер логов
du -sh logs/
```

---

## ❓ Решение проблем

### Бот не запускается

1. Проверьте логи:
```bash
docker-compose logs bot
```

2. Проверьте конфигурацию:
```bash
cat .env
```

3. Проверьте токен бота:
- Убедитесь, что токен правильный
- Проверьте, что в токене нет лишних пробелов

### База данных не подключается

```bash
# Проверьте статус контейнеров
docker-compose ps

# Перезапустите БД
docker-compose restart db

# Пересоздайте контейнеры
docker-compose down
docker-compose up -d
```

### Нехватка места на диске

```bash
# Очистите старые образы Docker
docker system prune -a

# Очистите логи
rm -rf logs/*

# Очистите скачанные файлы
rm -rf downloads/*
```

---

## 🔐 Безопасность

1. **Измените пароли в .env**
2. **Используйте firewall**
3. **Регулярно обновляйте систему:**
```bash
sudo apt update && sudo apt upgrade -y
```

4. **Настройте автоматические бэкапы БД:**
```bash
# Добавьте в crontab
0 3 * * * docker exec bot_postgres pg_dump -U botuser telegram_bot > /backups/bot_$(date +\%Y\%m\%d).sql
```

---

## 📞 Поддержка

Возникли проблемы? Создайте Issue на GitHub!

