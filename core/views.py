from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from core.constants import OrderConstant
from core.models import ExpenseTracker, Order, Item
from export.excel import export_data

import logging

User = get_user_model()

logger = logging.getLogger(__name__)


# @method_decorator(cache_page(60 * 10), name="dispatch")
class DashboardView(APIView):
    # throttle_classes = [AnonRateThrottle]

    def get(self, request):
        """This view returns following detail for react dashboard.
        1. total_dealers
        2. total_orders
        3. total_amount
        4. total_amount_received
        5. amount_submitted_to_admin
        6. amount_remaining_collected
        7. total_expense
        8. top_dealers : [{total_orders, total_amount}] Descending in terms of total_amount
        9. items_orders : [{item, total_weight, total_amount}] Descending in terms of total_amount
        10. item_sales_data

        Args:
            request (_type_): _description_

        Returns:
            JSON response containing above details
        """
        try:
            qs = Order.objects.prefetch_related("book", "book__dealer").exclude(
                status=OrderConstant.STATUS_CANCELLED.value
            )

            # 1. Total dealers
            total_dealers = User.objects.filter(is_dealer=True).count()

            # 2. Total orders
            # 3. Total amount
            # 4. Total amount received
            # 5. total_amount_received
            # 6. Amount remaining collected
            total_qs = qs.aggregate(
                total_order_amount=models.Sum("total_amount"),
                total_amount_received=models.Sum("amount_paid"),
                total_orders=models.Count("pk"),
                amount_remaining_collected=models.Sum(
                    models.Case(
                        models.When(
                            models.Q(
                                payment_received_to_dealer=False,
                                final_payment_received=False,
                            ),
                            then=models.F("total_amount") - models.F("amount_paid"),
                        ),
                        default=0,  # Set the default value to 0 if the condition is not met.
                        output_field=models.DecimalField(
                            max_digits=10, decimal_places=2
                        ),  # Adjust this based on your field type.
                    )
                ),
                amount_submitted_to_admin=models.Sum(
                    "total_amount", filter=models.Q(final_payment_received=True)
                ),
            )
            total_amount = total_qs["total_order_amount"] or 0
            total_amount_received = total_qs["total_amount_received"] or 0
            total_orders = total_qs["total_orders"] or 0
            amount_remaining_collected = total_qs["amount_remaining_collected"] or 0
            amount_submitted_to_admin = total_qs["amount_submitted_to_admin"] or 0

            # 7. Total expense
            total_expense = (
                ExpenseTracker.objects.aggregate(total_amount=models.Sum("amount"))[
                    "total_amount"
                ]
                or 0
            )

            # 8. Top dealers
            top_dealers = (
                qs.values("book__dealer")
                .annotate(
                    total_orders=models.Count("pk"),
                    total_amount=models.Sum("total_amount"),
                    dealer_phone=models.F("book__dealer__username"),
                    dealer_name=models.F("book__dealer__name"),
                )
                .order_by("-total_amount")[:5]
            )

            # 9. Items orders
            graph_data = (
                qs.annotate(
                    date=models.functions.TruncDate("created_at"),
                )
                .values("date")
                .annotate(
                    total_bills=models.Count("id"),
                    total_amount=models.Sum("total_amount"),
                )
                .order_by("date")
            )

            order_items_values = qs.values("items")
            items_detail = Item.objects.all().values_list("name", "packs")
            items_detail_dict = {
                item[0]: {i["box"]: i["price"] for i in item[1]}
                for item in items_detail
            }

            # 10. item_sales_data
            item_sales_data = {}
            for item in items_detail_dict.keys():
                item_sales_data[item] = {
                    "total_weight": sum(
                        sum(
                            int(p["box"].split()[0])
                            * (1000 if "KG" in p["box"] else 1)
                            * p["quantity"]
                            for p in order["items"]
                            if p["item"] == item
                        )
                        for order in order_items_values
                    ),
                    "total_amount": sum(
                        sum(
                            order_item["quantity"]
                            * items_detail_dict[item][order_item["box"]]
                            for order_item in order["items"]
                            if order_item["item"] == item
                        )
                        for order in order_items_values
                    ),
                    "total_quantity": 0,
                }

            response = {
                "total_dealers": total_dealers,
                "total_orders": total_orders,
                "total_amount": total_amount,
                "remaining_amount": amount_remaining_collected,
                "total_amount_received": total_amount_received,
                "amount_submitted_to_admin": amount_submitted_to_admin,
                "total_expense": total_expense,
                "top_dealers": top_dealers,
                "items_orders": item_sales_data,
                "graph_data": graph_data,
            }

            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(e)
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DealerView(APIView):
    def get(self, request):
        try:
            qs = Order.objects.prefetch_related("book", "book__dealer").exclude(
                status=OrderConstant.STATUS_CANCELLED.value
            )
            dealer = (
                qs.values("book__dealer")
                .annotate(
                    total_orders=models.Count("pk"),
                    total_amount=models.Sum("total_amount"),
                    dealer_phone=models.F("book__dealer__username"),
                    dealer_name=models.F("book__dealer__name"),
                )
                .order_by("-total_amount")
            )
            return Response(dealer, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(e)
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def download_excel(request):
    # Generate your Excel data and save it to a BytesIO object
    FILE_NAME = f"Sales Report ({timezone.now().strftime('%d-%m-%Y')}).xlsx"
    data = Order.objects.all().values()
    excel_buffer = export_data(data)
    # Create an HTTP response with the Excel data
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f'attachment; filename="{FILE_NAME}"'
    response.write(excel_buffer)
    return response
