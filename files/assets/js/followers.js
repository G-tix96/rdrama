function removeFollower(t, username) {
	post_toast(t,'/remove_follow/' + username);
	let table = document.getElementById("followers-table");
	table.removeChild(t.parentElement.parentElement);
}
