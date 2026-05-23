(function() {
  'use strict';
  try {
    if (window.innerWidth < 768) {
      var c = document.getElementById('globe-container');
      if (c) c.style.display = 'none';
      return;
    }

    var container = document.getElementById('globe-container');
    if (!container) { console.error('No globe-container'); return; }

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
    var renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    var R = 200;

    // ─── Draw continents on canvas texture ───
    function makeTexture() {
      var canvas = document.createElement('canvas');
      canvas.width = 1024;
      canvas.height = 512;
      var ctx = canvas.getContext('2d');

      // Ocean
      ctx.fillStyle = '#000';
      ctx.fillRect(0, 0, 1024, 512);

      // Simplified continent boundary polygons as [x,y] pairs (equirectangular projection)
      // x: 0-1024 (lon -180 to 180), y: 0-512 (lat 90 to -90)
      function toXY(lon, lat) {
        return [(lon + 180) / 360 * 1024, (90 - lat) / 180 * 512];
      }

      var continents = [
        // North America
        [[-130,50],[-125,55],[-120,60],[-115,65],[-80,70],[-60,65],[-55,50],[-65,45],[-75,35],[-80,30],[-85,25],[-90,22],[-100,25],[-105,30],[-115,35],[-120,40],[-125,45]],
        // Central America
        [[-90,22],[-85,25],[-80,30],[-85,20],[-90,18],[-95,20],[-100,15],[-98,12],[-92,10],[-88,12],[-85,15],[-90,22]],
        // South America
        [[-80,10],[-75,12],[-60,15],[-50,10],[-35,0],[-35,-10],[-40,-20],[-45,-25],[-50,-30],[-55,-35],[-60,-40],[-65,-50],[-70,-55],[-72,-50],[-70,-40],[-70,-30],[-75,-20],[-75,-10],[-80,0],[-80,10]],
        // Europe
        [[-10,36],[0,38],[3,40],[5,42],[10,44],[15,46],[20,48],[25,50],[30,55],[35,58],[40,60],[45,65],[40,68],[30,70],[20,68],[10,65],[5,60],[0,55],[-5,50],[-10,45],[-10,40]],
        // Africa
        [[-15,35],[-10,35],[-5,37],[0,37],[5,35],[10,35],[15,30],[20,25],[25,20],[30,15],[35,10],[40,5],[45,0],[50,-5],[50,-10],[45,-15],[40,-20],[35,-25],[30,-30],[25,-35],[20,-35],[15,-30],[10,-25],[10,-20],[5,-15],[0,-10],[-5,-5],[-10,0],[-15,5],[-20,10],[-20,15],[-17,20],[-15,25],[-15,30],[-15,35]],
        // Asia (main)
        [[30,60],[35,65],[40,68],[50,70],[60,72],[70,75],[80,80],[90,75],[100,70],[110,65],[120,60],[130,55],[135,50],[140,45],[145,50],[150,55],[155,60],[150,65],[145,70],[140,75],[145,80],[155,75],[160,70],[165,65],[170,60],[175,55],[180,50],[175,45],[170,40],[165,35],[160,30],[155,25],[150,20],[145,15],[140,10],[135,5],[130,0],[125,-5],[120,-10],[115,-8],[110,-5],[105,-2],[100,0],[95,5],[90,10],[85,15],[80,20],[75,25],[70,30],[65,35],[60,40],[55,45],[50,50],[45,55],[40,60],[35,60],[30,60]],
        // India
        [[68,8],[72,5],[76,5],[80,5],[84,8],[88,10],[90,15],[88,20],[85,25],[82,28],[78,30],[74,28],[72,25],[70,22],[68,18],[68,12]],
        // Southeast Asia
        [[100,20],[105,22],[110,22],[115,20],[120,18],[125,15],[130,12],[130,5],[125,0],[120,-5],[115,-5],[110,-2],[105,0],[100,2],[98,5],[95,8],[95,12],[98,15],[100,20]],
        // Australia
        [[115,-15],[120,-12],[125,-12],[130,-15],[135,-15],[140,-18],[145,-20],[150,-22],[150,-28],[145,-32],[140,-35],[135,-38],[130,-38],[125,-35],[120,-32],[115,-28],[113,-22],[115,-18]],
        // Greenland
        [[-55,60],[-50,62],[-45,65],[-40,68],[-35,72],[-30,76],[-25,80],[-20,82],[-15,80],[-20,78],[-25,75],[-30,72],[-35,68],[-40,64],[-45,62],[-50,60]],
        // Antarctica
        [[-180,-85],[-160,-82],[-140,-80],[-120,-78],[-100,-78],[-80,-80],[-60,-80],[-40,-78],[-20,-78],[0,-78],[20,-80],[40,-80],[60,-78],[80,-78],[100,-80],[120,-80],[140,-78],[160,-78],[180,-80],[180,-90],[-180,-90]],
      ];

      // Draw continent polygons (white fill, slightly transparent)
      ctx.fillStyle = 'rgba(255,255,255,0.25)';
      ctx.strokeStyle = 'rgba(255,255,255,0.5)';
      ctx.lineWidth = 1.5;
      for (var i = 0; i < continents.length; i++) {
        var pts = continents[i];
        ctx.beginPath();
        var xy = toXY(pts[0][0], pts[0][1]);
        ctx.moveTo(xy[0], xy[1]);
        for (var j = 1; j < pts.length; j++) {
          xy = toXY(pts[j][0], pts[j][1]);
          ctx.lineTo(xy[0], xy[1]);
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      }

      // Major rivers/lakes (simplified)
      ctx.strokeStyle = 'rgba(255,255,255,0.08)';
      ctx.lineWidth = 1;
      // Amazon
      ctx.beginPath();
      ctx.moveTo(toXY(-75,-10)[0], toXY(-75,-10)[1]);
      ctx.lineTo(toXY(-60,-5)[0], toXY(-60,-5)[1]);
      ctx.lineTo(toXY(-50,0)[0], toXY(-50,0)[1]);
      ctx.stroke();

      return new THREE.CanvasTexture(canvas);
    }

    var texture = makeTexture();
    var group = new THREE.Group();

    // Main sphere with texture
    var sphereMat = new THREE.MeshBasicMaterial({
      map: texture,
      transparent: true,
      opacity: 0.35
    });
    var sphere = new THREE.Mesh(new THREE.SphereGeometry(R, 48, 32), sphereMat);
    group.add(sphere);

    // Wireframe overlay
    var wireMat = new THREE.MeshBasicMaterial({
      color: 0x4488ff,
      wireframe: true,
      transparent: true,
      opacity: 0.12
    });
    var wire = new THREE.Mesh(new THREE.SphereGeometry(R * 1.002, 36, 24), wireMat);
    group.add(wire);

    // Bright grid lines (lat/lon)
    var gridMat = new THREE.LineBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.08
    });

    // Longitude lines
    for (var i = 0; i < 24; i++) {
      var theta = (i / 24) * Math.PI * 2;
      var pts = [];
      for (var j = 0; j <= 32; j++) {
        var phi = (j / 32) * Math.PI;
        pts.push(new THREE.Vector3(
          R * 1.001 * Math.sin(phi) * Math.cos(theta),
          R * 1.001 * Math.cos(phi),
          R * 1.001 * Math.sin(phi) * Math.sin(theta)
        ));
      }
      var g = new THREE.BufferGeometry().setFromPoints(pts);
      var line = new THREE.Line(g, gridMat);
      group.add(line);
    }

    // Latitude lines
    for (var i = 1; i < 12; i++) {
      var phi = (i / 12) * Math.PI;
      var pts = [];
      for (var j = 0; j <= 48; j++) {
        var theta = (j / 48) * Math.PI * 2;
        pts.push(new THREE.Vector3(
          R * 1.001 * Math.sin(phi) * Math.cos(theta),
          R * 1.001 * Math.cos(phi),
          R * 1.001 * Math.sin(phi) * Math.sin(theta)
        ));
      }
      var g = new THREE.BufferGeometry().setFromPoints(pts);
      var line = new THREE.Line(g, gridMat);
      group.add(line);
    }

    // Dots on surface
    var dotsPos = [];
    for (var i = 0; i < 800; i++) {
      var theta = Math.random() * Math.PI * 2;
      var phi = Math.acos((Math.random() * 2) - 1);
      var r = R * 1.03;
      dotsPos.push(r * Math.sin(phi) * Math.cos(theta));
      dotsPos.push(r * Math.sin(phi) * Math.sin(theta));
      dotsPos.push(r * Math.cos(phi));
    }
    var dotsGeo = new THREE.BufferGeometry();
    dotsGeo.setAttribute('position', new THREE.Float32BufferAttribute(dotsPos, 3));
    var dotsMat = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 1.6,
      transparent: true,
      opacity: 0.35
    });
    var dots = new THREE.Points(dotsGeo, dotsMat);
    group.add(dots);

    // Brighter city dots cluster near populated areas
    var cityPos = [];
    var cityLocs = [
      [40.7,-74.0],[34.0,-118.2],[51.5,-0.1],[48.8,2.3],[52.5,13.4],
      [55.7,37.6],[35.6,139.7],[31.2,121.5],[22.5,114.1],[39.9,116.4],
      [19.4,-99.1],[23.1,113.3],[28.6,77.2],[19.0,72.8],[1.3,103.8],
      [-33.8,151.2],[37.5,127.0],[41.0,28.9],[25.0,121.5],[13.7,100.5],
      [-23.5,-46.6],[40.4,-3.7],[30.0,31.2],[6.5,3.3],[-34.6,-58.4],
      [45.4,12.3],[52.3,4.8],[50.0,14.4],[59.3,18.0],[47.6,-122.3],
      [42.3,-83.0],[41.8,-87.6],[29.7,-95.3],[33.4,-112.0],[39.7,-105.0],
    ];
    for (var i = 0; i < cityLocs.length; i++) {
      var phi = (90 - cityLocs[i][0]) * Math.PI / 180;
      var theta = (cityLocs[i][1] + 180) * Math.PI / 180;
      var r = R * 1.04;
      cityPos.push(-r * Math.sin(phi) * Math.cos(theta));
      cityPos.push(r * Math.cos(phi));
      cityPos.push(r * Math.sin(phi) * Math.sin(theta));
    }
    var cityGeo = new THREE.BufferGeometry();
    cityGeo.setAttribute('position', new THREE.Float32BufferAttribute(cityPos, 3));
    var cityMat = new THREE.PointsMaterial({
      color: 0x66ccff,
      size: 2.5,
      transparent: true,
      opacity: 0.6
    });
    var cityDots = new THREE.Points(cityGeo, cityMat);
    group.add(cityDots);

    scene.add(group);

    // Orbital rings
    for (var ri = 0; ri < 3; ri++) {
      var ringR = R * (1.4 + ri * 0.35);
      var ringGeo = new THREE.RingGeometry(ringR, ringR + 3, 80);
      var ringMat = new THREE.MeshBasicMaterial({
        color: 0x4488ff,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.05 + ri * 0.02
      });
      var ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 3 + ri * 0.35;
      ring.rotation.z = 0.15 + ri * 0.3;
      scene.add(ring);
    }

    camera.position.set(0, 20, 400);
    camera.lookAt(0, 0, 0);

    var mouseX = 0, mouseY = 0;
    document.addEventListener('mousemove', function(e) {
      mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
      mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
    });

    function animate() {
      requestAnimationFrame(animate);
      group.rotation.y += 0.003;
      group.rotation.x += (mouseY * 0.03 - group.rotation.x) * 0.01;
      renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', function() {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  } catch(e) {
    console.error('Globe:', e.message);
  }
})();
