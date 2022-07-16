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
			if (xhr.status >= 200 && xhr.status < 300 && data && data['message']) {
				document.getElementById('toast-post-success-text').innerText = data["message"];
				bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-success')).show();
			} else {
				document.getElementById('toast-post-error-text').innerText = "Error, please try again later."
				if (data && data["error"]) document.getElementById('toast-post-error-text').innerText = data["error"];
				bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-error')).show();
			}
		};
	
		xhr.send(form);
	}
}