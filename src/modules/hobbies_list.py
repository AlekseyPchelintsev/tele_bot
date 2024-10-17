import asyncio


async def hobbies_list(hobbies):
    if hobbies:
        return ''.join(f'\n► {hobby}' for hobby in hobbies)
    else:
        return '-'
