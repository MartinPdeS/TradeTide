import {number, date} from './research.mjs';
export const colors = ['#3459c7', '#bf8527', '#8964be', '#218c80'];
function svgNode(tag, attrs = {}, text) {
  const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
  Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
  if (text !== undefined) node.textContent = text;
  return node;
}
export function plot(container, series, times, {
  digits = 2, fill = false, markers = [], onInspect = () => {}, selectedTrade = null,
} = {}) {
  if (!container.clientWidth || !container.clientHeight) return;
  const width = Math.max(280, container.clientWidth), height = container.clientHeight;
  const left = 74, right = 14, top = 16, bottom = 30;
  let min = Infinity, max = -Infinity;
  for (const line of series) for (const value of line.values) {
    if (value != null && Number.isFinite(value)) { min = Math.min(min, value); max = Math.max(max, value); }
  }
  if (!Number.isFinite(min)) {
    const message = document.createElement('p'); message.className = 'placeholder';
    message.textContent = 'No values in this range. Expand the range or reduce the indicator window.';
    container.replaceChildren(message); return;
  }
  const padding = (max - min) * .12 || Math.abs(max) * .001 || 1;
  min -= padding; max += padding;
  const x = index => left + index / Math.max(1, times.length - 1) * (width - left - right);
  const y = value => top + (max - value) / (max - min) * (height - top - bottom);
  const svg = svgNode('svg', {
    viewBox: `0 0 ${width} ${height}`, role: 'img', tabindex: 0,
    'aria-label': `${series.map(s => s.name).join(', ')}. Use left and right arrow keys to inspect bars.`,
  });
  for (let tick = 0; tick < 5; tick++) {
    const value = min + (max - min) * tick / 4, yy = y(value);
    svg.append(svgNode('line', {x1: left, x2: width - right, y1: yy, y2: yy, stroke: '#e6ebf2', 'stroke-dasharray': '3 4'}));
    svg.append(svgNode('text', {x: left - 10, y: yy + 4, 'text-anchor': 'end', fill: '#74829a', 'font-size': 10}, number(value, digits)));
  }
  series.forEach((line, lineIndex) => {
    const values = line.values, indices = new Set([0, values.length - 1]);
    const step = Math.max(1, Math.ceil(values.length / 650));
    // Preserve extrema and gaps while keeping large samples responsive.
    for (let start = 0; start < values.length; start += step) {
      let low = null, high = null;
      for (let i = start; i < Math.min(start + step, values.length); i++) {
        if (values[i] == null) { indices.add(i); continue; }
        if (low == null || values[i] < values[low]) low = i;
        if (high == null || values[i] > values[high]) high = i;
      }
      if (low != null) { indices.add(low); indices.add(high); }
    }
    let path = '', pen = false;
    for (const i of [...indices].sort((a, b) => a - b)) {
      if (values[i] == null) { pen = false; continue; }
      path += `${pen ? ' L' : ' M'}${x(i)},${y(values[i])}`; pen = true;
    }
    const color = line.color || colors[lineIndex % colors.length];
    if (fill && series.length === 1 && values.every(v => v != null)) {
      svg.append(svgNode('path', {d: `${path} L${x(values.length - 1)},${height - bottom} L${x(0)},${height - bottom} Z`, fill: color, 'fill-opacity': .06}));
    }
    svg.append(svgNode('path', {d: path, fill: 'none', stroke: color, 'stroke-width': 1.8, 'stroke-linejoin': 'round'}));
  });
  for (const [index, anchor] of [[0, 'start'], ...(width > 520 ? [[Math.floor((times.length - 1) / 2), 'middle']] : []), [times.length - 1, 'end']]) {
    svg.append(svgNode('text', {x: x(index), y: height - 6, 'text-anchor': anchor, fill: '#74829a', 'font-size': 9}, date(times[index]).slice(width < 520 ? 5 : 0)));
  }
  const lookup = new Map(times.map((time, index) => [time, index]));
  markers.forEach(trade => {
    const index = lookup.get(trade.entry_time);
    if (index == null || series[0].values[index] == null) return;
    const marker = svgNode('circle', {cx: x(index), cy: y(series[0].values[index]), r: trade === selectedTrade ? 5 : 3, fill: trade.is_long ? '#178263' : '#bd5360', stroke: 'white', 'stroke-width': 1});
    marker.append(svgNode('title', {}, `${trade.is_long ? 'Long' : 'Short'} · ${date(trade.entry_time)} · Net P&L ${number(trade.net_pnl)}`));
    svg.append(marker);
  });
  if (selectedTrade) {
    for (const [key, label] of [['entry_time', 'Entry'], ['exit_time', 'Exit']]) {
      const index = lookup.get(selectedTrade[key]);
      if (index == null) continue;
      svg.append(svgNode('line', {x1: x(index), x2: x(index), y1: top, y2: height - bottom, stroke: '#3459c7', 'stroke-dasharray': '4 3'}));
      svg.append(svgNode('text', {x: Math.min(width - 40, x(index) + 4), y: top + 10, fill: '#3459c7', 'font-size': 10}, label));
    }
  }
  const guide = svgNode('line', {x1: left, x2: left, y1: top, y2: height - bottom, stroke: '#a5b2c8', visibility: 'hidden'});
  svg.append(guide);
  let current = 0;
  function inspect(index) {
    current = Math.max(0, Math.min(times.length - 1, index));
    guide.setAttribute('x1', x(current)); guide.setAttribute('x2', x(current)); guide.setAttribute('visibility', 'visible');
    onInspect(`${date(times[current])} · ${series.map(line => `${line.name}: ${number(line.values[current], digits)}`).join(' · ')}`);
  }
  svg.addEventListener('pointermove', event => {
    const rect = svg.getBoundingClientRect(), sx = (event.clientX - rect.left) * width / rect.width;
    inspect(Math.round((sx - left) / (width - left - right) * (times.length - 1)));
  });
  svg.addEventListener('pointerleave', () => guide.setAttribute('visibility', 'hidden'));
  svg.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const step = event.shiftKey ? 10 : 1;
    inspect(event.key === 'Home' ? 0 : event.key === 'End' ? times.length - 1 : current + (event.key === 'ArrowLeft' ? -step : step));
  });
  container.replaceChildren(svg);
}
