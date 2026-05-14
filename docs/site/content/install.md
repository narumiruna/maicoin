# 📦 Installation

`maicoin` requires **Python 3.12+**.

## With uv

```shell
uv add maicoin
```

## With pip

```shell
pip install maicoin
```

## Credentials

Private REST endpoints and private WebSocket channels need a MAX API key pair. Set them in your environment, or in a `.env` file at the project root:

```dotenv
MAX_API_KEY=your_key
MAX_API_SECRET=your_secret
```

!!! warning "🔐 Treat your secret like a password"
    The API secret can place orders, transfer funds, take loans, and trigger withdrawals. Never commit it. Prefer a vault or environment manager over plain `.env` files for production use.

## Optional dependencies

The example scripts use `python-dotenv` and `rich` to load credentials and pretty-print results. They are dev dependencies of this repo, not of the published package — install them yourself when running the examples:

```shell
uv add --dev python-dotenv rich
```
