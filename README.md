# Garment Demo (garment_demo)

A custom Frappe app modeling a garment manufacturing & export workflow on
ERPNext: **Style → Cutting → Stitching → QC → Packing → Export Shipment**,
plus a FrappeHR biometric-attendance integration stub.

See `/SETUP_GUIDE.md` (one level up, project root) for how to install this
on a live ERPNext instance, and `/CASE_STUDY.md` for the reasoning behind
each workflow decision.

## Module layout

```
garment_demo/
  hooks.py                  # app config, doc_events, scheduler_events
  tasks.py                  # scheduled jobs (line efficiency alerts)
  modules.txt
  api/
    biometric_webhook.py    # FrappeHR <-> biometric device integration
  workflow/
    qc_inspection_workflow.json
  doctype/
    garment_style/
    garment_style_size_ratio/     (child table)
    cutting_order/
    stitching_line_entry/
    stitching_hourly_output/      (child table)
    qc_inspection/
    qc_defect_entry/               (child table)
    packing_list/
    packing_carton_line/           (child table)
    export_shipment/
```

## Install

```bash
bench get-app garment_demo /path/to/this/folder
bench --site <site> install-app garment_demo
bench --site <site> migrate
```
