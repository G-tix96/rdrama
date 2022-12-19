var canvas = document.querySelector('#canvas-snowed-in-overlay');
var lineCanvas = document.querySelector('#canvas-snowed-in-lines');

var canvasContext = canvas.getContext('2d');
var lineCanvasContext = lineCanvas.getContext('2d');

var pointLifetime = 4000;
var points = [];

//FILL CANVAS
canvasContext.fillStyle="rgba(0, 0, 0, 0.1)";
canvasContext.fillRect(0, 0, canvas.width, canvas.height);

//INIT
function init() {
	document.addEventListener('mousemove', onMouseMove);
	window.addEventListener('resize', resizeCanvases);
	resizeCanvases();
	tick();
}

init();

//RESIZE CANVAS
function resizeCanvases() {
	canvas.width = lineCanvas.width = window.innerWidth;
	canvas.height = lineCanvas.height = window.innerHeight;
}

function onMouseMove(event) {
	points.push({
		time: Date.now(),
				x: event.clientX,
			 y: event.clientY
	});
}

function tick() {
	// Remove old points
	// points = points.filter(function(point) {
	//   var age = Date.now() - point.time;
	//   return age < pointLifetime;
	// });

	drawLineCanvas();
	drawImageCanvas();
	requestAnimationFrame(tick);
	//setTimeout(() => {
	//tick();
	//}, 1000 / 60);
}

function drawLineCanvas() {
	var minimumLineWidth = 40;
	var maximumLineWidth = 60;
	var lineWidthRange = maximumLineWidth - minimumLineWidth;
	var maximumSpeed = 200;

	lineCanvasContext.clearRect(0, 0, lineCanvas.width, lineCanvas.height);
	lineCanvasContext.lineCap = 'round';
	lineCanvasContext.shadowBlur = 90;
	lineCanvasContext.shadowColor = '#fff';

	for (var i = 1; i < points.length; i++) {
		var point = points[i];
		var previousPoint = points[i - 1];

		// Change line width based on speed
		var distance = getDistanceBetween(point, previousPoint);
		var speed = Math.max(0, Math.min(maximumSpeed, distance));
		var percentageLineWidth = (maximumSpeed - speed) / maximumSpeed;
		lineCanvasContext.lineWidth = minimumLineWidth + percentageLineWidth * lineWidthRange;

		// Fade points as they age
		// var age = Date.now() - point.time;
		// var opacity = (pointLifetime - age) / pointLifetime;
		// lineCanvasContext.strokeStyle = 'rgba(255, 255, 255, ' + opacity + ')';
		lineCanvasContext.strokeStyle = 'rgba(255, 255, 255, 1)';

		lineCanvasContext.beginPath();
		lineCanvasContext.moveTo(previousPoint.x, previousPoint.y);
		lineCanvasContext.lineTo(point.x, point.y);
		lineCanvasContext.stroke();
	}
}

function getDistanceBetween(a, b) {
	return Math.sqrt(Math.pow(a.x - b.x, 2) + Math.pow(a.y - b.y, 2));
}

function drawImageCanvas() {
	canvasContext.globalCompositeOperation = 'source-over';
	canvasContext.save();
	canvasContext.fillStyle="rgb(255,255,255)";
	canvasContext.globalAlpha = 0.09;
	canvasContext.fillRect(0, 0, canvas.width, canvas.height);
	canvasContext.restore();
	canvasContext.globalCompositeOperation = 'destination-out';
	canvasContext.drawImage(lineCanvas, 0, 0);

}
