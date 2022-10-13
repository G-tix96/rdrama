function removeFollowing(t, username) {
	post_toast(t,'/unfollow/' + username);
	let table = document.getElementById("followers-table");
	table.removeChild(t.parentElement.parentElement);
}
