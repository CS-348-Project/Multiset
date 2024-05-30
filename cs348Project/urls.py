from django.contrib import admin
from django.urls import path
from django.db import connection
from django.http import JsonResponse
from ninja import NinjaAPI, Schema
from typing import List


class PurchaseSplit(Schema):
    amount: int
    borrower: int


class Purchase(Schema):
    name: str
    category: str
    group_id: int
    total_cost: int
    purchaser: int
    purchase_splits: List[PurchaseSplit]


api = NinjaAPI()


@api.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}


@api.get("/")
def home(request):
    return {"message": "Hello, world!"}


@api.get("/users")
def get_users(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM multiset_user")
        rows = cursor.fetchall()
    return JsonResponse(rows, safe=False)


@api.post("/new-purchase")
def new_purchase(request, purchase: Purchase):
    """
    Creates a new purchase and its splits in the database.
    Args:
        purchase: the purchase object to be created and a list of purchase splits
    Returns:
        a JSON response with the status of the operation
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
                INSERT INTO purchase (name, category, group_id, total_cost, purchaser)
                VALUES (%s, %s, %s, %s, %s)
            """,
            [
                purchase.name,
                purchase.category,
                purchase.group_id,
                purchase.total_cost,
                purchase.purchaser,
            ],
        )

        purchase_id = cursor.lastrowid
        if not purchase_id:
            return JsonResponse({"status": "error, purchase_id not found"})

        for purchase_split in purchase.purchase_splits:
            cursor.execute(
                """
                    INSERT INTO purchase_splits (purchase_id, amount, borrower)
                    VALUES (%s, %s, %s)
                """,
                [
                    purchase_id,
                    purchase_split.amount,
                    purchase_split.borrower,
                ],
            )
    return JsonResponse({"status": "success"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
