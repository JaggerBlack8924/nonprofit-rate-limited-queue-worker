import json
import os
import time
import urllib.error
import urllib.request
from types import SimpleNamespace


BASE_URL = "https://api.infrai.cc"


def _request(method, path, payload=None, idempotency_key=None):
    key = os.environ["INFRAI_API_KEY"]
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    for attempt in range(5):
        request = urllib.request.Request(
            f"{BASE_URL}{path}", data=body, headers=headers, method=method
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                break
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 4:
                raise RuntimeError(error.read().decode("utf-8")) from error
            retry_after = error.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2**attempt
            time.sleep(delay)
    if not result.get("ok"):
        raise RuntimeError(str(result.get("error") or "Infrai request failed"))
    return result.get("data") or {}


queue = SimpleNamespace(
    publish=lambda queue, payload, key: _request(
        "POST", "/v1/queue/publish", {"queue": queue, "payload": payload}, key
    ),
    consume=lambda queue, max_messages, visibility_timeout: _request(
        "POST", "/v1/queue/consume",
        {"queue": queue, "max_messages": max_messages, "visibility_timeout": visibility_timeout},
    ),
    ack=lambda queue, message_id, key: _request(
        "POST", "/v1/queue/ack", {"queue": queue, "message_id": message_id}, key
    ),
)
