function trickOrTreat(cooldown){
	const game_cooldown = localStorage.getItem('cooldown_trickortreat'),
	game_button = document.getElementById("trick-or-treat")

	//1 second cooldown, change this to 3600 for prod
	if(cooldown > (Number(game_cooldown) + 1)){
		game_button.onclick = function(){
			const num = Math.random();
			//100% chance of jumpscare lol
			if (num < 1){
				scare()
			} else {
				//put award here
				alert('not jumpscared :)')
			}
			localStorage.setItem('cooldown_trickortreat', cooldown)
			game_button.setAttribute("class", "btn btn-success disabled")
		}
	} else {
		game_button.setAttribute("class", "btn btn-success disabled")
	}

	// Jump scare function
	const scare = () => {
		const images = [
			"/assets/images/halloween/jumpscare/jumpscare1.gif",
			"/assets/images/halloween/jumpscare/jumpscare2.gif",
			"/assets/images/halloween/jumpscare/jumpscare3.gif",
			"/assets/images/halloween/jumpscare/jumpscare4.gif"
			],
			sounds = ["/assets/media/halloween/psycho.mp3"]

		let selectedImage = images[0];
		const image = document.getElementById("jump-scare-img");

		const randomize = (array) => {
			return array[Math.floor(Math.random() * array.length)];
		}

		selectedImage = randomize(images);
		selectedSound = randomize(sounds);

		image.src = selectedImage;
		const audio = new Audio(selectedSound);

		audio.play();
		image.style.display = "block";

		// Hide image and reset sound
		setTimeout(function () {
			image.style.display = "none";
		}, 2700);
	}
}