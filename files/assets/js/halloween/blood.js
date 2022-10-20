/*
  A Bloody Mess by Rob Glazebrook
  By default, canvas does not clear between frames. I'm taking advantage of that to create the running blood effect.
  This pen was inspired by Katy Decorah's BLOOD: https://codepen.io/katydecorah/pen/Lkogi
*/


var i = 0;

var blood = Sketch.create({autoclear: false, autopause: false}),
    drops = [],
    dropCount = stabs*10,
    maxDrops = dropCount+1,
    Drop = function() {
      this.x = random(0,blood.width);
      this.radius = random(10,20);
      this.y = -this.radius - random(50,100);
      this.vy = this.radius/6;
      this.r = ~~random(240,255);
      this.g = ~~random(0,20);
      this.b = ~~random(0,20);
    };

blood.update = function() {
  var d = drops.length;
  while(d < dropCount && i < maxDrops) {
    var drop = new Drop();
    drops.push(drop);
    d++;
    i++;
  }
  while(d-- && i < maxDrops) {
    var drop = drops[d];
    drop.y += drop.vy;
    if(drop.y - drop.radius > blood.height) {
      drops.splice(d,1);
    }
  }
}

blood.draw = function() {
  var d = drops.length;
  while(d-- && i < maxDrops) {
    var drop = drops[d];
    blood.beginPath();
    blood.fillStyle = 'rgba('+drop.r+','+drop.g+','+drop.b+',.8)';
    blood.arc(drop.x,drop.y,drop.radius,0,TWO_PI);
    blood.fill();
  }
}

