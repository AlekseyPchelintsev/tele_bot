import asyncio

async def loader(message, text):
  response_message = await message.answer(f'{text}')    
  for i in range(1, 4):
    await response_message.edit_text(f'{text}{" ." * i}')
    await asyncio.sleep(.5)
    if i == 3:
      await asyncio.sleep(.3)
      try:
        await message.delete()
      except:
        pass
      await response_message.delete()