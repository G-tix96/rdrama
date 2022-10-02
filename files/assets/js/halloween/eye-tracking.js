/*init*/
const coordsLookup = {
	banner1: {
		left: {
			x: "72px",
			y: "-205px"
		},
		right: {
			x: "116px",
			y: "-209px"
		}	
	}, 	
	banner2: {
		left: {
			x: "35px",
			y: "-335px"
		},
		right: {
			x: "64px",
			y: "-337px"
		}	
	}
}

let sidebar = document.getElementById("main-content-row")
sidebar = sidebar.getElementsByClassName("sidebar")[0].firstElementChild

const eye_left = initEye("left"),
	  eye_right = initEye("right")

function initEye(side) {
	let eye = document.createElement("img")

	eye.setAttribute("class", "eye")
	eye.setAttribute("src", "/assets/images/halloween/eye.png")
	eye.style.left = coordsLookup[banner][side]["x"]
	eye.style.top = coordsLookup[banner][side]["y"]
	
	sidebar.appendChild(eye)
	return(eye)
}

/*eye movement*/
const eye_left_center = getCenter(eye_left),
	  eye_right_center = getCenter(eye_right)

document.onmousemove = function(event) {
	let click = {x: event.clientX, y: event.clientY}
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
