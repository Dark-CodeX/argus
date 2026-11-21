import { useRef, useState } from "react";
import { fmtNum } from "./ui";

/* Hand-drawn SVG line chart. points = [{ label, value }] */
export function LineChart({ points, format = (v) => fmtNum(v, 2) }) {
  const ref = useRef(null);
  const [hover, setHover] = useState(null);

  if (points.length < 2) return <p className="muted">Not enough data points to draw a chart.</p>;

  const W = 860, H = 300, L = 64, R = 18, T = 18, B = 30;
  const values = points.map((p) => p.value);
  let min = Math.min(...values);
  let max = Math.max(...values);
  const pad = (max - min || 1) * 0.08;
  min -= pad;
  max += pad;

  const x = (i) => L + (i / (points.length - 1)) * (W - L - R);
  const y = (v) => T + (1 - (v - min) / (max - min)) * (H - T - B);

  const line = points.map((p, i) => `${i ? "L" : "M"}${x(i).toFixed(1)} ${y(p.value).toFixed(1)}`).join(" ");
  const area = `${line} L${x(points.length - 1)} ${H - B} L${x(0)} ${H - B} Z`;
  const ticks = [0, 1, 2, 3].map((k) => min + (k / 3) * (max - min));

  const onMove = (e) => {
    const r = ref.current.getBoundingClientRect();
    const px = ((e.clientX - r.left) / r.width) * W;
    const i = Math.round(((px - L) / (W - L - R)) * (points.length - 1));
    setHover(Math.max(0, Math.min(points.length - 1, i)));
  };

  const h = hover != null ? points[hover] : null;

  return (
    <svg
      ref={ref}
      className="chart"
      viewBox={`0 0 ${W} ${H}`}
      onMouseMove={onMove}
      onMouseLeave={() => setHover(null)}
      role="img"
      aria-label="Price chart"
    >
      {ticks.map((t) => (
        <g key={t}>
          <line className="grid" x1={L} x2={W - R} y1={y(t)} y2={y(t)} />
          <text x={L - 8} y={y(t) + 4} textAnchor="end">{format(t)}</text>
        </g>
      ))}
      <path className="area" d={area} />
      <path className="line" d={line} />
      <text x={L} y={H - 8}>{points[0].label}</text>
      <text x={W - R} y={H - 8} textAnchor="end">{points[points.length - 1].label}</text>
      {h && (
        <g>
          <line className="cross" x1={x(hover)} x2={x(hover)} y1={T} y2={H - B} />
          <circle className="dot" cx={x(hover)} cy={y(h.value)} r="4" />
          <text
            className="tip"
            x={x(hover)}
            y={T + 10}
            textAnchor={x(hover) > W / 2 ? "end" : "start"}
            dx={x(hover) > W / 2 ? -8 : 8}
          >
            {h.label} · {format(h.value)}
          </text>
        </g>
      )}
    </svg>
  );
}

/* Horizontal bars. items = [{ label, value, text }] — width is scaled to the largest |value|. */
export function BarList({ items }) {
  const max = Math.max(...items.map((i) => Math.abs(i.value)), 1e-12);
  return (
    <div className="bars">
      {items.map((i) => (
        <div className="bar-row" key={i.label}>
          <span>{i.label}</span>
          <div className="bar-track">
            <div
              className={`bar-fill ${i.value < 0 ? "neg" : ""}`}
              style={{ width: `${(Math.abs(i.value) / max) * 100}%` }}
            />
          </div>
          <span className="num">{i.text}</span>
        </div>
      ))}
    </div>
  );
}

/* Range bar: shows where outcomes fall between min and max, with a highlighted p5–p95 core. */
export function RangeBar({ min, max, low, high, median, start, format }) {
  const pos = (v) => `${((v - min) / (max - min || 1)) * 100}%`;
  return (
    <div>
      <div className="range">
        <div className="range-core" style={{ left: pos(low), width: `calc(${pos(high)} - ${pos(low)})` }} />
        <div className="range-mark" style={{ left: pos(median) }}><span>median</span></div>
        <div className="range-mark start" style={{ left: pos(start) }}><span>today</span></div>
      </div>
      <div className="range-ends">
        <span>Worst {format(min)}</span>
        <span>Best {format(max)}</span>
      </div>
    </div>
  );
}
