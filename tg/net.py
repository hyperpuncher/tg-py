import httpx

timeout = httpx.Timeout(timeout=5, connect=2, read=120)
tg_client = httpx.AsyncClient(base_url="https://api.telegram.org/bot", timeout=timeout)
