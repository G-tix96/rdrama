function pinPost(t, id) {
	t.disabled = true;
	t.classList.add("disabled");
	post_toast_callback(`/sticky/${id}`,
		{
		},
		(xhr) => {
			if(xhr.status == 200) {
				t.innerHTML = t.innerHTML.replace(t.textContent, 'Pin permanently')
			}
			else if(xhr.status == 201) {
				t.innerHTML = t.innerHTML.replace(t.textContent, 'Pin for 1 hour')
				t.classList.add('d-none')
			}
			t.nextElementSibling.classList.remove('d-none')
			t.disabled = false;
			t.classList.remove("disabled");	
		}
	);
	setTimeout(() => {
		t.disabled = false;
		t.classList.remove("disabled");
	}, 2000);
}
