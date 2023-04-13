var	deg = 90;
var	p_global = 0.1;
if (document.getElementsByTagName("header").length !== 0) {
	let	elem = document.getElementsByTagName("header")[0];
	while (1) {
		elem.style.background =
			'linear-gradient(' + deg + 'deg, rgba(255,0,0,.8), rgba(255,0,0,0) 70.71%),' +
			'linear-gradient(' + (deg + 180) % 360 + 'deg, rgba(0,0,255,.8), rgba(0,0,255,0) 70.71%)';
		deg += 180;
		await new Promise(r => setTimeout(r, 1000));
	}
}
