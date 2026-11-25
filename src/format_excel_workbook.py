
from pathlib import Path
from datetime import datetime

from openpyxl import load_workbook
from openpyxl.styles import (
    Font,
    PatternFill,
    Alignment,
    Border,
    Side
)
from openpyxl.utils import get_column_letter

# ==================================================
# PROJECT CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[1]

EXCEL_FILE = (
    BASE_DIR / "excel" / "annual_financial_data.xlsx"
)

if not EXCEL_FILE.exists():
    raise FileNotFoundError(
        f"Excel workbook not found: {EXCEL_FILE}"
    )

workbook = load_workbook(EXCEL_FILE)

# ==================================================
# PROFESSIONAL COLOR PALETTE
# ==================================================

NAVY_BLUE = "17365D"
LIGHT_BLUE = "EAF1F8"
WHITE = "FFFFFF"
DARK_TEXT = "243447"
BORDER_COLOR = "D9E2F3"

GREEN_FILL = "E2F0D9"
GREEN_TEXT = "375623"

YELLOW_FILL = "FFF2CC"
YELLOW_TEXT = "9C6500"

RED_FILL = "FCE4D6"
RED_TEXT = "9C0006"

FINANCIAL_FORMAT = '#,##0;[Red](#,##0);"-"'

# ==================================================
# REUSABLE STYLES
# ==================================================

header_fill = PatternFill(
    fill_type="solid",
    fgColor=NAVY_BLUE
)

header_font = Font(
    name="Calibri",
    size=11,
    bold=True,
    color=WHITE
)

body_font = Font(
    name="Calibri",
    size=11,
    color=DARK_TEXT
)

light_fill = PatternFill(
    fill_type="solid",
    fgColor=LIGHT_BLUE
)

white_fill = PatternFill(
    fill_type="solid",
    fgColor=WHITE
)

bottom_border = Border(
    bottom=Side(
        style="thin",
        color=BORDER_COLOR
    )
)

# ==================================================
# VALIDATION STATUS FORMATTING
# ==================================================

def format_status(cell):

    status = str(cell.value).strip().upper()

    if status in {"PASS", "VERIFIED"}:

        fill_color = GREEN_FILL
        font_color = GREEN_TEXT

    elif status == "FAIL":

        fill_color = RED_FILL
        font_color = RED_TEXT

    elif (
        "WARNING" in status
        or "PENDING" in status
        or "PROVISIONAL" in status
        or "CONDITIONAL" in status
        or "REVIEW REQUIRED" in status
    ):

        fill_color = YELLOW_FILL
        font_color = YELLOW_TEXT

    else:
        return

    cell.fill = PatternFill(
        fill_type="solid",
        fgColor=fill_color
    )

    cell.font = Font(
        name="Calibri",
        size=11,
        bold=True,
        color=font_color
    )


# ==================================================
# FORMAT ALL WORKSHEETS
# ==================================================

print("=" * 70)
print("PROFESSIONAL EXCEL WORKBOOK FORMATTING")
print("=" * 70)

for sheet in workbook.worksheets:

    print(f"\nFormatting worksheet: {sheet.title}")

    # Hide default gridlines

    sheet.sheet_view.showGridLines = False

    # Freeze header row

    sheet.freeze_panes = "A2"

    # Enable column filters

    sheet.auto_filter.ref = sheet.dimensions

    # Format header row

    sheet.row_dimensions[1].height = 32

    for cell in sheet[1]:

        cell.fill = header_fill
        cell.font = header_font

        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True
        )

    # Identify column headings

    headers = {
        cell.column: str(cell.value).lower()
        for cell in sheet[1]
        if cell.value is not None
    }

    # Format body rows

    for row in sheet.iter_rows(min_row=2):

        sheet.row_dimensions[row[0].row].height = 22

        for cell in row:

            cell.font = body_font

            cell.fill = (
                light_fill
                if cell.row % 2 == 0
                else white_fill
            )

            cell.border = bottom_border

            cell.alignment = Alignment(
                vertical="center"
            )

            column_name = headers.get(
                cell.column, ""
            )

            # Format status columns

            if column_name in {
                "status",
                "review_status"
            }:

                format_status(cell)

            # Format financial values

            if sheet.title == "Financial Data":

                if (
                    cell.column >= 6
                    and isinstance(
                        cell.value, (int, float)
                    )
                ):

                    cell.number_format = (
                        FINANCIAL_FORMAT
                    )

                    cell.alignment = Alignment(
                        horizontal="right",
                        vertical="center"
                    )

                # Format fiscal year-end dates

                if (
                    column_name == "fiscal_year_end"
                    and cell.value is not None
                ):

                    if isinstance(cell.value, str):

                        cell.value = (
                            datetime.strptime(
                                cell.value,
                                "%Y-%m-%d"
                            ).date()
                        )

                    cell.number_format = "yyyy-mm-dd"

                # Center metadata columns

                if column_name in {
                    "ticker",
                    "fiscal_year",
                    "fiscal_year_end",
                    "currency"
                }:

                    cell.alignment = Alignment(
                        horizontal="center",
                        vertical="center"
                    )

            # Format reconciliation amounts

            if column_name in {
                "original_value",
                "reconciled_value"
            }:

                if isinstance(
                    cell.value, (int, float)
                ):

                    cell.number_format = (
                        FINANCIAL_FORMAT
                    )

    # ==================================================
    # AUTOMATIC COLUMN WIDTHS
    # ==================================================

    for column in sheet.columns:

        column_letter = get_column_letter(
            column[0].column
        )

        max_length = 0

        for cell in column:

            if cell.value is not None:

                value_length = len(
                    str(cell.value)
                )

                max_length = max(
                    max_length,
                    value_length
                )

        if sheet.title == "Financial Data":

            adjusted_width = min(
                max(max_length + 4, 15),
                32
            )

        else:

            adjusted_width = min(
                max(max_length + 4, 15),
                65
            )

        sheet.column_dimensions[
            column_letter
        ].width = adjusted_width

    # Wrap long descriptions and notes

    if sheet.title != "Financial Data":

        for row in sheet.iter_rows(min_row=2):

            required_lines = 1

            for cell in row:

                if isinstance(cell.value, str):

                    column_letter = (
                        get_column_letter(
                            cell.column
                        )
                    )

                    width = sheet.column_dimensions[
                        column_letter
                    ].width

                    estimated_lines = max(
                        1,
                        int(
                            len(cell.value)
                            / max(width - 5, 1)
                        ) + 1
                    )

                    required_lines = max(
                        required_lines,
                        estimated_lines
                    )

                    cell.alignment = Alignment(
                        vertical="center",
                        wrap_text=True
                    )

            sheet.row_dimensions[
                row[0].row
            ].height = max(
                22,
                required_lines * 16
            )

    print(
        f"Rows: {sheet.max_row - 1} | "
        f"Columns: {sheet.max_column}"
    )

    print("Formatting completed.")

# ==================================================
# FINANCIAL DATA SHEET CUSTOMIZATION
# ==================================================

financial_sheet = workbook["Financial Data"]

# Freeze header and metadata columns A-E

financial_sheet.freeze_panes = "F2"

financial_sheet.sheet_view.zoomScale = 85

financial_sheet.sheet_properties.tabColor = NAVY_BLUE

# ==================================================
# WORKSHEET TAB COLORS
# ==================================================

TAB_COLORS = {
    "Financial Data": "17365D",
    "Data Dictionary": "4472C4",
    "Validation Report": "70AD47",
    "Debt Reconciliation": "ED7D31",
    "Data Quality Notes": "FFC000"
}

for sheet_name, color in TAB_COLORS.items():

    if sheet_name in workbook.sheetnames:

        workbook[
            sheet_name
        ].sheet_properties.tabColor = color

# Set Financial Data as the active worksheet

workbook.active = workbook.sheetnames.index(
    "Financial Data"
)

# ==================================================
# SAVE FORMATTED WORKBOOK
# ==================================================

workbook.save(EXCEL_FILE)

# ==================================================
# DISPLAY FORMATTING SUMMARY
# ==================================================

print("\n" + "=" * 70)
print("EXCEL FORMATTING SUMMARY")
print("=" * 70)

print(
    f"Worksheets formatted: "
    f"{len(workbook.sheetnames)}"
)

print("Professional headers: Applied")
print("Alternating row colors: Applied")
print("Financial number formats: Applied")
print("Negative number formatting: Applied")
print("Automatic column widths: Applied")
print("Column filters: Enabled")
print("Freeze panes: Enabled")
print("Validation status colors: Applied")
print("Worksheet tab colors: Applied")
print("Gridlines: Hidden")

print(f"\nFormatted workbook: {EXCEL_FILE}")

print(
    "\nProfessional Excel formatting "
    "completed successfully."
)
