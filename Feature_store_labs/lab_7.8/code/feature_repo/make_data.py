import numpy as np
import pandas as pd


def main():
    rng = np.random.default_rng(7)
    user_count = 100
    categories = ["electronics", "books", "fashion", "grocery"]

    one_hour_ago = pd.Timestamp.now(tz="UTC") - pd.Timedelta(1, "h")

    users = pd.DataFrame(
        {
            "user_id": np.arange(1, user_count + 1, dtype="int64"),
            "event_timestamp": pd.to_datetime(
                [one_hour_ago] * user_count, utc=True
            ).astype("datetime64[ns, UTC]"),
            "orders_7d": rng.integers(0, 12, size=user_count).astype("int64"),
            "avg_order_value": np.round(rng.uniform(10, 120, size=user_count), 2),
            "top_category": rng.choice(categories, size=user_count),
        }
    )

    users.to_parquet("data/user_stats.parquet", index=False)
    print(users.head())
    print("Wrote data/user_stats.parquet with", len(users), "rows")


if __name__ == "__main__":
    main()
