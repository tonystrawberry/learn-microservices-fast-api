from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

redis = get_redis_connection(
    host="redis-14050.c294.ap-northeast-1-2.ec2.cloud.redislabs.com",
    port="14050",
    password="L5L7yr4uKho7bdFA1XPtGVk1gsXz6EED",
    decode_responses=True,
)


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


@app.get("/products")
def all():
    return [format(pk) for pk in Product.all_pks()]


def format(pk: str):
    product = Product.get(pk)

    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity,
    }


@app.post("/products")
def create(product: Product):
    return product.save()


@app.get("/products/{pk}")
def get(pk: str):
    return format(pk)


@app.delete("/products/{pk}")
def delete(pk: str):
    return Product.delete(pk)
