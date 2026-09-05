/**
 * AirfareX India — 3D Transforming Ticket & Aviation WebGL Scene
 * Built with Three.js (Procedural 3D Jetliner, Transforming Holographic Ticket, Dynamic Canvas Textures & Flight Arc)
 */

(function() {
  class ThreeAviationScene {
    constructor(containerId) {
      this.container = document.getElementById(containerId);
      if (!this.container) return;

      this.currentPlace = {
        code: 'DEL',
        name: 'Delhi',
        fare: 5240,
        airline: 'IndiGo',
        flightNo: '6E 203',
        origin: 'HYD',
        photo: '/assets/images/destination_delhi.jpg'
      };

      this.isTransforming = false;
      this.transformProgress = 0;
      this.cameraMode = 'ticket'; // 'ticket', 'plane', 'panoramic'
      this.autoRotate = true;

      this.init();
      this.createLights();
      this.createFloorGrid();
      this.createFlightArc();
      this.createJetliner();
      this.createTransformingTicket();
      this.setupControls();
      this.animate();

      // Handle resize
      window.addEventListener('resize', () => this.onWindowResize());
    }

    init() {
      this.scene = new THREE.Scene();
      this.scene.fog = new THREE.FogExp2(0x060b18, 0.015);

      const width = this.container.clientWidth || 800;
      const height = this.container.clientHeight || 450;

      this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
      this.camera.position.set(0, 3, 14);

      this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
      this.renderer.setSize(width, height);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      this.renderer.shadowMap.enabled = true;
      this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

      this.container.innerHTML = '';
      this.container.appendChild(this.renderer.domElement);
    }

    setupControls() {
      if (window.THREE && window.THREE.OrbitControls) {
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.maxPolarAngle = Math.PI / 2 - 0.05;
        this.controls.minDistance = 6;
        this.controls.maxDistance = 25;
        this.controls.target.set(0, 0, 0);
      }
    }

    createLights() {
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
      this.scene.add(ambientLight);

      // Cyan primary spotlight
      const cyanSpot = new THREE.SpotLight(0x0ea5e9, 2.5);
      cyanSpot.position.set(-8, 15, 12);
      cyanSpot.angle = Math.PI / 4;
      cyanSpot.penumbra = 0.8;
      cyanSpot.castShadow = true;
      this.scene.add(cyanSpot);

      // Mint fill spotlight
      const mintSpot = new THREE.SpotLight(0x10b981, 2.0);
      mintSpot.position.set(10, 12, 10);
      mintSpot.angle = Math.PI / 4;
      mintSpot.penumbra = 0.8;
      this.scene.add(mintSpot);

      // Back rim light
      const rimLight = new THREE.DirectionalLight(0x38bdf8, 1.2);
      rimLight.position.set(0, -6, -10);
      this.scene.add(rimLight);
    }

    createFloorGrid() {
      const grid = new THREE.GridHelper(40, 40, 0x0ea5e9, 0x1e293b);
      grid.position.y = -3.5;
      grid.material.opacity = 0.25;
      grid.material.transparent = true;
      this.scene.add(grid);

      // Glowing origin and destination beacon rings
      this.originBeacon = this.createBeacon(-7, -3.4, 3, 0x0ea5e9, 'HYD');
      this.destBeacon = this.createBeacon(7, -3.4, -2, 0x10b981, 'DEL');
      this.scene.add(this.originBeacon);
      this.scene.add(this.destBeacon);
    }

    createBeacon(x, y, z, color, label) {
      const group = new THREE.Group();
      group.position.set(x, y, z);

      // Cylinder core
      const coreGeo = new THREE.CylinderGeometry(0.3, 0.3, 0.2, 16);
      const coreMat = new THREE.MeshBasicMaterial({ color: color });
      const core = new THREE.Mesh(coreGeo, coreMat);
      group.add(core);

      // Concentric rings
      const ringGeo = new THREE.RingGeometry(0.5, 0.65, 32);
      ringGeo.rotateX(-Math.PI / 2);
      const ringMat = new THREE.MeshBasicMaterial({ color: color, transparent: true, opacity: 0.6, side: THREE.DoubleSide });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      group.add(ring);

      group.userData = { ring: ring, pulse: 0 };
      return group;
    }

    createFlightArc() {
      const p1 = new THREE.Vector3(-7, -3.4, 3);
      const p2 = new THREE.Vector3(0, 3.5, 0);
      const p3 = new THREE.Vector3(7, -3.4, -2);

      this.curve = new THREE.QuadraticBezierCurve3(p1, p2, p3);
      const points = this.curve.getPoints(50);
      const geometry = new THREE.BufferGeometry().setFromPoints(points);

      const material = new THREE.LineDashedMaterial({
        color: 0x38bdf8,
        dashSize: 0.4,
        gapSize: 0.2,
        linewidth: 2
      });

      this.arcLine = new THREE.Line(geometry, material);
      this.arcLine.computeLineDistances();
      this.scene.add(this.arcLine);
    }

    updateFlightArc(destX, destZ) {
      if (!this.curve) return;
      const p1 = new THREE.Vector3(-7, -3.4, 3);
      const p2 = new THREE.Vector3((p1.x + destX) / 2, 4.0, (p1.z + destZ) / 2);
      const p3 = new THREE.Vector3(destX, -3.4, destZ);

      this.curve = new THREE.QuadraticBezierCurve3(p1, p2, p3);
      const points = this.curve.getPoints(50);
      this.arcLine.geometry.setFromPoints(points);
      this.arcLine.computeLineDistances();

      if (this.destBeacon) {
        this.destBeacon.position.set(destX, -3.4, destZ);
      }
    }

    createJetliner() {
      this.planeGroup = new THREE.Group();

      const fuselageMat = new THREE.MeshStandardMaterial({
        color: 0xf8fafc,
        roughness: 0.2,
        metalness: 0.8
      });
      const wingMat = new THREE.MeshStandardMaterial({
        color: 0xe2e8f0,
        roughness: 0.3,
        metalness: 0.6
      });
      const accentMat = new THREE.MeshStandardMaterial({
        color: 0x0ea5e9,
        roughness: 0.2,
        metalness: 0.9
      });
      const glowEngineMat = new THREE.MeshBasicMaterial({
        color: 0x38bdf8
      });

      // 1. Fuselage
      const fuselageGeo = new THREE.CylinderGeometry(0.35, 0.35, 4.2, 24);
      fuselageGeo.rotateX(Math.PI / 2);
      const fuselage = new THREE.Mesh(fuselageGeo, fuselageMat);
      fuselage.castShadow = true;
      this.planeGroup.add(fuselage);

      // Nose Cone
      const noseGeo = new THREE.ConeGeometry(0.35, 1.1, 24);
      noseGeo.rotateX(-Math.PI / 2);
      const nose = new THREE.Mesh(noseGeo, fuselageMat);
      nose.position.z = 2.65;
      this.planeGroup.add(nose);

      // Cockpit Window Glass
      const cockpitGeo = new THREE.BoxGeometry(0.4, 0.18, 0.5);
      const cockpitMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.1 });
      const cockpit = new THREE.Mesh(cockpitGeo, cockpitMat);
      cockpit.position.set(0, 0.22, 2.2);
      this.planeGroup.add(cockpit);

      // 2. Main Wings (Swept)
      const wingShape = new THREE.Shape();
      wingShape.moveTo(-3.8, 0);
      wingShape.lineTo(3.8, 0);
      wingShape.lineTo(2.2, 1.2);
      wingShape.lineTo(-2.2, 1.2);
      wingShape.closePath();

      const wingExtrude = new THREE.ExtrudeGeometry(wingShape, { depth: 0.08, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02 });
      wingExtrude.rotateX(Math.PI / 2);
      const wings = new THREE.Mesh(wingExtrude, wingMat);
      wings.position.set(0, 0, 0.4);
      wings.castShadow = true;
      this.planeGroup.add(wings);

      // Wingtips
      const tipGeo = new THREE.BoxGeometry(0.08, 0.35, 0.4);
      const tipL = new THREE.Mesh(tipGeo, accentMat);
      tipL.position.set(-3.8, 0.15, 0.4);
      const tipR = new THREE.Mesh(tipGeo, accentMat);
      tipR.position.set(3.8, 0.15, 0.4);
      this.planeGroup.add(tipL);
      this.planeGroup.add(tipR);

      // 3. Turbofan Engines (Twin underslung)
      const engineGeo = new THREE.CylinderGeometry(0.22, 0.2, 1.1, 16);
      engineGeo.rotateX(Math.PI / 2);
      const engineL = new THREE.Mesh(engineGeo, fuselageMat);
      engineL.position.set(-1.4, -0.3, 0.3);
      const engineR = new THREE.Mesh(engineGeo, fuselageMat);
      engineR.position.set(1.4, -0.3, 0.3);

      // Engine exhaust glows
      const exhaustGeo = new THREE.CylinderGeometry(0.12, 0.16, 0.2, 16);
      exhaustGeo.rotateX(Math.PI / 2);
      const exhaustL = new THREE.Mesh(exhaustGeo, glowEngineMat);
      exhaustL.position.set(-1.4, -0.3, -0.35);
      const exhaustR = new THREE.Mesh(exhaustGeo, glowEngineMat);
      exhaustR.position.set(1.4, -0.3, -0.35);

      this.planeGroup.add(engineL);
      this.planeGroup.add(engineR);
      this.planeGroup.add(exhaustL);
      this.planeGroup.add(exhaustR);

      // 4. Tail Empennage
      const tailFinGeo = new THREE.BoxGeometry(0.06, 1.2, 0.9);
      const tailFin = new THREE.Mesh(tailFinGeo, accentMat);
      tailFin.position.set(0, 0.7, -1.8);
      tailFin.rotation.x = -Math.PI / 8;
      this.planeGroup.add(tailFin);

      // Horizontal Stabilizers
      const stabGeo = new THREE.BoxGeometry(2.0, 0.05, 0.6);
      const stab = new THREE.Mesh(stabGeo, wingMat);
      stab.position.set(0, 0.15, -1.9);
      this.planeGroup.add(stab);

      this.planeGroup.position.set(0, 2.5, 0);
      this.planeGroup.scale.set(0.85, 0.85, 0.85);
      this.scene.add(this.planeGroup);
    }

    createTransformingTicket() {
      this.ticketGroup = new THREE.Group();

      // Ticket geometry: 6.2 width, 3.2 height, 0.12 depth
      const ticketGeo = new THREE.BoxGeometry(6.2, 3.2, 0.12);

      // Generate dynamic texture on 2D canvas
      this.ticketCanvas = document.createElement('canvas');
      this.ticketCanvas.width = 1240;
      this.ticketCanvas.height = 640;
      this.ticketCtx = this.ticketCanvas.getContext('2d');

      this.ticketTexture = new THREE.CanvasTexture(this.ticketCanvas);
      this.ticketTexture.minFilter = THREE.LinearFilter;

      // Draw initial ticket graphics
      this.drawTicketCanvas();

      // Ticket Materials (Front textured, Sides metallic aerospace blue)
      const borderMat = new THREE.MeshStandardMaterial({
        color: 0x0f172a,
        metalness: 0.9,
        roughness: 0.2
      });

      const frontMat = new THREE.MeshStandardMaterial({
        map: this.ticketTexture,
        metalness: 0.15,
        roughness: 0.4
      });

      const materials = [
        borderMat, // Right
        borderMat, // Left
        borderMat, // Top
        borderMat, // Bottom
        frontMat,  // Front (Textured)
        borderMat  // Back
      ];

      this.ticketMesh = new THREE.Mesh(ticketGeo, materials);
      this.ticketMesh.castShadow = true;
      this.ticketMesh.receiveShadow = true;
      this.ticketGroup.add(this.ticketMesh);

      // Holographic glowing outline
      const edges = new THREE.EdgesGeometry(ticketGeo);
      const lineMat = new THREE.LineBasicMaterial({ color: 0x0ea5e9, linewidth: 2 });
      const wireframe = new THREE.LineSegments(edges, lineMat);
      this.ticketGroup.add(wireframe);

      // Ticket position
      this.ticketGroup.position.set(0, -0.4, 2.2);
      this.ticketGroup.rotation.x = 0.05;
      this.scene.add(this.ticketGroup);
    }

    drawTicketCanvas() {
      const ctx = this.ticketCtx;
      const w = this.ticketCanvas.width;
      const h = this.ticketCanvas.height;

      // 1. Dark Aerospace Background
      ctx.fillStyle = '#0a1128';
      ctx.fillRect(0, 0, w, h);

      // Decorative top gradient bar
      const grad = ctx.createLinearGradient(0, 0, w, 0);
      grad.addColorStop(0, '#0ea5e9');
      grad.addColorStop(0.5, '#10b981');
      grad.addColorStop(1, '#8b5cf6');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, w, 14);

      // 2. Left Photo Section (Destination Picture)
      const photoWidth = 500;
      
      // Load and draw image if available
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.src = this.currentPlace.photo;
      img.onload = () => {
        // Draw image clipped to left area
        ctx.save();
        ctx.drawImage(img, 0, 14, photoWidth, h - 14);
        
        // Gradient overlay for text readability
        const photoGrad = ctx.createLinearGradient(0, 0, photoWidth, 0);
        photoGrad.addColorStop(0, 'rgba(6, 11, 24, 0.3)');
        photoGrad.addColorStop(0.7, 'rgba(10, 17, 40, 0.85)');
        photoGrad.addColorStop(1, '#0a1128');
        ctx.fillStyle = photoGrad;
        ctx.fillRect(0, 14, photoWidth, h - 14);

        // Destination Badge on Photo
        ctx.fillStyle = '#0ea5e9';
        ctx.font = 'bold 20px sans-serif';
        ctx.fillText('DESTINATION SECTOR', 36, 60);

        ctx.fillStyle = '#ffffff';
        ctx.font = '900 48px sans-serif';
        ctx.fillText(this.currentPlace.name.toUpperCase(), 36, 115);

        ctx.fillStyle = '#10b981';
        ctx.font = 'bold 24px sans-serif';
        ctx.fillText(`● SECTOR ${this.currentPlace.code}`, 36, 155);

        ctx.restore();

        // 3. Right Section: Flight Telemetry & Live Fare
        this.renderTicketDetails(ctx, w, h);
        if (this.ticketTexture) this.ticketTexture.needsUpdate = true;
      };

      // Fallback if image load takes a second
      this.renderTicketDetails(ctx, w, h);
      if (this.ticketTexture) this.ticketTexture.needsUpdate = true;
    }

    renderTicketDetails(ctx, w, h) {
      const startX = 520;

      // Airline & Flight No
      ctx.fillStyle = '#94a3b8';
      ctx.font = 'bold 18px sans-serif';
      ctx.fillText('OPERATING AIRLINE', startX, 60);

      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 28px sans-serif';
      ctx.fillText(`${this.currentPlace.airline} · ${this.currentPlace.flightNo}`, startX, 95);

      // Perforated Divider line
      ctx.strokeStyle = '#1e293b';
      ctx.lineWidth = 3;
      ctx.setLineDash([8, 8]);
      ctx.beginPath();
      ctx.moveTo(startX, 125);
      ctx.lineTo(w - 30, 125);
      ctx.stroke();
      ctx.setLineDash([]);

      // Route & Schedule
      ctx.fillStyle = '#94a3b8';
      ctx.font = 'bold 18px sans-serif';
      ctx.fillText('ROUTE', startX, 165);
      ctx.fillText('FLIGHT STATUS', startX + 320, 165);

      ctx.fillStyle = '#38bdf8';
      ctx.font = '900 36px monospace';
      ctx.fillText(`${this.currentPlace.origin} ➔ ${this.currentPlace.code}`, startX, 210);

      ctx.fillStyle = '#10b981';
      ctx.font = 'bold 22px sans-serif';
      ctx.fillText('ON TIME (CONFIRMED)', startX + 320, 205);

      // Telemetry row (Seat, Gate, Terminal)
      ctx.fillStyle = '#64748b';
      ctx.font = 'bold 16px sans-serif';
      ctx.fillText('GATE', startX, 265);
      ctx.fillText('TERMINAL', startX + 130, 265);
      ctx.fillText('BOARDING', startX + 270, 265);
      ctx.fillText('CABIN', startX + 430, 265);

      ctx.fillStyle = '#f8fafc';
      ctx.font = 'bold 24px sans-serif';
      ctx.fillText('G14', startX, 300);
      ctx.fillText('T2', startX + 130, 300);
      ctx.fillText('05:45 AM', startX + 270, 300);
      ctx.fillText('Economy', startX + 430, 300);

      // Large Glowing Live Fare Box
      ctx.fillStyle = 'rgba(14, 165, 233, 0.12)';
      ctx.strokeStyle = '#0ea5e9';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(startX, 345, w - startX - 35, 160, 14);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#94a3b8';
      ctx.font = 'bold 18px sans-serif';
      ctx.fillText('LIVE BENCHMARK TICKET FARE', startX + 24, 385);

      ctx.fillStyle = '#34d399';
      ctx.font = '900 58px sans-serif';
      ctx.fillText(`₹${this.currentPlace.fare.toLocaleString('en-IN')}`, startX + 24, 455);

      ctx.fillStyle = '#94a3b8';
      ctx.font = '16px sans-serif';
      ctx.fillText('Taxes, Airport UDF & GST Included · Validated by DGCA Observation', startX + 24, 485);

      // Barcode simulation
      ctx.fillStyle = '#475569';
      const bcX = startX;
      const bcY = 535;
      for (let i = 0; i < 68; i++) {
        const barW = (i % 3 === 0) ? 5 : (i % 5 === 0) ? 3 : 2;
        ctx.fillRect(bcX + (i * 9), bcY, barW, 45);
      }
    }

    transformToDestination(cityCode, cityName, farePrice, airline = 'IndiGo', flightNo = '6E 203', photoUrl = null) {
      if (this.isTransforming) return;
      this.isTransforming = true;
      this.transformProgress = 0;

      // Coordinate mapping for 3D trajectory
      const coordMap = {
        DEL: { x: 6.5, z: -3.5, photo: '/assets/images/destination_delhi.jpg' },
        BOM: { x: 4.5, z: 2.5, photo: '/assets/images/destination_mumbai.jpg' },
        BLR: { x: 7.0, z: 4.0, photo: '/assets/images/destination_delhi.jpg' },
        GOI: { x: 3.5, z: 5.0, photo: '/assets/images/destination_mumbai.jpg' },
        HYD: { x: 5.5, z: 1.0, photo: '/assets/images/destination_delhi.jpg' },
        MAA: { x: 8.0, z: 3.5, photo: '/assets/images/destination_delhi.jpg' },
        CCU: { x: 9.0, z: -1.0, photo: '/assets/images/destination_delhi.jpg' }
      };

      const target = coordMap[cityCode] || { x: 6.5, z: -3.5, photo: '/assets/images/destination_delhi.jpg' };

      this.currentPlace = {
        code: cityCode,
        name: cityName,
        fare: farePrice || 5240,
        airline: airline,
        flightNo: flightNo,
        origin: 'HYD',
        photo: photoUrl || target.photo
      };

      // Redraw canvas texture with new destination and fare
      this.drawTicketCanvas();

      // Update 3D parabolic trajectory arc and beacon
      this.updateFlightArc(target.x, target.z);

      // 360 Spin & Transformation Animation
      const startRotY = this.ticketGroup.rotation.y;
      const targetRotY = startRotY + Math.PI * 2;
      const duration = 1200; // 1.2s
      const startTime = performance.now();

      const animateTransform = (now) => {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const ease = 0.5 - Math.cos(progress * Math.PI) / 2; // Smooth cubic ease-in-out

        this.ticketGroup.rotation.y = startRotY + (targetRotY - startRotY) * ease;
        this.ticketGroup.position.y = -0.4 + Math.sin(progress * Math.PI) * 0.8; // Lift up during spin

        // Jetliner banking tilt
        if (this.planeGroup) {
          this.planeGroup.rotation.z = Math.sin(progress * Math.PI * 2) * 0.35;
          this.planeGroup.rotation.y = Math.sin(progress * Math.PI) * 0.4;
        }

        if (progress < 1) {
          requestAnimationFrame(animateTransform);
        } else {
          this.ticketGroup.rotation.y = targetRotY % (Math.PI * 2);
          this.ticketGroup.position.y = -0.4;
          if (this.planeGroup) {
            this.planeGroup.rotation.z = 0;
            this.planeGroup.rotation.y = 0;
          }
          this.isTransforming = false;
        }
      };

      requestAnimationFrame(animateTransform);

      // Update HUD Overlay
      const hudRoute = document.getElementById('hudRouteText');
      if (hudRoute) hudRoute.textContent = `${this.currentPlace.origin} ➔ ${this.currentPlace.code} · ${this.currentPlace.name}`;

      const hudFare = document.getElementById('hudFareText');
      if (hudFare) hudFare.textContent = `₹${this.currentPlace.fare.toLocaleString('en-IN')}`;
    }

    setCameraMode(mode) {
      this.cameraMode = mode;
      const targetPos = new THREE.Vector3();
      const lookTarget = new THREE.Vector3();

      if (mode === 'ticket') {
        targetPos.set(0, 0.8, 8.5);
        lookTarget.set(0, -0.4, 2.2);
      } else if (mode === 'plane') {
        targetPos.set(-4, 4.5, 6);
        lookTarget.set(0, 2.5, 0);
      } else if (mode === 'panoramic') {
        targetPos.set(0, 8, 16);
        lookTarget.set(0, 0, 0);
      }

      this.camera.position.lerp(targetPos, 0.8);
      if (this.controls) {
        this.controls.target.copy(lookTarget);
      }
    }

    animate() {
      requestAnimationFrame(() => this.animate());

      const time = performance.now() * 0.001;

      // Gentle aircraft cruising floating motion
      if (this.planeGroup && !this.isTransforming) {
        this.planeGroup.position.y = 2.5 + Math.sin(time * 1.5) * 0.15;
        this.planeGroup.rotation.z = Math.sin(time * 0.8) * 0.04;
      }

      // Gentle floating ticket oscillation
      if (this.ticketGroup && !this.isTransforming) {
        this.ticketGroup.position.y = -0.4 + Math.sin(time * 1.2 + 1) * 0.08;
      }

      // Beacon ring pulses
      if (this.originBeacon && this.originBeacon.userData.ring) {
        const s = 1 + (Math.sin(time * 3) + 1) * 0.2;
        this.originBeacon.userData.ring.scale.set(s, s, s);
      }
      if (this.destBeacon && this.destBeacon.userData.ring) {
        const s = 1 + (Math.sin(time * 3 + 1.5) + 1) * 0.2;
        this.destBeacon.userData.ring.scale.set(s, s, s);
      }

      // Update OrbitControls
      if (this.controls) {
        if (this.autoRotate && !this.isTransforming && !this.controls.state) {
          this.scene.rotation.y = Math.sin(time * 0.2) * 0.08;
        }
        this.controls.update();
      }

      this.renderer.render(this.scene, this.camera);
    }

    onWindowResize() {
      if (!this.container) return;
      const width = this.container.clientWidth;
      const height = this.container.clientHeight;
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(width, height);
    }
  }

  window.ThreeAviationScene = ThreeAviationScene;
})();
