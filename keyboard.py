from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton


def create_keyboard(keyboard_data, back_button=False):

    keyboard = InlineKeyboardMarkup()

    for btn in keyboard_data:

        new_btn = InlineKeyboardButton(btn, callback_data=keyboard_data[btn])
        keyboard.add(new_btn)
    
    if back_button:
        keyboard.add(InlineKeyboardButton('Назад', callback_data='start'))

    return keyboard