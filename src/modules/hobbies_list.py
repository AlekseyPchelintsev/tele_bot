
'''
async def hobbies_list(hobbies):
    if hobbies:
        return ''.join(f'\n► {hobby}' for hobby in hobbies)
    else:
        return '-'
'''


async def hobbies_list(hobbies):
    if hobbies:
        return ' <b>|</b> '.join(f'<i>{hobby}</i>' for hobby in hobbies)
    else:
        return '-'
