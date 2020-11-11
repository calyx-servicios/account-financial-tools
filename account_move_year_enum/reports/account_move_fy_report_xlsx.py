# coding: utf-8
from datetime import datetime
import base64
import io

from odoo import models, _


class AccountMoveFYReport(models.AbstractModel):
    _name = "report.account_move_fiscal_year_id.account_move_fy_report_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, objs):

        #
        # Helper Method
        #
        def _format_date(date_utc_format):
            """Change the UTC format used by Odoo for dd-mm-yyyy

            Arguments:
                date_utc_format {str} -- Date UTC format yyyy-mm-dd

            Returns:
                str -- Date in dd-mm-yyyy format.
            """
            date_d_m_y_format = datetime.strptime(
                date_utc_format, "%Y-%m-%d"
            ).strftime("%d-%m-%Y")
            return date_d_m_y_format

        #
        # Formatting
        #
        heading_format = workbook.add_format(
            {
                "align": "center",
                "valign": "vcenter",
                "bold": True,
                "size": 12,
                "top": 1,
                "bottom": 1,
            }
        )

        heading_format_no_borders = workbook.add_format(
            {"align": "center", "valign": "vcenter", "bold": True, "size": 12}
        )

        sub_heading_format = workbook.add_format(
            {"align": "center", "valign": "vcenter", "bold": True, "size": 11,}
        )

        sub_heading_acc_format = workbook.add_format(
            {"align": "center", "valign": "vcenter", "bold": True, "size": 11,}
        )

        center_format = workbook.add_format(
            {"align": "center", "valign": "vcenter",}
        )

        monetary_format = workbook.add_format(
            {"num_format": "#,##0.00", "align": "center", "valign": "vcenter",}
        )

        date_range_format = workbook.add_format(
            {"align": "center", "valign": "vcenter", "bold": True, "size": 12,}
        )

        #
        # Adding Sheet
        #
        column = 0
        row = 0
        worksheet = workbook.add_worksheet(_("Account Moves"))

        #
        # Width of the Columns
        #
        worksheet.set_column(row, column, 16)
        worksheet.set_column(row + 1, column + 1, 35)
        worksheet.set_column(row + 2, column + 2, 60)
        worksheet.set_column(row + 3, column + 3, 23)
        worksheet.set_column(row + 4, column + 4, 23)
        worksheet.set_column(row + 5, column + 4, 23)
        worksheet.set_column(row + 6, column + 4, 23)
        worksheet.set_column(row + 7, column + 4, 23)

        #
        # Account Moves Query and Titles
        #
        imgdata = base64.b64decode(self.env.user.company_id.logo)
        image = io.BytesIO(imgdata)

        worksheet.insert_image(
            "A1:B4",
            "myimage.png",
            {"image_data": image, "x_scale": 0.53, "y_scale": 0.35},
        )

        if objs.by_period:
            worksheet.merge_range(
                "C1:C2", _("Journal Ledger"), heading_format_no_borders
            )
            worksheet.write(row, column + 3, _("Date From"), heading_format)
            worksheet.write(row, column + 4, _("Date to"), heading_format)
            worksheet.write(
                row + 1,
                column + 3,
                _format_date(objs.date_from),
                heading_format_no_borders,
            )
            worksheet.write(
                row + 1,
                column + 4,
                _format_date(objs.date_to),
                heading_format_no_borders,
            )

            account_move_objs = self.env["account.move"].search(
                [
                    ("date", ">=", objs.date_from),
                    ("date", "<=", objs.date_to),
                    ("state", "=", "posted"),
                    ("company_id", "=", self.env.user.company_id.id),
                ],
                order="date asc, numeration asc",
            )
        else:
            worksheet.merge_range(
                "C1:C2",
                _("Journal Ledger %s") % objs.fiscal_year.display_name,
                heading_format_no_borders,
            )
            account_move_objs = self.env["account.move"].search(
                [
                    ("date", ">=", objs.fiscal_year.date_from),
                    ("date", "<=", objs.fiscal_year.date_to),
                    ("state", "=", "posted"),
                    ("numeration", "!=", 0),
                ],
                order="date asc, numeration asc",
            )

        #
        # Account Moves Manipulation
        #
        row += 5
        for move in account_move_objs:

            worksheet.write(row, column, "", heading_format)
            worksheet.write(
                row,
                column + 1,
                _("Move N° {}").format(move.numeration),
                heading_format,
            )
            worksheet.write(row, column + 2, move.display_name, heading_format)

            worksheet.write(
                row, column + 3, _format_date(move.date), heading_format
            )
            worksheet.write(row, column + 4, _("Reference"), heading_format)
            # Next three columns are just for estethics purposes
            worksheet.write(row, column + 5, "", heading_format)
            worksheet.write(row, column + 6, "", heading_format)
            worksheet.write(row, column + 7, "", heading_format)

            row += 1

            worksheet.write(
                row, column + 2, move.partner_id.name or "", center_format
            )
            worksheet.write(row, column + 4, move.ref or "")

            row += 1

            worksheet.write(
                row, column, _("Account Move Nº"), sub_heading_format
            )
            worksheet.write(row, column + 1, _("Account"), sub_heading_format)
            worksheet.write(
                row, column + 2, _("Account Name"), sub_heading_format
            )
            worksheet.write(
                row, column + 3, _("Move Description"), sub_heading_format
            )
            worksheet.write(
                row, column + 4, _("Currency Amount"), sub_heading_format
            )
            worksheet.write(row, column + 5, _("Currency"), sub_heading_format)
            worksheet.write(
                row, column + 6, _("Debit"), sub_heading_acc_format
            )
            worksheet.write(
                row, column + 7, _("Credit"), sub_heading_acc_format
            )

            row += 1

            for line in move.line_ids:
                worksheet.write(row, column, move.numeration, center_format)
                worksheet.write(
                    row, column + 1, line.account_id.code, center_format
                )
                worksheet.write(
                    row, column + 2, line.account_id.name, center_format
                )
                worksheet.write(
                    row, column + 3, line.name or "", center_format
                )
                worksheet.write(
                    row,
                    column + 4,
                    line.amount_currency or "",
                    monetary_format,
                )
                if line.currency_id.name and line.currency_id.name != "ARS":
                    worksheet.write(
                        row, column + 5, line.currency_id.name, center_format
                    )
                worksheet.write(
                    row, column + 6, line.debit or "", monetary_format
                )
                worksheet.write(
                    row, column + 7, line.credit or "", monetary_format
                )
                row += 1

            row += 1
