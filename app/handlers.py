from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, URLInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
import os
from dotenv import load_dotenv
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import app.keyboards as kb
from app.states import Registration, ChangeCity
from app.request import *
from app.funcs import *

router = Router()
load_dotenv()
scheduler = AsyncIOScheduler()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, msg_to_del: dict):
    
    if check_user_in_db(message.from_user.id):
        user = get_user_name(message.from_user.id)
        await message.answer(f'''Добро пожаловать, {user}''', reply_markup=kb.main_inline_kb)
        await message.delete()
        msg_to_del[message.chat.id].clear()
    else:
        msg_to_del[message.chat.id] = []
        await state.set_state(Registration.name)
        msg = await message.answer(f'''Привет {message.from_user.username}!
                            Как к тебе можно обращаться?''')
        msg_to_del[message.chat.id].append(msg.message_id)
        print(msg_to_del)
        await message.delete()
    
    
@router.message(Registration.name)
async def process_name(message: Message, state: FSMContext, msg_to_del: dict):
    
    await state.update_data(name=message.text)
    await state.set_state(Registration.loc)
    msg = await message.answer('''Нажми на кнопку ниже для отправки мне твоего города проживания.
                         
Он понадобится только для определения погоды и новостей''', reply_markup=kb.start_location_kb)
    msg_to_del[message.chat.id].append(msg.message_id)
    msg_to_del[message.chat.id].append(message.message_id)
    print(msg_to_del)
    
    
@router.message(Registration.loc)
async def process_city(message: Message, state: FSMContext, msg_to_del: dict):
    print(message.content_type)
    if message.content_type == 'location':
        loc = f'{message.location.latitude},{message.location.longitude}'
        await state.update_data(loc=loc)
        await state.set_state(Registration.time)
        msg = await message.answer(f'''Теперь отправь время, когда ты хочешь получать ежедневный прогноз погоды
Формат: (ЧАС:МИНУТЫ)''', reply_markup=ReplyKeyboardRemove())
    else:
        msg = await message.answer(text='''Что-то пошло не так, попробуй еще раз''', reply_markup=kb.start_location_kb)
    msg_to_del[message.chat.id].append(msg.message_id)
    msg_to_del[message.chat.id].append(message.message_id)
    print(msg_to_del)
        

@router.message(Registration.time)
async def process_time(message: Message, state: FSMContext, msg_to_del: dict):
    await state.update_data(time=message.text)
    data = await state.get_data()
    write_to_users(message.from_user.id, data)
    await message.answer('''Отлично! Теперь я буду каждый день в указанное время отправлять тебе прогноз погоды.''', reply_markup=kb.return_kb)
    scheduler.add_job(scheduled, id=str(message.from_user.id),
                      args=(message.bot, message.chat.id), trigger='cron',
                      hour=data['time'].split(':')[0], minute=data['time'].split(':')[1],
                      start_date=datetime.now(), end_date=None)
    scheduler.start() if not scheduler.running else None
    await message.bot.delete_messages(chat_id=message.chat.id, message_ids=msg_to_del[message.chat.id] + [message.message_id])
    msg_to_del[message.chat.id] = []
    await state.clear()
    
    
@router.callback_query(F.data == 'weather_now')
async def weather_now(call: CallbackQuery):
    user_loc = get_user_lat_long(call.from_user.id)
    data = get_weather_now(user_loc[0], user_loc[1])
    if not data:
        await call.message.edit_text('Не удалось получить данные о погоде, проверь правильность города и повтори попытку', reply_markup=kb.return_kb)
    else:
        await call.message.edit_text(f'В городе {get_city_by_lat_long(*user_loc)} сейчас {data}', reply_markup=kb.return_kb)
        
        
async def scheduled(bot: Bot, chat_id: int):
    weather = get_weather_for_day(*get_user_lat_long(os.getenv('ADMIN_ID')))
    text = f'''Прогноз погоды на сегодня:

Средняя температура: {weather['avgtemp_c']}
Максимальная температура: {weather['maxtemp_c']}
Скорость ветра: {weather['maxwind_kph']}
Влажность: {weather['avghumidity']}
'''
    if 'daily_chance_of_rain' in weather.keys():
        text += f'\nВероятность дождя: {weather["daily_chance_of_rain"]}'
    if 'daily_chance_of_snow' in weather.keys():
        text += f'\nВероятность снегопада: {weather["daily_chance_of_snow"]}'

    audio_raw = get_song_of_a_day()
    audio = URLInputFile(audio_raw.url)
    
    await bot.send_audio(chat_id=chat_id, audio=audio, title=audio_raw.title, performer=audio_raw.artist, caption=text, reply_markup=kb.return_kb)
        
        
# TODO Добавить в настройки смену имени и времени
# TODO Добавить кнопку для вывода прогноза на день (макс и мин температуры, облачность, ветер, осадки)
# TODO Доделать рассылку (закончил на реквесте погоды)
@router.callback_query(F.data == 'return')
async def main_menu(call: CallbackQuery, msg_to_del: dict):
    if msg_to_del[call.message.chat.id] and msg_to_del[call.message.chat.id] != [call.message.message_id]:
        await call.message.bot.delete_messages(chat_id=call.message.chat.id, message_ids=msg_to_del[call.message.chat.id])
        msg_to_del[call.message.chat.id].clear()
        
    user_loc = get_user_lat_long(call.from_user.id)
    await call.message.edit_text(f'''Добро пожаловать, {get_user_name(call.from_user.id)}
                                 
Ваш город: {get_city_by_lat_long(*user_loc)}, {get_region_by_lat_long(*user_loc)}
Сейчас температура {get_weather_now(*user_loc)}''', reply_markup=kb.main_inline_kb) 

    
@router.callback_query(F.data == 'settings')
async def settings(call: CallbackQuery, msg_to_del: dict):
    msg = await call.message.edit_text(f'''Настройки
Ваш город: {get_city_by_lat_long(*get_user_lat_long(call.from_user.id))}, {get_region_by_lat_long(*get_user_lat_long(call.from_user.id))}
Время ежедневной рассылки погоды: {get_user_time(call.from_user.id)}''', reply_markup=kb.settings_kb)
    if call.message.chat.id in msg_to_del:
        msg_to_del[call.message.chat.id].append(msg.message_id)
    else:
        msg_to_del[call.message.chat.id] = [msg.message_id]
    
    
@router.callback_query(F.data == 'change_place')
async def change_place(call: CallbackQuery, state: FSMContext, msg_to_del: dict):
    
    await state.set_state(ChangeCity.loc)
    msg = await call.message.answer(f'''Чтобы поменять город, отправь мне твой город проживания. Повторно нажми на кнопку для отправки местоположения''', reply_markup=kb.start_location_kb)
    msg_to_del[call.message.chat.id].append(call.message.message_id)
    msg_to_del[call.message.chat.id].append(msg.message_id)
    
    
@router.message(ChangeCity.loc)
async def change_city(message: Message, state: FSMContext, msg_to_del: dict):
    if message.content_type == 'location':
        loc = f'{message.location.latitude},{message.location.longitude}'
        await state.update_data(loc=loc)
        data = await state.get_data()
        update_user_loc(message.from_user.id, data['loc'])
        msg = await message.answer(f'''Город успешно изменен на ''', reply_markup=kb.return_kb)
        await state.clear()
        msg_to_del[message.chat.id].append(message.message_id)
    else:
        await message.delete()
        msg = await message.answer('''Что-то пошло не так, попробуй еще раз''', reply_markup=kb.start_location_kb)
        msg_to_del[message.chat.id].append(message.message_id)
        msg_to_del[message.chat.id].append(msg.message_id)
    
    
@router.callback_query(F.data == 'change_time')
async def change_time(call: CallbackQuery):
    await call.message.edit_text('''Отправь время, когда ты хочешь получать ежедневный прогноз погоды
Формат: (ЧАС:МИНУТЫ)''', reply_markup=ReplyKeyboardRemove())

    
@router.message(Command('admin'))
async def admin_panel(message: Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.reply('''
Добро пожаловать в админ панель!
Выбери действие из списка ниже
''', reply_markup=kb.admin_kb)
    else:
        await message.reply('''Вы не являетесь администратором!''')


@router.callback_query(F.data == 'send_song_of_a_day')
async def send_song_of_a_day(call: CallbackQuery):
    audio_raw = get_song_of_a_day()
    audio = URLInputFile(audio_raw.url)
    await call.message.answer_audio(audio=audio, title=audio_raw.title, performer=audio_raw.artist)
    
    
@router.callback_query(F.data == 'forecast')
async def forecast(call: CallbackQuery):
    
    weather = get_weather_for_day(*get_user_lat_long(os.getenv('ADMIN_ID')))
    text = f'''Прогноз погоды на сегодня:

Средняя температура: {weather['avgtemp_c']}
Максимальная температура: {weather['maxtemp_c']}
Скорость ветра: {weather['maxwind_kph']}
Влажность: {weather['avghumidity']}
'''
    if 'daily_chance_of_rain' in weather.keys():
        text += f'\nВероятность дождя: {weather["daily_chance_of_rain"]}'
    if 'daily_chance_of_snow' in weather.keys():
        text += f'\nВероятность снегопада: {weather["daily_chance_of_snow"]}'

    audio_raw = get_song_of_a_day()
    audio = URLInputFile(audio_raw.url)
    
    await call.message.answer_audio(audio=audio, title=audio_raw.title, performer=audio_raw.artist, caption=text, reply_markup=kb.return_kb)
    
    
async def test():
    print(True)
    
    
@router.callback_query(F.data == 'schedule_messages')
async def schedule_message(call: CallbackQuery):
    for i in get_all_ids():
        i = str(i)
        if i not in [x.id for x in scheduler.get_jobs()]:
            scheduler.add_job(scheduled, id=i,
                              trigger='cron', args=[call.bot, i],
                              hour=int(get_user_time(i).split(':')[0]),
                              minute=int(get_user_time(i).split(':')[1]))
    scheduler.start() if not scheduler.running else None
    
    
@router.callback_query(F.data == 'get_scheduler_list')
async def get_scheduler_list(call: CallbackQuery):
    jobs = scheduler.get_jobs()
    for i in jobs:
        print(i.id, i.next_run_time)
    
    
@router.message()
async def no_message(message: Message):
    await message.reply(f'''Я пока не знаю это сообщение(''')
