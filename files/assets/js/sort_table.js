let desc = true;
function sort_table(n) {
	let rows, i, x, y, shouldSwitch, x_attribute, y_attribute, switchcount = 0;
	const table = this.event.target.parentElement.parentElement.parentElement
	let switching = true;
	while (switching) {
		switching = false;
		rows = table.rows;
		for (i = 1; i < (rows.length - 1); i++) {
			shouldSwitch = false;
			let x = rows[i].getElementsByTagName("TD")[n];
			let y = rows[i + 1].getElementsByTagName("TD")[n];
			const x_child = x.getElementsByTagName('a')[0]
			if (typeof x_child != 'undefined') x = x_child
			const y_child = y.getElementsByTagName('a')[0]
			if (typeof y_child != 'undefined') y = y_child
			if (x.dataset.time) {
				x_attribute = parseInt(x.dataset.time)
				y_attribute = parseInt(y.dataset.time)
			}
			else {
				x_attribute = parseInt(x.innerHTML)
				y_attribute = parseInt(y.innerHTML)
			}
			
			if (desc && x_attribute < y_attribute) {
				shouldSwitch = true;
				break;
			}
			else if (!desc && x_attribute > y_attribute) {
				shouldSwitch = true;
				break;
			}
		}
		if (shouldSwitch) {
			rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
			switching = true;
			switchcount ++;
		}
	}
	desc = !desc;
}