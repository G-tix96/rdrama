/*init*/
let sidebar = document.getElementById("main-content-row")
sidebar = sidebar.getElementsByClassName("sidebar")[0].firstElementChild

const eye_left = sidebar.getElementsByClassName("eye")[0],
	  eye_right = sidebar.getElementsByClassName("eye")[1]

/*eye movement*/
document.onmousemove = function(event) {
	let click = {x: event.clientX, y: event.clientY},
		/*recalculating eye position on every mousemove is less efficient
		but ensures eyes track properly upon pageload even if script doesnt fire*/
		eye_left_center = getCenter(eye_left),
		eye_right_center = getCenter(eye_right)

	eye_left.style.transform = 'rotate('+getAngle(click, eye_left_center)+'rad)'
	eye_right.style.transform = 'rotate('+getAngle(click, eye_right_center)+'rad)'
}

function getCenter(element) {
	const bounds = element.getBoundingClientRect()

	let centerX = bounds["left"] + bounds["width"]/2,
		centerY = bounds["top"] + bounds["height"]/2

	return({x: centerX, y: centerY})
}

function getAngle(point1, point2) {
	let x = point1["x"] - point2["x"],
		y = point1["y"] - point2["y"],
		angle = Math.atan(y/x)

	if(point1["x"] < point2["x"]) {
		angle += Math.PI
	}

	return(angle)
}
