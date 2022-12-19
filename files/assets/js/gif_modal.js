let commentFormID;

function commentForm(form) {
	commentFormID = form;
};

const gifSearchBar = document.getElementById('gifSearch')

async function getGif(searchTerm) {

	if (searchTerm !== undefined) {
		gifSearchBar.value = searchTerm;
	}
	else {
		gifSearchBar.value = null;
	}

	const loadGIFs = document.getElementById('gifs-load-more');

	const noGIFs = document.getElementById('no-gifs-found');

	const container = document.getElementById('GIFs');

	const backBtn = document.getElementById('gifs-back-btn');

	const cancelBtn = document.getElementById('gifs-cancel-btn');

	container.innerHTML = '';

	if (searchTerm == undefined) {
		container.innerHTML = '<div class="card" onclick="getGif(\'agree\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Agree</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/wGhYz3FHaRJgk/giphy.webp"> </div> <div class="card" onclick="getGif(\'laugh\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Laugh</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/O5NyCibf93upy/giphy.webp"> </div> <div class="card" onclick="getGif(\'confused\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Confused</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/3o7btPCcdNniyf0ArS/giphy.webp"> </div> <div class="card" onclick="getGif(\'sad\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Sad</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/ISOckXUybVfQ4/giphy.webp"> </div> <div class="card" onclick="getGif(\'happy\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Happy</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/XR9Dp54ZC4dji/giphy.webp"> </div> <div class="card" onclick="getGif(\'awesome\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Awesome</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/3ohzdIuqJoo8QdKlnW/giphy.webp"> </div> <div class="card" onclick="getGif(\'yes\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Yes</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/J336VCs1JC42zGRhjH/giphy.webp"> </div> <div class="card" onclick="getGif(\'no\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">No</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/1zSz5MVw4zKg0/giphy.webp"> </div> <div class="card" onclick="getGif(\'love\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Love</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/4N1wOi78ZGzSB6H7vK/giphy.webp"> </div> <div class="card" onclick="getGif(\'please\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Please</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/qUIm5wu6LAAog/giphy.webp"> </div> <div class="card" onclick="getGif(\'scared\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Scared</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/bEVKYB487Lqxy/giphy.webp"> </div> <div class="card" onclick="getGif(\'angry\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Angry</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/12Pb87uq0Vwq2c/giphy.webp"> </div> <div class="card" onclick="getGif(\'awkward\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Awkward</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/unFLKoAV3TkXe/giphy.webp"> </div> <div class="card" onclick="getGif(\'cringe\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Cringe</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/1jDvQyhGd3L2g/giphy.webp"> </div> <div class="card" onclick="getGif(\'omg\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">OMG</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/3o72F8t9TDi2xVnxOE/giphy.webp"> </div> <div class="card" onclick="getGif(\'why\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Why</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/1M9fmo1WAFVK0/giphy.webp"> </div> <div class="card" onclick="getGif(\'gross\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Gross</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/pVAMI8QYM42n6/giphy.webp"> </div> <div class="card" onclick="getGif(\'meh\')" style="overflow: hidden"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold">Meh</div> </div> <img loading="lazy" class="img-fluid" src="https://media.giphy.com/media/xT77XTpyEzJ4OJO06c/giphy.webp"> </div>'

		backBtn.innerHTML = null;

		cancelBtn.innerHTML = null;

		noGIFs.innerHTML = null;

		loadGIFs.innerHTML = null;
	}
	else {
		backBtn.innerHTML = '<button class="btn btn-link pl-0 pr-3" id="gifs-back-btn" onclick="getGif()"><i class="fas fa-long-arrow-left text-muted ml-3"></i></button>';

		cancelBtn.innerHTML = '<button class="btn btn-link pl-3 pr-0" id="gifs-cancel-btn" onclick="getGif()"><i class="fas fa-times text-muted"></i></button>';

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
			gifURL[i] = "https://media.giphy.com/media/" + data[i].id + "/giphy.webp";
			if (data[i].username==''){
				const insert = '<div class="card bg-white" style="overflow: hidden" data-bs-dismiss="modal" aria-label="Close" onclick="insertGIF(\'' + 'https://media.giphy.com/media/' + data[i].id + '/giphy.webp' + '\',\'' + commentFormID + '\')"><img loading="lazy" class="img-fluid" src="' + gifURL[i] + '"></div>'
				container.insertAdjacentHTML('beforeend', insert);
			}
			else {
				const insert = '<div class="card bg-white" style="overflow: hidden" data-bs-dismiss="modal" aria-label="Close" title="by '+data[i].username+' on GIPHY" onclick="insertGIF(\'' + 'https://media.giphy.com/media/' + data[i].id + '/giphy.webp' + '\',\'' + commentFormID + '\')"><img loading="lazy" class="img-fluid" src="' + gifURL[i] + '"></div>'
				container.insertAdjacentHTML('beforeend', insert);
			}
			noGIFs.innerHTML = null;
			loadGIFs.innerHTML = '<div class="text-center py-3"><div class="mb-3"><i class="fas fa-grin-beam-sweat text-gray-500" style="font-size: 3.5rem"></i></div><p class="font-weight-bold text-gray-500 mb-0">Thou&#39;ve reached the end of the list!</p></div>';
			}
		}
	}
}

function insertGIF(url,form) {

	const commentBox = document.getElementById(form);
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
