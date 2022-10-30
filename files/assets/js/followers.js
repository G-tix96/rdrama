function removeFollower(t, username) {
	postToast(t,'/remove_follow/' + username);
	t.parentElement.parentElement.remove();
}
