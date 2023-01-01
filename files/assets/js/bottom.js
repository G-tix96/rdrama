function execute(element, attr) {
	if (element.dataset.nonce != nonce) return
	const funcs = element.getAttribute(`data-${attr}`).split(';')
	for (const func of funcs) {
		if (func) {
			const split = func.split('(')
			const name = split[0]
			const args = split[1].replace(/[' )]/g, "").split(',')
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
	if (element instanceof HTMLImageElement && element.alt.startsWith('![]('))
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

const onclick = document.querySelectorAll('[data-onclick]');
for (const element of onclick) {
	element.onclick = ()=>{execute(element, 'onclick')};
}

const oninput = document.querySelectorAll('[data-oninput]');
for (const element of oninput) {
	element.oninput = ()=>{execute(element, 'oninput')};
}

const onmouseover = document.querySelectorAll('[data-onmouseover]');
for (const element of onmouseover) {
	element.onmouseover = ()=>{execute(element, 'onmouseover')};
}

const onchange = document.querySelectorAll('[data-onchange]');
for (const element of onchange) {
	element.onchange = ()=>{execute(element, 'onchange')};
}

const onsubmit = document.querySelectorAll('[data-onsubmit]');
for (const element of onsubmit) {
	element.onsubmit = (event)=>{
		event.preventDefault();
		execute(element, 'onsubmit')
	};
}

const onfocus = document.querySelectorAll('[data-onfocus]');
for (const element of onfocus) {
	element.onfocus = ()=>{execute(element, 'onfocus')};
}

const click_submit = document.querySelectorAll('[click_submit]');
for (const element of click_submit) {
	if (element.dataset.nonce != nonce) continue
	element.onclick = () => {element.form.submit()};
}

const change_submit = document.querySelectorAll('[change_submit]');
for (const element of change_submit) {
	if (element.dataset.nonce != nonce) continue
	element.onchange = () => {element.form.submit()};
}

const undisable_element = document.querySelectorAll('[data-undisable_element]');
for (const element of undisable_element) {
	if (element.dataset.nonce != nonce) continue
	element.oninput = () => {
		document.getElementById(element.dataset.undisable_element).disabled = false;
	};
}

// data-on[^"]*?="[^"]+?\.(?![%a-z._ ]+?\})

const setting_switchs = document.getElementsByClassName('setting_switch');
for (const element of setting_switchs) {
	if (element.dataset.nonce != nonce) continue
	element.onchange = () => {
		postToastSwitch(this,`/settings/${element.name}?poor=${element.checked}`);
	};
}

const setting_reloads = document.getElementsByClassName('setting_reload');
for (const element of setting_reloads) {
	if (element.dataset.nonce != nonce) continue
	element.onchange = () => {
		postToastReload(this,`/settings/${element.name}?poor=${element.checked}`);
	};
}

const reload_page = document.getElementById('reload-page')
if (reload_page)
	reload_page.onclick = ()=>{location.reload()};
