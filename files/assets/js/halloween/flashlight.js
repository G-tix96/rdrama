// Original codepen: https://codepen.io/Coding-Artist/pen/ExLyRJg

let mouseX = 0;
let mouseY = 0;

// Detect touch device
const isTouchDevice = () => {
	try {
		// We try to create TouchEvent (it would fail for desktops and throw error)
		document.createEvent("TouchEvent");
		return true;
	} catch (e) {
		return false;
	}
};
function getMousePosition(e) {
	try {
		// Get position of mouse or touch
		mouseX = !isTouchDevice() ? e.pageX : e.touches[0].pageX;
		mouseY = !isTouchDevice() ? e.pageY : e.touches[0].pageY;

		// Set the Xpos and Ypos variables to current mouse/touch position
		document.documentElement.style.setProperty("--Xpos", mouseX + "px");
document.documentElement.style.setProperty("--Ypos", mouseY + "px");
	} catch (e) {}
}

// Update mouse position on mouse move / touch move
document.addEventListener("mousemove", getMousePosition);
document.addEventListener("touchmove", getMousePosition);
