(function() {
  if (window.innerWidth < 768) return;

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
  var renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  var container = document.getElementById('globe-container');
  container.appendChild(renderer.domElement);

  var radius = 220;
  var group = new THREE.Group();

  // Earth texture (B&W map with country borders)
  var textureLoader = new THREE.TextureLoader();
  var earthMap = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg');

  // Convert texture to B&W via canvas
  var canvas = document.createElement('canvas');
  var ctx = canvas.getContext('2d');
  var img = new Image();
  img.crossOrigin = 'anonymous';
  img.onload = function() {
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);
    var imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    var data = imageData.data;
    for (var i = 0; i < data.length; i += 4) {
      var bw = 0.34 * data[i] + 0.5 * data[i+1] + 0.16 * data[i+2];
      data[i] = bw;
      data[i+1] = bw;
      data[i+2] = bw;
      data[i+3] = bw > 60 ? 80 : 120;
    }
    ctx.putImageData(imageData, 0, 0);
    var bwTexture = new THREE.CanvasTexture(canvas);
    var earthMat = new THREE.MeshBasicMaterial({
      map: bwTexture,
      transparent: true,
      opacity: 0.5,
      side: THREE.DoubleSide
    });
    var earthMesh = new THREE.Mesh(new THREE.SphereGeometry(radius * 0.99, 64, 64), earthMat);
    group.add(earthMesh);
  };
  img.src = 'https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg';

  // Wireframe overlay (longitude/latitude lines)
  var wireMat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    wireframe: true,
    transparent: true,
    opacity: 0.15
  });
  var wireGlobe = new THREE.Mesh(new THREE.SphereGeometry(radius, 32, 24), wireMat);
  group.add(wireGlobe);

  // Inner wireframe for depth
  var innerWire = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    wireframe: true,
    transparent: true,
    opacity: 0.05
  });
  var innerGlobe = new THREE.Mesh(new THREE.SphereGeometry(radius * 0.97, 24, 18), innerWire);
  group.add(innerGlobe);

  // Scattered dots
  var dotsCount = 800;
  var positions = new Float32Array(dotsCount * 3);
  for (var i = 0; i < dotsCount; i++) {
    var theta = Math.random() * Math.PI * 2;
    var phi = Math.acos((Math.random() * 2) - 1);
    var r = radius * 1.02;
    positions[i*3] = r * Math.sin(phi) * Math.cos(theta);
    positions[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
    positions[i*3+2] = r * Math.cos(phi);
  }
  var dotsGeo = new THREE.BufferGeometry();
  dotsGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  var dotsMat = new THREE.PointsMaterial({
    color: 0xffffff,
    size: 1.5,
    transparent: true,
    opacity: 0.4
  });
  var dots = new THREE.Points(dotsGeo, dotsMat);
  group.add(dots);

  // Orbital rings
  for (var r = 0; r < 2; r++) {
    var ringGeo = new THREE.RingGeometry(radius * (1.5 + r * 0.3), radius * (1.51 + r * 0.3), 80);
    var ringMat = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.06
    });
    var ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = Math.PI / 3 + r * 0.5;
    ring.rotation.z = Math.PI / 6 + r * 0.3;
    scene.add(ring);
  }

  scene.add(group);

  camera.position.set(0, 60, 500);
  camera.lookAt(0, 0, 0);

  var mouseX = 0, mouseY = 0;
  document.addEventListener('mousemove', function(e) {
    mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
  });

  function animate() {
    requestAnimationFrame(animate);
    group.rotation.y += 0.0018;
    group.rotation.x += (mouseY * 0.03 - group.rotation.x) * 0.015;
    group.rotation.y += (mouseX * 0.03) * 0.015;
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener('resize', function() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
})();
