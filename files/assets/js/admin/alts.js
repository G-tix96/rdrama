function submitAddAlt(element) {
	if (!element || !element.form) return;
	const isLinking = element.id == 'add-alt-form-link';
	const otherElement = isLinking ? document.getElementById('add-alt-form-delink') : document.getElementById('add-alt-form-link');
	if (!otherElement) return;
	element.disabled = true;
	otherElement.disabled = true;
	element.classList.add('disabled');
	otherElement.classList.add('disabled');
	const form = new FormData();
	if (!isLinking) form.append('deleted', 'true');
	form.append('other_username', document.getElementById('link-input-other').value);
	const xhr = createXhrWithFormKey('/@{{u.username}}/alts/', 'POST', form);
	xhr[0].onload = function() {
		let data;
		try {
			data = JSON.parse(xhr[0].response);
		}
		catch(e) {
			console.log(e);
		}
		if (xhr[0].status >= 200 && xhr[0].status < 300) {
			showToast(true, getMessageFromJsonData(true, data));
			window.location.reload();
		} else {
			showToast(false, getMessageFromJsonData(false, data));
			element.disabled = false;
			otherElement.disabled = false;
			element.classList.remove('disabled');
			otherElement.classList.remove('disabled');
		}
	}
	xhr[0].send(xhr[1]);
}
