from config_reader import config
from keyboard import create_keyboard
import database

import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.builtin import IDFilter
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from multiprocessing import Process


from pyrogram import Client, filters

app = Client("client", config.api_id.get_secret_value(), config.api_hash.get_secret_value())



# logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher(bot, storage=MemoryStorage())

official_chat = int(config.official_chat.get_secret_value())


class UserState(StatesGroup):
    title_add = State()
    title_delete = State()



@dp.callback_query_handler(lambda c: c.data == "start")
async def start_func(message: types.Message):    

    await message.message.edit_text("Привет, я - бот канала Imperial Sky для рассылки!",
                        reply_markup=create_keyboard({'Добавить новый тайтл':'add_title', 'Просмотр активных тайтлов':'active_titles'}))


@dp.message_handler(commands=['start'])
async def start_func(message: types.Message):

    database.create_user(message.from_user.id)

    await message.answer("Привет, я - бот канала Imperial Sky для рассылки!",
                        reply_markup=create_keyboard({'Добавить новый тайтл':'add_title', 'Просмотр активных тайтлов':'active_titles'}))


@dp.callback_query_handler(lambda c: c.data == "delete_title")
async def process_callback_delete_titles(callback_query: types.CallbackQuery):

    active_user_titles = database.get_user(callback_query["from"].id)["active_titles"]

    result_titles = ""
    
    for idx, title in enumerate(active_user_titles):
        result_titles += f"{idx+1}. {title}\n"


    if active_user_titles == []:
        result_titles = "Нет тайтлов!"

    
    await callback_query.message.edit_text('Введите тайтл, который нужно удалить:\n\n' + result_titles)

    await UserState.title_delete.set()


@dp.message_handler(state=UserState.title_delete)
async def title_delete(message: types.Message, state: FSMContext):

    await state.update_data(title_delete=message.text)
    
    finish_data = await state.get_data()

    database.delete_user_title(message.from_user.id, finish_data['title_delete'])

    print('[+] Title deleted')

    await message.answer(f"Тайтл {str(finish_data['title_delete'])} успешно удален!",
    reply_markup=create_keyboard({}, back_button=True))

    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "active_titles")
async def process_callback_edit_titles(callback_query: types.CallbackQuery):

    active_user_titles = database.get_user(callback_query["from"].id)["active_titles"]

    result_titles = "\n".join(active_user_titles)

    keyboard = create_keyboard({}, back_button=True)

    if active_user_titles == []:
        result_titles = "Нет тайтлов!\nНазад: /start"


        keyboard = create_keyboard({'Удалить тайтл':'delete_title'}, back_button=True)




    
    await callback_query.message.edit_text('Ваши активные тайтлы:\n\n' + result_titles,                           
                                            reply_markup=keyboard)



@dp.callback_query_handler(lambda c: c.data == "add_title")
async def process_callback_add_title_cat(callback_query: types.CallbackQuery):

    await callback_query.message.edit_text('Выберите категорию:', 
                        reply_markup=create_keyboard({'Основное':'add_title_1', 'Культивации':'add_title_2', 'Седзе':'add_title_3', 'Лицензии':'add_title_4'}, back_button=True))



@dp.callback_query_handler(lambda c: "add_title_" in c.data)
async def process_callback_add_title(callback_query: types.CallbackQuery):

    with open(f'assets/titles_{callback_query.data[-1]}.txt', 'r') as file:
        
        read_data = file.readlines()

        read_data_num = []

        for idx, value in enumerate(read_data):
            
            read_data_num.append(f"{idx+1}. {value}")

            

        for x in range(0, len(read_data_num), 85):

            await callback_query.message.answer("".join(read_data_num[x:x+85]))

        await callback_query.message.answer('Выберите номер тайтла:')

        database.adding_active_title(callback_query["from"].id, callback_query.data[-1])
    
    await UserState.title_add.set()


@dp.message_handler(state=UserState.title_add)
async def title_add(message: types.Message, state: FSMContext):

    await state.update_data(title_add=message.text)
    
    finish_data = await state.get_data()

    id_cat_title = database.get_user(message.from_user.id)['cat_active_title']

    with open(f'assets/titles_{id_cat_title}.txt', 'r') as file:
        
        read_data = file.readlines()[int(finish_data['title_add'])-1].strip()
        
        database.create_user_title(message.from_user.id, read_data)

    print('[+] Title added')

    await message.answer(f"Тайтл {str(finish_data['title_add'])} успешно добавлен!",
    reply_markup=create_keyboard({}, back_button=True))

    await state.finish()


@app.on_message(filters=filters.channel)
async def my_handler(client: Client, message: types.Message):


    if message.chat.id != official_chat:
        return
    
    title = message.caption.split()[0].strip()
    users = database.get_users_by_title(title)


    for user in users:
        await bot.send_message(user["user_id"], f"Новый пост!\nТайтл: {title}\n\nСсылка на пост: t.me/{message.chat.username}/{message.forward_from_message_id}")



if __name__ == '__main__':

    p = Process(target=app.run, daemon=True)
    p.start()

    executor.start_polling(dp, skip_updates=True)
    

