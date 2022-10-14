function delete_postModal(id) {
	document.getElementById("deletePostButton").onclick = function() {
		const xhr = createXhrWithFormKey(`/delete_post/${id}`);
		xhr[0].onload = function() {
			let data
			try {data = JSON.parse(xhr.response)}
			catch(e) {console.log(e)}
			success = xhr[0].status >= 200 && xhr[0].status < 300;
			showToast(success, getMessageFromJsonData(success, data));
			if (success && data["message"]) {
				document.getElementById(`post-${id}`).classList.add('deleted');
				document.getElementById(`delete-${id}`).classList.add('d-none');
				document.getElementById(`undelete-${id}`).classList.remove('d-none');
				document.getElementById(`delete2-${id}`).classList.add('d-none');
				document.getElementById(`undelete2-${id}`).classList.remove('d-none');
			} else {
				showToast(false, getMessageFromJsonData(false, data));
			}
		};
		xhr[0].send(xhr[1]);
	};
}