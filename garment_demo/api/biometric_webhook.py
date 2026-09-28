# Copyright (c) 2026, Nikunj
#
# FrappeHR <-> biometric hardware integration
# --------------------------------------------
# Most garment factories run a biometric fingerprint/RFID attendance device
# (ESSL, ZKTeco, Matrix COSEC are common in India) at the shop-floor gate.
# These devices don't speak Frappe natively — they either:
#   (a) push punch data to a URL you give them (HTTP push, some ZKTeco/eSSL
#       models support this out of the box), or
#   (b) sit on a local network and need a small polling agent (a Python/Node
#       service on a factory PC using the vendor SDK, e.g. pyzk for ZKTeco)
#       that reads punches and forwards them here.
#
# Either way, the ERP-side contract is the same: a whitelisted endpoint that
# takes a normalized punch record and creates an "Employee Checkin" in
# FrappeHR, which HR's attendance/payroll processes already consume.
#
# This file is the (a)/(b) landing point. The device-specific polling agent
# (option b) is out of scope for ERPNext itself and would be a small
# separate service — happy to build that once we know the exact device model
# and whether it exposes push, SDK, or only a local log file.

import frappe
from frappe.utils import get_datetime


@frappe.whitelist(allow_guest=True)
def record_punch(device_serial: str, biometric_id: str, punch_time: str, direction: str = None):
	"""Landing endpoint for a biometric device (or its polling agent).

	Args:
		device_serial: Serial/ID of the physical device, used to identify
			which factory gate/line the punch came from.
		biometric_id: The ID enrolled on the device, mapped to an Employee
			via the 'attendance_device_id' field on the Employee doctype
			(a standard FrappeHR field).
		punch_time: ISO datetime string of the punch.
		direction: "IN" or "OUT" if the device reports it; otherwise
			FrappeHR's own logic alternates IN/OUT automatically.

	Returns:
		dict: the created Employee Checkin name, or an error detail if the
		biometric ID isn't mapped to any employee yet (common on day one of
		a rollout — logged instead of silently dropped).
	"""
	employee = frappe.db.get_value(
		"Employee", {"attendance_device_id": biometric_id}, "name"
	)

	if not employee:
		frappe.log_error(
			title="Unmapped biometric punch",
			message=f"Device {device_serial} sent biometric_id={biometric_id} "
			f"with no matching Employee.attendance_device_id. Punch dropped.",
		)
		return {"status": "error", "reason": "employee_not_mapped", "biometric_id": biometric_id}

	checkin = frappe.get_doc({
		"doctype": "Employee Checkin",
		"employee": employee,
		"time": get_datetime(punch_time),
		"log_type": _normalize_direction(direction),
		"device_id": device_serial,
	})
	checkin.insert(ignore_permissions=True)
	frappe.db.commit()

	return {"status": "ok", "checkin": checkin.name, "employee": employee}


def _normalize_direction(direction):
	if not direction:
		return None
	direction = direction.strip().upper()
	return "IN" if direction in ("IN", "I") else "OUT" if direction in ("OUT", "O") else None
