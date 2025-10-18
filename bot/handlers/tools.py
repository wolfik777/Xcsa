"""
Tools handlers (QR codes, translator, etc.)
"""
import io
import qrcode
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from deep_translator import GoogleTranslator
from langdetect import detect

from ..keyboards import get_main_menu, get_cancel_keyboard

router = Router()


async def safe_delete_message(message):
    """Безопасное удаление сообщения"""
    try:
        await message.delete()
    except Exception:
        pass  # Игнорируем ошибки удаления


class ToolStates(StatesGroup):
    """Tool states"""
    waiting_qr_text = State()
    waiting_translate_text = State()
    waiting_translate_target = State()
    waiting_short_url = State()
    waiting_currency = State()
    waiting_wiki = State()
    waiting_calc = State()
    waiting_compress = State()
    waiting_weather = State()


@router.callback_query(F.data == "tool_qr")
async def qr_tool(callback: CallbackQuery, state: FSMContext):
    """QR code generator"""
    await state.set_state(ToolStates.waiting_qr_text)
    await safe_delete_message(callback.message)
    await callback.message.answer(
        "📊 <b>Генератор QR-кодов</b>\n\n"
        "Отправь текст или ссылку для создания QR-кода:",
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.message(ToolStates.waiting_qr_text)
async def generate_qr(message: Message, state: FSMContext):
    """Generate QR code"""
    # Check if user wants to cancel or use menu
    if message.text in ["❌ Отмена", "📥 Скачать видео/музыку", "🛠 Инструменты", 
                        "🎁 Реферальная программа", "📊 Моя статистика", 
                        "🏆 Топ рефералов", "❓ Помощь"]:
        await state.clear()
        if message.text == "❌ Отмена":
            await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    try:
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(message.text)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to bytes
        bio = io.BytesIO()
        img.save(bio, 'PNG')
        bio.seek(0)
        
        # Send image
        photo = BufferedInputFile(bio.read(), filename="qrcode.png")
        await message.answer_photo(
            photo=photo,
            caption="📊 QR-код создан!",
            reply_markup=get_main_menu()
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при создании QR-кода: {str(e)}",
            reply_markup=get_main_menu()
        )
    
    finally:
        await state.clear()


@router.callback_query(F.data == "tool_translator")
async def translator_tool(callback: CallbackQuery, state: FSMContext):
    """Translator tool"""
    await state.set_state(ToolStates.waiting_translate_target)
    await safe_delete_message(callback.message)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇷🇺 На русский", callback_data="translate_ru"),
        InlineKeyboardButton(text="🇬🇧 На английский", callback_data="translate_en")
    )
    builder.row(
        InlineKeyboardButton(text="🇪🇸 На испанский", callback_data="translate_es"),
        InlineKeyboardButton(text="🇩🇪 На немецкий", callback_data="translate_de")
    )
    builder.row(
        InlineKeyboardButton(text="🇫🇷 На французский", callback_data="translate_fr"),
        InlineKeyboardButton(text="🇨🇳 На китайский", callback_data="translate_zh-CN")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="back_main")
    )
    
    await callback.message.answer(
        "🌐 <b>Переводчик</b>\n\n"
        "Выбери язык для перевода:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


# Обработчики выбора языка перевода
@router.callback_query(F.data.startswith("translate_"))
async def select_translation_language(callback: CallbackQuery, state: FSMContext):
    """Select target language for translation"""
    target_lang = callback.data.replace("translate_", "")
    await state.update_data(target_lang=target_lang)
    await state.set_state(ToolStates.waiting_translate_text)
    
    lang_names = {
        "ru": "русский",
        "en": "английский",
        "es": "испанский",
        "de": "немецкий",
        "fr": "французский",
        "zh-CN": "китайский"
    }
    
    await safe_delete_message(callback.message)
    await callback.message.answer(
        f"🌐 <b>Переводчик</b>\n\n"
        f"Выбран язык: <b>{lang_names.get(target_lang, target_lang)}</b>\n\n"
        f"Отправь текст для перевода:",
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.message(ToolStates.waiting_translate_text)
async def translate_text(message: Message, state: FSMContext):
    """Translate text"""
    # Check if user wants to cancel or use menu
    if message.text in ["❌ Отмена", "📥 Скачать видео/музыку", "🛠 Инструменты", 
                        "🎁 Реферальная программа", "📊 Моя статистика", 
                        "🏆 Топ рефералов", "❓ Помощь"]:
        await state.clear()
        if message.text == "❌ Отмена":
            await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    try:
        # Get selected target language
        data = await state.get_data()
        target_lang = data.get('target_lang', 'ru')
        
        # Detect source language
        detected_lang = detect(message.text)
        
        # Translate
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(message.text)
        
        # Language names
        lang_names = {
            "en": "Английский",
            "ru": "Русский",
            "es": "Испанский",
            "fr": "Французский",
            "de": "Немецкий",
            "it": "Итальянский",
            "pt": "Португальский",
            "uk": "Украинский",
            "zh-cn": "Китайский",
            "zh-CN": "Китайский",
            "ja": "Японский",
            "ko": "Корейский",
            "ar": "Арабский",
        }
        
        source_name = lang_names.get(detected_lang, detected_lang.upper())
        target_name = lang_names.get(target_lang, target_lang.upper())
        
        response = f"""
🌐 <b>Перевод</b>

<b>Исходный текст</b> ({source_name}):
{message.text}

<b>Перевод</b> ({target_name}):
{translated}
"""
        
        await message.answer(response, reply_markup=get_main_menu())
        
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при переводе: {str(e)}",
            reply_markup=get_main_menu()
        )
    
    finally:
        await state.clear()


@router.callback_query(F.data == "tool_shorturl")
async def shorturl_tool(callback: CallbackQuery, state: FSMContext):
    """URL shortener tool"""
    await state.set_state(ToolStates.waiting_short_url)
    await safe_delete_message(callback.message)
    await callback.message.answer(
        "🔗 <b>Сокращение ссылок</b>\n\n"
        "Отправь длинную ссылку для сокращения:",
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.message(ToolStates.waiting_short_url)
async def shorten_url(message: Message, state: FSMContext):
    """Shorten URL"""
    # Check if user wants to cancel or use menu
    if message.text in ["❌ Отмена", "📥 Скачать видео/музыку", "🛠 Инструменты", 
                        "🎁 Реферальная программа", "📊 Моя статистика", 
                        "🏆 Топ рефералов", "❓ Помощь"]:
        await state.clear()
        if message.text == "❌ Отмена":
            await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    try:
        import pyshorteners
        
        s = pyshorteners.Shortener()
        short_url = s.tinyurl.short(message.text)
        
        response = f"""
🔗 <b>Ссылка сокращена!</b>

<b>Оригинал:</b>
{message.text}

<b>Короткая ссылка:</b>
{short_url}
"""
        
        await message.answer(response, reply_markup=get_main_menu())
        
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при сокращении ссылки: {str(e)}",
            reply_markup=get_main_menu()
        )
    
    finally:
        await state.clear()


# ============= КОНВЕРТЕР ВАЛЮТ =============

@router.callback_query(F.data == "tool_currency")
async def currency_tool(callback: CallbackQuery, state: FSMContext):
    """Currency converter tool"""
    await state.set_state(ToolStates.waiting_currency)
    await safe_delete_message(callback.message)
    await callback.message.answer(
        "💱 <b>Конвертер валют</b>\n\n"
        "Отправь сумму и валюты в формате:\n"
        "<code>100 USD в RUB</code>\n"
        "<code>50 EUR в USD</code>\n\n"
        "Доступные валюты: USD, EUR, RUB, GBP, JPY, CNY",
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.message(ToolStates.waiting_currency)
async def convert_currency(message: Message, state: FSMContext):
    """Convert currency with multiple API fallbacks"""
    if message.text in ["❌ Отмена", "📥 Скачать видео/музыку", "🛠 Инструменты", 
                        "🎁 Реферальная программа", "📊 Моя статистика", 
                        "🏆 Топ рефералов", "❓ Помощь"]:
        await state.clear()
        if message.text == "❌ Отмена":
            await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    try:
        import re
        import aiohttp
        
        # Парсим запрос: "100 USD в RUB" или "100 USD to RUB" или "100 usd rub"
        text = message.text.strip()
        
        # Пробуем разные варианты регулярок
        patterns = [
            r'(\d+(?:[.,]\d+)?)\s*([A-Za-zА-Яа-я]{3})\s*(?:в|В|to|TO|in|IN|->)\s*([A-Za-zА-Яа-я]{3})',
            r'(\d+(?:[.,]\d+)?)\s+([A-Za-zА-Яа-я]{3})\s+([A-Za-zА-Яа-я]{3})',  # "100 USD RUB"
        ]
        
        match = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                break
        
        if not match:
            print(f"[DEBUG] Currency parse failed for: {text}")
            await message.answer(
                "❌ Неверный формат!\n\n"
                "Используй: <code>100 USD в RUB</code>\n"
                "Или: <code>100 USD RUB</code>\n\n"
                "Доступные валюты: USD, EUR, RUB, GBP, JPY, CNY, KZT, UAH, BYN",
                reply_markup=get_main_menu()
            )
            await state.clear()
            return
        
        # Заменяем запятую на точку для float
        amount = float(match.group(1).replace(',', '.'))
        from_currency = match.group(2).upper()
        to_currency = match.group(3).upper()
        
        # Список API (пробуем по порядку)
        apis = [
            # API 1: exchangerate-api.com (главный)
            {
                "url": f"https://api.exchangerate-api.com/v4/latest/{from_currency}",
                "parser": lambda data: data.get('rates', {}).get(to_currency)
            },
            # API 2: fawazahmed0 (резерв 1)
            {
                "url": f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{from_currency.lower()}.json",
                "parser": lambda data: data.get(from_currency.lower(), {}).get(to_currency.lower())
            },
            # API 3: exchangerate.host (резерв 2)
            {
                "url": f"https://api.exchangerate.host/latest?base={from_currency}&symbols={to_currency}",
                "parser": lambda data: data.get('rates', {}).get(to_currency)
            }
        ]
        
        rate = None
        last_error = None
        
        async with aiohttp.ClientSession() as session:
            for api in apis:
                try:
                    async with session.get(api['url'], timeout=aiohttp.ClientTimeout(total=5)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            rate = api['parser'](data)
                            if rate:
                                break
                except Exception as e:
                    last_error = str(e)
                    continue
        
        if not rate:
            raise Exception(f"Не удалось получить курс валют. {last_error or 'Все API недоступны'}")
        
        result = amount * rate
        
        response = f"""
💱 <b>Конвертер валют</b>

<b>{amount:,.2f} {from_currency}</b> = <b>{result:,.2f} {to_currency}</b>

Курс: 1 {from_currency} = {rate:.4f} {to_currency}
"""
        
        await message.answer(response, reply_markup=get_main_menu())
        
    except Exception as e:
        await message.answer(
            f"❌ Ошибка конвертации: {str(e)}\n\n"
            "Проверьте правильность валют и формата.\n"
            "Доступные: USD, EUR, RUB, GBP, JPY, CNY, KZT, UAH, BYN",
            reply_markup=get_main_menu()
        )
    
    finally:
        await state.clear()


# ============= ГЕНЕРАТОР ПАРОЛЕЙ =============

@router.callback_query(F.data == "tool_password")
async def password_tool(callback: CallbackQuery):
    """Password generator tool"""
    import secrets
    import string
    import html
    
    # Генерируем 3 пароля разной сложности
    # Используем безопасные символы без < > & чтобы избежать проблем с HTML
    safe_punctuation = '!@#$%^&*()-_=+[]{}|;:,.'
    
    easy = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    medium = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range(16))
    strong = ''.join(secrets.choice(string.ascii_letters + string.digits + safe_punctuation) for _ in range(20))
    
    # Экранируем HTML специальные символы
    easy = html.escape(easy)
    medium = html.escape(medium)
    strong = html.escape(strong)
    
    response = f"""
🎲 <b>Генератор паролей</b>

<b>Легкий (12 символов):</b>
<code>{easy}</code>

<b>Средний (16 символов):</b>
<code>{medium}</code>

<b>Сильный (20 символов):</b>
<code>{strong}</code>

💡 Нажми на пароль чтобы скопировать
"""
    
    await callback.answer("✅ Пароли сгенерированы!")
    await callback.message.answer(response, reply_markup=get_main_menu())


# ============= WIKIPEDIA =============

@router.callback_query(F.data == "tool_wiki")
async def wiki_tool(callback: CallbackQuery, state: FSMContext):
    """Wikipedia search tool"""
    await state.set_state(ToolStates.waiting_wiki)
    await safe_delete_message(callback.message)
    await callback.message.answer(
        "🔍 <b>Поиск в Wikipedia</b>\n\n"
        "Отправь запрос для поиска:",
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.message(ToolStates.waiting_wiki)
async def search_wiki(message: Message, state: FSMContext):
    """Search Wikipedia"""
    if message.text in ["❌ Отмена", "📥 Скачать видео/музыку", "🛠 Инструменты", 
                        "🎁 Реферальная программа", "📊 Моя статистика", 
                        "🏆 Топ рефералов", "❓ Помощь"]:
        await state.clear()
        if message.text == "❌ Отмена":
            await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    try:
        import wikipedia
        
        # Пытаемся на русском
        wikipedia.set_lang("ru")
        
        try:
            summary = wikipedia.summary(message.text, sentences=5)
            page = wikipedia.page(message.text)
            
            response = f"""
🔍 <b>Wikipedia</b>

<b>{page.title}</b>

{summary}

<a href="{page.url}">Читать полностью</a>
"""
        except:
            # Если не найдено на русском, пробуем на английском
            wikipedia.set_lang("en")
            summary = wikipedia.summary(message.text, sentences=5)
            page = wikipedia.page(message.text)
            
            response = f"""
🔍 <b>Wikipedia</b>

<b>{page.title}</b>

{summary}

<a href="{page.url}">Read more</a>
"""
        
        await message.answer(response, reply_markup=get_main_menu(), disable_web_page_preview=True)
        
    except Exception as e:
        await message.answer(
            f"❌ Ничего не найдено: {message.text}\n\n"
            "Попробуй другой запрос.",
            reply_markup=get_main_menu()
        )
    
    finally:
        await state.clear()


# ============= КАЛЬКУЛЯТОР =============

@router.callback_query(F.data == "tool_calc")
async def calc_tool(callback: CallbackQuery, state: FSMContext):
    """Calculator tool"""
    await state.set_state(ToolStates.waiting_calc)
    await safe_delete_message(callback.message)
    await callback.message.answer(
        "🧮 <b>Мощный калькулятор</b>\n\n"
        "<b>Базовые операции:</b>\n"
        "• <code>3 / 7</code> - деление\n"
        "• <code>2 + 2 * 5</code> - порядок операций\n"
        "• <code>2^3</code> - степень (2³ = 8)\n\n"
        "<b>Функции:</b>\n"
        "• <code>sqrt(16)</code> - корень (√16 = 4)\n"
        "• <code>cosd(90)</code> - косинус 90° = 0\n"
        "• <code>sind(30)</code> - синус 30° = 0.5\n"
        "• <code>log(100)</code> - логарифм\n"
        "• <code>factorial(5)</code> - 5! = 120\n\n"
        "<b>Константы:</b> pi, e",
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.message(ToolStates.waiting_calc)
async def calculate(message: Message, state: FSMContext):
    """Calculate expression"""
    if message.text in ["❌ Отмена", "📥 Скачать видео/музыку", "🛠 Инструменты", 
                        "🎁 Реферальная программа", "📊 Моя статистика", 
                        "🏆 Топ рефералов", "❓ Помощь"]:
        await state.clear()
        if message.text == "❌ Отмена":
            await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    try:
        import math
        import re
        
        # Функции для работы с градусами
        def sind(x):
            """Синус от градусов"""
            return math.sin(math.radians(x))
        
        def cosd(x):
            """Косинус от градусов"""
            return math.cos(math.radians(x))
        
        def tand(x):
            """Тангенс от градусов"""
            return math.tan(math.radians(x))
        
        # Расширенный набор функций
        allowed_names = {
            # Базовые функции
            'abs': abs,
            'round': round,
            'int': int,
            'float': float,
            
            # Математические функции (радианы)
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            
            # Математические функции (градусы)
            'sind': sind,
            'cosd': cosd,
            'tand': tand,
            
            # Корни и степени
            'sqrt': math.sqrt,
            'pow': math.pow,
            'exp': math.exp,
            
            # Логарифмы
            'log': math.log,
            'log10': math.log10,
            'ln': math.log,
            
            # Константы
            'pi': math.pi,
            'e': math.e,
            
            # Округление
            'ceil': math.ceil,
            'floor': math.floor,
            
            # Факториал
            'factorial': math.factorial,
        }
        
        # Сохраняем оригинальное выражение
        original_expr = message.text
        
        # Подготовка выражения
        expr = message.text
        
        # Заменяем различные символы деления на /
        expr = expr.replace('÷', '/')
        expr = expr.replace(':', '/')
        expr = expr.replace('х', '*')
        expr = expr.replace('Х', '*')
        expr = expr.replace('×', '*')
        expr = expr.replace(',', '.')
        
        # Добавляем поддержку степеней через ^
        expr = expr.replace('^', '**')
        
        # Безопасная очистка (разрешаем больше символов)
        # Разрешены: цифры, операторы, скобки, точка, пробелы, буквы для функций
        expr = re.sub(r'[^\w0-9+\-*/().\s]', '', expr)
        
        # Вычисляем
        result = eval(expr, {"__builtins__": {}}, allowed_names)
        
        # Форматируем результат
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                result = round(result, 10)  # Округляем до 10 знаков
        
        response = f"""
🧮 <b>Калькулятор</b>

<b>Выражение:</b> <code>{original_expr}</code>

<b>Результат:</b> <code>{result}</code>
"""
        
        await message.answer(response, reply_markup=get_main_menu())
        
    except ZeroDivisionError:
        await message.answer(
            f"❌ Ошибка: деление на ноль!\n\n"
            "Нельзя делить на 0.",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        await message.answer(
            f"❌ Ошибка вычисления!\n\n"
            "Проверь правильность выражения.\n\n"
            "Примеры:\n"
            "• 3 / 7 (деление)\n"
            "• cosd(90) (косинус 90°)\n"
            "• sqrt(16) (корень)\n"
            "• 2^3 (степень)",
            reply_markup=get_main_menu()
        )
    
    finally:
        await state.clear()


# ============= СЖАТИЕ ИЗОБРАЖЕНИЙ =============

@router.callback_query(F.data == "tool_compress")
async def compress_tool(callback: CallbackQuery, state: FSMContext):
    """Image compression tool"""
    await state.set_state(ToolStates.waiting_compress)
    await safe_delete_message(callback.message)
    await callback.message.answer(
        "📸 <b>Сжатие изображений</b>\n\n"
        "Отправь фото для сжатия:",
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.message(ToolStates.waiting_compress, F.photo)
async def compress_image(message: Message, state: FSMContext):
    """Compress image"""
    try:
        from PIL import Image
        import io
        
        # Получаем фото
        photo = message.photo[-1]
        file = await message.bot.download(photo.file_id)
        
        # Открываем изображение
        img = Image.open(file)
        
        # Сжимаем
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=50, optimize=True)
        output.seek(0)
        
        # Размеры
        original_size = photo.file_size / 1024  # KB
        compressed_size = len(output.getvalue()) / 1024  # KB
        saved = ((original_size - compressed_size) / original_size) * 100
        
        # Отправляем
        from aiogram.types import BufferedInputFile
        compressed_file = BufferedInputFile(output.getvalue(), filename="compressed.jpg")
        
        await message.answer_photo(
            photo=compressed_file,
            caption=f"📸 <b>Изображение сжато!</b>\n\n"
                   f"Было: {original_size:.1f} KB\n"
                   f"Стало: {compressed_size:.1f} KB\n"
                   f"Сэкономлено: {saved:.1f}%",
            reply_markup=get_main_menu()
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Ошибка сжатия: {str(e)}",
            reply_markup=get_main_menu()
        )
    
    finally:
        await state.clear()


@router.message(ToolStates.waiting_compress)
async def compress_wrong_type(message: Message, state: FSMContext):
    """Handle wrong type for compression"""
    if message.text in ["❌ Отмена", "📥 Скачать видео/музыку", "🛠 Инструменты", 
                        "🎁 Реферальная программа", "📊 Моя статистика", 
                        "🏆 Топ рефералов", "❓ Помощь"]:
        await state.clear()
        if message.text == "❌ Отмена":
            await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    await message.answer(
        "❌ Отправь фото для сжатия!",
        reply_markup=get_main_menu()
    )


# ============= ПОГОДА =============

@router.callback_query(F.data == "tool_weather")
async def weather_tool(callback: CallbackQuery, state: FSMContext):
    """Weather tool"""
    await state.set_state(ToolStates.waiting_weather)
    await safe_delete_message(callback.message)
    await callback.message.answer(
        "🌤 <b>Погода</b>\n\n"
        "Отправь название города на русском или английском:\n"
        "<code>Москва</code>\n"
        "<code>London</code>\n"
        "<code>New York</code>",
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.message(ToolStates.waiting_weather)
async def get_weather(message: Message, state: FSMContext):
    """Get weather for city"""
    if message.text in ["❌ Отмена", "📥 Скачать видео/музыку", "🛠 Инструменты", 
                        "🎁 Реферальная программа", "📊 Моя статистика", 
                        "🏆 Топ рефералов", "❓ Помощь"]:
        await state.clear()
        if message.text == "❌ Отмена":
            await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    try:
        import aiohttp
        
        city = message.text.strip()
        
        # Используем OpenWeatherMap API (бесплатный, без ключа через wttr.in)
        async with aiohttp.ClientSession() as session:
            url = f"https://wttr.in/{city}?format=j1&lang=ru"
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception("Город не найден")
                data = await resp.json()
        
        current = data['current_condition'][0]
        
        # Погодные условия на русском
        weather_desc = current['lang_ru'][0]['value'] if 'lang_ru' in current else current['weatherDesc'][0]['value']
        temp = current['temp_C']
        feels_like = current['FeelsLikeC']
        humidity = current['humidity']
        wind_speed = current['windspeedKmph']
        pressure = current['pressure']
        
        # Эмодзи для погоды
        weather_emoji = "☀️"
        if "облач" in weather_desc.lower() or "cloud" in weather_desc.lower():
            weather_emoji = "☁️"
        elif "дожд" in weather_desc.lower() or "rain" in weather_desc.lower():
            weather_emoji = "🌧"
        elif "снег" in weather_desc.lower() or "snow" in weather_desc.lower():
            weather_emoji = "❄️"
        elif "гроз" in weather_desc.lower() or "storm" in weather_desc.lower():
            weather_emoji = "⛈"
        elif "туман" in weather_desc.lower() or "fog" in weather_desc.lower():
            weather_emoji = "🌫"
        
        response = f"""
🌤 <b>Погода в {city.title()}</b>

{weather_emoji} <b>{weather_desc}</b>

🌡 Температура: <b>{temp}°C</b>
🤚 Ощущается как: <b>{feels_like}°C</b>
💧 Влажность: <b>{humidity}%</b>
💨 Ветер: <b>{wind_speed} км/ч</b>
🔽 Давление: <b>{pressure} мб</b>
"""
        
        await message.answer(response, reply_markup=get_main_menu())
        
    except Exception as e:
        await message.answer(
            f"❌ Не удалось получить погоду для: {message.text}\n\n"
            "Попробуй другое название города.\n"
            "Примеры: Москва, London, Paris, Tokyo",
            reply_markup=get_main_menu()
        )
    
    finally:
        await state.clear()

