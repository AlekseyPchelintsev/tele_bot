import asyncio


async def check_gender(gender):
    if gender == 'male':
        return '🚹'
    elif gender == 'female':
        return '🚺'
    else:
        return '🚻'
