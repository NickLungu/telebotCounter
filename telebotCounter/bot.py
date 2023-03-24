import asyncio
import time

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ParseMode

import datetime

import os, hashlib

from dotenv import load_dotenv

import sources.tools as tools
import sources.responceItems as responceItems
import database.dbtools as dbtools

load_dotenv()

import logging

logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()
bot = Bot(token=os.getenv('TELEGRAM_TOKEN'))
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_intro(message):
    reply = "Hello, this bot will tell you how much time is left until a certain event " \
            "/help now to get the manual"
    await bot.send_message(message.chat.id, reply)


@dp.message_handler(commands=['help'])
async def send_manual(message):
    now_ = datetime.datetime.now()
    reply = "Manual \U000023F0\n"
    reply += "How it works: \n"\
        "Just open any chat, make sure the text field is empty and enter something like the following: \n\n" \
        f'<code>@EventCounter_wlya_Bot Day x {now_.year+1}-{now_.month}-{now_.day}-{now_.hour}-{now_.minute}</code> \n\n'\
        "The countdown has the following format: yy-mm-dd-hh-mm \n"\
        "You may place this countdown only once in your text! \n\n" \
        "<strong>IMPORTANT</strong>: to use you need to register (/settimezone) your current GMT time \n"
    await bot.send_message(message.chat.id, reply, parse_mode='html')


@dp.message_handler(commands=['test'])
async def test(message):
    await bot.send_message(message.chat.id, str(time.timezone), parse_mode='html')


@dp.message_handler(commands=['settimezone'])
async def set_time_zone(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    timezones_list = [0,1,2,3,4,5,6,7,8,9,10,11,12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1]
    for i in range(0,24,4):
        keyboard.row(
            types.InlineKeyboardButton('GMT ' + str(timezones_list[i]), callback_data='utc ' + str(timezones_list[i])),
            types.InlineKeyboardButton('GMT ' + str(timezones_list[i + 1]), callback_data='utc ' + str(timezones_list[i + 1])),
            types.InlineKeyboardButton('GMT ' + str(timezones_list[i + 2]), callback_data='utc ' + str(timezones_list[i + 2])),
            types.InlineKeyboardButton('GMT ' + str(timezones_list[i + 3]), callback_data='utc ' + str(timezones_list[i + 3])),
        )

    await bot.send_message(message.chat.id, text='Chose your timezone \n(you can find it here: https://24timezones.com/timezone-map)', reply_markup=keyboard)


@dp.inline_handler()
async def inline_echo(inline_query: types.InlineQuery):

    input_text = inline_query.query or 'echo'
    flag_parse, date_point, title, splitted = tools.parse_query(input_text)
    if not flag_parse and input_text != 'echo':
        item = responceItems.get_items("WRONG")
        await inline_query.answer(results=[item], cache_time=1, is_personal=True)
    if flag_parse:
        date_point_dict = tools.make_dict_from_splitted_date(splitted)
        if dbtools.check_user_exist(inline_query.from_user.id):
            timezone = dbtools.get_timezone(inline_query.from_user.id)
            date_point_dict["timezone"] = timezone
            flag, difference = tools.calculate_difference(date_point_dict)
            if flag:
                item = types.InlineQueryResultArticle(
                    id='1',
                    title='Valid format! Click here to calculate :)',
                    input_message_content=types.InputTextMessageContent(
                        f'{title}: {difference["days"]} day, {difference["hours"]} hour, {difference["minutes"]} minute'
                    )
                )
            else:
                item = responceItems.get_items("WRONG")
        else:
            item = responceItems.get_items("REGISTER")

        await inline_query.answer(results=[item], cache_time=1, is_personal=True)
    else:
        items = []
        query_res = dbtools.select_date_point(inline_query.from_user.id)
        for res in set(query_res):
            all = f'{res[0]} {res[1]} {res[2]} {res[3]} {res[4]} {res[5]}'
            flag, difference = tools.calculate_difference({
                'year': res[0],
                'month': res[1],
                'day': res[2],
                'hour': res[3],
                'minute': res[4],
                'timezone': res[6]
            })
            if not flag:
                break

            title = res[5]
            title = '\U0001F566' + title if title == "" else '\U0001F566 ' + title

            result_id: str = hashlib.md5((all).encode()).hexdigest()
            items.append(types.InlineQueryResultArticle(
                    id= result_id,
                    title=f'{title} ({res[0]}-{res[1]}-{res[2]}-{res[3]}-{res[4]})',
                    input_message_content=types.InputTextMessageContent(
                        message_text = f'{title}: {difference["days"]} day, {difference["hours"]} hour, {difference["minutes"]} minute',
                        parse_mode = ParseMode.HTML
                    )
                )
            )
        if len(items) == 0:
            items.append(responceItems.get_items("REGISTER"))
        await inline_query.answer(results=items, cache_time=1, is_personal=True)


@dp.chosen_inline_handler(lambda chosen_inline_query: True)
async def chosen(chosen_res: types.ChosenInlineResult):
    flag, date_point, title, splitted = tools.parse_query(chosen_res.query)
    if flag:
        dbtools.insert_date_point([chosen_res.from_user.id,
                           splitted[0],
                           splitted[1],
                           splitted[2],
                           splitted[3],
                           splitted[4],
                           title,
                           False]
        )


@dp.callback_query_handler(lambda call: True)
async def timezone_hw(call):
    gmt_ = call.data.split(' ')[-1]
    dbtools.insert_timezone(call.message.chat.id, int(gmt_))
    await bot.send_message(call.message.chat.id, text='Okay! Now you can use bot totally :)')


if __name__ == '__main__':
    executor.start_polling(dp,loop=loop,skip_updates=True)