function removeFollowing(t, username) {
	post_toast(t,'/unfollow/' + username);
	t.parentElement.parentElement.remove();
}
