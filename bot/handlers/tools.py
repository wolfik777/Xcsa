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


@router.callback_query(F.data == "tool_converter")
async def converter_tool(callback: CallbackQuery):
    """File converter tool"""
    await callback.answer("Эта функция в разработке! 🔧")
    await callback.message.answer(
        "📝 <b>Конвертер файлов</b>\n\n"
        "Эта функция в разработке.\n"
        "Скоро добавим конвертацию PDF, Word, изображений и других форматов!"
    )


@router.callback_query(F.data == "tool_image")
async def image_tool(callback: CallbackQuery):
    """Image processing tool"""
    await callback.answer("Эта функция в разработке! 🔧")
    await callback.message.answer(
        "🎨 <b>Обработка изображений</b>\n\n"
        "Эта функция в разработке.\n"
        "Скоро добавим сжатие, изменение размера и другие функции!"
    )


@router.callback_query(F.data == "tool_currency")
async def currency_tool(callback: CallbackQuery):
    """Currency converter tool"""
    await callback.answer("Эта функция в разработке! 🔧")
    await callback.message.answer(
        "💱 <b>Конвертер валют</b>\n\n"
        "Эта функция в разработке.\n"
        "Скоро добавим конвертацию валют с актуальными курсами!"
    )


@router.callback_query(F.data == "tool_weather")
async def weather_tool(callback: CallbackQuery):
    """Weather tool"""
    await callback.answer("Эта функция в разработке! 🔧")
    await callback.message.answer(
        "🌤 <b>Погода</b>\n\n"
        "Эта функция в разработке.\n"
        "Скоро добавим прогноз погоды для вашего города!"
    )

