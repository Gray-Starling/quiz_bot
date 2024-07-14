import random
import time

async def wait_for_result(message):
    random_sec = random.randint(3,5)
    for sec in range(random_sec):
        time.sleep(1)
        await message.answer(".")