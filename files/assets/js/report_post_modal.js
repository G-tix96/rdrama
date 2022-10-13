const reason_post = document.getElementById("reason_post")
const reportPostButton = document.getElementById("reportPostButton");

reason_post.addEventListener('keydown', (e) => {
	if(!((e.ctrlKey || e.metaKey) && e.key === "Enter")) return;

	const targetDOM = document.activeElement;
	if(!(targetDOM instanceof HTMLInputElement)) return;

	reportPostButton.click()
	bootstrap.Modal.getOrCreateInstance(document.getElementById('reportPostModal')).hide()
});

function report_postModal(id) {

	reportPostButton.disabled = false;
	reportPostButton.classList.remove('disabled');
	reportPostButton.innerHTML='Report post';

	reason_post.value = ""
	setTimeout(() => {
		reason_post.focus()
	}, 500);

	reportPostButton.onclick = function() {

		this.innerHTML='Reporting post';
		this.disabled = true;
		this.classList.add('disabled');

		const xhr = new XMLHttpRequest();
		xhr.open("POST", '/report/post/'+id);
		xhr.setRequestHeader('xhr', 'xhr');
		const form = new FormData()
		form.append("formkey", formkey());
		form.append("reason", reason_post.value);

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
				if (data && data["details"]) document.getElementById('toast-post-error-text').innerText = data["details"];
				bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-error')).show();
			}
		};

		xhr.onerror=function(){alert(errortext)};
		xhr.send(form);

	}
};