function banModal(link, id, name) {
	document.getElementById("banModalTitle").innerHTML = `Ban @${name}`;
	document.getElementById("ban-modal-link").value = link;
	document.getElementById("banUserButton").innerHTML = `Ban @${name}`;

	document.getElementById("banUserButton").onclick = function() {
		let form = new FormData(document.getElementById("banModalForm"));
		form.append("formkey", formkey());

		const xhr = new XMLHttpRequest();
		xhr.open("POST", `/ban_user/${id}?form`);
		xhr.setRequestHeader('xhr', 'xhr');

		xhr.onload = function() {
			let data
			try {data = JSON.parse(xhr.response)}
			catch(e) {console.log(e)}
			success = xhr.status >= 200 && xhr.status < 300;
			showToast(success, getMessageFromJsonData(success, data));
		};

		xhr.send(form);
	}
}