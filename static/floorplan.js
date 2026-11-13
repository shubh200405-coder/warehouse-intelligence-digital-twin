(function () {
    const racks = window.WH_RACKS || [], svg = document.getElementById('floorSvg');
    const ns = 'http://www.w3.org/2000/svg';
    let selectedId = racks[0]?.rack_id || null;
    let heatMode = 'occupancy';
    const cols = 8, cellW = 100, cellH = 78, startX = 115, startY = 95;
    const maxValue = Math.max(1, ...racks.map(r => r.inventory_value || 0));
    const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    const fmt = n => n == null ? '—' : Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });
    const money = n => n == null ? '—' : '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });
    function fillFor(r) { if (r.rack_id === selectedId)
        return '#167c99'; if (heatMode === 'value') {
        let p = Math.min(1, (r.inventory_value || 0) / maxValue);
        return `rgb(${Math.round(30 + p * 170)},${Math.round(83 + p * 34)},${Math.round(110 - p * 65)})`;
    } if (heatMode === 'status') {
        if (r.low_stock_sku_count > 0)
            return '#a84b4b';
        return r.rack_status === 'Empty' ? '#63758b' : '#267c65';
    } if (r.rack_status === 'Empty')
        return '#63758b'; if (r.utilization_pct >= 95)
        return '#b84f55'; if (r.utilization_pct >= 85)
        return '#a87d31'; return '#247b61'; }
    function renderFloor() {
        svg.innerHTML = '';
        const bg = document.createElementNS(ns, 'rect');
        bg.setAttribute('x', 10);
        bg.setAttribute('y', 10);
        bg.setAttribute('width', 980);
        bg.setAttribute('height', 540);
        bg.setAttribute('rx', 18);
        bg.setAttribute('fill', '#0c1b2b');
        bg.setAttribute('stroke', '#29415c');
        svg.appendChild(bg);
        const title = document.createElementNS(ns, 'text');
        title.setAttribute('x', 34);
        title.setAttribute('y', 42);
        title.setAttribute('class', 'floor-small');
        title.textContent = 'WAREHOUSE BOUNDARY / RACK GRID';
        svg.appendChild(title);
        [['RECEIVING', 25, 85, 78, 145], ['STAGING', 25, 270, 78, 110], ['DISPATCH', 897, 85, 78, 145]].forEach(([t, x, y, w, h]) => { let r = document.createElementNS(ns, 'rect'); r.setAttribute('x', x); r.setAttribute('y', y); r.setAttribute('width', w); r.setAttribute('height', h); r.setAttribute('rx', 7); r.setAttribute('fill', '#193149'); r.setAttribute('stroke', '#3a5c7c'); svg.appendChild(r); let tx = document.createElementNS(ns, 'text'); tx.setAttribute('x', x + w / 2); tx.setAttribute('y', y + h / 2); tx.setAttribute('class', 'floor-small'); tx.setAttribute('text-anchor', 'middle'); tx.textContent = t; svg.appendChild(tx); });
        for (let row = 0; row < 5; row++) {
            let lane = document.createElementNS(ns, 'rect');
            lane.setAttribute('x', 112);
            lane.setAttribute('y', startY + row * cellH + 54);
            lane.setAttribute('width', 770);
            lane.setAttribute('height', 9);
            lane.setAttribute('fill', '#13263a');
            lane.setAttribute('rx', 4);
            svg.appendChild(lane);
        }
        racks.forEach((r, i) => { let col = i % cols, row = Math.floor(i / cols), x = startX + col * cellW, y = startY + row * cellH; let g = document.createElementNS(ns, 'g'); g.setAttribute('data-rack', r.rack_id); g.style.cursor = 'pointer'; let rect = document.createElementNS(ns, 'rect'); rect.setAttribute('x', x); rect.setAttribute('y', y); rect.setAttribute('width', 68); rect.setAttribute('height', 43); rect.setAttribute('rx', 5); rect.setAttribute('fill', fillFor(r)); rect.setAttribute('class', 'rack-shape' + (r.rack_id === selectedId ? ' selected' : '')); rect.addEventListener('click', () => selectRack(r.rack_id, true)); g.appendChild(rect); let tx = document.createElementNS(ns, 'text'); tx.setAttribute('x', x + 34); tx.setAttribute('y', y + 17); tx.setAttribute('class', 'rack-label'); tx.textContent = document.getElementById('showIds').checked ? r.rack_id.replace(/^.*-R/, 'R') : ''; g.appendChild(tx); let val = document.createElementNS(ns, 'text'); val.setAttribute('x', x + 34); val.setAttribute('y', y + 32); val.setAttribute('class', 'rack-label'); val.textContent = (r.utilization_pct || 0).toFixed(0) + '%'; g.appendChild(val); g.addEventListener('mouseenter', () => { document.getElementById('detailLocation').textContent = `${r.warehouse_id} · ${r.zone_id} · ${fmt(r.occupied_units)} / ${fmt(r.capacity_units)} units`; }); g.addEventListener('click', () => selectRack(r.rack_id, true)); svg.appendChild(g); });
        if (document.getElementById('showPaths').checked) {
            let path = document.createElementNS(ns, 'path');
            path.setAttribute('d', 'M105 210 L120 210 L120 510 L870 510 L870 210 L895 210');
            path.setAttribute('stroke', '#45bce2');
            path.setAttribute('stroke-width', '3');
            path.setAttribute('stroke-dasharray', '8 8');
            path.setAttribute('fill', 'none');
            path.setAttribute('opacity', '.8');
            svg.appendChild(path);
        }
    }
    function selectRack(id, from2d) {
        selectedId = id;
        renderFloor();
        let r = racks.find(x => x.rack_id === id);
        if (!r)
            return;
        document.getElementById('detailTitle').textContent = r.rack_id;
        document.getElementById('detailLocation').textContent = `${r.warehouse_id} · ${r.zone_id} · ${r.rack_name}`;
        document.getElementById('detailStatus').textContent = r.rack_status.toUpperCase();
        document.getElementById('detailMetrics').innerHTML = [['Capacity', fmt(r.capacity_units)], ['Occupied', fmt(r.occupied_units)], ['Available', fmt(r.available_units)], ['Utilization', (r.utilization_pct || 0).toFixed(1) + '%'], ['Inventory value', money(r.inventory_value)], ['SKU count', fmt(r.sku_count)]].map(([a, b]) => `<div class="metric"><label>${a}</label><b>${b}</b></div>`).join('');
        let rows = r.sku_rows || [];
        document.getElementById('skuRows').innerHTML = rows.length ? rows.map(s => `<tr><td>${esc(s.sku_id)}</td><td>${esc(s.product_name)}</td><td>${esc(s.category)}</td><td>${fmt(s.quantity)}</td><td>${money(s.inventory_value)}</td><td>${s.days_since_movement == null ? '—' : fmt(s.days_since_movement)}</td><td>${esc(s.stock_status)}</td></tr>`).join('') : '<tr><td colspan="7" class="empty">No SKU-level rows in the active filtered dataset.</td></tr>';
        if (from2d && window.focusThreeRack)
            window.focusThreeRack(id);
        if (window.highlightThreeRack)
            window.highlightThreeRack(id);
    }
    window.selectTwinRack = (id) => selectRack(id, true);
    window.selectRackFrom3D = (id) => selectRack(id, false);
    document.getElementById('heatMode').addEventListener('change', e => { heatMode = e.target.value; renderFloor(); if (window.updateThreeHeatmap)
        window.updateThreeHeatmap(); });
    window.getTwinHeatMode = () => heatMode;
    document.getElementById('showIds').addEventListener('change', renderFloor);
    document.getElementById('showPaths').addEventListener('change', renderFloor);
    document.getElementById('skuSearch').addEventListener('keydown', e => { if (e.key === 'Enter') {
        let q = e.target.value.toLowerCase().trim();
        let match = racks.find(r => r.rack_id.toLowerCase().includes(q) || (r.sku_rows || []).some(s => s.sku_id.toLowerCase().includes(q) || s.product_name.toLowerCase().includes(q)));
        if (match)
            selectRack(match.rack_id, true);
        else
            document.getElementById('detailLocation').textContent = 'No rack or SKU match found in the active filtered data.';
    } });
    document.getElementById('focusRack').addEventListener('click', () => { if (selectedId && window.focusThreeRack)
        window.focusThreeRack(selectedId); });
    document.getElementById('resetCamera').addEventListener('click', () => { if (window.resetThreeCamera)
        window.resetThreeCamera(); });
    renderFloor();
    if (selectedId)
        selectRack(selectedId, false);
})();

