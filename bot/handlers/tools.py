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


class ToolStates(StatesGroup):
    """Tool states"""
    waiting_qr_text = State()
    waiting_translate_text = State()
    waiting_short_url = State()
    waiting_currency = State()
    waiting_wiki = State()
    waiting_calc = State()
    waiting_compress = State()


@router.callback_query(F.data == "tool_qr")
async def qr_tool(callback: CallbackQuery, state: FSMContext):
    """QR code generator"""
    await state.set_state(ToolStates.waiting_qr_text)
    await callback.message.delete()
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
    await state.set_state(ToolStates.waiting_translate_text)
    await callback.message.delete()
    await callback.message.answer(
        "🌐 <b>Переводчик</b>\n\n"
        "Отправь текст для перевода.\n"
        "Язык будет определен автоматически, перевод на русский или английский.",
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
        # Detect language
        detected_lang = detect(message.text)
        
        # Choose target language
        target_lang = "ru" if detected_lang != "ru" else "en"
        
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
    await callback.message.delete()
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
    await callback.message.delete()
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
    """Convert currency"""
    if message.text in ["❌ Отмена", "📥 Скачать видео/музыку", "🛠 Инструменты", 
                        "🎁 Реферальная программа", "📊 Моя статистика", 
                        "🏆 Топ рефералов", "❓ Помощь"]:
        await state.clear()
        if message.text == "❌ Отмена":
            await message.answer("❌ Отменено", reply_markup=get_main_menu())
        return
    
    try:
        import re
        from forex_python.converter import CurrencyRates
        
        c = CurrencyRates()
        
        # Парсим запрос: "100 USD в RUB" или "100 USD to RUB"
        pattern = r'(\d+(?:\.\d+)?)\s*([A-Z]{3})\s*(?:в|to|in)\s*([A-Z]{3})'
        match = re.search(pattern, message.text.upper())
        
        if not match:
            await message.answer(
                "❌ Неверный формат!\n\n"
                "Используй: <code>100 USD в RUB</code>",
                reply_markup=get_main_menu()
            )
            await state.clear()
            return
        
        amount = float(match.group(1))
        from_currency = match.group(2)
        to_currency = match.group(3)
        
        # Конвертируем
        result = c.convert(from_currency, to_currency, amount)
        rate = c.get_rate(from_currency, to_currency)
        
        response = f"""
💱 <b>Конвертер валют</b>

<b>{amount:,.2f} {from_currency}</b> = <b>{result:,.2f} {to_currency}</b>

Курс: 1 {from_currency} = {rate:.4f} {to_currency}
"""
        
        await message.answer(response, reply_markup=get_main_menu())
        
    except Exception as e:
        await message.answer(
            f"❌ Ошибка конвертации: {str(e)}\n\n"
            "Проверьте правильность валют и формата.",
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
    
    # Генерируем 3 пароля разной сложности
    easy = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    medium = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%') for _ in range(16))
    strong = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(20))
    
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
    await callback.message.delete()
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
    await callback.message.delete()
    await callback.message.answer(
        "🧮 <b>Калькулятор</b>\n\n"
        "Отправь математическое выражение:\n"
        "<code>2 + 2</code>\n"
        "<code>100 * 3.5</code>\n"
        "<code>sqrt(144)</code>\n"
        "<code>pi * 10</code>",
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
        
        # Безопасное вычисление
        allowed_names = {
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'pi': math.pi,
            'e': math.e,
            'log': math.log,
            'pow': math.pow,
        }
        
        # Заменяем русские буквы на английские операторы
        expr = message.text.replace('х', '*').replace('Х', '*')
        expr = re.sub(r'[^0-9+\-*/().\s,sqrtincosgpielw]', '', expr)
        
        # Вычисляем
        result = eval(expr, {"__builtins__": {}}, allowed_names)
        
        response = f"""
🧮 <b>Калькулятор</b>

<b>Выражение:</b> <code>{message.text}</code>

<b>Результат:</b> <code>{result}</code>
"""
        
        await message.answer(response, reply_markup=get_main_menu())
        
    except Exception as e:
        await message.answer(
            f"❌ Ошибка вычисления!\n\n"
            "Проверь правильность выражения.",
            reply_markup=get_main_menu()
        )
    
    finally:
        await state.clear()


# ============= СЖАТИЕ ИЗОБРАЖЕНИЙ =============

@router.callback_query(F.data == "tool_compress")
async def compress_tool(callback: CallbackQuery, state: FSMContext):
    """Image compression tool"""
    await state.set_state(ToolStates.waiting_compress)
    await callback.message.delete()
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

