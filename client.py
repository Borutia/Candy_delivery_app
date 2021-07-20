import asyncio

import aiohttp


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def main():
    chunk = 10
    url = 'http://0.0.0.0:8080/couriers/1'
    while True:
        async with aiohttp.ClientSession() as session:
            tasks = [fetch(session, url) for _ in range(chunk)]
            responses = await asyncio.gather(*tasks)
            for response in responses:
                print(response)
        await asyncio.sleep(chunk)


if __name__ == '__main__':
    asyncio.run(main())
