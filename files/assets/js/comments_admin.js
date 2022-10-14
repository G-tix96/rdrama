function removeComment(post_id,button1,button2) {
	url="/remove_comment/"+post_id

	post(url)

	try {
		document.getElementById("comment-"+post_id+"-only").classList.add("banned");
	} catch(e) {
		document.getElementById("context").classList.add("banned");
	}

	var button=document.getElementById("remove-"+post_id);
	button.onclick=function(){approveComment(post_id)};
	button.innerHTML='<i class="fas fa-clipboard-check"></i>Approve'

	if (typeof button1 !== 'undefined') {
		document.getElementById(button1).classList.toggle("d-md-block");
		document.getElementById(button2).classList.toggle("d-md-block");
	}
};

function approveComment(post_id,button1,button2) {
	url="/approve_comment/"+post_id

	post(url)

	try {
		document.getElementById("comment-"+post_id+"-only").classList.remove("banned");
	} catch(e) {
		document.getElementById("context").classList.remove("banned");
	}

	var button=document.getElementById("remove-"+post_id);
	button.onclick=function(){removeComment(post_id)};
	button.innerHTML='<i class="fas fa-trash-alt"></i>Remove'

	if (typeof button1 !== 'undefined') {
		document.getElementById(button1).classList.toggle("d-md-block");
		document.getElementById(button2).classList.toggle("d-md-block");
	}
}


function removeComment2(post_id,button1,button2) {
	url="/remove_comment/"+post_id

	post(url)

	document.getElementById("comment-"+post_id+"-only").classList.add("banned");
	var button=document.getElementById("remove-"+post_id);
	button.onclick=function(){approveComment(post_id)};
	button.innerHTML='<i class="fas fa-clipboard-check"></i>Approve'

	if (typeof button1 !== 'undefined') {
		document.getElementById(button1).classList.toggle("d-none");
		document.getElementById(button2).classList.toggle("d-none");
	}
};

function approveComment2(post_id,button1,button2) {
	url="/approve_comment/"+post_id

	post(url)

	document.getElementById("comment-"+post_id+"-only").classList.remove("banned");
	var button=document.getElementById("remove-"+post_id);
	button.onclick=function(){removeComment(post_id)};
	button.innerHTML='<i class="fas fa-trash-alt"></i>Remove'

	if (typeof button1 !== 'undefined') {
		document.getElementById(button1).classList.toggle("d-none");
		document.getElementById(button2).classList.toggle("d-none");
	}
}

function adminMuteUser(userId, muteStatus, buttonId) {
	let form = new FormData();
	form.append("formkey", formkey());

	const xhr = new XMLHttpRequest();
	xhr.open("POST", `/mute_user/${userId}/${muteStatus}`);
	xhr.setRequestHeader('xhr', 'xhr');

	xhr.onload = function() {
		let data
		try {data = JSON.parse(xhr.response)}
		catch(e) {console.log(e)}
		success = xhr.status >= 200 && xhr.status < 300;
		showToast(success, getMessageFromJsonData(success, data));
	};

	xhr.send(form);

	document.getElementById('mute-user-' + buttonId).classList.add("d-none");
}
