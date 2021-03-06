# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, math
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document

from erpnext.hr.doctype.employee_loan.employee_loan import get_monthly_repayment_amount, check_repayment_method

class EmployeeLoanApplication(Document):
	def validate(self):
		check_repayment_method(self.repayment_method, self.loan_amount, self.repayment_amount, self.repayment_periods)
		self.validate_loan_amount()
		self.get_repayment_details()

	def validate_loan_amount(self):
		maximum_loan_limit = frappe.db.get_value('Loan Type', self.loan_type, 'maximum_loan_amount')
		if self.loan_amount > maximum_loan_limit:
			frappe.throw(_("Loan Amount cannot exceed Maximum Loan Amount of {0}").format(maximum_loan_limit))

	def get_repayment_details(self):
		if self.repayment_method == "Repay Over Number of Periods":
			self.repayment_amount = get_monthly_repayment_amount(self.repayment_method, self.loan_amount, self.rate_of_interest, self.repayment_periods)

		if self.repayment_method == "Repay Fixed Amount per Period":
			monthly_interest_rate = flt(self.rate_of_interest) / (12 *100)
			self.repayment_periods = math.ceil((math.log(self.repayment_amount) - math.log(self.repayment_amount - \
									(self.loan_amount*monthly_interest_rate)))/(math.log(1+monthly_interest_rate)))

		self.total_payable_amount = self.repayment_amount * self.repayment_periods
		self.total_payable_interest = self.total_payable_amount - self.loan_amount