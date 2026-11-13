const racks = window.WH_RACKS || [], mount = document.getElementById('threeMount'), status = document.getElementById('sceneStatus');
try {
    const THREE = await import('https://esm.sh/three@0.160.0');
    const { OrbitControls } = await import('https://esm.sh/three@0.160.0/examples/jsm/controls/OrbitControls.js');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#091624');
    scene.fog = new THREE.Fog('#091624', 35, 90);
    const camera = new THREE.PerspectiveCamera(48, mount.clientWidth / 390, .1, 180);
    camera.position.set(24, 22, 30);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 1.6));
    renderer.setSize(mount.clientWidth, 390);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    mount.appendChild(renderer.domElement);
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = .07;
    controls.maxPolarAngle = Math.PI * .49;
    controls.target.set(0, 1, 0);
    scene.add(new THREE.HemisphereLight(0xb9dcff, 0x1b2633, 2.0));
    const key = new THREE.DirectionalLight(0xffffff, 2.2);
    key.position.set(-14, 28, 16);
    key.castShadow = true;
    scene.add(key);
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(64, 48), new THREE.MeshStandardMaterial({ color: '#172739', roughness: .92 }));
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = -.08;
    floor.receiveShadow = true;
    scene.add(floor);
    const grid = new THREE.GridHelper(64, 32, '#34506c', '#263b52');
    grid.position.y = -.04;
    scene.add(grid);
    for (let x = -28; x <= 28; x += 14)
        for (let z = -20; z <= 20; z += 20) {
            let col = new THREE.Mesh(new THREE.BoxGeometry(.42, 6, .42), new THREE.MeshStandardMaterial({ color: '#60758c', metalness: .55, roughness: .5 }));
            col.position.set(x, 3, z);
            col.castShadow = true;
            scene.add(col);
        }
    const roof = new THREE.Mesh(new THREE.BoxGeometry(60, .24, 42), new THREE.MeshStandardMaterial({ color: '#30465c', metalness: .35, roughness: .7, transparent: true, opacity: .18, side: THREE.DoubleSide }));
    roof.position.y = 6.4;
    scene.add(roof);
    const positions = new Map(), groups = new Map(), rackMaterials = new Map();
    const cols = 8, cellX = 4.4, cellZ = 5.1;
    function rackColour(r) { if (r.rack_status === 'Empty')
        return '#73869a'; if (r.utilization_pct >= 95)
        return '#ed646d'; if (r.utilization_pct >= 85)
        return '#e2ae49'; return '#35bb8a'; }
    racks.forEach((r, i) => {
        const col = i % cols, row = Math.floor(i / cols), x = (col - (cols - 1) / 2) * cellX, z = (row - Math.floor((racks.length - 1) / cols) / 2) * cellZ;
        positions.set(r.rack_id, new THREE.Vector3(x, 0, z));
        const group = new THREE.Group();
        group.position.set(x, 0, z);
        group.userData.rackId = r.rack_id;
        const steel = new THREE.MeshStandardMaterial({ color: rackColour(r), metalness: .58, roughness: .42 });
        rackMaterials.set(r.rack_id, steel);
        const darkSteel = new THREE.MeshStandardMaterial({ color: '#3b526b', metalness: .5, roughness: .55 });
        const carton = new THREE.MeshStandardMaterial({ color: r.low_stock_sku_count ? '#c98c4b' : '#ba9a6e', roughness: .85 });
        for (const px of [-.95, .95])
            for (const pz of [-.42, .42]) {
                const post = new THREE.Mesh(new THREE.BoxGeometry(.12, 3.25, .12), darkSteel);
                post.position.set(px, 1.62, pz);
                post.castShadow = true;
                post.userData.rackId = r.rack_id;
                group.add(post);
            }
        for (const y of [.55, 1.55, 2.55]) {
            const beam = new THREE.Mesh(new THREE.BoxGeometry(2.05, .12, .95), steel);
            beam.position.y = y;
            beam.castShadow = true;
            beam.userData.rackId = r.rack_id;
            group.add(beam);
        }
        const boxCount = Math.max(0, Math.min(6, Math.round((r.utilization_pct || 0) / 17)));
        for (let b = 0; b < boxCount; b++) {
            const w = .46, h = .42, d = .34;
            const box = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), carton);
            box.position.set(-.48 + (b % 3) * .48, .82 + Math.floor(b / 3) * 1.05, .03);
            box.castShadow = true;
            box.userData.rackId = r.rack_id;
            group.add(box);
        }
        group.traverse(o => { if (o.isMesh)
            o.userData.rackId = r.rack_id; });
        scene.add(group);
        groups.set(r.rack_id, group);
    });
    function dock(x, z, color, label) { const m = new THREE.Mesh(new THREE.BoxGeometry(5, .35, 3), new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: .1 })); m.position.set(x, .15, z); scene.add(m); }
    dock(-27, 0, '#246c9e', 'RECEIVING');
    dock(27, 0, '#267b67', 'DISPATCH');
    const aisle = new THREE.Mesh(new THREE.BoxGeometry(56, .04, 1.15), new THREE.MeshStandardMaterial({ color: '#d7a94d', emissive: '#684d1e', emissiveIntensity: .12 }));
    aisle.position.set(0, .03, -13);
    scene.add(aisle);
    const forklift = new THREE.Group();
    const forkBody = new THREE.Mesh(new THREE.BoxGeometry(1.5, .72, 1.05), new THREE.MeshStandardMaterial({ color: '#e3ad42', metalness: .25, roughness: .6 }));
    forkBody.position.y = .72;
    forklift.add(forkBody);
    const cabin = new THREE.Mesh(new THREE.BoxGeometry(.62, .95, .9), new THREE.MeshStandardMaterial({ color: '#263b52', metalness: .3, roughness: .45 }));
    cabin.position.set(-.18, 1.48, -.02);
    forklift.add(cabin);
    const mast = new THREE.Mesh(new THREE.BoxGeometry(.16, 2.2, .18), new THREE.MeshStandardMaterial({ color: '#a9b7c6', metalness: .7, roughness: .35 }));
    mast.position.set(.68, 1.25, 0);
    forklift.add(mast);
    const forks = new THREE.Mesh(new THREE.BoxGeometry(1.1, .08, .72), new THREE.MeshStandardMaterial({ color: '#bcc9d5', metalness: .75, roughness: .25 }));
    forks.position.set(1.02, .32, 0);
    forklift.add(forks);
    for (const wx of [-.48, .48])
        for (const wz of [-.48, .48]) {
            const wheel = new THREE.Mesh(new THREE.CylinderGeometry(.22, .22, .16, 12), new THREE.MeshStandardMaterial({ color: '#141c27', roughness: .9 }));
            wheel.rotation.x = Math.PI / 2;
            wheel.position.set(wx, .28, wz);
            forklift.add(wheel);
        }
    forklift.traverse(o => { if (o.isMesh)
        o.castShadow = true; });
    scene.add(forklift);
    const routeCurve = new THREE.CatmullRomCurve3([new THREE.Vector3(-27, 0, 0), new THREE.Vector3(-18, 0, -8), new THREE.Vector3(-8, 0, -13), new THREE.Vector3(5, 0, -13), new THREE.Vector3(18, 0, -9), new THREE.Vector3(26, 0, 0), new THREE.Vector3(14, 0, 8), new THREE.Vector3(-8, 0, 8), new THREE.Vector3(-27, 0, 0)]);
    const routeGeo = new THREE.BufferGeometry().setFromPoints(routeCurve.getPoints(120));
    const routeLine = new THREE.Line(routeGeo, new THREE.LineDashedMaterial({ color: '#4bc8e8', dashSize: 1.3, gapSize: .8, transparent: true, opacity: .85 }));
    routeLine.computeLineDistances();
    routeLine.visible = false;
    scene.add(routeLine);
    let simRunning = false, simProgress = 0, simSpeed = 1, lastFrame = performance.now();
    document.getElementById('playForklift').addEventListener('click', () => { simRunning = true; status.textContent = 'FORKLIFT FKL-01 · ROUTE ACTIVE'; });
    document.getElementById('pauseForklift').addEventListener('click', () => { simRunning = false; status.textContent = 'Route paused'; });
    document.getElementById('simSpeed').addEventListener('change', e => { simSpeed = Number(e.target.value) || 1; });
    document.getElementById('showPaths').addEventListener('change', e => { routeLine.visible = e.target.checked; });
    window.updateThreeHeatmap = () => { const mode = window.getTwinHeatMode ? window.getTwinHeatMode() : 'occupancy'; const maxVal = Math.max(1, ...racks.map(r => r.inventory_value || 0)); racks.forEach(r => { const mat = rackMaterials.get(r.rack_id); if (!mat)
        return; let color = rackColour(r); if (mode === 'value') {
        const p = Math.min(1, (r.inventory_value || 0) / maxVal);
        color = new THREE.Color().setRGB(.12 + p * .68, .34 + p * .13, .48 - p * .27);
    }
    else if (mode === 'status') {
        color = r.low_stock_sku_count ? '#ad5258' : (r.rack_status === 'Empty' ? '#73869a' : '#35bb8a');
    } mat.color.set(color); }); };
    const raycaster = new THREE.Raycaster(), pointer = new THREE.Vector2();
    let selectedHelper = null;
    let defaultCam = camera.position.clone(), defaultTarget = controls.target.clone();
    function highlight(id) { if (selectedHelper) {
        scene.remove(selectedHelper);
        selectedHelper.geometry.dispose();
        selectedHelper.material.dispose();
        selectedHelper = null;
    } const g = groups.get(id); if (g) {
        selectedHelper = new THREE.BoxHelper(g, new THREE.Color('#43dfff'));
        selectedHelper.material.depthTest = false;
        selectedHelper.material.transparent = true;
        selectedHelper.material.opacity = .95;
        scene.add(selectedHelper);
    } }
    function focus(id) { const p = positions.get(id); if (!p)
        return; controls.target.copy(p).add(new THREE.Vector3(0, 1.2, 0)); const offset = new THREE.Vector3(5, 4.5, 7); camera.position.copy(p).add(offset); controls.update(); }
    window.focusThreeRack = focus;
    window.highlightThreeRack = highlight;
    window.resetThreeCamera = () => { camera.position.copy(defaultCam); controls.target.copy(defaultTarget); controls.update(); };
    renderer.domElement.addEventListener('pointerdown', e => { const rect = renderer.domElement.getBoundingClientRect(); pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1; pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1; raycaster.setFromCamera(pointer, camera); const hits = raycaster.intersectObjects([...groups.values()], true); if (hits.length) {
        let o = hits[0].object;
        while (o && !o.userData.rackId)
            o = o.parent;
        if (o && o.userData.rackId) {
            window.selectRackFrom3D(o.userData.rackId);
            highlight(o.userData.rackId);
        }
    } });
    const resize = () => { const w = mount.clientWidth, h = mount.clientHeight || 390; camera.aspect = w / h; camera.updateProjectionMatrix(); renderer.setSize(w, h); };
    new ResizeObserver(resize).observe(mount);
    function animate() { requestAnimationFrame(animate); const now = performance.now(), dt = Math.min(.05, (now - lastFrame) / 1000); lastFrame = now; if (simRunning) {
        simProgress = (simProgress + dt * .025 * simSpeed) % 1;
        const p = routeCurve.getPointAt(simProgress), t = routeCurve.getTangentAt(simProgress);
        forklift.position.set(p.x, 0, p.z);
        forklift.rotation.y = Math.atan2(t.x, t.z);
    } controls.update(); if (selectedHelper)
        selectedHelper.update(); renderer.render(scene, camera); }
    animate();
    status.textContent = '3D scene ready · click a rack to sync with 2D';
    status.style.color = '#92d8bd';
    const activeRack = document.getElementById('detailTitle').textContent;
    if (racks.some(r => r.rack_id === activeRack))
        highlight(activeRack);
    else if (racks.length)
        highlight(racks[0].rack_id);
}
catch (err) {
    console.error(err);
    status.textContent = '3D renderer unavailable · use the interactive 2D floor plan';
    status.style.color = '#ffd27b';
    document.getElementById('playForklift').disabled = true;
    document.getElementById('pauseForklift').disabled = true;
    document.getElementById('simSpeed').disabled = true;
}

