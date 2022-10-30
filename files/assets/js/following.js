function removeFollowing(t, username) {
	postToast(t,'/unfollow/' + username);
	t.parentElement.parentElement.remove();
}
