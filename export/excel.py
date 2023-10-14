from django.db.models import Prefetch, Count, Sum
from django.contrib.auth import get_user_model
from io import BytesIO
import xlsxwriter

from core.models import Item, Order
from core.constants import BoxConstant

User = get_user_model()

COMMON_COLOR = "#82CD47"
WHITE = "#fff"
BOX_LABLES = [
    BoxConstant.BOX_250.value,
    BoxConstant.BOX_500.value,
    BoxConstant.BOX_1000.value,
    BoxConstant.BOX_2000.value,
]
COLORS = [
    "#FFD933",
    "#33FFD9",
    "#FF33FF",
    "#33D9FF",
    "#FF6633",
    "#33FF66",
    "#FF9933",
    "#3399FF",
    "#FF3399",
    "#99FF33",
    "#33CCFF",
    "#FFCC33",
    "#33FFCC",
    "#FF5733",
    "#33FF57",
    "#3366FF",
    "#FF33B8",
    "#33FFFF",
    "#FF3366",
    "#66FF33",
]


def extract_data(pack):
    data = {}
    for p in pack:
        item = data.get(p["item"])

        if item is None:
            data[p["item"]] = {}
            data[p["item"]][p["box"]] = p["quantity"]
        else:
            box = item.get(p["box"])
            if box is None:
                item[p["box"]] = p["quantity"]
            else:
                item[p["box"]] += p["quantity"]
    return data


EXPORT_FORMAT = [
    {
        "title": "Name",
        "col-type": "single",
        "bg-color": COMMON_COLOR,
        "text-color": WHITE,
        "key": "customer",
        "pre-func": lambda x: x,
    },
    {
        "title": "Phone",
        "col-type": "single",
        "bg-color": COMMON_COLOR,
        "text-color": WHITE,
        "key": "phone",
        "pre-func": lambda x: x,
    },
    {
        "title": "City",
        "col-type": "single",
        "bg-color": COMMON_COLOR,
        "text-color": WHITE,
        "key": "city_area",
        "pre-func": lambda x: x,
    },
    {
        "title": "Address",
        "col-type": "single",
        "bg-color": COMMON_COLOR,
        "text-color": WHITE,
        "key": "address",
        "pre-func": lambda x: x,
    },
    {
        "title": "Address",
        "col-type": "span",
        "bg-color": COMMON_COLOR,
        "text-color": WHITE,
        "key": "items",
        "child": Item.objects.all().values_list("name", flat=True),
        "pre-func": extract_data,
    },
    {
        "title": "Total Amount",
        "col-type": "single",
        "bg-color": COMMON_COLOR,
        "text-color": WHITE,
        "key": "total_amount",
        "pre-func": lambda x: x,
    },
    {
        "title": "Amount Paid",
        "col-type": "single",
        "bg-color": COMMON_COLOR,
        "text-color": WHITE,
        "key": "amount_paid",
        "pre-func": lambda x: x,
    },
    {
        "title": "Dealer received payment",
        "col-type": "single",
        "bg-color": COMMON_COLOR,
        "text-color": WHITE,
        "key": "payment_received_to_dealer",
        "pre-func": lambda x: "Yes" if x else "No",
    },
    {
        "title": "Payment Received",
        "col-type": "single",
        "bg-color": COMMON_COLOR,
        "text-color": WHITE,
        "key": "final_payment_received",
        "pre-func": lambda x: "Yes" if x else "No",
    },
]


def write_orders_data(worksheet, excel_file, data):
    DATA_CELL_FORMAT = excel_file.add_format(
        {
            "align": "center",
            "valign": "vcenter",
            "border": 1,
        }
    )

    curr_row, curr_col = 0, 0
    # Heading Section
    for field in EXPORT_FORMAT:
        if field["col-type"] == "single":
            worksheet.merge_range(
                curr_row,
                curr_col,
                curr_row + 1,
                curr_col,
                field["title"],
                excel_file.add_format(
                    {
                        "bold": True,
                        "align": "center",
                        "valign": "vcenter",
                        "font_size": "14",
                        "bg_color": COMMON_COLOR,
                        "border": 1,
                    }
                ),
            )
            curr_col += 1
        else:
            co = 0
            for child in field["child"]:
                bg_color = COLORS[co]
                worksheet.merge_range(
                    curr_row,
                    curr_col,
                    curr_row,
                    curr_col + len(BOX_LABLES) - 1,
                    child,
                    excel_file.add_format(
                        {
                            "bold": True,
                            "align": "center",
                            "valign": "vcenter",
                            "bg_color": bg_color,
                            "font_size": "14",
                            "border": 1,
                        }
                    ),
                )

                for lable in BOX_LABLES:
                    worksheet.write(
                        curr_row + 1,
                        curr_col,
                        lable,
                        excel_file.add_format(
                            {
                                "bold": True,
                                "align": "center",
                                "valign": "vcenter",
                                "bg_color": bg_color,
                                "font_size": "14",
                                "border": 1,
                            }
                        ),
                    )
                    curr_col += 1
                co += 1
                co = co % len(COLORS)
    curr_row = 2
    # # Add Data
    for d in data:
        curr_col = 0
        for field in EXPORT_FORMAT:
            if field["col-type"] == "single":
                worksheet.write(
                    curr_row,
                    curr_col,
                    field["pre-func"](d[field["key"]]),
                    DATA_CELL_FORMAT,
                )
                curr_col += 1
            else:
                for child in field["child"]:
                    field_data = field["pre-func"](d[field["key"]])
                    for lable in BOX_LABLES:
                        worksheet.write(
                            curr_row,
                            curr_col,
                            field_data.get(child, {}).get(lable) or 0,
                            DATA_CELL_FORMAT,
                        )
                        curr_col += 1
        curr_row += 1


def write_dealers_data(
    worksheet: xlsxwriter.workbook.Worksheet, excel_file: xlsxwriter.Workbook, data
) -> None:
    """Function to write dealer data in table in excel sheet.

    Args:
        worksheet (_type_)
        excel_file (_type_): _description_
        data (_type_): _description_
    """
    data = (
        User.objects.filter(is_dealer=True)
        .prefetch_related(Prefetch("billbook", Order.objects.all(), to_attr="orders"))
        .values("username")
        .annotate(
            total_amount=Sum("orders__total_amount"),
            total_orders=Count("orders__pk"),
        )
    )

    print(data)



def export_data():
    with BytesIO() as output:
        SHEET_NAME = "Orders"
        excel_file = xlsxwriter.Workbook(output)
        worksheet = excel_file.add_worksheet(SHEET_NAME)
        data = Order.objects.all().values()
        write_orders_data(worksheet, excel_file, data)
        excel_file.close()
        output.seek(0)
        return output.read()
