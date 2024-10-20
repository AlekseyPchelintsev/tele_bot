import asyncio


# имитация загрузки (самоудаляется)
async def loader(message, text):
    response_message = await message.answer(f'{text}')
    for i in range(1, 4):
        await response_message.edit_text(f'{text} {"○" * i}', parse_mode='HTML')
        await asyncio.sleep(.1)
    for i in range(1, 4):
        symbols = '●' * i + '○' * (3 - i)
        await response_message.edit_text(f'{text} {symbols}', parse_mode='HTML')
        await asyncio.sleep(.1)
    await asyncio.sleep(.3)
    '''try:
        await message.delete()
    except:
        pass'''
    await response_message.delete()


# уведомление с передачей текста (замоудаляющееся)
async def notification(message, text):
    temporary_message = await message.answer(f'{text}', parse_mode='HTML')
    await asyncio.sleep(2)
    await temporary_message.delete()
    try:
        await message.delete()
    except:
        pass


# уведомление с передачей текста и таймера удаления (самоудаляющееся)
async def attention_message(message, text, timer):

    temporary_message = await message.answer(f'{text}', parse_mode='HTML')
    await asyncio.sleep(timer)
    await temporary_message.delete()
