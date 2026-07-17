import os
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from .state import pogodai, fakti, escursi, cursi
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
import aiohttp
import json

load_dotenv()
API_WEATHER = os.getenv("api_weather") 
router = Router()


async def wikipedia_search(query: str, limit: int = 3) -> str:
    """Поиск фактов через Wikipedia API"""
    url = "https://ru.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "utf8": 1
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return "Ошибка получения данных"
            data = await resp.json()
            results = data.get("query", {}).get("search", [])
            if not results:
                return "Ничего не найдено."
            
            facts = []
            for r in results:
                title = r['title']
                snippet = r['snippet'].replace('<span class="searchmatch">', '').replace('</span>', '')
                facts.append(f"{title}: {snippet[:200]}...")
            
            return "Результаты поиска: " + " ".join(facts[:limit])

async def get_weather(city: str, period: str) -> str:
    """Получение погоды через OpenWeatherMap"""
    if not API_WEATHER:
        return "Ошибка: не указан API ключ для погоды"
    
    days = 1
    if "3" in period or "три" in period:
        days = 3
    elif "5" in period or "пять" in period:
        days = 5
    elif "7" in period or "семь" in period or "недел" in period:
        days = 7
    
    if days == 1:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": API_WEATHER,
            "lang": "ru",
            "units": "metric"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    return f"Город '{city}' не найден"
                data = await resp.json()
                temp = data['main']['temp']
                feels = data['main']['feels_like']
                desc = data['weather'][0]['description']
                humidity = data['main']['humidity']
                wind = data['wind']['speed']
                return (
                    f" Погода в {city}:
"
                    f" Температура: {temp}°C (ощущается {feels}°C)
"
                    f"{desc.capitalize()}
"
                    f"Влажность: {humidity}%
"
                    f" Ветер: {wind} м/с"
                )
    else:
        # Прогноз на несколько дней
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": city,
            "appid": API_WEATHER,
            "lang": "ru",
            "units": "metric",
            "cnt": days * 8  # каждые 3 часа
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    return f"Город '{city}' не найден"
                data = await resp.json()
                
                # Группируем по дням
                daily = {}
                for item in data['list']:
                    date = item['dt_txt'][:10]
                    if date not in daily:
                        daily[date] = []
                    daily[date].append(item)
                
                result = [f"🌤 Прогноз погоды в {city} на {days} дн.:"]
                for date, items in list(daily.items())[:days]:
                    temps = [i['main']['temp'] for i in items]
                    descs = [i['weather'][0]['description'] for i in items]
                    avg_temp = sum(temps) / len(temps)
                    main_desc = max(set(descs), key=descs.count)
                    result.append(f"
{date}: {avg_temp:.1f}°C, {main_desc}")
                
                return " ".join(result)

async def get_currency(amount: float, from_cur: str, to_cur: str) -> str:
    """Конвертация валют через ExchangeRate-API"""
    url = f"https://api.exchangerate-api.com/v4/latest/{from_cur.upper()}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return "Ошибка получения курса валют"
            data = await resp.json()
            if to_cur.upper() not in data['rates']:
                return f"Валюта '{to_cur}' не найдена"
            rate = data['rates'][to_cur.upper()]
            result = amount * rate
            return (
                f"💱 Конвертация валют:
"
                f"{amount} {from_cur.upper()} = {result:.2f} {to_cur.upper()}
"
                f"Курс: 1 {from_cur.upper()} = {rate:.4f} {to_cur.upper()}"
            )

@router.message(CommandStart)
async def start(message: Message):
    await message.answer("Это бот для информации о разных странах")
    await message.answer("Команды:
 /pogoda - погода
 /fakt - факты
 /escurs - экскурсии
 /curs - курс валют")

@router.message(Command("pogoda"))
async def cmd_pogoda(message: Message, state: FSMContext):
    await message.answer("Введите город/страну, в которой хотите узнать погоду")
    await state.set_state(pogodai.strana)

@router.message(pogodai.strana)
async def process_pogoda_strana(message: Message, state: FSMContext):
    await state.update_data({"strana": message.text})
    await message.answer("Введите срок (сегодня, завтра, 3 дня, 5 дней, 7 дней)")
    await state.set_state(pogodai.srok)

@router.message(pogodai.srok)
async def process_pogoda_srok(message: Message, state: FSMContext):
    await state.update_data({"srok": message.text})
    data = await state.get_data()
    strana = data.get('strana')
    srok = data.get('srok')
    await message.answer(f"🔍 Ищу погоду в {strana} на {srok}...")
    result = await get_weather(strana, srok)
    await message.answer(result)
    await state.clear()

@router.message(Command("fakt"))
async def cmd_fakt(message: Message, state: FSMContext):
    await message.answer("Введите страну, про которую хотите узнать факты")
    await state.set_state(fakti.strana)

@router.message(fakti.strana)
async def process_fakt_strana(message: Message, state: FSMContext):
    await state.update_data({"strana": message.text})
    await message.answer("Введите количество фактов (1-5)")
    await state.set_state(fakti.col)

@router.message(fakti.col)
async def process_fakt_col(message: Message, state: FSMContext):
    await state.update_data({"col": message.text})
    data = await state.get_data()
    strana = data.get('strana')
    try:
        col = min(int(data.get('col', 3)), 5)
    except:
        col = 3
    await message.answer(f"🔍 Ищу факты о {strana}...")
    result = await wikipedia_search(f"интересные факты о {strana}", col)
    await message.answer(result)
    await state.clear()

# === ЭКСКУРСИИ ===
@router.message(Command("escurs"))
async def cmd_escurs(message: Message, state: FSMContext):
    await message.answer("Введите страну/город для поиска экскурсий")
    await state.set_state(escursi.strana)

@router.message(escursi.strana)
async def process_escurs_strana(message: Message, state: FSMContext):
    await state.update_data({"strana": message.text})
    await message.answer("Введите количество экскурсий (1-5)")
    await state.set_state(escursi.col)

@router.message(escursi.col)
async def process_escurs_col(message: Message, state: FSMContext):
    await state.update_data({"col": message.text})
    data = await state.get_data()
    strana = data.get('strana')
    try:
        col = min(int(data.get('col', 3)), 5)
    except:
        col = 3
    await message.answer(f"🔍 Ищу экскурсии в {strana}...")
    result = await wikipedia_search(f"экскурсии в {strana} достопримечательности", col)
    await message.answer(result)
    await state.clear()

# === КУРС ВАЛЮТ ===
@router.message(Command("curs"))
async def cmd_curs(message: Message, state: FSMContext):
    await message.answer("Введите валюту, в которую конвертируем (например: USD, EUR, RUB)")
    await state.set_state(cursi.vala)

@router.message(cursi.vala)
async def process_curs_vala(message: Message, state: FSMContext):
    await state.update_data({"vala": message.text.upper()})
    await message.answer("Введите валюту, из которой конвертируем (например: USD, EUR, RUB)")
    await state.set_state(cursi.valb)

@router.message(cursi.valb)
async def process_curs_valb(message: Message, state: FSMContext):
    await state.update_data({"valb": message.text.upper()})
    await message.answer("Введите сумму для конвертации")
    await state.set_state(cursi.col)

@router.message(cursi.col)
async def process_curs_col(message: Message, state: FSMContext):
    await state.update_data({"col": message.text})
    data = await state.get_data()
    vala = data.get('vala')
    valb = data.get('valb')
    try:
        amount = float(data.get('col', 1))
    except:
        amount = 1
    await message.answer(f"🔍 Конвертирую {amount} {valb} в {vala}...")
    result = await get_currency(amount, valb, vala)
    await message.answer(result)
    await state.clear()
