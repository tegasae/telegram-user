import asyncio
import json

import aiohttp


async def long_operation():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://192.168.100.148:8080/api/v1/n/user/') as response:

                response.raise_for_status()  # Raise exception for bad status
                src = await response.json()  # Directly parse JSON

    except aiohttp.ClientError as e:
        print(f"HTTP request failed: {e}")

        # You might want to keep old data or raise an exception here
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")


async def wait_message():
    while True:
        print("Ждите...", end="", flush=True)  # Убрали \r и добавили flush
        await asyncio.sleep(0.5)
        print("\n", end="", flush=True)  # Возврат каретки отдельно


async def main():
    task = asyncio.create_task(long_operation())
    wait_task = asyncio.create_task(wait_message())

    result = await task
    wait_task.cancel()

    print("\nРезультат:", result)

if __name__=="__main__":
    asyncio.run(main())