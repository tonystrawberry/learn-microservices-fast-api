from main import redis, Order
import time

key = "refund_order"
group = "inventory_group"

try:
    redis.xgroup_create(key, group)
except:
    print("Group already exists!")

while True:
    try:
        results = redis.xreadgroup(group, key, {key: ">"}, None)

        print(results)

        # [['order_completed', [('1648862765029-0', {'pk': '01FZKY20V3WPDA9VPG7G4HFNW8', 'product_id': '01FZJTWQMPB3EJN3QPC8N8VWP8', 'price': '20.0', 'fee': '4.0', 'total': '24.0', 'quantity': '4', 'status': 'completed'})]]]

        if results != []:
            for result in results:
                obj = result[1][0][1]
                order = Order.get(obj["pk"])
                order.status = "refunded"

                order.save()

    except Exception as e:
        print(str(e))

    time.sleep(1)  # every second, messages will be consumed
