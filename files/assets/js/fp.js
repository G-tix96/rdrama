const fp_token = document.getElementById('fp_token').value

function fp(fp) {
	const xhr = new XMLHttpRequest();
	xhr.open("POST", '/fp/'+fp);
	xhr.setRequestHeader('xhr', 'xhr');
	const form = new FormData()
	form.append("formkey", formkey());
	xhr.send(form);
};

const fpPromise = new Promise((resolve, reject) => {
	const script = document.createElement('script');
	script.onload = resolve;
	script.onerror = reject;
	script.async = true;
	script.src = "{{'js/vendor/fp.js' | asset}}";
	document.head.appendChild(script);
})
	.then(() => FingerprintJS.load({token: fp_token}));

fpPromise
	.then(fp => fp.get())
	.then(result => {fp(result.visitorId);})
