const gifSearchBar = document.getElementById('gifSearch')
const loadGIFs = document.getElementById('gifs-load-more');
const noGIFs = document.getElementById('no-gifs-found');
const container = document.getElementById('GIFs');
const backBtn = document.getElementById('gifs-back-btn');
const cancelBtn = document.getElementById('gifs-cancel-btn');

let commentFormID;

function insertGIF(url) {
	const commentBox = document.getElementById(commentFormID);
	const old = commentBox.value;

	if (old) commentBox.value = `${old}\n${url}`;
	else commentBox.value = url

	if (typeof checkForRequired === "function") checkForRequired();
}

document.getElementById('gifModal').addEventListener('shown.bs.modal', function () {
	gifSearchBar.focus();
	setTimeout(() => {
		gifSearchBar.focus();
	}, 200);
	setTimeout(() => {
		gifSearchBar.focus();
	}, 1000);
});

document.getElementById('gifModal').addEventListener('shown.bs.modal', function () {
	gifSearchBar.focus();
	setTimeout(() => {
		gifSearchBar.focus();
	}, 200);
	setTimeout(() => {
		gifSearchBar.focus();
	}, 1000);
});


async function getGifs(form) {
	commentFormID = form;

	gifSearchBar.value = null;
	backBtn.innerHTML = null;
	cancelBtn.innerHTML = null;
	noGIFs.innerHTML = null;
	loadGIFs.innerHTML = null;

	container.innerHTML = `	
	<div class="card">
		<div class="gif-cat-overlay"><div>Agree</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/wGhYz3FHaRJgk/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Laugh</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/O5NyCibf93upy/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Confused</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/3o7btPCcdNniyf0ArS/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Sad</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/ISOckXUybVfQ4/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Happy</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/XR9Dp54ZC4dji/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Awesome</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/3ohzdIuqJoo8QdKlnW/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Yes</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/J336VCs1JC42zGRhjH/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>No</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/1zSz5MVw4zKg0/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Love</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/4N1wOi78ZGzSB6H7vK/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Please</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/qUIm5wu6LAAog/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Scared</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/bEVKYB487Lqxy/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Angry</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/12Pb87uq0Vwq2c/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Awkward</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/unFLKoAV3TkXe/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Cringe</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/1jDvQyhGd3L2g/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>OMG</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/3o72F8t9TDi2xVnxOE/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Why</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/1M9fmo1WAFVK0/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Gross</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/pVAMI8QYM42n6/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Meh</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/xT77XTpyEzJ4OJO06c/200w.webp">
	</div>`
}

async function searchGifs(searchTerm) {

	if (searchTerm !== undefined) {
		gifSearchBar.value = searchTerm;
	}
	else {
		gifSearchBar.value = null;
	}

	container.innerHTML = '';

	backBtn.innerHTML = '<button class="btn btn-link pl-0 pr-3" id="gifs-back-btn" onclick="getGifs()"><i class="fas fa-long-arrow-left text-muted ml-3"></i></button>';

	cancelBtn.innerHTML = '<button class="btn btn-link pl-3 pr-0" id="gifs-cancel-btn" onclick="getGifs()"><i class="fas fa-times text-muted"></i></button>';

	let response = await fetch("/giphy?searchTerm=" + searchTerm + "&limit=48");
	let data = await response.json()
	const max = data.length - 1
	data = data.data
	const gifURL = [];

	if (max <= 0) {
		noGIFs.innerHTML = '<div class="text-center py-3 mt-3"></div><div class="mb-3"><i class="fas fa-frown text-gray-500" style="font-size: 3.5rem"></i></div><p class="font-weight-bold text-gray-500 mb-0">Aw shucks. No GIFs found...</p></div>';
		container.innerHTML = null;
		loadGIFs.innerHTML = null;
	}
	else {
		for (let i = 0; i < 48; i++) {
			gifURL[i] = "https://media.giphy.com/media/" + data[i].id + "/200w.webp";
			const insert = `<img class="giphy" loading="lazy" data-bs-dismiss="modal" src="${gifURL[i]}"></div>`
			container.insertAdjacentHTML('beforeend', insert);
			noGIFs.innerHTML = null;
			loadGIFs.innerHTML = '<div class="text-center py-3"></div><div class="mb-3"><i class="fas fa-grin-beam-sweat text-gray-500" style="font-size: 3.5rem"></i></div><p class="font-weight-bold text-gray-500 mb-0">Thou&#39;ve reached the end of the list!</p></div>';
		}
	}
}
