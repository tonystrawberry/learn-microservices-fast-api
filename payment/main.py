from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests, time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# This should be a different database
redis = get_redis_connection(
    host="redis-14050.c294.ap-northeast-1-2.ec2.cloud.redislabs.com",
    port="14050",
    password="L5L7yr4uKho7bdFA1XPtGVk1gsXz6EED",
    decode_responses=True,
)


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str  # pending, completed, refunded

    class Meta:
        database = redis


@app.get("/orders/")
def get():
    return [format(pk) for pk in Order.all_pks()]


def format(pk: str):
    order = Order.get(pk)

    return {
        "id": order.pk,
        "product_id": order.product_id,
        "price": order.price,
        "fee": order.fee,
        "quantity": order.quantity,
        "total": order.total,
        "status": order.status,
    }


@app.get("/orders/{pk}")
def get(pk: str):
    order = Order.get(pk)
    return order


@app.post("/orders")
async def create(request: Request, background_tasks: BackgroundTasks):  # id, quantity
    body = await request.json()

    req = requests.get("http://localhost:8000/products/%s" % body["id"])
    product = req.json()

    order = Order(
        product_id=body["id"],
        price=product["price"],
        fee=0.2 * product["price"],
        total=1.2 * product["price"],
        quantity=body["quantity"],
        status="pending",
    )

    order.save()

    # Run function in background
    background_tasks.add_task(order_completed, order)

    return order


def order_completed(order: Order):
    time.sleep(5)
    order.status = "completed"
    order.save()
    redis.xadd("order_completed", order.dict(), "*")  # * for auto-generated ids
