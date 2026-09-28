# Copyright (c) 2026, Nikunj
# Cutting Order controller
#
# Business rule (garment cutting floor): wastage% is never entered manually —
# it is derived from fabric actually consumed vs. panels actually cut, using
# the style's standard consumption. This keeps the number honest instead of
# letting the cutting master self-report a "good" wastage figure.

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class CuttingOrder(Document):
	def validate(self):
		self.calculate_wastage()
		self.set_status()

	def calculate_wastage(self):
		"""Wastage % = (fabric consumed - theoretical fabric need) / fabric consumed.

		Theoretical need is pulled from the standard consumption stored against
		the style's BOM (per-piece fabric qty * panels cut). If no BOM/rate is
		set up yet, we skip the calc rather than show a misleading 0%.
		"""
		if not (self.fabric_consumed_meters and self.panels_cut_qty):
			return

		per_piece_std = frappe.db.get_value(
			"Garment Style", self.style, "target_smv"
		)  # placeholder link point — in a real build this reads a
		   # "standard_fabric_consumption" field on the BOM/Style instead of SMV

		std_consumption_field = frappe.db.get_value(
			"BOM",
			frappe.db.get_value("Garment Style", self.style, "bom"),
			"quantity",
		) if frappe.db.get_value("Garment Style", self.style, "bom") else None

		if not std_consumption_field:
			return

		theoretical_need = flt(std_consumption_field) * flt(self.panels_cut_qty)
		if theoretical_need:
			wastage = (flt(self.fabric_consumed_meters) - theoretical_need) / flt(
				self.fabric_consumed_meters
			) * 100
			self.fabric_wastage_pct = max(wastage, 0)

	def set_status(self):
		if self.docstatus == 1 and self.status == "Draft":
			self.status = "Cutting In Progress"

	def on_submit(self):
		if self.panels_cut_qty and self.order_qty and self.panels_cut_qty < self.order_qty:
			frappe.msgprint(
				f"Panels cut ({self.panels_cut_qty}) is short of order qty ({self.order_qty}). "
				f"Shortfall: {self.order_qty - self.panels_cut_qty} pcs — flag for re-cut before "
				f"releasing to stitching.",
				indicator="orange",
				alert=True,
			)
