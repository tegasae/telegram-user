import asyncio


async def long_request():
    print("Начало запроса...", flush=True)  # Принудительный вывод
    await asyncio.sleep(3)
    return "Данные получены!"


async def wait_message(future):
    first_run = True
    while not future.done():
        if first_run:
            print("Ждите...", end="", flush=True)  # Первый вывод без \r
            first_run = False
        else:
            print(".", end="", flush=True)  # Добавляем точки
        await asyncio.sleep(0.5)
    print("\r" + " " * 20 + "\r", end="", flush=True)  # Полная очистка строки


async def main():
    future = asyncio.create_task(long_request())  # Современный аналог ensure_future
    wait_task = asyncio.create_task(wait_message(future))

    result = await future
    await wait_task

    print("Результат:", result, flush=True)


if __name__ == "__main__":
    asyncio.run(main())