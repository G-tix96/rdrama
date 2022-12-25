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

	container.innerHTML = '<div class="card" onclick="searchGifs(\'agree\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Agree</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/wGhYz3FHaRJgk/200w.webp"> </div> <div class="card" onclick="searchGifs(\'laugh\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Laugh</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/O5NyCibf93upy/200w.webp"> </div> <div class="card" onclick="searchGifs(\'confused\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Confused</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/3o7btPCcdNniyf0ArS/200w.webp"> </div> <div class="card" onclick="searchGifs(\'sad\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Sad</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/ISOckXUybVfQ4/200w.webp"> </div> <div class="card" onclick="searchGifs(\'happy\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Happy</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/XR9Dp54ZC4dji/200w.webp"> </div> <div class="card" onclick="searchGifs(\'awesome\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Awesome</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/3ohzdIuqJoo8QdKlnW/200w.webp"> </div> <div class="card" onclick="searchGifs(\'yes\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Yes</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/J336VCs1JC42zGRhjH/200w.webp"> </div> <div class="card" onclick="searchGifs(\'no\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">No</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/1zSz5MVw4zKg0/200w.webp"> </div> <div class="card" onclick="searchGifs(\'love\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Love</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/4N1wOi78ZGzSB6H7vK/200w.webp"> </div> <div class="card" onclick="searchGifs(\'please\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Please</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/qUIm5wu6LAAog/200w.webp"> </div> <div class="card" onclick="searchGifs(\'scared\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Scared</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/bEVKYB487Lqxy/200w.webp"> </div> <div class="card" onclick="searchGifs(\'angry\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Angry</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/12Pb87uq0Vwq2c/200w.webp"> </div> <div class="card" onclick="searchGifs(\'awkward\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Awkward</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/unFLKoAV3TkXe/200w.webp"> </div> <div class="card" onclick="searchGifs(\'cringe\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Cringe</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/1jDvQyhGd3L2g/200w.webp"> </div> <div class="card" onclick="searchGifs(\'omg\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">OMG</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/3o72F8t9TDi2xVnxOE/200w.webp"> </div> <div class="card" onclick="searchGifs(\'why\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Why</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/1M9fmo1WAFVK0/200w.webp"> </div> <div class="card" onclick="searchGifs(\'gross\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Gross</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/pVAMI8QYM42n6/200w.webp"> </div> <div class="card" onclick="searchGifs(\'meh\')"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Meh</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/xT77XTpyEzJ4OJO06c/200w.webp"> </div>'
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
		noGIFs.innerHTML = '<div class="text-center py-3 mt-3"><div class="mb-3"><i class="fas fa-frown text-gray-500" style="font-size: 3.5rem"></i></div><p class="font-weight-bold text-gray-500 mb-0">Aw shucks. No GIFs found...</p></div>';
		container.innerHTML = null;
		loadGIFs.innerHTML = null;
	}
	else {
		for (let i = 0; i < 48; i++) {
			gifURL[i] = "https://media.giphy.com/media/" + data[i].id + "/200w.webp";
			const insert = `<img loading="lazy" class="card giphy img-fluid" data-bs-dismiss="modal" src="${gifURL[i]}"></div>`
			container.insertAdjacentHTML('beforeend', insert);
			noGIFs.innerHTML = null;
			loadGIFs.innerHTML = '<div class="text-center py-3"><div class="mb-3"><i class="fas fa-grin-beam-sweat text-gray-500" style="font-size: 3.5rem"></i></div><p class="font-weight-bold text-gray-500 mb-0">Thou&#39;ve reached the end of the list!</p></div>';
		}
	}
}
