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
					try {
						document.getElementById(button1).classList.toggle(cls);
					}
					catch (e) {}
					try {
						document.getElementById(button2).classList.toggle(cls);
					}
					catch (e) {}
				}
			}
			if (typeof extraActionsOnSuccess == 'function')
			extraActionsOnSuccess(xhr);
		}
	, method);
}

if (location.pathname != '/submit')
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

document.addEventListener('show.bs.modal', function (e) {
	location.hash = "modal";
});

document.addEventListener('hide.bs.modal', function (e) {
	if(location.hash == "#modal") {
		history.back();
	}
});

window.addEventListener('hashchange', function (e) {
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

	let computed = window.getComputedStyle(field);

	let height = parseInt(computed.getPropertyValue('border-top-width'), 10)
	+ parseInt(computed.getPropertyValue('padding-top'), 10)
	+ field.scrollHeight
	+ parseInt(computed.getPropertyValue('padding-bottom'), 10)
	+ parseInt(computed.getPropertyValue('border-bottom-width'), 10);

	field.style.height = height + 'px';
	if (Math.abs(window.scrollX - xpos) < 1 && Math.abs(window.scrollY - ypos) < 1) return;
	window.scrollTo(xpos,ypos);
};

const textareas = document.getElementsByTagName('textarea')
for (const element of textareas) {
	element.addEventListener('input', () => {
		autoExpand(element)
	});
}

function smoothScrollTop()
{
	window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Click navbar to scroll back to top
const nav = document.getElementsByTagName('nav')

if (nav.length) {
	nav[0].addEventListener('click', (e) => {
		if (e.target.id === "navbar" ||
			e.target.classList.contains("container-fluid") ||
			e.target.id == "navbarResponsive" ||
			e.target.id == "logo-container" ||
			e.target.classList.contains("srd"))
			smoothScrollTop();
	}, false);
}

function formkey() {
	let formkey = document.getElementById("formkey")
	if (formkey) return formkey.innerHTML;
	else return null;
}

function expandImage(url) {
	const e = this.event
	if(e.ctrlKey || e.metaKey || e.shiftKey || e.altKey)
		return;
	e.preventDefault();
	if (!url)
	{
		url = e.target.dataset.src
		if (!url) url = e.target.src
	}
	document.getElementById("desktop-expanded-image").src = url.replace("200w.webp", "giphy.webp");
	document.getElementById("desktop-expanded-image-wrap-link").href = url.replace("200w.webp", "giphy.webp");

	bootstrap.Modal.getOrCreateInstance(document.getElementById('expandImageModal')).show();
};

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

function escapeHTML(unsafe) {
	return unsafe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function changename(s1,s2) {
	const files = document.getElementById(s2).files;
	if (files.length > 4)
	{
		alert("You can't upload more than 4 files at one time!")
		document.getElementById(s2).value = null
		return
	}
	let filename = '';
	for (const e of files) {
		filename += e.name.substr(0, 22) + ', ';
	}
	document.getElementById(s1).innerHTML = escapeHTML(filename.slice(0, -2));
}

function showmore(t) {
	const div = t.parentElement.nextElementSibling
	div.classList.toggle('d-none')
	if (div.classList.contains('d-none'))
		t.innerHTML = 'SHOW MORE'
	else
		t.innerHTML = 'SHOW LESS'
}

function formatDate(d) {
	let year = d.getFullYear();
	let monthAbbr = d.toLocaleDateString('en-us', {month: 'short'});
	let day = d.getDate();
	let hour = ("0" + d.getHours()).slice(-2);
	let minute = ("0" + d.getMinutes()).slice(-2);
	let second = ("0" + d.getSeconds()).slice(-2);
	let tzAbbr = d.toLocaleTimeString('en-us', {timeZoneName: 'short'}).split(' ')[2];

	return (day + " " + monthAbbr + " " + year + " "
			 + hour + ":" + minute + ":" + second + " " + tzAbbr);
}

const timestamps = document.querySelectorAll('[data-time]');

for (const e of timestamps) {
	e.innerHTML = formatDate(new Date(e.dataset.time*1000));
};

function timestamp(t, ti) {
	const date = formatDate(new Date(ti*1000));
	t.setAttribute("data-bs-original-title", date);
};

function areyousure(t) {
	if (t.value)
		t.value = 'Are you sure?'
	else
		t.innerHTML = t.innerHTML.replace(t.textContent, 'Are you sure?')

	t.setAttribute("data-onclick", t.dataset.areyousure);

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

	document.addEventListener('click', (e) => {
		if ((e.target.tagName.toLowerCase() == "lite-youtube" || e.target.classList.contains('lty-playbtn')) && !audio.paused) {
			audio.pause();
		}
	});
}

function sendFormXHR(form, extraActionsOnSuccess) {
	const xhr = new XMLHttpRequest();

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
				bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-error')).show();
				document.getElementById('toast-post-error-text').innerText = data["error"];
				if (data && data["details"]) document.getElementById('toast-post-error-text').innerText = data["details"];
			} catch(e) {
				bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-success')).hide();
				bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-error')).show();
			}
		}
	};

	xhr.send(formData);
}

function sendFormXHRSwitch(form) {
	sendFormXHR(form,
		() => {
			form.previousElementSibling.classList.remove('d-none');
			form.classList.add('d-none');
		}
	)
}

let sortAscending = {};

function sort_table(t) {
	const n = Array.prototype.indexOf.call(t.parentElement.children, t);
	const table = this.event.target.parentElement.parentElement.parentElement
	const rows = table.rows;
	let items = [];
	for (let i = 1; i < rows.length; i++) {
		const ele = rows[i];
		let x = rows[i].getElementsByTagName("TD")[n];
		if (!('sortKey' in x.dataset)) {
			x = x.getElementsByTagName('a')[0] || x;
		}
		let attr;
		if ('sortKey' in x.dataset) {
			attr = x.dataset.sortKey;
		} else if ('time' in x.dataset) {
			attr = parseInt(x.dataset.time);
		} else {
			attr = x.innerText
			if (/^[\d-,]+$/.test(x.innerHTML)) {
				attr = parseInt(attr.replace(/,/g, ''))
			}
		}
		items.push({ele, attr});
	}
	if (sortAscending[n]) {
		items.sort((a, b) => a.attr > b.attr ? 1 : -1);
		sortAscending[n] = false;
	} else {
		items.sort((a, b) => a.attr < b.attr ? 1 : -1);
		sortAscending[n] = true;
	}

	for (let i = items.length - 1; i--;) {
		items[i].ele.parentNode.insertBefore(items[i].ele, items[i + 1].ele);
	}
}

if (window.matchMedia('(display-mode: minimal-ui)')['matches']) {
	const links = document.querySelectorAll('a[data-target="t"]');
	for (const link of links) {
		link.removeAttribute("target");
	}
}

if (document.getElementById('gbrowser').value == 'apple') {
	const videos = document.querySelectorAll('video')

	for (const video of videos) {
		const link = video.src
		const htmlString = `
			<a rel="nofollow noopener" href="${link}" target="_blank">
				<div class="d-flex justify-content-between align-items-center border rounded p-2 mb-3 download-video">
					<span>${link}</span>
					<i class="fas fa-external-link-alt text-small"></i>
				</div>
			</a>`
		const div = document.createElement('div');
		div.innerHTML = htmlString;
		video.after(div)
	}
}

function logout(t) {
	postToast(t, '/logout',
		{
		},
		() => {
			location.href = '/'
		});
}

function execute(element, attr) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		return
	}
	const funcs = element.getAttribute(`data-${attr}`).split(';')
	for (const func of funcs) {
		if (func) {
			const split = func.split('(')
			const name = split[0]
			const args = split[1].replace(/[')]/g, "").split(',').map(a => a.trim());
			if (args[0] == 'this') args[0] = element
			try {
				window[name](...args);
			}
			catch (e) {
				console.log(e)
				console.log(name)
			}
		}
	}
}

const onsubmit = document.querySelectorAll('[data-onsubmit]');
for (const element of onsubmit) {
	element.addEventListener('submit', (event)=>{
		event.preventDefault();
		execute(element, 'onsubmit')
	});
}

const onfocus = document.querySelectorAll('[data-onfocus]');
for (const element of onfocus) {
	element.addEventListener('focus', () => {execute(element, 'onfocus')});
}

const onclick_submit = document.querySelectorAll('[onclick_submit]');
for (const element of onclick_submit) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('click', () => {element.form.submit()});
}

const onchange_submit = document.querySelectorAll('[onchange_submit]');
for (const element of onchange_submit) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('change', () => {element.form.submit()});
}

const undisable_element = document.querySelectorAll('[data-undisable_element]');
for (const element of undisable_element) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('input', () => {
		document.getElementById(element.dataset.undisable_element).disabled = false;
	});
}

const setting_switchs = document.getElementsByClassName('setting_switch');
for (const element of setting_switchs) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('change', () => {
		postToastSwitch(element,`/settings/personal?${element.name}=${element.checked}`);
	});
}

const setting_selects = document.getElementsByClassName('setting_select');
for (const element of setting_selects) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('change', () => {
		if (element.dataset.reload)
			postToastReload(element,`/settings/personal?${element.name}=${element.value}`);
		else
			postToast(element,`/settings/personal?${element.name}=${element.value}`);
	});
}

const reload_page = document.getElementById('reload_page')
if (reload_page) {
	reload_page.addEventListener('click', () => {location.reload()});
}

const TH = document.getElementsByTagName('th')
for (const element of TH) {
	element.addEventListener('click', () => {sort_table(element)});
}

const toggleelement = document.querySelectorAll('[data-toggleelement]');
for (const element of toggleelement) {
	element.addEventListener('click', () => {
		document.getElementById(element.dataset.toggleelement).classList.toggle(element.dataset.toggleattr);
	});
}

function register_new_elements(e) {
	const showmores = document.getElementsByClassName('showmore')
	for (const element of showmores) {
		element.addEventListener('click', () => {showmore(element)});
	}
	
	const onclick = e.querySelectorAll('[data-onclick]');
	for (const element of onclick) {
		element.addEventListener('click', () => {execute(element, 'onclick')});
	}

	const oninput = e.querySelectorAll('[data-oninput]');
	for (const element of oninput) {
		element.addEventListener('input', () => {execute(element, 'oninput')});
	}

	const onmouseover = e.querySelectorAll('[data-onmouseover]');
	for (const element of onmouseover) {
		element.addEventListener('mouseover', () => {execute(element, 'onmouseover')});
	}

	const onchange = e.querySelectorAll('[data-onchange]');
	for (const element of onchange) {
		element.addEventListener('change', () => {execute(element, 'onchange')});
	}

	const popover_triggers = document.getElementsByClassName('user-name');
	for (const element of popover_triggers) {
		element.addEventListener('click', (e) => {popclick(e)});
	}

	const expandable = document.querySelectorAll('.in-comment-image, img[alt^="![]("]');
	for (const element of expandable) {
		element.addEventListener('click', () => {expandImage()});
	}
}

register_new_elements(document);
bs_trigger(document);
