function removePost(t,post_id,button1,button2,cls) {
	url="/remove_post/"+post_id

	t.disabled = true;
	t.classList.add("disabled");
	postToastCallback(url,
		{
		},
		(xhr) => {
			if (xhr.status >= 200 && xhr.status < 300) {
				if (window.location.pathname == '/admin/reported/posts')
				{
					document.getElementById("flaggers-"+post_id).remove()
					document.getElementById("post-"+post_id).remove()
				}
				else
				{
					document.getElementById("post-"+post_id).classList.add("banned");
					document.getElementById(button1).classList.toggle(cls);
					document.getElementById(button2).classList.toggle(cls);	
				}
			}
			t.disabled = false;
			t.classList.remove("disabled");		
		}
	);
}


function approvePost(t,post_id,button1,button2,cls) {
	url="/approve_post/"+post_id

	t.disabled = true;
	t.classList.add("disabled");
	postToastCallback(url,
		{
		},
		(xhr) => {
			if (xhr.status >= 200 && xhr.status < 300) {
				if (window.location.pathname == '/admin/reported/posts')
				{
					document.getElementById("flaggers-"+post_id).remove()
					document.getElementById("post-"+post_id).remove()
				}
				else
				{
					document.getElementById("post-"+post_id).classList.remove("banned");
					document.getElementById(button1).classList.toggle(cls);
					document.getElementById(button2).classList.toggle(cls);
				}
			}
			t.disabled = false;
			t.classList.remove("disabled");		
		}
	);
}
