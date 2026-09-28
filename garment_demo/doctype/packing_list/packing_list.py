# Copyright (c) 2026, Nikunj
# Packing List controller

import frappe
from frappe.model.document import Document
from frappe.utils import cint


class PackingList(Document):
	def validate(self):
		self.total_cartons = len(self.carton_lines)
		self.total_packed_qty = sum(cint(c.qty_in_carton) for c in self.carton_lines)

		if self.total_packed_qty and self.passed_qty and self.total_packed_qty > self.passed_qty:
			frappe.throw(
				f"Packed qty ({self.total_packed_qty}) exceeds passed QC qty ({self.passed_qty}). "
				f"You cannot pack more than what passed final inspection."
			)

		if self.carton_lines and self.status == "Ready to Pack":
			self.status = "Cartons Assigned"

		if self.total_packed_qty and self.passed_qty and self.total_packed_qty == self.passed_qty:
			self.status = "Packed"
