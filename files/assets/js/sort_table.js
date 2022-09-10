let sortAscending = {};

function sort_table(n) {
	const table = this.event.target.parentElement.parentElement.parentElement
	const rows = table.rows;
	let items = [];
	for (let i = 1; i < rows.length; i++) {
		const ele = rows[i];
		let x = rows[i].getElementsByTagName("TD")[n];
		x = x.getElementsByTagName('a')[0] || x;
		x =
		const attr = x.dataset.time ? parseInt(x.dataset.time) : parseInt(x.innerHTML);
		items.push({ ele, attr });
	}
	if (sortAscending[n]) {
		items.sort((a, b) => a.attr - b.attr);
		sortAscending[n] = false;
	} else {
		items.sort((a, b) => b.attr - a.attr);
		sortAscending[n] = true;
	}

	for (let i = items.length - 1; i--;) {
		items[i].ele.parentNode.insertBefore(items[i].ele, items[i + 1].ele);
	}
}
