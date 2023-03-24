from aiogram import Bot, types


def get_items(_type):
    if _type == "WRONG":
        item = types.InlineQueryResultArticle(
            id='1',
            title='Wrong format :(',
            input_message_content=types.InputTextMessageContent(
                'https://t.me/EventCounter_wlya_Bot'
            )
        )
    elif _type == "REGISTER":
        item = types.InlineQueryResultArticle(
            id='1',
            title='Please, enter GMT in private messages of the bot',
            input_message_content=types.InputTextMessageContent(
                'https://t.me/EventCounter_wlya_Bot'
            )
        )
    return item

