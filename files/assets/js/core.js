function getMessageFromJsonData(success, json) {
	let message = success ? "Success!" : "Error, please try again later";
	let key = success ? "message" : "error";
	if (!json || !json[key]) return message;
	message = json[key];
	if (!success && json["details"]) {
		message = json["details"];
	}
	return message;
}

function showToast(success, message, isToastTwo=false) {
	let element = success ? "toast-post-success" : "toast-post-error";
	let textElement = element + "-text";
	if (isToastTwo) {
		element = element + "2";
		textElement = textElement + "2";
	}
	if (!message) {
		message = success ? "Success" : "Error, please try again later";
	}
	document.getElementById(textElement).innerText = message;
	bootstrap.Toast.getOrCreateInstance(document.getElementById(element)).show();
}

function createXhrWithFormKey(url, method="POST", form=new FormData()) {
	const xhr = new XMLHttpRequest();
	xhr.open(method, url);
	xhr.setRequestHeader('xhr', 'xhr');
	if (!form) form = new FormData();
	form.append("formkey", formkey());
	return [xhr, form]; // hacky but less stupid than what we were doing before
}

function postToast(t, url, data, extraActionsOnSuccess, method="POST") {
	const isShopConfirm = t.id.startsWith('buy1-') || t.id.startsWith('buy2-') || t.id.startsWith('giveaward')

	if (!isShopConfirm)
	{
		t.disabled = true;
		t.classList.add("disabled");
	}

	let form = new FormData();
	if(typeof data === 'object' && data !== null) {
		for(let k of Object.keys(data)) {
			form.append(k, data[k]);
		}
	}
	const xhr = createXhrWithFormKey(url, method, form);
	xhr[0].onload = function() {
		let result
		let message;
		let success = xhr[0].status >= 200 && xhr[0].status < 300;
		if (success && extraActionsOnSuccess) result = extraActionsOnSuccess(xhr[0]);
		if (typeof result == "string") {
			message = result;
		} else {
			message = getMessageFromJsonData(success, JSON.parse(xhr[0].response));
		}
		let oldToast = bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-' + (success ? 'error': 'success'))); // intentionally reversed here: this is the old toast
		oldToast.hide();
		showToast(success, message);
		if (!isShopConfirm) {
			t.disabled = false;
			t.classList.remove("disabled");			
		}
		return success;
	};
	xhr[0].send(xhr[1]);

	if (!isShopConfirm)
	{
		setTimeout(() => {
			t.disabled = false;
			t.classList.remove("disabled");
		}, 2000);
	}
}

function postToastReload(t, url, method="POST") {
	postToast(t, url,
		{
		},
		() => {
			location.reload()
		}
	, method);
}

function postToastSwitch(t, url, button1, button2, cls, extraActionsOnSuccess, method="POST") {
	postToast(t, url,
		{
		},
		(xhr) => {
			if (button1)
			{
				if (typeof(button1) == 'boolean') {
					location.reload()
				} else {
					document.getElementById(button1).classList.toggle(cls);
					document.getElementById(button2).classList.toggle(cls);
				}
			}
			if (extraActionsOnSuccess) extraActionsOnSuccess(xhr);
		}
	, method);
}

if (window.location.pathname != '/submit')
{
	document.addEventListener('keydown', (e) => {
		if(!((e.ctrlKey || e.metaKey) && e.key === "Enter")) return;

		const targetDOM = document.activeElement;
		if(!(targetDOM instanceof HTMLTextAreaElement || targetDOM instanceof HTMLInputElement)) return;

		const formDOM = targetDOM.parentElement;

		const submitButtonDOMs = formDOM.querySelectorAll('input[type=submit], .btn-primary');
		if(submitButtonDOMs.length === 0)
			throw new TypeError("I am unable to find the submit button :(. Contact the head custodian immediately.")

		const btn = submitButtonDOMs[0]
		btn.click();
	});
}

addEventListener('show.bs.modal', function (e) {
	location.hash = "modal";
});

addEventListener('hide.bs.modal', function (e) {
	if(location.hash == "#modal") {
		history.back();
	}
});

addEventListener('hashchange', function (e) {
	if(location.hash != "#modal") {
		const curr_modal = bootstrap.Modal.getInstance(document.getElementsByClassName('show')[0])
		if (curr_modal) curr_modal.hide()
	}
});

function disable(t) {
	t.classList.add('disabled');
	setTimeout(() => {
		t.classList.remove("disabled");
	}, 2000);
}

function autoExpand(field) {
	xpos=window.scrollX;
	ypos=window.scrollY;

	field.style.height = 'inherit';

	var computed = window.getComputedStyle(field);

	var height = parseInt(computed.getPropertyValue('border-top-width'), 10)
	+ parseInt(computed.getPropertyValue('padding-top'), 10)
	+ field.scrollHeight
	+ parseInt(computed.getPropertyValue('padding-bottom'), 10)
	+ parseInt(computed.getPropertyValue('border-bottom-width'), 10);

	field.style.height = height + 'px';
	if (Math.abs(window.scrollX - xpos) < 1 && Math.abs(window.scrollY - ypos) < 1) return;
	window.scrollTo(xpos,ypos);
};

document.addEventListener('input', function (event) {
	if (event.target.tagName.toLowerCase() !== 'textarea') return;
	autoExpand(event.target);
}, false);

function smoothScrollTop()
{
	window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Click navbar to scroll back to top
document.getElementsByTagName('nav')[0].addEventListener('click', (e) => {
	if (e.target.id === "navbar" ||
		e.target.classList.contains("container-fluid") ||
		e.target.id == "navbarResponsive" ||
		e.target.id == "logo-container" ||
		e.target.classList.contains("srd"))
		smoothScrollTop();
}, false);

// Dynamic shadow when the user scrolls
document.addEventListener('scroll',function (event) {
	let nav = document.querySelector("nav");
	let i = (Math.min(20, window.scrollY/4)+1)/21;
	nav.style.boxShadow="0px 2px "+i*21+"px rgba(15,15,15,"+i*.3+")";
	if (window.scrollY <= 0)
	{
//		nav.classList.remove("shadow");
		nav.classList.remove("navbar-active");
		nav.style.boxShadow = "unset";
	}
	else
	{
//		nav.classList.add("shadow");
		nav.classList.add("navbar-active");
	}

}, false);

function formkey() {
	let formkey = document.getElementById("formkey")
	if (formkey) return formkey.innerHTML;
	else return null;
}

function expandDesktopImage(url) {
	const e = this.event
	if(e.ctrlKey || e.metaKey || e.shiftKey || e.altKey)
		return;
	e.preventDefault();
	if (!url)
	{
		url = e.target.dataset.src
		if (!url) url = e.target.src
	}
	document.getElementById("desktop-expanded-image").src = url.replace("200w_d.webp", "giphy.webp");
	document.getElementById("desktop-expanded-image-wrap-link").href = url;
	bootstrap.Modal.getOrCreateInstance(document.getElementById('expandImageModal')).show();
};

document.addEventListener("click", function(e){
	const element = e.target
	if (element instanceof HTMLImageElement && element.alt.startsWith('![]('))
		expandDesktopImage()
});

function bs_trigger(e) {
	let tooltipTriggerList = [].slice.call(e.querySelectorAll('[data-bs-toggle="tooltip"]'));
	tooltipTriggerList.map(function(element){
		return bootstrap.Tooltip.getOrCreateInstance(element);
	});

	const popoverTriggerList = [].slice.call(e.querySelectorAll('[data-bs-toggle="popover"]'));
	popoverTriggerList.map(function(popoverTriggerEl) {
		const popoverId = popoverTriggerEl.getAttribute('data-content-id');
		let contentEl;
		try {contentEl = e.getElementById(popoverId);}
		catch(t) {contentEl = document.getElementById(popoverId);}
		if (contentEl) {
			return bootstrap.Popover.getOrCreateInstance(popoverTriggerEl, {
				content: contentEl.innerHTML,
				html: true,
			});
		}
	})

	if (typeof update_speed_emoji_modal == 'function') {
		let forms = e.querySelectorAll("textarea, .allow-emojis");
		forms.forEach(i => {
			let pseudo_div = document.createElement("div");
			pseudo_div.className = "ghostdiv";
			pseudo_div.style.display = "none";
			i.after(pseudo_div);
			i.addEventListener('input', update_speed_emoji_modal, false);
			i.addEventListener('keydown', speed_carot_navigate, false);
		});
	}
}

var bsTriggerOnReady = function() {
	bs_trigger(document);
}

if (document.readyState === "complete" ||
		(document.readyState !== "loading" && !document.documentElement.doScroll)) {
	bsTriggerOnReady();
} else {
	document.addEventListener("DOMContentLoaded", bsTriggerOnReady);
}

function escapeHTML(unsafe) {
	return unsafe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function changename(s1,s2) {
	const files = document.getElementById(s2).files;
	if (files.length > 4)
	{
		alert("You can't upload more than 4 files at one time!")
		document.getElementById(s2).files = null
		return
	}
	let filename = '';
	for (const e of files) {
		filename += e.name.substr(0, 22) + ', ';
	}
	document.getElementById(s1).innerHTML = escapeHTML(filename.slice(0, -2));
}

function showmore() {
	const btn = this.event.target
	const div = btn.parentElement.nextElementSibling
	div.classList.toggle('d-none')
	if (div.classList.contains('d-none'))
		btn.innerHTML = 'SHOW MORE'
	else
		btn.innerHTML = 'SHOW LESS'
}

function formatDate(d) {
	var year = d.getFullYear();
	var monthAbbr = d.toLocaleDateString('en-us', {month: 'short'});
	var day = d.getDate();
	var hour = ("0" + d.getHours()).slice(-2);
	var minute = ("0" + d.getMinutes()).slice(-2);
	var second = ("0" + d.getSeconds()).slice(-2);
	var tzAbbr = d.toLocaleTimeString('en-us', {timeZoneName: 'short'}).split(' ')[2];

	return (day + " " + monthAbbr + " " + year + " "
			 + hour + ":" + minute + ":" + second + " " + tzAbbr);
}

const timestamps = document.querySelectorAll('[data-time]');

for (const e of timestamps) {
	e.innerHTML = formatDate(new Date(e.dataset.time*1000));
};

function timestamp(str, ti) {
	const date = formatDate(new Date(ti*1000));
	document.getElementById(str).setAttribute("data-bs-original-title", date);
};

function areyousure(t) {
	if (t.value)
		t.value = 'Are you sure?'
	else
		t.innerHTML = t.innerHTML.replace(t.textContent, 'Are you sure?')

	t.setAttribute("onclick", t.dataset.click);

	if (t.dataset.dismiss)
		t.setAttribute("data-bs-dismiss", t.dataset.dismiss);
}

function prepare_to_pause(audio) {
	for (const e of document.querySelectorAll('video,audio'))
	{
		e.addEventListener('play', () => {
			if (!audio.paused) audio.pause();
		});
	}

	window.addEventListener('click', (e) => {
		if (e.target.tagName.toLowerCase() == "lite-youtube" && !audio.paused) audio.pause();
	});
}

function sendFormXHR(e, extraActionsOnSuccess) {
	const form = e.target;
	const xhr = new XMLHttpRequest();
	e.preventDefault();

	formData = new FormData(form);

	formData.append("formkey", formkey());
	actionPath = form.getAttribute("action");

	xhr.open("POST", actionPath);
	xhr.setRequestHeader('xhr', 'xhr');

	xhr.onload = function() {
		if (xhr.status >= 200 && xhr.status < 300) {
			let data = JSON.parse(xhr.response);
			showToast(true, getMessageFromJsonData(true, data));
			if (extraActionsOnSuccess) extraActionsOnSuccess(xhr);
		} else {
			document.getElementById('toast-post-error-text').innerText = "Error, please try again later."
			try {
				let data=JSON.parse(xhr.response);
				var myToast = bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-error'));
				myToast.show();
				document.getElementById('toast-post-error-text').innerText = data["error"];
				if (data && data["details"]) document.getElementById('toast-post-error-text').innerText = data["details"];
			} catch(e) {
				var myToast = bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-success'));
				myToast.hide();
				var myToast = bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-error'));
				myToast.show();
			}
		}
	};

	xhr.send(formData);
}

function sendFormXHRSwitch(e) {
	sendFormXHR(e,
		() => {
			e.target.previousElementSibling.classList.remove('d-none');
			e.target.classList.add('d-none');
		}
	)
}

if ("serviceWorker" in navigator) {
	navigator.serviceWorker.register("/service-worker.js?v=3")
		.then((registration) => registration.update())
		.catch((e) => console.log("Service worker update failed with error", e));
}
