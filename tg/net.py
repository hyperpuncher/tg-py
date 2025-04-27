import httpx

timeout = httpx.Timeout(timeout=5, connect=2, read=120)
client = httpx.AsyncClient(timeout=timeout)
