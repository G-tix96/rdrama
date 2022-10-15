function banModal(link, id, name) {
	document.getElementById("banModalTitle").innerHTML = `Ban @${name}`;
	document.getElementById("ban-modal-link").value = link;
	document.getElementById("banUserButton").innerHTML = `Ban @${name}`;

	document.getElementById("banUserButton").onclick = function() {
		let form = new FormData(document.getElementById("banModalForm"));
		const xhr = createXhrWithFormKey(`/ban_user/${id}?form`, "POST", form);
		xhr[0].onload = function() {
			let data
			try {data = JSON.parse(xhr.response)}
			catch(e) {console.log(e)}
			success = xhr[0].status >= 200 && xhr[0].status < 300;
			showToast(success, getMessageFromJsonData(success, data));
		};

		xhr[0].send(xhr[1]);
	}
}