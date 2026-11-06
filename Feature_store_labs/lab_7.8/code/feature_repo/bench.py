import statistics
import time

import httpx

URL = "http://127.0.0.1:8000/predict"
WARMUP_REQUESTS = 10
REQUESTS = 200
TARGET_MS = 50


def main():
    latencies = []

    with httpx.Client(timeout=5.0) as client:
        for i in range(WARMUP_REQUESTS):
            client.post(URL, json={"user_id": (i % 100) + 1}).raise_for_status()

        for i in range(REQUESTS):
            user_id = (i % 100) + 1
            started = time.perf_counter()
            response = client.post(URL, json={"user_id": user_id})
            latencies.append((time.perf_counter() - started) * 1000)
            response.raise_for_status()

    latencies.sort()
    p50 = statistics.median(latencies)
    p95 = latencies[int(len(latencies) * 0.95) - 1]

    print(f"requests: {REQUESTS}")
    print(f"p50: {p50:.2f} ms")
    print(f"p95: {p95:.2f} ms")
    print(f"max: {latencies[-1]:.2f} ms")
    print("PASS" if p95 < TARGET_MS else f"FAIL: p95 is above {TARGET_MS} ms")


if __name__ == "__main__":
    main()
