/* coordinate lookup */
const coordsLookup = {
	banner1: {
		left: {
			x: "79px",
			y: "-208px"
		},
		right: {
			x: "126px",
			y: "-212px"
		}	
	}
}

const banner = document.querySelector("img[alt~=sidebar]")
const eye_left = document.getElementById("eye-left")
const eye_right = document.getElementById("eye-right")

eye_left.style.left = coordsLookup["banner1"]["left"]["x"]
eye_left.style.top = coordsLookup["banner1"]["left"]["y"]

eye_right.style.left = coordsLookup["banner1"]["right"]["x"]
eye_right.style.top = coordsLookup["banner1"]["right"]["y"]

/* tracking */
const pupil_left = eye_left.getElementsByClassName("pupil")[0]
const pupil_right = eye_right.getElementsByClassName("pupil")[0]

const eye_left_center = getCenter(eye_left)
const eye_right_center = getCenter(eye_right)

document.onmousemove = function(event){
	let click = {x: event.clientX, y: event.clientY}
	
	let new_left = newCenter(click, eye_left_center)
	pupil_left.style.cx = new_left["x"]
	pupil_left.style.cy = new_left["y"]
	
	let new_right = newCenter(click, eye_right_center)
	pupil_right.style.cx = new_right["x"]
	pupil_right.style.cy = new_right["y"]
}

function newCenter(click, eye){
	let angleX = getAngle(click, eye)
	let newX = (Math.cos(angleX)*6)
	
	let angleY = getAngle(click, eye)
	let newY = (Math.sin(angleY)*6)
		
	if(click["x"] > eye["x"]){
		newX += 14, newY += 14
	} else {
		newX = 14-newX, newY = 14-newY
	}
	
	return({x: newX, y: newY})
}

function getCenter(element){
	const bounds = element.getBoundingClientRect()

	var centerX = Math.trunc(bounds["left"]) + Math.trunc(bounds["width"]/2)
	var centerY = Math.trunc(bounds["top"]) + Math.trunc(bounds["height"]/2)

	return({x: centerX, y: centerY})
}

function getAngle(point1, point2) {
	let x = point1["x"] - point2["x"]
	let y = point1["y"] - point2["y"]

	return(Math.atan(y/x))
}
