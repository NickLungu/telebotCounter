import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ParseMode

import datetime

import os, hashlib

from dotenv import load_dotenv

import sources.tools as tools
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
        "Just open any chat, make sure the text field is empty and enter something like the following: \n" \
        f'@EventCounter_wlya_Bot Day x {now_.year+1}-{now_.month}-{now_.day}-{now_.hour}-{now_.minute}. \n'\
        "The countdown has the following format: %%yy-mm-dd-hh-mm%% \n"\
        "You may place this countdown only once in your text!"
    await bot.send_message(message.chat.id, reply, parse_mode='html')


@dp.inline_handler()
async def inline_echo(inline_query: types.InlineQuery):

    input_text = inline_query.query or 'echo'
    flag_parse, date_point, title, splitted = tools.parse_query(input_text)
    if not flag_parse and input_text != 'echo':
        item = types.InlineQueryResultArticle(
            id='1',
            title='Wrong format :(',
            input_message_content=types.InputTextMessageContent(
                'try change date', parse_mode=ParseMode.MARKDOWN
            )
        )
        await inline_query.answer(results=[item], cache_time=1, is_personal=True)
    if flag_parse:

        date_point_dict = {
            'year': int(splitted[0]),
            'month': int(splitted[1]),
            'day': int(splitted[2]),
            'hour': int(splitted[3]),
            'minute': int(splitted[4])
        }
        try:
            flag, difference = tools.calculate_difference(date_point_dict)
            if flag:
                item = types.InlineQueryResultArticle(
                    id='1',
                    title='Valid format! Click here to calculate :)',
                    input_message_content=types.InputTextMessageContent(
                        f'{difference["days"]} day, {difference["hours"]} hour, {difference["minutes"]} minute'
                    )
                )
            else:
                item = types.InlineQueryResultArticle(
                    id='1',
                    title='Wrong format :(',
                    input_message_content=types.InputTextMessageContent(
                        'try change data'
                    )
                )
            await inline_query.answer(results=[item], cache_time=1, is_personal=True)
        except Exception as e:
            print(e)
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
                'minute': res[4]
            })
            if not flag:
                break
            title = res[5]
            title4hash = all
            result_id: str = hashlib.md5((title4hash).encode()).hexdigest()
            items.append(types.InlineQueryResultArticle(
                    id= result_id,
                    title=f'{title} ({res[0]}-{res[1]}-{res[2]}-{res[3]}-{res[4]})',
                    input_message_content=types.InputTextMessageContent(
                        f'Time left: {difference["days"]} day, {difference["hours"]} hour, {difference["minutes"]} minute'
                    )
                )
            )
        await inline_query.answer(results=items, cache_time=1, is_personal=True)


@dp.chosen_inline_handler(lambda chosen_inline_query: True)
async def chosen(chosen_res: types.ChosenInlineResult):
    flag, date_point, title, splitted = tools.parse_query(chosen_res.query)

    dbtools.insert_date_point([chosen_res.from_user.id,
                       splitted[0],
                       splitted[1],
                       splitted[2],
                       splitted[3],
                       splitted[4],
                       title,
                       False]
    )


if __name__ == '__main__':
    executor.start_polling(dp,loop=loop,skip_updates=True)