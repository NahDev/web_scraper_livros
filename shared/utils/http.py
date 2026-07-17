import time

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class HttpClient:
    def __init__(
        self,
        base_url: str = "",
        delay_seconds: float = 0.4,
        timeout: float = 30.0,
    ) -> None:
        self.delay_seconds = delay_seconds
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; BookstoreScraper/0.1; "
                    "+research educational use)"
                ),
                "Accept": "application/json, text/html;q=0.9,*/*;q=0.8",
            },
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def get(self, url: str, **kwargs: object) -> httpx.Response:
        time.sleep(self.delay_seconds)
        response = self._client.get(url, **kwargs)
        response.raise_for_status()
        return response
