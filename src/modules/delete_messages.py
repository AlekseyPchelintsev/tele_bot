
async def del_messages(chat_id, delete_messages):
    from main import bot
    for message_id in delete_messages:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass


async def del_last_message(callback_message):
    try:
        await callback_message.delete()
    except:
        await callback_message.answer('Что-то пошло не так 🫠')
        await callback_message.delete()
