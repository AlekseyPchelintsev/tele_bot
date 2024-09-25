import asyncio

async def hobbies_list(hobbies):
  if hobbies:
    return ' | '.join(f'<i>{hobby}</i>' for hobby in hobbies)
  else:
    return '-'