from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


start_location_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отправить местоположение', request_location=True)]
], resize_keyboard=True, one_time_keyboard=True)

main_inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Настройки', callback_data='settings')]
])

settings_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить местоположение', callback_data='change_place')],
    [InlineKeyboardButton(text='Изменить время ежедневной рассылки', callback_data='change_time')],
    [InlineKeyboardButton(text='На главную', callback_data='return')]
])

return_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='На главную', callback_data='return')]
])

admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отправить песню дня', callback_data='send_song_of_a_day')],
    [InlineKeyboardButton(text='Прогноз погоды', callback_data='forecast')],
    [InlineKeyboardButton(text='Запланировать сообщения всем пользователям', callback_data='schedule_messages')],
    [InlineKeyboardButton(text='Получить список scheduler', callback_data='get_scheduler_list')],
])