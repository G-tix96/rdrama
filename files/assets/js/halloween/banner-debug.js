function setBannerDay(day){
	let sky = document.getElementById("banner-halloween-svg"),
		moon = document.getElementById("banner-halloween-moon"),
		house = document.getElementById("house-fill-gradient-stop"),
		ground = document.getElementById("ground-gradient-stop"),
		objects = document.getElementById("banner-halloween-objects"),
		stars = document.getElementById("banner-halloween-stars")

	sky.style.backgroundImage = "var(--sky-gradient-day"+day+")"
	moon.style.fill = "var(--moon-fill-day"+day+")"
	moon.style.filter = "var(--moon-shadow-day"+day+")"
	moon.style.cy = "var(--moon-position-day"+day+")"
	house.style.stopColor = "var(--house-shadow-day"+day+")"
	ground.style.stopColor = "var(--ground-shadow-day"+day+")" 
	objects.style.fill = "var(--object-fill-day"+day+")"
	stars.style.opacity = "var(--star-opacity-day"+day+")"
}

function cycleBanner(){
	i=1
	asdf = setInterval(function(){
		setBannerDay(i)
		if (i > 9){clearInterval(asdf)}
		i++
	}, 250)
}
