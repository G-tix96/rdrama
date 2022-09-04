const fireworks = document.getElementsByClassName("firework")
var counter = 0

for (let firework of fireworks){
var timeout = 2000 * counter
counter++
setTimeout(() => {
	setInterval(() => {
	firework.firstElementChild.src = "/i/firework-trail.webp"

	var xpos = Math.floor(Math.random() * 80) + 5
	var ypos = 95
	firework.style.top=ypos+"%"
	firework.style.left=xpos+"%"

	firework.style.display="inline-block"
	var hue = Math.floor(Math.random()*360)+1
	firework.style.filter="hue-rotate("+hue+"deg)"

	var id = null
	var height = Math.floor(Math.random()*60)+15
	clearInterval(id);
	id = setInterval(frame, 20);

	var vnum = Math.floor(Math.random()*1000)

	function frame() {
		if (ypos <= height) {
		clearInterval(id);
		firework.firstElementChild.src = "/i/firework-explosion.webp?v="+vnum
		} else {
		ypos--;
		firework.style.top=ypos+"%"
		}
	}
	}, 5000)
}, timeout)
}