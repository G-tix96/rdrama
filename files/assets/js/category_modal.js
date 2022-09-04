function category_modal(id, title, sub) {
	document.getElementById("category-modal-title").innerHTML = `Category: ${title}`;

	xhrCategories = new XMLHttpRequest();
	xhrCategories.open("GET", "/categories.json");
	xhrCategories.onload = function () {
		let data;
		try {
			data = JSON.parse(xhrCategories.response);
		} catch(e) { console.log(e) }

		categories = [{id: '', name: 'None', sub: sub, color_text: '#000', color_bg: '#FFF'}];
		categories = [].concat(categories, data[sub]);

		document.getElementById("category-modal-body").innerHTML = '';
		categories.forEach(function (c) {
			document.getElementById("category-modal-body").innerHTML +=
				`<div class="category--tag-button" data-category="${c.id}">` +
				`<span class="post--category-tag" style="color:${c.color_text}; ` +
					`background-color:${c.color_bg};">${c.name}</span>` +
				`</div>`;
		});

		document.querySelectorAll('.category--tag-button').forEach(tag =>
			tag.addEventListener('click', function (e) {
				reqBody = new FormData();
				reqBody.append('formkey', formkey());
				reqBody.append('post_id', id);
				reqBody.append('category_id', tag.dataset.category);

				xhrSubmit = new XMLHttpRequest();
				xhrSubmit.open('POST', `/post_recategorize`);
				xhrSubmit.onload = function () {
					window.location.reload();
				}
				xhrSubmit.send(reqBody);
			})
		);
	}
	xhrCategories.send();
}
