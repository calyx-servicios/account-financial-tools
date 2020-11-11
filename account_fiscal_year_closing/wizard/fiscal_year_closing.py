# coding: utf-8
from datetime import datetime
from datetime import timedelta
from calendar import monthrange
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class FiscalYearClosing(models.TransientModel):
    _name = "account.fiscal.year.closing"

    @api.multi
    def _default_equity_accounts(self):
        type_equity = self.env.ref(
            "account.data_account_type_equity"
        ).id
        return [("user_type_id", "=", type_equity)]

    fiscal_year = fields.Many2one("account.fiscal.year", required=True)
    date_from = fields.Date(
        "Date From", related="fiscal_year.date_from"
    )
    date_to = fields.Date("Date To", related="fiscal_year.date_to")
    date_origin = fields.Date("Origin date")
    account_account_id = fields.Many2one(
        "account.account",
        string="Capital Acount",
        domain=_default_equity_accounts,
    )

    fiscal_year_closing = fields.Boolean(
        "Fiscal Year Closing", default=False
    )
    fiscal_year_opening = fields.Boolean(
        "Fiscal Year Opening", default=False
    )

    recasting_acc_move = fields.Boolean("Recasting", default=False)
    consolidation_acc_move = fields.Boolean(
        "Consolidation Results", default=False
    )
    closing_equity_move = fields.Boolean(
        "Equity Closing", default=False
    )

    opening_fiscal_year = fields.Many2one(
        "account.fiscal.year", string="Opening Fiscal Year"
    )
    opening_date_from = fields.Date(
        "Opening Date From", related="opening_fiscal_year.date_from"
    )
    opening_date_to = fields.Date(
        "Opening Date To", related="opening_fiscal_year.date_to"
    )

    @api.onchange("fiscal_year")
    def _onchange_fiscal_year(self):
        for record in self:
            if record.fiscal_year:
                record.opening_fiscal_year = False
                datee = datetime.strptime(record.date_to, "%Y-%m-%d")
                month = datee.month
                year = datee.year
                lst_day_month = str(monthrange(year, month)[1])
                date_one = (
                    str(year) + "-" + str(month) + "-" + lst_day_month
                )
                record.date_origin = datetime.strptime(
                    date_one, "%Y-%m-%d"
                )
            if not record.fiscal_year:
                record.date_origin = False

    @api.onchange("date_origin")
    def _onchange_date_origin(self):
        for record in self:
            if record.fiscal_year:
                datee = datetime.strptime(
                    record.date_origin, "%Y-%m-%d"
                )
                month_origin = datee.month
                year_origin = datee.year

                date_fy = datetime.strptime(record.date_to, "%Y-%m-%d")
                month_fy = date_fy.month
                year_fy = date_fy.year

                error_string = (
                    _(
                        "The origin date has to be in the same month (%s) \
                    and the same year (%s) that \
                    the date to from the fiscal year."
                    )
                    % (month_fy, year_fy)
                )

                if (month_origin != month_fy) or (
                    year_origin != year_fy
                ):
                    lst_day_month = str(
                        monthrange(year_fy, month_fy)[1]
                    )
                    date_one = (
                        str(year_fy)
                        + "-"
                        + str(month_fy)
                        + "-"
                        + lst_day_month
                    )
                    record.date_origin = datetime.strptime(
                        date_one, "%Y-%m-%d"
                    )
                    self.env.user.notify_warning(error_string, "Error")

    @api.onchange("recasting_acc_move")
    def _onchange_recasting_acc_move(self):
        for record in self:
            if record.closing_equity_move and record.recasting_acc_move:
                record.consolidation_acc_move = True
            if record.recasting_acc_move and record.fiscal_year_opening:
                record.consolidation_acc_move = True
                record.closing_equity_move = True

    @api.onchange("consolidation_acc_move")
    def _onchange_consolidation_acc_move(self):
        for record in self:
            if (
                not record.consolidation_acc_move
                and record.closing_equity_move
                and record.recasting_acc_move
            ):
                record.consolidation_acc_move = True
            elif not record.consolidation_acc_move:
                record.account_account_id = False

            if (
                record.consolidation_acc_move
                and record.fiscal_year_opening
            ):
                record.closing_equity_move = True

    @api.onchange("closing_equity_move")
    def _onchange_closing_equity_move(self):
        for record in self:
            if record.closing_equity_move and record.recasting_acc_move:
                record.consolidation_acc_move = True
            if (
                not record.closing_equity_move
                and record.fiscal_year_opening
            ):
                record.closing_equity_move = True

    @api.onchange("fiscal_year_opening")
    def _onchange_fiscal_year_opening(self):
        for record in self:
            if record.fiscal_year_opening and record.recasting_acc_move:
                record.consolidation_acc_move = True
                record.closing_equity_move = True

            if (
                record.fiscal_year_opening
                and record.consolidation_acc_move
            ):
                record.closing_equity_move = True

    @api.onchange("opening_fiscal_year")
    def _onchange_opening_fiscal_year(self):
        for record in self:
            if record.opening_fiscal_year and record.fiscal_year:
                error_string = _(
                    "The opening date from in opening fiscal year \
                        have to be one day exactly after date to \
                            in closing fiscal year."
                )
                day_init = fields.Date.from_string(
                    record.date_to
                ) + timedelta(days=1)
                day_init = fields.Date.to_string(day_init)
                if record.opening_date_from != day_init:
                    self.env.user.notify_warning(error_string, "Error")
                    record.opening_fiscal_year = False

    @api.multi
    def confirm(self):

        acc_move_ids = []

        if self.consolidation_acc_move:
            if not self.account_account_id:
                raise UserError(
                    _(
                        "You have to choose a account \
                    for this process."
                    )
                )

        if self.recasting_acc_move:
            recasting_move_id = self._recasting_process()
            acc_move_ids.append(recasting_move_id.id)
        if self.consolidation_acc_move:
            consolidation_move_id = self._consolidation_process()
            acc_move_ids.append(consolidation_move_id.id)
        if self.closing_equity_move:
            closing_equity_id = self._equity_closing_process()
            acc_move_ids.append(closing_equity_id.id)
        if self.fiscal_year_opening:
            opening_equity_id = self._equity_opening_fiscal_year()
            acc_move_ids.append(opening_equity_id.id)
            self.fiscal_year.fiscal_year_close = True
            fy_string = _("The fiscal year (%r) was blocked.") % (
                self.fiscal_year.name
            )
            self.env.user.notify_info(fy_string, "Info")

        if (
            not self.recasting_acc_move
            and not self.consolidation_acc_move
            and not self.closing_equity_move
            and not self.fiscal_year_opening
        ):
            error_string = _("You have to select at lest one option.")
            raise UserError(error_string)

        # domain = [
        #     "&",
        #     "|",
        #     ("fiscal_year", "=", self.fiscal_year.id),
        #     ("fiscal_year", "=", self.opening_fiscal_year.id),
        #     "|",
        #     ("fy_closing_acc_move", "=", True),
        #     ("fy_opening_acc_move", "=", True),
        # ]
        domain = [("id", "in", acc_move_ids)]
        view_tree = self.env.ref("account.view_move_tree").id
        view_form = self.env.ref("account.view_move_form").id

        return {
            "type": "ir.actions.act_window",
            "name": _("Closing Fiscal Year"),
            "views": [[view_tree, "tree"], [view_form, "form"]],
            "res_model": "account.move",
            "domain": domain,
            "target": "current",
        }

    @api.multi
    def remove_moves(self):
        account_move_id = False

        if self.recasting_acc_move:
            account_move_id = self._get_fy_move("closing_recasting")
            account_move_id += self._get_fy_move(
                "closing_consolidation"
            )
            account_move_id += self._get_fy_move("closing_equity")
            account_move_id += self._get_fy_move("opening_move")

        elif (
            self.consolidation_acc_move
            and not self.closing_equity_move
            and not self.fiscal_year_opening
        ):
            account_move_id = self._get_fy_move("closing_consolidation")
            account_move_id += self._get_fy_move("closing_equity")
            account_move_id += self._get_fy_move("opening_move")

        elif self.closing_equity_move and not self.fiscal_year_opening:
            account_move_id = self._get_fy_move("closing_equity")
            account_move_id += self._get_fy_move("opening_move")

        elif self.fiscal_year_opening:
            account_move_id = self._get_fy_move("opening_move_check")

        if account_move_id:

            for move in account_move_id:
                move.button_cancel()
                remove_string = (
                    _(
                        "The move (%r) for the fiscal year (%r) \
                        was remove."
                    )
                    % (move.name, self.fiscal_year.name)
                )
                self.env.user.notify_info(remove_string, "Info")
                move.unlink()

            self.fiscal_year.fiscal_year_close = False
            fy_string = _(
                "You can register move in the fiscal year (%r)"
            ) % (self.fiscal_year.name)
            self.env.user.notify_info(fy_string, "Info")

        else:
            error_string = (
                _("There is not moves for the fiscal year (%r)")
                % self.fiscal_year.name
            )
            raise ValidationError(error_string)

        if (
            not self.recasting_acc_move
            and not self.consolidation_acc_move
            and not self.closing_equity_move
            and not self.fiscal_year_opening
        ):
            error_string = _("You have to select at lest one option.")
            raise UserError(error_string)

    def _recasting_process(self):
        type_move = "closing_recasting"

        acc_result_ids = self._get_result_accounts()
        account_move_id = self._get_fy_move(type_move)
        account_account_obj = self.env["account.account"]
        acc_recasting = account_account_obj.search(
            [("recasting_account", "=", True)], limit=1
        )

        final_balance = 0

        if account_move_id:
            error_string = (
                _(
                    "Already exist another recasting move for this fiscal year (%r) \
                        please remove it before continue."
                )
                % (account_move_id.name)
            )
            raise ValidationError(error_string)

        if not acc_recasting:
            raise UserError(
                _(
                    "You have to assign a account for the recasting exercise \
                        before continue."
                )
            )

        final_debit, final_credit, moves = self._prepare_acc_move_line(
            acc_result_ids, type_move
        )

        final_balance = abs(final_debit - final_credit)

        moves += [
            (
                0,
                0,
                {
                    "account_id": acc_recasting.id,
                    "name": _("Recasting Exercise"),
                    "debit": final_balance
                    if (final_credit > final_debit)
                    else 0,
                    "credit": final_balance
                    if (final_debit > final_credit)
                    else 0,
                },
            )
        ]

        new_move = self._create_move(moves, type_move)

        return new_move

    def _consolidation_process(self):
        consolidation_move = []
        acc_move_line_obj = self.env["account.move.line"]
        account_account_obj = self.env["account.account"]
        type_move = "closing_consolidation"
        account_move_id = self._get_fy_move(type_move)

        if account_move_id:
            error_string = (
                _(
                    "Already exist another consolidation results move \
                        for this fiscal year (%r) \
                        please remove it before continue."
                )
                % (account_move_id.name)
            )
            raise ValidationError(error_string)

        type_move = "closing_recasting"
        account_move_id = self._get_fy_move(type_move)
        acc_recasting = account_account_obj.search(
            [("recasting_account", "=", True)], limit=1
        )
        if not account_move_id:
            error_string = _(
                "For this process you need to recasting move \
                for this fiscal year."
            )
            raise UserError(error_string)
        else:
            move_id = acc_move_line_obj.search(
                [
                    ("account_id", "=", acc_recasting.id),
                    ("move_id.id", "=", account_move_id.id),
                ],
                limit=1,
            )

        final_balance = (
            move_id.credit if (move_id.credit != 0.0) else move_id.debit
        )

        type_move = "closing_consolidation"

        consolidation_move += [
            (
                0,
                0,
                {
                    "account_id": acc_recasting.id,
                    "name": _("Consolidation Results"),
                    "credit": final_balance
                    if (move_id.debit > move_id.credit)
                    else 0,
                    "debit": final_balance
                    if (move_id.credit > move_id.debit)
                    else 0,
                },
            )
        ]

        consolidation_move += [
            (
                0,
                0,
                {
                    "account_id": self.account_account_id.id,
                    "name": _("Consolidation Results"),
                    "credit": final_balance
                    if (move_id.credit > move_id.debit)
                    else 0,
                    "debit": final_balance
                    if (move_id.debit > move_id.credit)
                    else 0,
                },
            )
        ]

        new_move = self._create_move(consolidation_move, type_move)

        return new_move

    def _equity_closing_process(self):
        acc_result_ids = self._get_result_accounts()

        type_move = "closing_consolidation"
        account_move_id = self._get_fy_move(type_move)

        if not account_move_id:
            error_string = _(
                "For this process you need to consolidation results move \
                for this fiscal year."
            )
            raise UserError(error_string)

        type_move = "closing_equity"
        account_move_id = self._get_fy_move(type_move)
        if account_move_id:
            error_string = (
                _(
                    "Already exist another equity closing move \
                        for this fiscal year (%r) \
                        please remove it before continue."
                )
                % (account_move_id.name)
            )
            raise ValidationError(error_string)

        unaffected_earnings = self.env.ref(
            "account.data_unaffected_earnings"
        )
        acc_result_ids.append(unaffected_earnings.id)

        final_debit, final_credit, moves = self._prepare_acc_move_line(
            acc_result_ids, type_move
        )

        new_move = self._create_move(moves, type_move)
        return new_move

    def _create_move(self, moves, type_move):
        account_move_obj = self.env["account.move"]

        fiscal_year = self.fiscal_year.id
        closing_equity = False
        recasting = False
        consolidation = False
        opening = False
        closing = False
        journal_id = False
        ref = ""

        if type_move == "closing_recasting":
            journal_id = self.env["account.journal"].search(
                [("recasting_journal", "=", True)], limit=1
            )
            recasting = True
            closing = True
            ref = _("Recasting Process")
        elif type_move == "closing_consolidation":
            journal_id = self.env["account.journal"].search(
                [("consolidation_results_journal", "=", True)], limit=1
            )
            consolidation = True
            closing = True
            ref = _("Consolidation Process")
        elif type_move == "closing_equity":
            journal_id = self.env["account.journal"].search(
                [("equity_closing_journal", "=", True)], limit=1
            )
            closing_equity = True
            closing = True
            ref = _("Equity Closing Process")

        elif type_move == "opening_equity":
            journal_id = self.env["account.journal"].search(
                [("equity_opening_journal", "=", True)], limit=1
            )
            opening = True
            ref = _("Equity Opening Process")
            fiscal_year = self.opening_fiscal_year.id

        if not journal_id:
            raise UserError(
                _(
                    "You have to assign a journal for (%r) \
                        before continue."
                )
                % (ref)
            )

        values = {
            "date": self.date_origin,
            "journal_id": journal_id.id,
            "ref": ref,
            "fiscal_year": fiscal_year,
            "recasting_acc_move": recasting,
            "consolidation_acc_move": consolidation,
            "closing_equity_move": closing_equity,
            "fy_closing_acc_move": closing,
            "fy_opening_acc_move": opening,
            "line_ids": moves,
        }

        new_move = account_move_obj.create(values)
        new_move.post()

        return new_move

    def _get_result_accounts(self):
        acc_ids = []
        other_income = self.env.ref(
            "account.data_account_type_other_income"
        )
        acc_ids.append(other_income.id)

        revenue = self.env.ref("account.data_account_type_revenue")
        acc_ids.append(revenue.id)

        depreciation = self.env.ref(
            "account.data_account_type_depreciation"
        )
        acc_ids.append(depreciation.id)

        expenses = self.env.ref("account.data_account_type_expenses")
        acc_ids.append(expenses.id)

        direct_costs = self.env.ref(
            "account.data_account_type_direct_costs"
        )
        acc_ids.append(direct_costs.id)

        return acc_ids

    def _get_fy_move(self, type_move):
        account_move_obj = self.env["account.move"]

        if type_move == "closing_recasting":
            account_move_id = account_move_obj.search(
                [
                    ("fiscal_year", "=", self.fiscal_year.id),
                    ("recasting_acc_move", "=", True),
                ],
                limit=1,
            )
        elif type_move == "closing_consolidation":
            account_move_id = account_move_obj.search(
                [
                    ("fiscal_year", "=", self.fiscal_year.id),
                    ("consolidation_acc_move", "=", True),
                ],
                limit=1,
            )
        elif type_move == "closing_equity":
            account_move_id = account_move_obj.search(
                [
                    ("fiscal_year", "=", self.fiscal_year.id),
                    ("closing_equity_move", "=", True),
                ],
                limit=1,
            )
        elif type_move == "opening_move":
            fy_obj = self.env["account.fiscal.year"]
            fy_day_init = fields.Date.from_string(
                self.date_to
            ) + timedelta(days=1)
            fy_day_init = fields.Date.to_string(fy_day_init)
            fy_id = fy_obj.search([("date_from", "=", fy_day_init)])
            account_move_id = account_move_obj.search(
                [
                    ("fiscal_year", "=", fy_id.id),
                    ("fy_opening_acc_move", "=", True),
                ],
                limit=1,
            )
        elif type_move == "opening_move_check":
            account_move_id = account_move_obj.search(
                [
                    ("fiscal_year", "=", self.opening_fiscal_year.id),
                    ("fy_opening_acc_move", "=", True),
                ],
                limit=1,
            )
        return account_move_id

    def _equity_opening_fiscal_year(self):

        account_move_id = self._get_fy_move("closing_equity")

        if not account_move_id:
            error_string = _(
                "For this process you need create firts the closing equity move \
                for this fiscal year."
            )
            raise UserError(error_string)

        acc_result_ids = self._get_result_accounts()
        unaffected_earnings = self.env.ref(
            "account.data_unaffected_earnings"
        )
        acc_result_ids.append(unaffected_earnings.id)

        type_move = "opening_equity"

        final_debit, final_credit, moves = self._prepare_acc_move_line(
            acc_result_ids, type_move
        )

        new_move = self._create_move(moves, type_move)
        return new_move

    def _prepare_acc_move_line(self, acc_ids, type_search):
        account_account_obj = self.env["account.account"]
        acc_move_line_obj = self.env["account.move.line"]
        ref_name = ""

        if type_search == "closing_equity":
            accounts_ids = account_account_obj.search(
                [("user_type_id", "not in", acc_ids)],
                order="user_type_id",
            )
            ref_name = _("Equity Closing Exercise")

        elif type_search == "closing_recasting":
            accounts_ids = account_account_obj.search(
                [("user_type_id", "in", acc_ids)], order="user_type_id",
            )
            ref_name = _("Recasting Exercise")

        elif type_search == "opening_equity":
            accounts_ids = account_account_obj.search(
                [("user_type_id", "not in", acc_ids)],
                order="user_type_id",
            )
            ref_name = _("Equity Opening Exercise")

        moves = []
        final_debit = 0
        final_credit = 0
        error_string = ""

        for account in accounts_ids:
            debit = 0
            credit = 0
            balance = 0
            acc_move_line_ids = acc_move_line_obj.search(
                [
                    ("account_id", "=", account.id),
                    ("date", ">=", self.date_from),
                    ("date", "<=", self.date_to),
                    ("move_id.closing_equity_move", "=", False),
                ]
            )
            if acc_move_line_ids:
                for move in acc_move_line_ids:
                    error_string = (
                        _(
                            "At least one move isn't posted (%r), you have to validate all \
                            moves before continue"
                        )
                        % (move.move_id.name)
                    )
                    if move.move_id.state != "posted":
                        raise ValidationError(error_string)
                    if not move.move_id.fiscal_year:
                        move.move_id.fiscal_year = self.fiscal_year.id
                    debit += move.debit
                    credit += move.credit

            balance = debit - credit
            balance = float("{:.2f}".format(balance))
            final_debit += -balance if (balance < 0) else 0
            final_credit += balance if (balance > 0) else 0

            if balance != 0.0:
                if type_search == "opening_equity":
                    moves += [
                        (
                            0,
                            0,
                            {
                                "account_id": account.id,
                                "name": ref_name,
                                "date": self.opening_date_from,
                                "credit": -balance
                                if (balance < 0)
                                else 0,
                                "debit": balance
                                if (balance > 0)
                                else 0,
                            },
                        )
                    ]
                else:
                    moves += [
                        (
                            0,
                            0,
                            {
                                "account_id": account.id,
                                "name": ref_name,
                                "date": self.date_origin,
                                "debit": -balance
                                if (balance < 0)
                                else 0,
                                "credit": balance
                                if (balance > 0)
                                else 0,
                            },
                        )
                    ]

        return final_debit, final_credit, moves
