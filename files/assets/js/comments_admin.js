function removeComment(post_id,button1,button2,cls) {
	url="/remove_comment/"+post_id

	post(url)

	if (window.location.pathname == '/admin/reported/comments')
	{
		document.getElementById("post-info-"+post_id).remove()
		document.getElementById("comment-"+post_id).remove()
	}
	else
	{
		try {
			document.getElementById("comment-"+post_id+"-only").classList.add("banned");
		} catch(e) {
			document.getElementById("context").classList.add("banned");
		}
		document.getElementById(button1).classList.toggle(cls);
		document.getElementById(button2).classList.toggle(cls);
	}
};

function approveComment(post_id,button1,button2,cls) {
	url="/approve_comment/"+post_id

	post(url)

	if (window.location.pathname == '/admin/reported/comments')
	{
		document.getElementById("post-info-"+post_id).remove()
		document.getElementById("comment-"+post_id).remove()
	}
	else
	{
		try {
			document.getElementById("comment-"+post_id+"-only").classList.remove("banned");
		} catch(e) {
			document.getElementById("context").classList.remove("banned");
		}
		document.getElementById(button1).classList.toggle(cls);
		document.getElementById(button2).classList.toggle(cls);
	}
}

function adminMuteUser(userId, muteStatus, buttonId) {
	const xhr = createXhrWithFormKey(`/mute_user/${userId}/${muteStatus}`);
	xhr[0].onload = function() {
		let data
		try {data = JSON.parse(xhr[0].response)}
		catch(e) {console.log(e)}
		success = xhr[0].status >= 200 && xhr[0].status < 300;
		showToast(success, getMessageFromJsonData(success, data));
	};
	xhr[0].send(xhr[1]);
	document.getElementById('mute-user-' + buttonId).classList.add("d-none");
}
