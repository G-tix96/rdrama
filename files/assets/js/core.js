/*const bootstrap = require("./bootstrap");*/

function isShopConfirmation(t) {
	return t.id.startsWith('buy1-') || t.id.startsWith('buy2-');
}

function prePostToastNonShopActions(t, url, button1, button2, className) {
	let isShopConfirm = isShopConfirmation(t);

	if (!isShopConfirm)
	{
		t.disabled = true;
		t.classList.add("disabled");
	}
}

function showToast(success, message) {
	let element = success ? "toast-post-success" : "toast-post-error"
	if (!message) {
		message = success ? "Success" : "Error, please try again later";
	}
	document.getElementById(element + "-text").innerText = message;
	bootstrap.Toast.getOrCreateInstance(document.getElementById(element)).show();
}

function postToastLoad(xhr, className, extraActionsOnSuccess, extraActionsOnError) {
	let data
	try {
		data = JSON.parse(xhr.response)
	}
	catch (e) {
		console.log(e)
	}
	if (xhr.status >= 200 && xhr.status < 300) {
		showToast(true, data && data["message"] ? data["message"] : "Success!");
		if (button1)
		{
			if (typeof(button1) == 'boolean') {
				location.reload()
            } else {
				document.getElementById(button1).classList.toggle(className);
				document.getElementById(button2).classList.toggle(className);
			}
		}
		if (extraActionsOnSuccess) extraActionsOnSuccess(xhr);
	} else {
		let message = data && data["error"] ? data["error"] : "Error, please try again later"
		if (data && data["details"]) message = data["details"];
		showToast(false, message);
		if (extraActionsOnError) extraActionsOnError(xhr);
	}
}

function postPostToastNonShopActions(t, url, button1, button2, className) {
	let isShopConfirm = isShopConfirmation(t);
	if (!isShopConfirm)
	{
		setTimeout(() => {
			t.disabled = false;
			t.classList.remove("disabled");
		}, 2000);
	}
}

function postToast(t, url, button1, button2, className, extraActions, extraActionsError) {
	prePostToastNonShopActions(t, url, button1, button2, className)
	const xhr = new XMLHttpRequest();
	xhr.open("POST", url);
	xhr.setRequestHeader('xhr', 'xhr');
	const form = new FormData()
	form.append("formkey", formkey());

	xhr.onload = function() {
		postToastLoad(xhr, className, extraActions, extraActionsError)
		postPostToastNonShopActions(t, url, button1, button2, className)
	};
	xhr.send(form);
}

/* temporary compatability function. js styling wants us to use thisCase so any new things should use that */
function post_toast(t, url, button1, button2, classname, extra_actions, extra_actions_error) {
	postToast(t, url, button1, button2, classname, extra_actions, extra_actions_error);
}

function post_toast_callback(url, data, callback) {
	const xhr = new XMLHttpRequest();
	xhr.open("POST", url);
	xhr.setRequestHeader('xhr', 'xhr');
	const form = new FormData()
	form.append("formkey", formkey());

	if(typeof data === 'object' && data !== null) {
		for(let k of Object.keys(data)) {
			form.append(k, data[k]);
		}
	}

	form.append("formkey", formkey());
	xhr.onload = function() {
		let result
		if (callback) result = callback(xhr);
		if (xhr.status >= 200 && xhr.status < 300) {
			var myToast = bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-error'));
			myToast.hide();

			var myToast = bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-success'));
			myToast.show();

			try {
				if(typeof result == "string") {
					document.getElementById('toast-post-success-text').innerText = result;
				} else {
					document.getElementById('toast-post-success-text').innerText = JSON.parse(xhr.response)["message"];
				}
			} catch(e) {
			}

			return true;
		} else {
			var myToast = bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-success'));
			myToast.hide();

			var myToast = bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-error'));
			myToast.show();

			try {
				if(typeof result == "string") {
					document.getElementById('toast-post-error-text').innerText = result;
				} else {
					document.getElementById('toast-post-error-text').innerText = JSON.parse(xhr.response)["error"];
				}
				return false
			} catch(e) {console.log(e)}

			return false;
		}
	};
	xhr.send(form);
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

function autoExpand (field) {
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
(() => {
	let toplisteners = [
		document.querySelector('nav')
	];

	for (let i of toplisteners)
	{
		i.addEventListener('click', (e) => {
			if (e.target.id === "navbar" ||
				e.target.classList.contains("container-fluid") ||
				e.target.id == "navbarResponsive" ||
				e.target.id == "logo-container" ||
				e.target.classList.contains("srd"))
				smoothScrollTop();
		}, false);
	}
})();

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
		return true;
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

	if (typeof update_speed_emoji_modal != 'undefined') {
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
		filename += e.name.substr(0, 20) + ', ';
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
	const date = new Date(e.dataset.time*1000);
	e.innerHTML = formatDate(date);
};

function timestamp(str, ti) {
	const date = new Date(ti*1000);
	document.getElementById(str).setAttribute("data-bs-original-title", formatDate(date));
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