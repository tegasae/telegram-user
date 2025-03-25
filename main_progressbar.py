import asyncio


class Progress:
    def __init__(self):
        self.value = 0

    def update(self, val):
        self.value = val


async def worker(progress):
    for i in range(1, 11):
        await asyncio.sleep(0.3)
        progress.update(i * 10)  # Обновляем через метод


async def progress_bar(progress):
    while progress.value < 100:
        print(f"\rProgress: {'⬛' * (progress.value // 10)}{'⬜' * (10 - progress.value // 10)} {progress.value}%",
              end="", flush=True)
        await asyncio.sleep(0.1)
    print("\nDone!")


async def main():
    progress = Progress()
    await asyncio.gather(
        worker(progress),
        progress_bar(progress)
    )


asyncio.run(main())