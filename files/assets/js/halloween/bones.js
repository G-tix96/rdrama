function bones(number){
    var container = document.getElementById('animate');

    // Stackable
    // With each award, append a new image to array
    const sources = ['skeleton1.webp','skeleton2.webp','skeleton3.webp','skeleton4.webp','skeleton5.webp','skeleton6.webp'];

    if(number > sources.length){
        number = sources.length
    }

    const n = sources.length - number,
        emoji = sources.slice(n),
        pw = screen.availWidth/6

    let circles = [];

    for (var i = 0; i < 3; i++) {
        addCircle(i * 150, [10 + 0, pw], emoji[Math.floor(Math.random() * emoji.length)]);
        addCircle(i * 150, [10 + 0, -pw], emoji[Math.floor(Math.random() * emoji.length)]);
        addCircle(i * 150, [10 - (0.5*pw), -pw], emoji[Math.floor(Math.random() * emoji.length)]);
        addCircle(i * 150, [10 + (0.5*pw), pw], emoji[Math.floor(Math.random() * emoji.length)]);
        addCircle(i * 150, [10 - (1.5*pw), -pw], emoji[Math.floor(Math.random() * emoji.length)]);
        addCircle(i * 150, [10 + (1.5*pw), pw], emoji[Math.floor(Math.random() * emoji.length)]);
    }


    function addCircle(delay, range, color) {
        setTimeout(function() {
            var c = new Circle(range[0] + Math.random() * range[1], 80 + Math.random() * 4, color, {
                x: -0.15 + Math.random() * 0.3,
                y: 1 + Math.random() * 1
            }, range);
            circles.push(c);
        }, delay);
    }

    function Circle(x, y, c, v, range) {
        var _this = this;
        this.x = x;
        this.y = y;
        this.color = c;
        this.v = v;
        this.range = range;
        this.element = document.createElement('img');
        /*this.element.style.display = 'block';*/
        this.element.style.opacity = 0;
        this.element.style.position = 'absolute';
        this.element.style.height = '3rem';
        this.element.src = "/assets/images/halloween/skeletons/"+c;
        container.appendChild(this.element);

        this.update = function() {
            if (_this.y > window.innerHeight) {
                _this.y = 80 + Math.random() * 4;
                _this.x = _this.range[0] + Math.random() * _this.range[1];
            }
            _this.y += _this.v.y;
            _this.x += _this.v.x;
            this.element.style.opacity = 1;
            this.element.style.transform = 'translate3d(' + _this.x + 'px, ' + _this.y + 'px, 0px)';
            this.element.style.webkitTransform = 'translate3d(' + _this.x + 'px, ' + _this.y + 'px, 0px)';
            this.element.style.mozTransform = 'translate3d(' + _this.x + 'px, ' + _this.y + 'px, 0px)';
        };
    }

    function animate() {
        for (var i in circles) {
            circles[i].update();
        }
        requestAnimationFrame(animate);
    }

    animate();
}
