// Copyright (c) 2026, Nikunj
// Client-side UX: QC inspectors work fast on a shop floor tablet — this gives
// an instant color-coded read of "are we passing this lot" before submit,
// instead of making them save and reopen to see the computed result.

frappe.ui.form.on('QC Inspection', {
	refresh: function (frm) {
		render_result_indicator(frm);

		if (frm.doc.result && frm.doc.result.startsWith('Failed') && frm.doc.docstatus === 1) {
			frm.add_custom_button('Create Rework Order', function () {
				frappe.set_route('Form', 'Stitching Line Entry', 'new');
			});
		}
	},

	defects_on_form_rendered: function (frm) {
		render_result_indicator(frm);
	},

	validate: function (frm) {
		if (frm.doc.aql_level && !frm.doc.sample_size) {
			frappe.throw(__('Sample Size is required to evaluate AQL result.'));
		}
	}
});

function render_result_indicator(frm) {
	if (!frm.doc.result) return;

	const color_map = {
		'Passed': 'green',
		'Under Inspection': 'blue',
		'Failed - Rework Required': 'orange',
		'Failed - Reject': 'red',
	};

	frm.dashboard.clear_headline();
	frm.dashboard.set_headline(
		`<span class="indicator-pill ${color_map[frm.doc.result] || 'gray'}">
			${frappe.utils.escape_html(frm.doc.result)}
			${frm.doc.defect_rate_pct ? ' — ' + frm.doc.defect_rate_pct.toFixed(1) + '% defect rate' : ''}
		</span>`
	);
}
