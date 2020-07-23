# proxypool

使用 MongoDB 和 flask 构建一个代理池

运行 scheduler.py 文件即可开始

通过 API 获取 IP

```python
import requests

PROXY_POOL_URL = 'http://localhost:5000/one'  # one proxy

PROXIES_POOL_URL = 'http://127.0.0.1:5000/all'  # all proxies


def get_proxy():

    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        return None
```
