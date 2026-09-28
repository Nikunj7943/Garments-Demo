# Copyright (c) 2026, Nikunj
# Stitching Line Entry controller
#
# This is the core "translate operations into ERP" example: garment lines are
# measured on efficiency%, not just output count, because two lines with the
# same output but different operator counts / shift hours are not performing
# the same. Efficiency = earned minutes / available minutes.

import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint


class StitchingLineEntry(Document):
	def validate(self):
		self.calculate_totals()
		self.calculate_efficiency()

	def calculate_totals(self):
		self.total_output_pcs = sum(cint(row.output_qty) for row in self.hourly_output)

	def calculate_efficiency(self):
		if not (self.operators_on_line and self.shift_hours and self.total_output_pcs):
			self.line_efficiency_pct = 0
			return

		target_smv = frappe.db.get_value("Garment Style", self.style, "target_smv")
		if not target_smv:
			frappe.msgprint(
				"Target SMV is not set on this Style — efficiency cannot be calculated. "
				"Set it once during style setup and every line entry after that "
				"auto-calculates.",
				indicator="orange",
			)
			self.line_efficiency_pct = 0
			return

		earned_minutes = flt(target_smv) * self.total_output_pcs
		available_minutes = flt(self.operators_on_line) * flt(self.shift_hours) * 60

		if available_minutes:
			self.line_efficiency_pct = min((earned_minutes / available_minutes) * 100, 100)
