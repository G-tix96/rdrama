// Jump scare function
const scare = () => {
	const image = document.getElementById("jump-scare-img");

	jumpscare_audio.play();
	image.style.display = "block";

	// Hide image and reset sound
	setTimeout(function () {
		image.style.display = "none";
		jumpscare_audio.pause()
		jumpscare_audio.currentTime = 0;
	}, 3000);
}
