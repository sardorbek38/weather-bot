import asyncio
import requests
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ========= SOZLAMALAR =========
BOT_TOKEN = "TOKENINGIZNI_BU_YERGA_QOYING"
WEATHER_API_KEY = "API_KEYINGIZNI_BU_YERGA_QOYING"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========= EMOJI =========
weather_emoji = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Haze": "🌫️"
}

# ========= KLAVIATURA =========
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌍 Shahar kiriting")],
        [KeyboardButton(text="📍 Mening joylashuvim", request_location=True)],
        [KeyboardButton(text="⭐ Mashhur shaharlar")],
        [KeyboardButton(text="ℹ️ Yordam")]
    ],
    resize_keyboard=True
)

cities_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Toshkent"), KeyboardButton(text="Samarqand")],
        [KeyboardButton(text="Andijon"), KeyboardButton(text="Namangan")],
        [KeyboardButton(text="Farg'ona"), KeyboardButton(text="Buxoro")],
        [KeyboardButton(text="Jizzax"), KeyboardButton(text="Qarshi")],
        [KeyboardButton(text="🔙 Orqaga")]
    ],
    resize_keyboard=True
)

# ========= OB-HAVO OLISH =========
def get_weather(city=None, lat=None, lon=None):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "uz"
    }

    if city:
        params["q"] = city
    else:
        params["lat"] = lat
        params["lon"] = lon

    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print("XATO:", e)

    return None

# ========= PROGNOZ =========
def get_forecast(city):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "uz"
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass

    return None

# ========= FORMAT =========
def format_weather(data):
    if not data:
        return "❌ Ob-havo ma'lumoti topilmadi"

    city = data.get("name", "Noma'lum")
    country = data.get("sys", {}).get("country", "")
    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    hum = data["main"]["humidity"]
    pres = data["main"]["pressure"]
    wind = data["wind"]["speed"]

    desc = data["weather"][0]["description"]
    main = data["weather"][0]["main"]
    emoji = weather_emoji.get(main, "🌈")

    sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M")
    sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")

    return (
        f"{emoji} {city}, {country}\n\n"
        f"🌡️ Harorat: {temp:.1f}°C\n"
        f"🤔 His qilinadi: {feels:.1f}°C\n"
        f"📝 Holat: {desc}\n\n"
        f"💧 Namlik: {hum}%\n"
        f"🌪️ Shamol: {wind} m/s\n"
        f"🔽 Bosim: {pres} hPa\n\n"
        f"🌅 Quyosh chiqishi: {sunrise}\n"
        f"🌇 Quyosh botishi: {sunset}"
    )

# ========= START =========
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "🌤️ OB-HAVO BOT\n\nShahar nomini yozing yoki joylashuvingizni yuboring 👇",
        reply_markup=main_keyboard
    )

# ========= YORDAM =========
@dp.message(F.text == "ℹ️ Yordam")
async def help_cmd(message: types.Message):
    await message.answer(
        "📌 FOYDALANISH:\n"
        "• Shahar yozing\n"
        "• Joylashuv yuboring\n"
        "• Mashhur shaharlarni tanlang",
        reply_markup=main_keyboard
    )

# ========= MASHHUR SHAHARLAR =========
@dp.message(F.text == "⭐ Mashhur shaharlar")
async def cities(message: types.Message):
    await message.answer("Shaharni tanlang:", reply_markup=cities_keyboard)

# ========= ORQAGA =========
@dp.message(F.text == "🔙 Orqaga")
async def back(message: types.Message):
    await message.answer("Bosh menyu", reply_markup=main_keyboard)

# ========= PROGNOZ (YUQORIGA KO‘CHIRILDI) =========
@dp.message(F.text.startswith("/forecast"))
async def forecast(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Masalan: /forecast Toshkent")
        return

    city = parts[1]
    loading = await message.answer("⏳ Prognoz yuklanmoqda...")
    data = get_forecast(city)
    await loading.delete()

    if not data:
        await message.answer("❌ Prognoz topilmadi")
        return

    text = f"📊 {city.upper()} - 5 KUNLIK PROGNOZ\n\n"

    for item in data["list"][::8][:5]:
        date = datetime.fromtimestamp(item["dt"]).strftime("%d.%m")
        temp = item["main"]["temp"]
        desc = item["weather"][0]["description"]
        emoji = weather_emoji.get(item["weather"][0]["main"], "🌈")
        text += f"{emoji} {date}: {temp:.1f}°C, {desc}\n"

    await message.answer(text)

# ========= JOYLASHUV =========
@dp.message(F.location)
async def location_weather(message: types.Message):
    loading = await message.answer("⏳ Yuklanmoqda...")
    data = get_weather(
        lat=message.location.latitude,
        lon=message.location.longitude
    )
    await loading.delete()
    await message.answer(format_weather(data))

# ========= SHAHAR =========
@dp.message(F.text)
async def city_weather(message: types.Message):
    city = message.text

    if city in [
        "🌍 Shahar kiriting",
        "📍 Mening joylashuvim",
        "⭐ Mashhur shaharlar",
        "ℹ️ Yordam"
    ]:
        return

    loading = await message.answer("⏳ Ob-havo olinmoqda...")
    data = get_weather(city=city)
    await loading.delete()

    if data:
        await message.answer(format_weather(data))
        await message.answer(f"📊 Prognoz uchun yozing:\n/forecast {city}")
    else:
        await message.answer("❌ Shahar topilmadi")

# ========= ISHGA TUSHIRISH =========
async def main():
    print("🌤️ Bot ishga tushdi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())