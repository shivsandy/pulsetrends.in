(function() {
  if (window.innerWidth < 768) return;

  var container = document.getElementById('globe-container');
  if (!container) return;

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
  var renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  var radius = 200;
  var group = new THREE.Group();

  // 1. Draw Earth map on canvas (procedural B&W continent outlines)
  function createEarthTexture() {
    var c = document.createElement('canvas');
    c.width = 1024;
    c.height = 512;
    var ctx = c.getContext('2d');

    // Ocean background
    ctx.fillStyle = '#111';
    ctx.fillRect(0, 0, c.width, c.height);

    // Draw simplified continent shapes as latitude/longitude blobs
    ctx.strokeStyle = 'rgba(255,255,255,0.3)';
    ctx.lineWidth = 1.5;
    ctx.fillStyle = 'rgba(255,255,255,0.12)';

    // Continent data as [lat, lon, width, height] approximations
    var continents = [
      // North America
      {lat: 40, lon: -100, w: 40, h: 35},
      {lat: 50, lon: -110, w: 30, h: 20},
      {lat: 30, lon: -90, w: 20, h: 15},
      // South America
      {lat: -15, lon: -60, w: 15, h: 45},
      // Europe
      {lat: 50, lon: 10, w: 25, h: 15},
      {lat: 55, lon: 20, w: 20, h: 12},
      // Africa
      {lat: 5, lon: 20, w: 25, h: 40},
      // Asia
      {lat: 40, lon: 90, w: 55, h: 30},
      {lat: 30, lon: 75, w: 30, h: 20},
      {lat: 50, lon: 120, w: 40, h: 15},
      // India
      {lat: 20, lon: 78, w: 10, h: 15},
      // Australia
      {lat: -25, lon: 135, w: 15, h: 12},
      // Greenland
      {lat: 72, lon: -40, w: 15, h: 10},
    ];

    for (var i = 0; i < continents.length; i++) {
      var cont = continents[i];
      // Convert lat/lon to equirectangular x,y
      var cx = (cont.lon + 180) / 360 * c.width;
      var cy = (90 - cont.lat) / 180 * c.height;
      var cw = cont.w / 360 * c.width;
      var ch = cont.h / 180 * c.height;

      ctx.beginPath();
      ctx.ellipse(cx, cy, cw/2, ch/2, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    }

    // Grid lines (longitude/latitude)
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 0.5;
    for (var lat = -80; lat <= 80; lat += 20) {
      var y = (90 - lat) / 180 * c.height;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(c.width, y);
      ctx.stroke();
    }
    for (var lon = -180; lon <= 180; lon += 20) {
      var x = (lon + 180) / 360 * c.width;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, c.height);
      ctx.stroke();
    }

    return new THREE.CanvasTexture(c);
  }

  // Earth sphere with procedural texture
  var earthMat = new THREE.MeshBasicMaterial({
    map: createEarthTexture(),
    transparent: true,
    opacity: 0.6,
    side: THREE.DoubleSide
  });
  var earth = new THREE.Mesh(new THREE.SphereGeometry(radius, 64, 48), earthMat);
  group.add(earth);

  // Wireframe overlay
  var wireMat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    wireframe: true,
    transparent: true,
    opacity: 0.12
  });
  var wire = new THREE.Mesh(new THREE.SphereGeometry(radius * 1.002, 32, 24), wireMat);
  group.add(wire);

  // Inner glow
  var innerMat = new THREE.MeshBasicMaterial({
    color: 0x4488ff,
    wireframe: false,
    transparent: true,
    opacity: 0.08,
    side: THREE.BackSide
  });
  var inner = new THREE.Mesh(new THREE.SphereGeometry(radius * 0.9, 24, 18), innerMat);
  group.add(inner);

  // Scattered dots
  var dotsCount = 600;
  var positions = new Float32Array(dotsCount * 3);
  for (var i = 0; i < dotsCount; i++) {
    var theta = Math.random() * Math.PI * 2;
    var phi = Math.acos((Math.random() * 2) - 1);
    var r = radius * 1.03;
    positions[i*3] = r * Math.sin(phi) * Math.cos(theta);
    positions[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
    positions[i*3+2] = r * Math.cos(phi);
  }
  var dotsGeo = new THREE.BufferGeometry();
  dotsGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  var dotsMat = new THREE.PointsMaterial({
    color: 0xffffff,
    size: 1.8,
    transparent: true,
    opacity: 0.35
  });
  var dots = new THREE.Points(dotsGeo, dotsMat);
  group.add(dots);

  // Orbital ring
  var ringGeo = new THREE.RingGeometry(radius * 1.6, radius * 1.62, 80);
  var ringMat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.08
  });
  var ring = new THREE.Mesh(ringGeo, ringMat);
  ring.rotation.x = Math.PI / 2.5;
  ring.rotation.z = 0.3;
  scene.add(ring);

  var ring2 = new THREE.Mesh(ringGeo.clone(), ringMat.clone());
  ring2.material.opacity = 0.05;
  ring2.scale.set(1.3, 1.3, 1.3);
  ring2.rotation.x = Math.PI / 4;
  ring2.rotation.z = 0.8;
  scene.add(ring2);

  scene.add(group);

  camera.position.set(0, 50, 450);
  camera.lookAt(0, 0, 0);

  var mouseX = 0, mouseY = 0;
  document.addEventListener('mousemove', function(e) {
    mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
  });

  var time = 0;
  function animate() {
    requestAnimationFrame(animate);
    time += 0.01;

    // Auto rotation
    group.rotation.y += 0.003;
    group.rotation.x = Math.sin(time * 0.15) * 0.05;

    // Mouse parallax (subtle)
    group.rotation.x += (mouseY * 0.04 - group.rotation.x) * 0.01;
    group.rotation.y += mouseX * 0.002;

    // Rings rotate slowly
    ring.rotation.z += 0.0003;
    ring2.rotation.z -= 0.0005;

    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener('resize', function() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
})();
