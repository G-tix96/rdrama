const thunder1 = new Audio(`/assets/media/halloween/haunted/thunder1.mp3`),
      thunder2 = new Audio(`/assets/media/halloween/haunted/thunder2.mp3`),
      stylesheet_haunted = document.createElement("STYLE")

window.onload = function(){
    temp = document.createTextNode("#banner-halloween-title {opacity:0;}#banner-halloween-text-evil {opacity:1!important;}img {filter: invert(1);}")
    stylesheet_haunted.appendChild(temp)
    document.head.appendChild(stylesheet_haunted)
    stylesheet_haunted.disabled = true

    thunder2.volume = 0.5

    lightningStrike("normal")
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
        stylesheet_haunted.disabled = false
        thunder2.play()
        setTimeout(function(){
            stylesheet_haunted.disabled = true
        },700)
    }

    thunder1.play()
    setTimeout(function(){
        document.body.style.animation = "none"
    },1000)
}