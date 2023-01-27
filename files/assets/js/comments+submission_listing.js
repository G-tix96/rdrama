function pinned_timestamp(id) {
	const el = document.getElementById(id)
	const pintooltip = el.getAttribute("data-bs-original-title")
	if (!pintooltip.includes('until'))
		{
			const time = formatDate(new Date(parseInt(el.dataset.timestamp)*1000))
			el.setAttribute("data-bs-original-title", `${pintooltip} until ${time}`)
		}
}

/** @type {HTMLImageElement} */
const popClickBadgeTemplateDOM = document.createElement("IMG");
popClickBadgeTemplateDOM.classList.add("pop-badge");
popClickBadgeTemplateDOM.loading = "lazy";
popClickBadgeTemplateDOM.alt = "badge";

/**
* @param {MouseEvent} e
*/
function popclick(e) {
	// We let through those methods
	if(e.ctrlKey || e.metaKey || e.shiftKey || e.altKey)
		return;
	e.preventDefault();

	if(e.currentTarget.dataset.popInfo === undefined)
		throw new SyntaxError("ill formed HTML! data-pop-info not present!!!");

	const author = JSON.parse(e.currentTarget.dataset.popInfo);
	if(!(author instanceof Object))
		throw new SyntaxError("data-pop-info was not valid!");

	// This is terrible lol. in header.js:bs_trigger() we should add
	// to the ANCHOR element an event handler for "show.bs.tooltip" to build this
	// when the DOM is ready.
	// PROBLEM: IT DOES NOT WORK :MARSEYCRAZYTROLL: idk why it should work according to
	// boostrap docs!
	setTimeout(() => {
		let popover = document.getElementsByClassName("popover")
		popover = popover[popover.length-1]

		if (popover.getElementsByClassName('pop-badges')) {
			const badgesDOM = popover.getElementsByClassName('pop-badges')[0];
			badgesDOM.innerHTML = "";
			for (const badge of author["badges"]) {
				const badgeDOM = popClickBadgeTemplateDOM.cloneNode();
				badgeDOM.src = badge + "?b=6";

				badgesDOM.append(badgeDOM);
			}
		}

		popover.getElementsByClassName('pop-banner')[0].src = author["bannerurl"]
		popover.getElementsByClassName('pop-picture')[0].src = author["profile_url"]
		if (author["hat"]) popover.getElementsByClassName('pop-hat')[0].src = author['hat'] + "?h=7"
		popover.getElementsByClassName('pop-username')[0].innerHTML = author["username"]
		if (popover.getElementsByClassName('pop-bio').length > 0) {
			popover.getElementsByClassName('pop-bio')[0].innerHTML = author["bio_html"]
		}
		popover.getElementsByClassName('pop-postcount')[0].innerHTML = author["post_count"]
		popover.getElementsByClassName('pop-commentcount')[0].innerHTML = author["comment_count"]
		popover.getElementsByClassName('pop-coins')[0].innerHTML = author["coins"]
		popover.getElementsByClassName('pop-view_more')[0].href = author["url"]
		popover.getElementsByClassName('pop-created-date')[0].innerHTML = author["created_date"]
	}, 5);
}

document.addEventListener("click", function(){
	active = document.activeElement.getAttributeNode("class");
	if (active && active.nodeValue == "user-name text-decoration-none"){
		pops = document.getElementsByClassName('popover')
		if (pops.length > 1) pops[0].remove()
	}
	else document.querySelectorAll('.popover').forEach(e => e.remove());
});

function post(url) {
	const xhr = createXhrWithFormKey(url);
	xhr[0].send(xhr[1]);
};

function poll_vote_0(oid, parentid, kind) {
	for(let el of document.getElementsByClassName('presult-'+parentid)) {
		el.classList.remove('d-none');
	}
	const full_oid = kind + '-' + oid
	const type = document.getElementById(full_oid).checked;
	const scoretext = document.getElementById('score-' + full_oid);
	const score = Number(scoretext.textContent);
	if (type == true) scoretext.textContent = score + 1;
	else scoretext.textContent = score - 1;
	post(`/vote/${kind}/option/${oid}`);
}

function poll_vote_1(oid, parentid, kind) {
	for(let el of document.getElementsByClassName('presult-'+parentid)) {
		el.classList.remove('d-none');
	}
	const full_oid = kind + '-' + oid
	let curr = document.getElementById(`current-${kind}-${parentid}`)
	if (curr && curr.value)
	{
		const scoretext = document.getElementById('score-' + curr.value);
		const score = Number(scoretext.textContent);
		scoretext.textContent = score - 1;
	}

	const scoretext = document.getElementById('score-' + full_oid);

	const score = Number(scoretext.textContent);
	scoretext.textContent = score + 1;
	post(`/vote/${kind}/option/${oid}`);
	curr.value = full_oid
}

function bet_vote(t, oid) {
	postToast(t, `/vote/post/option/${oid}`,
		{
		},
		() => {
			for(let el of document.getElementsByClassName('bet')) {
				el.disabled = true;
			}
			for(let el of document.getElementsByClassName('cost')) {
				el.classList.add('d-none')
			}
			const scoretext = document.getElementById('option-' + oid);
			const score = Number(scoretext.textContent);
			scoretext.textContent = score + 1;

			document.getElementById("user-coins-amount").innerText = parseInt(document.getElementById("user-coins-amount").innerText) - 200;
		}
	);
}
