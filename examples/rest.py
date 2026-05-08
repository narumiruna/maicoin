import os

from dotenv import find_dotenv
from dotenv import load_dotenv
from rich import print

from maicoin.v3 import Client


def public_examples(client: Client) -> None:
    print("[bold cyan]markets[/bold cyan]")
    print(client.markets()[:3])

    print("[bold cyan]ticker btctwd[/bold cyan]")
    print(client.ticker("btctwd"))

    print("[bold cyan]kline btctwd (period=1, limit=5)[/bold cyan]")
    print(client.kline("btctwd", period=1, limit=5))

    print("[bold cyan]depth btctwd (limit=5)[/bold cyan]")
    print(client.depth("btctwd", limit=5))


def private_examples(client: Client) -> None:
    print("[bold magenta]user info[/bold magenta]")
    print(client.info())

    print("[bold magenta]spot accounts[/bold magenta]")
    print(client.accounts())

    print("[bold magenta]open orders btctwd[/bold magenta]")
    print(client.open_orders(market="btctwd"))


def main() -> None:
    load_dotenv(find_dotenv())

    public_examples(Client())

    api_key = os.environ.get("MAX_API_KEY")
    api_secret = os.environ.get("MAX_API_SECRET")
    if api_key and api_secret:
        private_examples(Client(api_key=api_key, api_secret=api_secret))
    else:
        print("[yellow]MAX_API_KEY / MAX_API_SECRET not set — skipping private examples[/yellow]")


if __name__ == "__main__":
    main()
