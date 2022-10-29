function removeFollower(t, username) {
	post_toast(t,'/remove_follow/' + username);
	t.parentElement.parentElement.remove();
}
