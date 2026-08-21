import json
import os
import math

import geopandas as gpd
import pandas as pd


FWI_FILE = "data/fwi_fars.json"

PROTECTED_FILE = "protected_areas.geojson"

HUNTING_FILE = "hunting_banned.geojson"

OUTPUT_FILE = "data/FARS_FWI_GeoReport.xlsx"


# =========================================================
# طبقه‌بندی خطر FWI
# =========================================================

def fwi_class(value):

    if value < 11.2:
        return "کم"

    if value < 21.3:
        return "متوسط"

    if value < 38:
        return "زیاد"

    if value < 50:
        return "خیلی زیاد"

    if value <= 70:
        return "شدید"

    return "بسیار شدید"


# =========================================================
# پیدا کردن نام منطقه
# =========================================================

def get_name(properties):

    if not properties:
        return "بدون نام"

    possible_names = [
        "name",
        "NAME",
        "Name",
        "NAME_1",
        "NAME_2",
        "Name_1",
        "Name_2",
        "title",
        "TITLE",
        "site_name",
        "SITE_NAME",
        "area_name",
        "AREA_NAME",
        "نام",
        "نام منطقه",
        "نام_منطقه"
    ]

    for key in possible_names:

        if key in properties:

            value = properties[key]

            if (
                value is not None
                and str(value).strip() != ""
            ):

                return str(value).strip()

    for value in properties.values():

        if (
            isinstance(value, str)
            and len(value.strip()) > 2
        ):

            return value.strip()

    return "بدون نام"


# =========================================================
# خواندن FWI
# =========================================================

print("Loading FWI...")

with open(
    FWI_FILE,
    encoding="utf-8"
) as f:

    fwi_data = json.load(f)


forecast_gregorian = (
    fwi_data["forecast_gregorian"]
)

forecast_shamsi = (
    fwi_data["forecast_shamsi"]
)

points = fwi_data.get(
    "points",
    []
)


# =========================================================
# تبدیل نقاط به GeoDataFrame
# =========================================================

fwi_rows = []

for point in points:

    lat = float(
        point["lat"]
    )

    lon = float(
        point["lon"]
    )

    value = float(
        point["fwi"]
    )

    if not math.isfinite(value):
        continue

    fwi_rows.append({
        "lat": lat,
        "lon": lon,
        "fwi": value
    })


fwi_gdf = gpd.GeoDataFrame(
    fwi_rows,
    geometry=gpd.points_from_xy(
        [p["lon"] for p in fwi_rows],
        [p["lat"] for p in fwi_rows]
    ),
    crs="EPSG:4326"
)


print(
    "FWI points:",
    len(fwi_gdf)
)


# =========================================================
# خواندن لایه‌های مکانی
# =========================================================

layers = []


# ---------------------------------------------------------
# مناطق حفاظت‌شده / چهارگانه
# ---------------------------------------------------------

if os.path.exists(
    PROTECTED_FILE
):

    print(
        "Loading:",
        PROTECTED_FILE
    )

    protected = gpd.read_file(
        PROTECTED_FILE
    )

    if protected.crs is None:

        protected = protected.set_crs(
            "EPSG:4326"
        )

    else:

        protected = protected.to_crs(
            "EPSG:4326"
        )


    protected["نوع محدوده"] = (
        "مناطق حفاظت‌شده"
    )


    protected["نام منطقه"] = (
        protected["geometry"]
        .apply(
            lambda geometry:
            "بدون نام"
        )
    )


    for idx, row in protected.iterrows():

        properties = row.drop(
            labels=["geometry"],
            errors="ignore"
        ).to_dict()

        protected.at[
            idx,
            "نام منطقه"
        ] = get_name(
            properties
        )


    layers.append(
        protected[
            [
                "نام منطقه",
                "نوع محدوده",
                "geometry"
            ]
        ]
    )


# ---------------------------------------------------------
# شکار ممنوع
# ---------------------------------------------------------

if os.path.exists(
    HUNTING_FILE
):

    print(
        "Loading:",
        HUNTING_FILE
    )

    hunting = gpd.read_file(
        HUNTING_FILE
    )

    if hunting.crs is None:

        hunting = hunting.set_crs(
            "EPSG:4326"
        )

    else:

        hunting = hunting.to_crs(
            "EPSG:4326"
        )


    hunting["نوع محدوده"] = (
        "مناطق ممنوعه شکار"
    )


    hunting["نام منطقه"] = (
        hunting["geometry"]
        .apply(
            lambda geometry:
            "بدون نام"
        )
    )


    for idx, row in hunting.iterrows():

        properties = row.drop(
            labels=["geometry"],
            errors="ignore"
        ).to_dict()

        hunting.at[
            idx,
            "نام منطقه"
        ] = get_name(
            properties
        )


    layers.append(
        hunting[
            [
                "نام منطقه",
                "نوع محدوده",
                "geometry"
            ]
        ]
    )


# =========================================================
# اگر هیچ محدوده‌ای نبود
# =========================================================

if not layers:

    raise RuntimeError(
        "No spatial boundary files found."
    )


# =========================================================
# ترکیب محدوده‌ها
# =========================================================

areas = gpd.GeoDataFrame(
    pd.concat(
        layers,
        ignore_index=True
    ),
    crs="EPSG:4326"
)


# =========================================================
# محاسبه گزارش هر منطقه
# =========================================================

report = []


for idx, area in areas.iterrows():

    name = (
        area["نام منطقه"]
    )

    area_type = (
        area["نوع محدوده"]
    )

    geometry = (
        area.geometry
    )

    if geometry is None:
        continue


    # نقاط داخل محدوده
    mask = (
        fwi_gdf.geometry
        .within(geometry)
    )

    selected = (
        fwi_gdf.loc[mask]
    )


    if selected.empty:

        report.append({

            "نام منطقه":
                name,

            "نوع محدوده":
                area_type,

            "تاریخ شمسی":
                forecast_shamsi,

            "تاریخ میلادی":
                forecast_gregorian,

            "تعداد نقاط FWI":
                0,

            "حداقل FWI":
                None,

            "میانگین FWI":
                None,

            "حداکثر FWI":
                None,

            "طبقه خطر":
                "بدون داده"

        })

        continue


    values = (
        selected["fwi"]
        .astype(float)
        .tolist()
    )


    minimum = min(
        values
    )

    maximum = max(
        values
    )

    mean = (
        sum(values)
        /
        len(values)
    )


    # طبقه خطر براساس میانگین
    risk = fwi_class(
        mean
    )


    report.append({

        "نام منطقه":
            name,

        "نوع محدوده":
            area_type,

        "تاریخ شمسی":
            forecast_shamsi,

        "تاریخ میلادی":
            forecast_gregorian,

        "تعداد نقاط FWI":
            len(values),

        "حداقل FWI":
            round(
                minimum,
                2
            ),

        "میانگین FWI":
            round(
                mean,
                2
            ),

        "حداکثر FWI":
            round(
                maximum,
                2
            ),

        "طبقه خطر":
            risk

    })


# =========================================================
# ساخت DataFrame
# =========================================================

report_df = pd.DataFrame(
    report
)


# =========================================================
# مرتب‌سازی
# =========================================================

risk_order = {
    "بسیار شدید": 6,
    "شدید": 5,
    "خیلی زیاد": 4,
    "زیاد": 3,
    "متوسط": 2,
    "کم": 1,
    "بدون داده": 0
}


report_df["_order"] = (
    report_df["طبقه خطر"]
    .map(risk_order)
    .fillna(0)
)


report_df = (
    report_df
    .sort_values(
        [
            "_order",
            "میانگین FWI"
        ],
        ascending=[
            False,
            False
        ]
    )
    .drop(
        columns=["_order"]
    )
)


# =========================================================
# خروجی Excel
# =========================================================

os.makedirs(
    "data",
    exist_ok=True
)


with pd.ExcelWriter(
    OUTPUT_FILE,
    engine="xlsxwriter"
) as writer:

    report_df.to_excel(
        writer,
        sheet_name="گزارش مناطق",
        index=False
    )


    workbook = (
        writer.book
    )

    worksheet = (
        writer.sheets["گزارش مناطق"]
    )


    # -----------------------------------------------------
    # قالب‌ها
    # -----------------------------------------------------

    header_format = (
        workbook.add_format({

            "bold": True,

            "font_color": "white",

            "bg_color": "#9E1B1B",

            "align": "center",

            "valign": "vcenter",

            "border": 1
        })
    )


    text_format = (
        workbook.add_format({

            "align": "right",

            "valign": "vcenter",

            "border": 1
        })
    )


    number_format = (
        workbook.add_format({

            "num_format": "0.00",

            "align": "center",

            "border": 1
        })
    )


    date_format = (
        workbook.add_format({

            "align": "center",

            "border": 1
        })
    )


    # -----------------------------------------------------
    # هدر
    # -----------------------------------------------------

    for col, value in enumerate(
        report_df.columns
    ):

        worksheet.write(
            0,
            col,
            value,
            header_format
        )


    # -----------------------------------------------------
    # عرض ستون‌ها
    # -----------------------------------------------------

    widths = {

        "A:A": 28,
        "B:B": 22,
        "C:D": 17,
        "E:E": 16,
        "F:H": 15,
        "I:I": 20
    }


    for columns, width in widths.items():

        worksheet.set_column(
            columns,
            width
        )


    # -----------------------------------------------------
    # فریز هدر
    # -----------------------------------------------------

    worksheet.freeze_panes(
        1,
        0
    )


    # -----------------------------------------------------
    # Autofilter
    # -----------------------------------------------------

    worksheet.autofilter(
        0,
        0,
        len(report_df),
        len(report_df.columns) - 1
    )


    # -----------------------------------------------------
    # رنگ‌بندی طبقه خطر
    # -----------------------------------------------------

    risk_col = (
        report_df.columns
        .get_loc(
            "طبقه خطر"
        )
    )


    first_data_row = 1

    last_data_row = len(
        report_df
    )


    worksheet.conditional_format(
        first_data_row,
        risk_col,
        last_data_row,
        risk_col,
        {
            "type": "text",
            "criteria": "containing",
            "value": "بسیار شدید",
            "format": workbook.add_format({
                "bg_color": "#4A235A",
                "font_color": "#FFFFFF"
            })
        }
    )


    worksheet.conditional_format(
        first_data_row,
        risk_col,
        last_data_row,
        risk_col,
        {
            "type": "text",
            "criteria": "containing",
            "value": "شدید",
            "format": workbook.add_format({
                "bg_color": "#8E44AD",
                "font_color": "#FFFFFF"
            })
        }
    )


    worksheet.conditional_format(
        first_data_row,
        risk_col,
        last_data_row,
        risk_col,
        {
            "type": "text",
            "criteria": "containing",
            "value": "خیلی زیاد",
            "format": workbook.add_format({
                "bg_color": "#E74C3C",
                "font_color": "#FFFFFF"
            })
        }
    )


    worksheet.conditional_format(
        first_data_row,
        risk_col,
        last_data_row,
        risk_col,
        {
            "type": "text",
            "criteria": "containing",
            "value": "زیاد",
            "format": workbook.add_format({
                "bg_color": "#E67E22",
                "font_color": "#FFFFFF"
            })
        }
    )


print("================================")
print("FWI GEO REPORT READY")
print("================================")

print(
    "File:",
    OUTPUT_FILE
)

print(
    "Regions:",
    len(report_df)
)

print("================================")
