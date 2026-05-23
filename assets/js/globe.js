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
  var globeGeo = new THREE.SphereGeometry(radius, 40, 40);
  var wireframeMat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    wireframe: true,
    transparent: true,
    opacity: 0.25
  });
  var globe = new THREE.Mesh(globeGeo, wireframeMat);

  var innerGeo = new THREE.SphereGeometry(radius * 0.96, 30, 30);
  var innerWire = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    wireframe: true,
    transparent: true,
    opacity: 0.08
  });
  var innerGlobe = new THREE.Mesh(innerGeo, innerWire);

  var group = new THREE.Group();
  group.add(globe);
  group.add(innerGlobe);

  var dotsGeo = new THREE.BufferGeometry();
  var dotsCount = 600;
  var positions = new Float32Array(dotsCount * 3);
  for (var i = 0; i < dotsCount; i++) {
    var theta = Math.random() * Math.PI * 2;
    var phi = Math.acos((Math.random() * 2) - 1);
    var r = radius * 1.01;
    positions[i*3] = r * Math.sin(phi) * Math.cos(theta);
    positions[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
    positions[i*3+2] = r * Math.cos(phi);
  }
  dotsGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  var dotsMat = new THREE.PointsMaterial({
    color: 0xffffff,
    size: 1.8,
    transparent: true,
    opacity: 0.5
  });
  var dots = new THREE.Points(dotsGeo, dotsMat);
  group.add(dots);

  var ringGeo = new THREE.RingGeometry(radius * 1.6, radius * 1.62, 80);
  var ringMat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.08
  });
  var ring = new THREE.Mesh(ringGeo, ringMat);
  ring.rotation.x = Math.PI / 3;
  ring.rotation.z = Math.PI / 6;

  scene.add(group);
  scene.add(ring);

  camera.position.set(0, 80, 550);
  camera.lookAt(0, 0, 0);

  var mouseX = 0, mouseY = 0;
  document.addEventListener('mousemove', function(e) {
    mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
  });

  function animate() {
    requestAnimationFrame(animate);
    group.rotation.y += 0.002;
    group.rotation.x += Math.sin(Date.now() * 0.0003) * 0.0003;
    ring.rotation.z += 0.0005;

    var targetRotX = mouseY * 0.05;
    var targetRotY = mouseX * 0.05;
    group.rotation.x += (targetRotX - group.rotation.x) * 0.02;
    group.rotation.y += (targetRotY - group.rotation.y) * 0.02 + 0.002;

    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener('resize', function() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
})();
