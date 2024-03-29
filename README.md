# maicoin

A Python package for MaiCoin MAX API

## Usage

Install package
```shell
pip install .
```

Create `.env` file
```
MAX_API_KEY=
MAX_API_SECRET=
```

Run [example.py](example.py):
```shell
python example.py
```

## To-Do List

- [x] [WebSocket API](https://maicoin.github.io/max-websocket-docs)
  - [x] Public channels
    - [x] Subscribe
    - [x] Unsubscribe
    - [x] Orderbook
    - [x] Trade
    - [x] Ticker
    - [x] Kline
    - [x] Market Status
  - [x] Authentication
  - [x] Private channels
    - [x] Order
    - [x] Trade
    - [x] Account
- [ ] [HTTP API](https://max.maicoin.com/documents/api_list/v2)
