/**
 * AirfareX India — Dynamic SVG Chart & Map Visualizations
 */

const Charts = {
  // Render Bar Pillars for Index Trend
  renderTrendBars(containerId, points) {
    const container = document.getElementById(containerId);
    if (!container || !points || !points.length) return;

    const values = points.map(p => p.value);
    const minVal = Math.min(...values) * 0.95;
    const maxVal = Math.max(...values) * 1.05;
    const range = maxVal - minVal || 1;

    let html = '<div class="chart-bars-wrap">';
    points.forEach((pt, index) => {
      const heightPct = Math.round(((pt.value - minVal) / range) * 85) + 15;
      const isLatest = index >= points.length - 2;
      const pillarClass = isLatest ? 'chart-bar-pillar accent' : 'chart-bar-pillar';

      html += `
        <div class="chart-bar-col">
          <div class="chart-bar-val">${pt.value.toFixed(1)}</div>
          <div class="${pillarClass}" style="height: ${heightPct}%;" title="${pt.label}: ${pt.value}"></div>
          <div class="chart-bar-lbl">${pt.label}</div>
        </div>
      `;
    });
    html += '</div>';
    container.innerHTML = html;
  },

  // Render SVG Network Route Map
  renderNetworkMap(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Hub coordinates normalized in 500x320 viewBox
    const hubs = {
      DEL: { x: 230, y: 80, name: "Delhi", code: "DEL", hot: true },
      BOM: { x: 155, y: 195, name: "Mumbai", code: "BOM", hot: false },
      BLR: { x: 235, y: 260, name: "Bengaluru", code: "BLR", hot: false },
      HYD: { x: 245, y: 200, name: "Hyderabad", code: "HYD", hot: true },
      MAA: { x: 265, y: 270, name: "Chennai", code: "MAA", hot: true },
      CCU: { x: 375, y: 150, name: "Kolkata", code: "CCU", hot: false },
      GOI: { x: 165, y: 240, name: "Goa", code: "GOI", hot: false },
      PNQ: { x: 175, y: 205, name: "Pune", code: "PNQ", hot: false },
      JAI: { x: 195, y: 105, name: "Jaipur", code: "JAI", hot: false }
    };

    const routes = [
      ["DEL", "BOM"],
      ["DEL", "BLR"],
      ["BLR", "HYD"],
      ["HYD", "DEL"],
      ["MAA", "DEL"],
      ["CCU", "DEL"],
      ["BOM", "GOI"],
      ["PNQ", "DEL"],
      ["JAI", "BOM"]
    ];

    let svg = `
      <svg viewBox="0 0 500 320" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="routeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#1769e0" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#10a56f" stop-opacity="0.8"/>
          </linearGradient>
          <radialGradient id="hotGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#e11d48" stop-opacity="0.6"/>
            <stop offset="100%" stop-color="#e11d48" stop-opacity="0"/>
          </radialGradient>
        </defs>
    `;

    // Draw route curves
    routes.forEach(([from, to], i) => {
      const p1 = hubs[from];
      const p2 = hubs[to];
      if (!p1 || !p2) return;
      const mx = (p1.x + p2.x) / 2 + (i % 2 === 0 ? 15 : -15);
      const my = (p1.y + p2.y) / 2 - 10;
      const isActive = i < 3;
      svg += `
        <path d="M ${p1.x} ${p1.y} Q ${mx} ${my} ${p2.x} ${p2.y}" 
              fill="none" 
              class="flight-path-line ${isActive ? 'active' : ''}" 
              stroke="${isActive ? '#10a56f' : 'rgba(56, 189, 248, 0.4)'}" 
              stroke-width="${isActive ? '2' : '1.5'}"/>
      `;
    });

    // Draw airport nodes
    Object.values(hubs).forEach(h => {
      const nodeColor = h.hot ? '#e11d48' : '#1769e0';
      svg += `
        <g class="city-node" onclick="window.selectCity('${h.code}', '${h.name}')">
          ${h.hot ? `<circle cx="${h.x}" cy="${h.y}" r="16" fill="url(#hotGlow)"/>` : ''}
          <circle cx="${h.x}" cy="${h.y}" r="8" fill="#ffffff" stroke="${nodeColor}" stroke-width="3"/>
          <text x="${h.x}" y="${h.y - 12}" text-anchor="middle" fill="#f8fafc" font-size="10" font-weight="800" letter-spacing="0.5">${h.code}</text>
        </g>
      `;
    });

    svg += '</svg>';
    container.innerHTML = svg;
  }
};

window.Charts = Charts;
