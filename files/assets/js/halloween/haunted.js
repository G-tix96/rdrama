const thunder1 = new Audio(`/assets/media/halloween/haunted/thunder1.mp3`),
      thunder2 = new Audio(`/assets/media/halloween/haunted/thunder2.mp3`)

window.onload = function(){
    lightningStrike("normal")
    thunder2.volume = 0.5
}

setInterval(function(){
    if(Math.floor(Math.random()*3) > 1){
        lightningStrike("haunted")
    } else {
        lightningStrike("normal")
    }
},14000)

function lightningStrike(strike) {
    document.body.style.overflowX = "hidden"
    document.body.style.animation = "haunted 20s"

    if(strike == "haunted"){
        let art1 = sidebar.firstElementChild,
            art2 = document.getElementsByClassName("banner")[0]

        thunder2.play()
        art1.style.setProperty("filter","invert(1)")
        art2.setAttribute("src", "/assets/images/halloween/banner_evil.png")

        setTimeout(function(){
            art1.style.setProperty("filter","invert(0)")
            art2.setAttribute("src", "/assets/images/halloween/banner.png")
        },750)
    }

    thunder1.play()
    setTimeout(function(){
        document.body.style.animation = "none"
    },1000)
}