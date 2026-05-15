import asyncio
import os

from dotenv import find_dotenv
from dotenv import load_dotenv
from rich import print

from maicoin.v3 import Client


async def public_examples(client: Client) -> None:
    print("[bold cyan]markets[/bold cyan]")
    print((await client.markets())[:3])

    print("[bold cyan]ticker btctwd[/bold cyan]")
    print(await client.ticker("btctwd"))

    print("[bold cyan]kline btctwd (period=1, limit=5)[/bold cyan]")
    print(await client.kline("btctwd", period=1, limit=5))

    print("[bold cyan]depth btctwd (limit=5)[/bold cyan]")
    print(await client.depth("btctwd", limit=5))


async def private_examples(client: Client) -> None:
    print("[bold magenta]user info[/bold magenta]")
    print(await client.info())

    print("[bold magenta]spot accounts[/bold magenta]")
    print(await client.accounts())

    print("[bold magenta]open orders btctwd[/bold magenta]")
    print(await client.open_orders(market="btctwd"))

    print("[bold magenta]recent order history btctwd[/bold magenta]")
    async for order in client.iter_order_history("btctwd", page_limit=10, max_items=3):
        print({"id": order.id, "state": order.state, "market": order.market})


async def main() -> None:
    load_dotenv(find_dotenv())

    async with Client() as public_client:
        await public_examples(public_client)

    api_key = os.environ.get("MAX_API_KEY")
    api_secret = os.environ.get("MAX_API_SECRET")
    if api_key and api_secret:
        async with Client(api_key=api_key, api_secret=api_secret) as private_client:
            await private_examples(private_client)
    else:
        print("[yellow]MAX_API_KEY / MAX_API_SECRET not set — skipping private examples[/yellow]")


if __name__ == "__main__":
    asyncio.run(main())
