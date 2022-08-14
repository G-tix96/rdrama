const title = document.getElementById("post-title");
const text = document.getElementById("post-text");
const url = document.getElementById("post-url");
const button = document.getElementById("create_button");
const image = document.getElementById("file-upload");
const image2 = document.getElementById("file-upload-submit");

title.value = localStorage.getItem("post_title")
text.value = localStorage.getItem("post_text")
url.value = localStorage.getItem("post_url")

markdown(text);

function checkForRequired() {
	if (url.value.length > 0 || image.files.length > 0 || image2.files.length > 0) {
		text.required = false;
		url.required=false;
	} else if (text.value.length > 0 || image.files.length > 0 || image2.files.length > 0) {
		url.required = false;
	} else {
		text.required = true;
		url.required = true;
	}

	const isValidTitle = title.checkValidity();
	const isValidURL = url.checkValidity();
	const isValidText = text.checkValidity();

	if (isValidTitle && (isValidURL || image.files.length > 0 || image2.files.length > 0)) {
		button.disabled = false;
	} else if (isValidTitle && isValidText) {
		button.disabled = false;
	} else {
		button.disabled = true;
	}
}
checkForRequired();

function hide_image() {
	const x=document.getElementById('image-upload-block');
	let url=document.getElementById('post-url').value;
	if (url.length>=1){
		x.classList.add('d-none');
	}
	else {
		x.classList.remove('d-none');
	}
}

document.onpaste = function(event) {
	files = event.clipboardData.files

	filename = files[0]

	if (filename)
	{
		filename = filename.name.toLowerCase()
		if (document.activeElement.id == 'post-text') {
			let filename = ''
			for (const file of files)
				filename += file.name + ', '
			filename = filename.toLowerCase().slice(0, -2)
			document.getElementById('file-upload-submit').files = files;
			document.getElementById('filename-show-submit').textContent = filename;
		}
		else {
			f=document.getElementById('file-upload');
			f.files = files;
			document.getElementById('filename-show').textContent = filename;
			document.getElementById('urlblock').classList.add('d-none');
			if (filename.endsWith(".jpg") || filename.endsWith(".jpeg") || filename.endsWith(".png") || filename.endsWith(".gif") || filename.endsWith(".webp"))
			{
				var fileReader = new FileReader();
				fileReader.readAsDataURL(f.files[0]);
				fileReader.addEventListener("load", function () {document.getElementById('image-preview').setAttribute('src', this.result);});
			}
			document.getElementById('file-upload').setAttribute('required', 'false');
		}
		document.getElementById('post-url').value = null;
		localStorage.setItem("post_url", "")
		checkForRequired();
	}
}

document.getElementById('file-upload').addEventListener('change', function(){
	f=document.getElementById('file-upload');
	document.getElementById('urlblock').classList.add('d-none');
	document.getElementById('filename-show').textContent = document.getElementById('file-upload').files[0].name.substr(0, 20);
	filename = f.files[0].name.toLowerCase()
	if (filename.endsWith(".jpg") || filename.endsWith(".jpeg") || filename.endsWith(".png") || filename.endsWith(".gif") || filename.endsWith(".webp"))
	{
		var fileReader = new FileReader();
		fileReader.readAsDataURL(f.files[0]);
		fileReader.addEventListener("load", function () {document.getElementById('image-preview').setAttribute('src', this.result);});  
	}
	checkForRequired();
})

function savetext() {
	localStorage.setItem("post_title", document.getElementById('post-title').value)
	localStorage.setItem("post_text", document.getElementById('post-text').value)
	localStorage.setItem("post_url", document.getElementById('post-url').value)
	let sub = document.getElementById('sub')
	if (sub) localStorage.setItem("sub", sub.value)
}


function autoSuggestTitle()	{

	var urlField = document.getElementById("post-url");

	var titleField = document.getElementById("post-title");

	var isValidURL = urlField.checkValidity();

	if (isValidURL && urlField.value.length > 0 && titleField.value === "") {

		var x = new XMLHttpRequest();
		x.withCredentials=true;
		x.onreadystatechange = function() {
			if (x.readyState == 4 && x.status == 200 && !titleField.value) {

				title=JSON.parse(x.responseText)["title"];
				titleField.value=title;
				checkForRequired()
			}
		}
		x.open('get','/submit/title?url=' + urlField.value);
		x.send(null);

	};

};

function draft(t) {
	const followers = document.getElementById("followers")
	if (t.checked == true) {
		followers.checked = false;
		followers.disabled = true;
	} else {
		followers.disabled = false;
   }
}

function checkRepost() {
	const system = document.getElementById('system')
	system.innerHTML = `To post an image, use a direct image link such as i.imgur.com`;
	const url = document.getElementById('post-url').value

	if (url) {
		const xhr = new XMLHttpRequest();
		xhr.open("post", "/is_repost");
		xhr.setRequestHeader('xhr', 'xhr');
		const form = new FormData()
		form.append("url", url);

		xhr.onload=function(){
			try {data = JSON.parse(xhr.response)}
			catch(e) {console.log(e)}
			
			if (data && data["permalink"]) {
				const permalink = data["permalink"]
				if (permalink) {
					system.innerHTML = `<span class='text-danger'>This is a repost of <a href=${permalink}>${permalink}</a></span>`;
				}
			}
		}
		xhr.send(form)
	}
}

function updateCategories() {
	if (document.getElementById("submit-categories") == null) {
		return;
	}
	sub = document.getElementById("sub").value;

	xhrCategories = new XMLHttpRequest();
	xhrCategories.open("GET", "/categories.json");
	xhrCategories.onload = function () {
		let data;
		try {
			data = JSON.parse(xhrCategories.response);
		} catch(e) { console.log(e) }

		document.getElementById("submit-categories").innerHTML = '';
		data[sub].forEach(function (c) {
			document.getElementById("submit-categories").innerHTML += 
				`<input type="radio" id="category-${c.id}" name="category" value="${c.id}">` +
				`<label for="category-${c.id}" class="post--category-tag" ` +
					`style="color:${c.color_text}; background-color:${c.color_bg};">` +
					`${c.name}</label>`;
		});
	}
	xhrCategories.send();
}

document.addEventListener('keydown', (e) => {
   if(!((e.ctrlKey || e.metaKey) && e.key === "Enter"))
	   return;

   const submitButton = document.getElementById('create_button')

   submitButton.click();
});

checkRepost();
updateCategories();
