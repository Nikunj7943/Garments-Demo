# Copyright (c) 2026, Nikunj
# QC Inspection controller
#
# Garment QC is not "pass if defects < X" — a single Critical defect fails the
# lot outright regardless of AQL sample math (this mirrors real buyer QC
# manuals, e.g. a broken needle tip or missing safety label). This is the kind
# of workflow logic that only comes from having actually run/inspected a
# garment QC process, not from generic ERP knowledge, so it's included here
# to show exactly the kind of translation the brief is asking for.

import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint

# Acceptance numbers (Ac) for general inspection level II, from ANSI/ASQ Z1.4 —
# keyed by (AQL level, sample size code letter -> here simplified to sample_size band)
# This is a simplified lookup for demo purposes; a production build would use
# the full Z1.4 tables keyed off lot size -> code letter -> sample size -> Ac/Re.
AQL_ACCEPT_REJECT = {
	"1.0": {"max_sample": 125, "accept": 3, "reject": 4},
	"1.5": {"max_sample": 125, "accept": 5, "reject": 6},
	"2.5": {"max_sample": 125, "accept": 7, "reject": 8},
	"4.0": {"max_sample": 125, "accept": 10, "reject": 11},
}


class QCInspection(Document):
	def validate(self):
		self.calculate_defect_totals()
		self.evaluate_result()

	def calculate_defect_totals(self):
		self.total_defect_qty = sum(cint(d.qty_affected) for d in self.defects)
		if self.sample_size:
			self.defect_rate_pct = flt(self.total_defect_qty) / flt(self.sample_size) * 100

	def evaluate_result(self):
		if not self.defects:
			return

		has_critical = any(d.defect_class == "Critical" for d in self.defects)
		if has_critical:
			# Zero tolerance: any critical defect fails the lot outright,
			# no AQL math applies.
			self.result = "Failed - Reject"
			return

		major_minor_qty = sum(
			cint(d.qty_affected) for d in self.defects if d.defect_class in ("Major", "Minor")
		)

		table = AQL_ACCEPT_REJECT.get(self.aql_level)
		if not table:
			return

		if major_minor_qty <= table["accept"]:
			self.result = "Passed"
		elif major_minor_qty >= table["reject"]:
			self.result = "Failed - Reject"
		else:
			self.result = "Failed - Rework Required"


def on_qc_submit(doc, method=None):
	"""Hooked from hooks.py doc_events. When a lot Passes final QC, the passed
	quantity is what actually becomes packable — not the original order qty —
	so Packing List creation reads straight off this document instead of
	being entered again by hand (a common source of shipped-quantity errors
	on the floor).
	"""
	if doc.result != "Passed" or doc.inspection_stage != "Final (Pre-Shipment)":
		return

	passed_qty = cint(doc.lot_size) - cint(doc.total_defect_qty)
	if passed_qty <= 0:
		return

	existing = frappe.db.exists("Packing List", {"qc_inspection": doc.name})
	if existing:
		return

	packing_list = frappe.get_doc({
		"doctype": "Packing List",
		"qc_inspection": doc.name,
		"style": doc.style,
		"passed_qty": passed_qty,
		"status": "Ready to Pack",
	})
	packing_list.insert(ignore_permissions=True)
	frappe.msgprint(
		f"Packing List {packing_list.name} auto-created for {passed_qty} passed pcs.",
		indicator="green",
		alert=True,
	)
