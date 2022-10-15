const reason_comment = document.getElementById("reason_comment")
const reportCommentButton = document.getElementById("reportCommentButton");

reason_comment.addEventListener('keydown', (e) => {
	if(!((e.ctrlKey || e.metaKey) && e.key === "Enter")) return;

	const targetDOM = document.activeElement;
	if(!(targetDOM instanceof HTMLInputElement)) return;

	reportCommentButton.click()
	bootstrap.Modal.getOrCreateInstance(document.getElementById('reportCommentModal')).hide()
});


function report_commentModal(id, author) {

	document.getElementById("comment-author").textContent = author;

	reportCommentButton.innerHTML='Report comment';
	reportCommentButton.disabled = false;
	reportCommentButton.classList.remove('disabled');

	reason_comment.value = ""
	setTimeout(() => {
		reason_comment.focus()
	}, 500);

	reportCommentButton.onclick = function() {
		this.innerHTML='Reporting comment';
		this.disabled = true;
		this.classList.add('disabled');
		const form = new FormData();
		form.append("reason", reason_comment.value);
		const xhr = createXhrWithFormKey("/report/comment/" + id, "POST", form);

		xhr[0].onload = function() {
			let data
			try {data = JSON.parse(xhr[0].response)}
			catch(e) {console.log(e)}
			success = xhr[0].status >= 200 && xhr[0].status < 300;
			showToast(success, getMessageFromJsonData(success, data));
		};

		xhr[0].onerror=function(){alert(errortext)};
		xhr[0].send(xhr[1]);
	}

};

// Returns the selection text based on the range with the HTML
function getSelectionTextHtml() {
	let html = "";
	let sel = getSelection();
	if (sel.rangeCount) {
		let container = document.createElement("div");
		container.appendChild(sel.getRangeAt(0).cloneContents());
		html += container.innerHTML;
	}
	return html;
}

function ToggleReplyBox(id) {
	const element = document.getElementById(id);
	const textarea = element.getElementsByTagName('textarea')[0]
	element.classList.toggle('d-none')

	if (!element.classList.contains('d-none'))
	{
		let text = getSelection().toString().trim()
		if (text)
		{
			textarea.value = '> ' + text
			textarea.value = textarea.value.replace(/\n/g,"\n> ").replace(/\*/g,"\\*")
			if (!textarea.value.endsWith('\n')) textarea.value += '\n'
		}
		textarea.focus()
	}
}

function toggleEdit(id){
	comment=document.getElementById("comment-text-"+id);
	form=document.getElementById("comment-edit-"+id);
	box=document.getElementById('comment-edit-body-'+id);
	actions = document.getElementById('comment-' + id +'-actions');

	comment.classList.toggle("d-none");
	form.classList.toggle("d-none");
	actions.classList.toggle("d-none");
	autoExpand(box);
};


function delete_commentModal(id) {
	document.getElementById("deleteCommentButton").onclick = function() {
		const xhr = createXhrWithFormKey(`/delete/comment/${id}`);
		xhr[0].onload = function() {
			let data
			try {data = JSON.parse(xhr[0].response)}
			catch(e) {console.log(e)}
			if (xhr[0].status >= 200 && xhr[0].status < 300 && data && data['message']) {
				document.getElementsByClassName(`comment-${id}-only`)[0].classList.add('deleted');
				document.getElementById(`delete-${id}`).classList.add('d-none');
				document.getElementById(`undelete-${id}`).classList.remove('d-none');
				document.getElementById(`delete2-${id}`).classList.add('d-none');
				document.getElementById(`undelete2-${id}`).classList.remove('d-none');
				showToast(true, getMessageFromJsonData(true, data));
			} else {
				showToast(false, getMessageFromJsonData(false, data));
			}
		};
		xhr[0].send(xhr[1]);
	};
}

function post_reply(id){
	const btn = document.getElementById(`save-reply-to-${id}`)
	btn.disabled = true;
	btn.classList.add('disabled');

	const form = new FormData();
	form.append('parent_id', id);
	form.append('body', document.getElementById('reply-form-body-'+id).value);
	try {
		for (const e of document.getElementById('file-upload').files)
			form.append('file', e);
	}
	catch(e) {}
	
	const xhr = createXhrWithFormKey("/reply", "POST", form);
	xhr[0].onload=function(){
		let data
		try {data = JSON.parse(xhr[0].response)}
		catch(e) {console.log(e)}
		if (data && data["comment"]) {
			const comments = document.getElementById('replies-of-c_' + id);
			const comment = data["comment"].replace(/data-src/g, 'src').replace(/data-cfsrc/g, 'src').replace(/style="display:none;visibility:hidden;"/g, '');
			
			comments.innerHTML = comments.innerHTML + comment;

			bs_trigger(comments);

			btn.disabled = false;
			btn.classList.remove('disabled');

			document.getElementById('reply-form-body-'+id).value = ''
			document.getElementById('message-reply-'+id).innerHTML = ''
			ToggleReplyBox('reply-message-'+id)
		} else {
			showToast(false, getMessageFromJsonData(false, data));
		}
		setTimeout(() => {
			btn.disabled = false;
			btn.classList.remove('disabled');
		}, 2000);
	}
	xhr[0].send(xhr[1]);
}

function comment_edit(id){
	const btn = document.getElementById(`edit-btn-${id}`)
	btn.disabled = true
	btn.classList.add('disabled');

	const form = new FormData();
	form.append('body', document.getElementById('comment-edit-body-'+id).value);

	try {
		for (const e of document.getElementById('file-edit-reply-'+id).files)
			form.append('file', e);
	}
	catch(e) {}
	const xhr = createXhrWithFormKey("/edit_comment/"+id, "POST", form);
	xhr[0].onload=function(){
		let data
		try {data = JSON.parse(xhr[0].response)}
		catch(e) {console.log(e)}
		if (data && data["comment"]) {
			commentForm=document.getElementById('comment-text-'+id);
			commentForm.innerHTML = data["comment"].replace(/data-src/g, 'src').replace(/data-cfsrc/g, 'src').replace(/style="display:none;visibility:hidden;"/g, '')
			document.getElementById('cancel-edit-'+id).click()
			bs_trigger(commentForm);
			document.getElementById('filename-edit-reply-' + id).innerHTML = '<i class="fas fa-file"></i>';
		}
		else {
			showToast(false, getMessageFromJsonData(false, data));
		}
		setTimeout(() => {
			btn.disabled = false;
			btn.classList.remove('disabled');
		}, 1000);
	}
	xhr[0].send(xhr[1]);
}

function post_comment(fullname, hide){
	const btn = document.getElementById('save-reply-to-'+fullname)
	btn.disabled = true
	btn.classList.add('disabled');

	const form = new FormData();

	form.append('formkey', formkey());
	form.append('parent_fullname', fullname);
	form.append('submission', document.getElementById('reply-form-submission-'+fullname).value);
	form.append('body', document.getElementById('reply-form-body-'+fullname).value);

	try {
		for (const e of document.getElementById('file-upload-reply-'+fullname).files)
			form.append('file', e);
	}
	catch(e) {}

	const xhr = new XMLHttpRequest();
	xhr.open("post", "/comment");
	xhr.setRequestHeader('xhr', 'xhr');
	xhr.onload=function(){
		let data
		try {data = JSON.parse(xhr.response)}
		catch(e) {console.log(e)}
		if (data && data["comment"]) {
			if (hide) document.getElementById(hide).classList.add('d-none');

			let name = 'comment-form-space-' + fullname;
			commentForm = document.getElementById(name);

			let comments = document.getElementById('replies-of-' + fullname);
			let comment = data["comment"].replace(/data-src/g, 'src').replace(/data-cfsrc/g, 'src').replace(/style="display:none;visibility:hidden;"/g, '');

			comments.innerHTML = comment + comments.innerHTML;
			if (!hide) comments.scrollIntoView()

			bs_trigger(comments);

			btn.disabled = false;
			btn.classList.remove('disabled');

			document.getElementById('reply-form-body-'+fullname).value = ''
			document.getElementById('form-preview-'+fullname).innerHTML = ''
			document.getElementById('filename-show-reply-' + fullname).innerHTML = '<i class="fas fa-file"></i>';
		}
		else {
			showToast(false, getMessageFromJsonData(false, data));
			setTimeout(() => {
				btn.disabled = false;
				btn.classList.remove('disabled');
			}, 2000);
		}
	}
	xhr.send(form)
}

document.onpaste = function(event) {
	var focused = document.activeElement;
	const files = event.clipboardData.files

	if (files.length > 4)
	{
		alert("You can't upload more than 4 files at one time!")
		return
	}

	if (!files.length) return

	if (focused.id.includes('reply-form-body-')) {
		var fullname = focused.dataset.fullname;
		f=document.getElementById('file-upload-reply-' + fullname);
		try {
			let filename = ''
			for (const file of files)
				filename += file.name + ', '
			filename = filename.toLowerCase().slice(0, -2)
			f.files = files;
			document.getElementById('filename-show-reply-' + fullname).textContent = filename;
		}
		catch(e) {}
	}
	else if (focused.id.includes('comment-edit-body-')) {
		var id = focused.dataset.id;
		f=document.getElementById('file-edit-reply-' + id);
		let filename = ''
		for (const file of files)
			filename += file.name + ', '
		filename = filename.toLowerCase().slice(0, -2)
		f.files = files;
		document.getElementById('filename-edit-reply-' + id).textContent = filename;
	}
	else if (focused.id.includes('post-edit-box-')) {
		var id = focused.dataset.id;
		f=document.getElementById('file-upload-edit-' + id);
		let filename = ''
		for (const file of files)
			filename += file.name + ', '
		filename = filename.toLowerCase().slice(0, -2)
		f.files = files;
		document.getElementById('filename-show-edit-' + id).textContent = filename;
	}
}

function handle_action(type, cid, thing) {
	const btns = document.getElementsByClassName(`action-${cid}`)
	for (const btn of btns)
	{
		btn.disabled = true;
		btn.classList.add('disabled');
	}

	const form = new FormData();
	form.append('formkey', formkey());
	form.append('comment_id', cid);
	form.append('thing', thing);

	const xhr = new XMLHttpRequest();
	xhr.open("post", `/${type}/${cid}`);
	xhr.setRequestHeader('xhr', 'xhr');



	xhr.onload=function(){
		let data
		try {data = JSON.parse(xhr.response)}
		catch(e) {console.log(e)}
		if (data && data["response"]) {
			const element = document.getElementById(`${type}-${cid}`);
			element.innerHTML = data["response"]
		} else {
			showToast(false, getMessageFromJsonData(false, data));
		}
		setTimeout(() => {
			for (const btn of btns)
			{
				btn.disabled = false;
				btn.classList.remove('disabled');
			}
		}, 2000);
	}
	xhr.send(form)
}
