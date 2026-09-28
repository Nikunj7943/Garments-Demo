# Copyright (c) 2026, Nikunj
# Scheduled tasks (hooks.py -> scheduler_events)

import frappe


def sync_stitching_efficiency():
	"""Hourly rollup: flag any line running below 60% efficiency in the last
	completed shift so a supervisor sees it without opening every line entry.
	In a real deployment this would push to a dashboard chart / Slack alert
	rather than just a log — wiring depends on what the floor already uses.
	"""
	low_performers = frappe.db.get_all(
		"Stitching Line Entry",
		filters={"line_efficiency_pct": ["<", 60]},
		fields=["name", "line_no", "shift_date", "line_efficiency_pct"],
		order_by="shift_date desc",
		limit=20,
	)
	if low_performers:
		frappe.log_error(
			title="Low line efficiency alert",
			message=frappe.as_json(low_performers),
		)
