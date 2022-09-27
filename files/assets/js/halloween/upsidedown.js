function update(e){
  var x = e.clientX || e.touches[0].clientX
  var y = e.clientY || e.touches[0].clientY

  document.documentElement.style.setProperty('--cursorX', x + 'px')
  document.documentElement.style.setProperty('--cursorY', y + 'px')
}

document.addEventListener('mousemove',update)
document.addEventListener('touchmove',update)

let st = init("canvas"), // stranger things var
w = (canvas.width = window.innerWidth),
h = (canvas.height = window.innerHeight);
//initiation

class firefly{
  constructor(){
    this.x = Math.random()*w;
    this.y = Math.random()*h;
    this.s = Math.random()*2;
    this.ang = Math.random()*2*Math.PI;
    this.v = this.s*this.s/4;
  }
  move(){
    this.x += this.v*Math.cos(this.ang);
    this.y += this.v*Math.sin(this.ang);
    this.ang += Math.random()*20*Math.PI/180-10*Math.PI/180;
  }
  show(){
    st.beginPath();
    st.arc(this.x,this.y,this.s,0,2*Math.PI);
    st.fillStyle="#fff";
    st.fill();
  }
}

let f = [];

function draw() {
  if(f.length < 100){
    for(let j = 0; j < 10; j++){
     f.push(new firefly());
   }
 }
  //animation
  for(let i = 0; i < f.length; i++){
    f[i].move();
    f[i].show();
    if(f[i].x < 0 || f[i].x > w || f[i].y < 0 || f[i].y > h){
     f.splice(i,1);
   }
 }
}

let mouse = {};
let last_mouse = {};

canvas.addEventListener(
  "mousemove",
  function(e) {
    last_mouse.x = mouse.x;
    last_mouse.y = mouse.y;

    mouse.x = e.pageX - this.offsetLeft;
    mouse.y = e.pageY - this.offsetTop;
  },
  false
  );
function init(elemid) {
  let canvas = document.getElementById(elemid),
  st = canvas.getContext("2d"),
  w = (canvas.width = window.innerWidth),
  h = (canvas.height = window.innerHeight);
  st.fillStyle = "rgba(30,30,30,1)";
  st.fillRect(0, 0, w, h);
  return st;
}

window.requestAnimFrame = (function() {
  return (
    window.requestAnimationFrame ||
    window.webkitRequestAnimationFrame ||
    window.mozRequestAnimationFrame ||
    window.oRequestAnimationFrame ||
    window.msRequestAnimationFrame ||
    function(callback) {
      window.setTimeout(callback);
    }
    );
});

function loop() {
  window.requestAnimFrame(loop);
  st.clearRect(0, 0, w, h);
  draw();
}

window.addEventListener("resize", function() {
  (w = canvas.width = window.innerWidth),
  (h = canvas.height = window.innerHeight);
  loop();
});

loop();
setInterval(loop, 1000 / 60);

// Audio

var audio = new Audio('/assets/media/halloween/Stranger%20things%20demogorgon%20theme.mp3');
audio.loop=true;

function pause() {
  audio.pause();
}

function play() {
  audio.play();
}


window.addEventListener( 'load', function() {
  let demogorgon1 = document.getElementById('demogorgon-1')
  let demogorgon2 = document.getElementById('demogorgon-2')
  //audio.play();
  document.getElementById('thread').addEventListener('click', () => {
    console.log('Watch out for the Demogorgon.');
    if (Math.random() < 0.6) {
          document.querySelector(":root").style.animation = 'lightning 1350ms ease-out 37100ms 1, lightning 1350ms ease-out 66400ms 1'
          demogorgon1.classList.add('audio-playing');
          setTimeout(function(){ demogorgon2.classList.add('audio-playing'); }, 66400);
    }
    if (audio.paused) audio.play();
  }, {once : true});

});
