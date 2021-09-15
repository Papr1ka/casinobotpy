import motor.motor_asyncio
import os
import time
import asyncio
from random import randint

tasks = []



client = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb+srv://user:{os.environ.get('MONGO_PASSWORD')}@cluster0.qbwbb.mongodb.net/{'casino'}?retryWrites=true&w=majority")
db = client['casino']
client.get_io_loop = asyncio.get_running_loop


async def do_update(guild_id, user_id, query):
    coll = db[str(guild_id)]
    result = await coll.update_one({'_id': user_id}, {'$inc': query})
    return result


async def handler2():
    while True:
        tasks.extend([ {'money': -500} for i in range(randint(1, 100)) ] )
        print('tasks added:', tasks)
        await asyncio.sleep(5)


async def handler3():
    while True:
        served = []
        for i in tasks:
            r = await do_update(750791175606239397, 397352286487052288, i)
            print(r.raw_result)
            served.append(i)
        for i in served:
            tasks.remove(i)

async def main():
    task = asyncio.create_task(handler2())
    task2 = asyncio.create_task(handler3())
    await asyncio.gather(task, task2)


asyncio.run(main())
print('finished')