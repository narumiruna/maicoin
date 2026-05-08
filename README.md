# maicoin

A Python package for MaiCoin MAX API.

## Usage

Install package:

```shell
# uv
uv add maicoin

# pip
pip install maicoin
```

Create `.env` file for private API examples:

```dotenv
MAX_API_KEY=
MAX_API_SECRET=
```

Run [example.py](example.py):

```shell
python example.py
```

## REST API v3

REST v3 support includes the foundation client, authentication helpers, error handling, public/private endpoint wrappers,
and typed response models.

### Public requests

```python
from maicoin.v3 import Client

client = Client()
markets = client.markets()
ticker = client.ticker("btctwd")
klines = client.kline("btctwd", period=1, limit=30)
```

Use `Client.request(...)` for low-level access when a high-level wrapper is not available yet:

```python
from maicoin.v3 import Client

client = Client()
markets = client.request("GET", "/api/v3/markets")
```

### Private requests

Private requests require MAX credentials and are signed with `X-MAX-ACCESSKEY`, `X-MAX-PAYLOAD`, and
`X-MAX-SIGNATURE` headers.

```python
import os

from maicoin.v3 import Client

client = Client(
    api_key=os.environ["MAX_API_KEY"],
    api_secret=os.environ["MAX_API_SECRET"],
)

accounts = client.accounts()
open_orders = client.open_orders(market="btctwd")
withdrawals = client.withdrawals(currency="btc", limit=10)
```

Use `Client.request(...)` for low-level private access when a high-level wrapper is not available:

```python
import os

from maicoin.v3 import Client

client = Client(
    api_key=os.environ["MAX_API_KEY"],
    api_secret=os.environ["MAX_API_SECRET"],
)
accounts = client.request("GET", "/api/v3/wallet/spot/accounts", auth=True)
```

> [!WARNING]
> Some private methods create real account actions, including orders, withdrawals, loans, transfers, repayments,
> and converts. Review parameters carefully before calling state-changing methods.

## WebSocket API

Use `Stream` with one or more subscriptions to receive typed WebSocket responses:

```python
from maicoin.ws import Channel
from maicoin.ws import Response
from maicoin.ws import Stream
from maicoin.ws import Subscription


def handle_response(response: Response) -> None:
    print(response.model_dump(exclude_none=True))


stream = Stream()
stream.subscribe(
    [
        Subscription(channel=Channel.BOOK, market="btcusdt", depth=5),
        Subscription(channel=Channel.TICKER, market="btcusdt"),
        Subscription(channel=Channel.TRADE, market="btcusdt"),
        Subscription(channel=Channel.MARKET_STATUS),
    ]
)
stream.add_handler(handle_response)
stream.run()
```

For authenticated private WebSocket channels, create the stream with credentials or use `Stream.from_env()` with
`MAX_API_KEY` and `MAX_API_SECRET`.
