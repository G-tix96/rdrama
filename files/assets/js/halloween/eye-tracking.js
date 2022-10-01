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
	}
}

let sidebar = document.getElementById("main-content-row")
sidebar = sidebar.getElementsByClassName("sidebar")[0]

const banner = sidebar.firstElementChild

const eye_left = document.createElement("img")
eye_left.setAttribute("class", "eye")
eye_left.setAttribute("src", "/assets/images/halloween/eye.png")
eye_left.style.left = coordsLookup["banner1"]["left"]["x"]
eye_left.style.top = coordsLookup["banner1"]["left"]["y"]

const eye_right = document.createElement("img")
eye_right.setAttribute("class", "eye")
eye_right.setAttribute("src", "/assets/images/halloween/eye.png")
eye_right.style.left = coordsLookup["banner1"]["right"]["x"]
eye_right.style.top = coordsLookup["banner1"]["right"]["y"]

banner.appendChild(eye_left)
banner.appendChild(eye_right)

/*eye movement*/
const eye_left_center = getCenter(eye_left)
const eye_right_center = getCenter(eye_right)

document.onmousemove = function(event){
	let click = {x: event.clientX, y: event.clientY}
	eye_left.style.transform = 'rotate('+getAngle(click, eye_left_center)+'rad)'
	eye_right.style.transform = 'rotate('+getAngle(click, eye_right_center)+'rad)'
}

function getCenter(element){
	const bounds = element.getBoundingClientRect()
	let centerX = Math.trunc(bounds["left"]) + Math.trunc(bounds["width"]/2)
	let centerY = Math.trunc(bounds["top"]) + Math.trunc(bounds["height"]/2)
	return({x: centerX, y: centerY})
}

function getAngle(point1, point2) {
	let x = point1["x"] - point2["x"]
	let y = point1["y"] - point2["y"]
	let angle = Math.atan(y/x)
	if(point1["x"] < point2["x"]){
		angle += Math.PI
	}
	return(angle)
}
