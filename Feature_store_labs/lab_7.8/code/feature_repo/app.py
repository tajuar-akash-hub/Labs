import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel
from feast import FeatureStore

FEATURES = [
    "user_stats:orders_7d",
    "user_stats:avg_order_value",
    "user_stats:top_category",
]

CATEGORY_ITEMS = {
    "electronics": ["wireless-earbuds", "usb-c-hub"],
    "books": ["bestseller-novel", "ebook-reader"],
    "fashion": ["canvas-sneakers", "denim-jacket"],
    "grocery": ["organic-coffee", "pantry-bundle"],
}
FALLBACK_ITEMS = ["popular-gift-card", "weekly-deals-pack"]

store = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global store
    store = FeatureStore(repo_path=".")
    store.get_online_features(
        features=FEATURES, entity_rows=[{"user_id": 1}]
    ).to_dict()
    yield


app = FastAPI(title="Feast recommendation API", lifespan=lifespan)


class PredictRequest(BaseModel):
    user_id: int


def first_value(result: dict, feature_name: str):
    for key, values in result.items():
        if key == feature_name or key.endswith(f"__{feature_name}"):
            return values[0]
    return None


def recommend(features: dict) -> list:
    items = list(CATEGORY_ITEMS.get(features["top_category"], FALLBACK_ITEMS))
    if features["orders_7d"] >= 5:
        items.append("loyalty-bundle")
    if features["avg_order_value"] >= 60:
        items.append("premium-pick")
    return items


@app.post("/predict")
def predict(request: PredictRequest):
    started = time.perf_counter()

    feast_started = time.perf_counter()
    result = store.get_online_features(
        features=FEATURES, entity_rows=[{"user_id": request.user_id}]
    ).to_dict()
    feast_ms = (time.perf_counter() - feast_started) * 1000

    features = {
        "orders_7d": first_value(result, "orders_7d"),
        "avg_order_value": first_value(result, "avg_order_value"),
        "top_category": first_value(result, "top_category"),
    }
    known_user = features["orders_7d"] is not None

    if known_user:
        recommendations = recommend(features)
    else:
        recommendations = FALLBACK_ITEMS

    total_ms = (time.perf_counter() - started) * 1000
    return {
        "user_id": request.user_id,
        "known_user": known_user,
        "recommendations": recommendations,
        "features": {
            "orders_7d": features["orders_7d"],
            "avg_order_value": features["avg_order_value"],
            "top_category": features["top_category"],
        },
        "feast_ms": round(feast_ms, 2),
        "total_ms": round(total_ms, 2),
    }
