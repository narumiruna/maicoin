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

REST v3 support includes the foundation client, authentication helpers, error handling, public endpoint wrappers, and typed public response models.

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

### Low-level private request

Private requests require MAX credentials and are signed with `X-MAX-ACCESSKEY`, `X-MAX-PAYLOAD`, and `X-MAX-SIGNATURE` headers.

```python
import os

from maicoin.v3 import Client

client = Client(
    api_key=os.environ["MAX_API_KEY"],
    api_secret=os.environ["MAX_API_SECRET"],
)
accounts = client.request("GET", "/api/v3/wallet/spot/accounts", auth=True)
```

Do not run state-changing private requests, such as order creation or withdrawals, without reviewing the parameters carefully.
