app_name = "garment_demo"
app_title = "Garment Ops"
app_publisher = "Nikunj"
app_description = "Garment manufacturing & export operations on ERPNext — Cutting, Stitching, QC, Packing, Shipment, and biometric attendance -> FrappeHR integration."
app_email = "nikunj7943@gmail.com"
app_license = "MIT"

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "QC Inspection": {
        "on_submit": "garment_demo.garment_demo.doctype.qc_inspection.qc_inspection.on_qc_submit"
    }
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "hourly": [
        "garment_demo.garment_demo.tasks.sync_stitching_efficiency"
    ]
}
