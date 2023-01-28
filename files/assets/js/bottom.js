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

document.addEventListener("click", function(e){
	const element = e.target
	if (element instanceof HTMLImageElement && (element.alt.startsWith('![](')) || element.classList.contains('in-comment-image'))
		expandImage()
	else if (element.tagName == "TH")
		sort_table(element)
	else if (element.classList.contains('giphy'))
		insertGIF(e.target.src);
	else if (element.classList.contains('gif-cat-overlay'))
		searchGifs(e.target.firstElementChild.innerHTML);
	else if (element.dataset.href)
		location.href = element.dataset.href;

	if (element.dataset.toggleelement) {
		document.getElementById(element.dataset.toggleelement).classList.toggle(element.dataset.toggleattr)
	}
});

const onsubmit = document.querySelectorAll('[data-onsubmit]');
for (const element of onsubmit) {
	element.onsubmit = (event)=>{
		event.preventDefault();
		execute(element, 'onsubmit')
	};
}

const onfocus = document.querySelectorAll('[data-onfocus]');
for (const element of onfocus) {
	element.onfocus = () => {execute(element, 'onfocus')};
}

const onclick_submit = document.querySelectorAll('[onclick_submit]');
for (const element of onclick_submit) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.onclick = () => {element.form.submit()};
}

const onchange_submit = document.querySelectorAll('[onchange_submit]');
for (const element of onchange_submit) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.onchange = () => {element.form.submit()};
}

const undisable_element = document.querySelectorAll('[data-undisable_element]');
for (const element of undisable_element) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.oninput = () => {
		document.getElementById(element.dataset.undisable_element).disabled = false;
	};
}

const setting_switchs = document.getElementsByClassName('setting_switch');
for (const element of setting_switchs) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.onchange = () => {
		postToastSwitch(element,`/settings/personal?${element.name}=${element.checked}`);
	};
}

const setting_selects = document.getElementsByClassName('setting_select');
for (const element of setting_selects) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.onchange = () => {
		if (element.dataset.reload)
			postToastReload(element,`/settings/personal?${element.name}=${element.value}`);
		else
			postToast(element,`/settings/personal?${element.name}=${element.value}`);
	};
}

const reload_page = document.getElementById('reload_page')
if (reload_page) {
	reload_page.onclick = () => {location.reload()};
}
}

function register_new_elements(e) {
	const showmores = document.getElementsByClassName('showmore')
	for (const element of showmores) {
		element.onclick = () => {showmore(element)};
	}
	
	const onclick = e.querySelectorAll('[data-onclick]');
	for (const element of onclick) {
		element.onclick = () => {execute(element, 'onclick')};
	}

	const oninput = e.querySelectorAll('[data-oninput]');
	for (const element of oninput) {
		element.oninput = () => {execute(element, 'oninput')};
	}

	const onmouseover = e.querySelectorAll('[data-onmouseover]');
	for (const element of onmouseover) {
		element.onmouseover = () => {execute(element, 'onmouseover')};
	}

	const onchange = e.querySelectorAll('[data-onchange]');
	for (const element of onchange) {
		element.onchange = () => {execute(element, 'onchange')};
	}

	const popover_triggers = document.getElementsByClassName('user-name');
	for (const element of popover_triggers) {
		element.onclick = (e) => {popclick(e)};
	}
	}
}

register_new_elements(document);
bs_trigger(document);
