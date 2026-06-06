import { useMemo } from 'react';

interface DataPoint {
  label: string;
  value: number;
}

type ChartInput = DataPoint[] | number[];

interface PerformanceChartProps {
  data: ChartInput;
  baseline?: number;
  height?: number;
  unit?: string;
  title?: string;
  description?: string;
  yLabel?: string;
  mode?: 'absolute' | 'return';
}

function generateSmoothPath(points: { x: number; y: number }[]): string {
  if (points.length === 0) return '';
  if (points.length === 1) return `M ${points[0].x},${points[0].y}`;
  let d = `M ${points[0].x},${points[0].y}`;
  for (let i = 1; i < points.length - 1; i++) {
    const p0 = points[i - 1];
    const p1 = points[i];
    const p2 = points[i + 1];
    const cp1x = p1.x - (p2.x - p0.x) * 0.15;
    const cp1y = p1.y - (p2.y - p0.y) * 0.15;
    const cp2x = p1.x + (p2.x - p0.x) * 0.15;
    const cp2y = p1.y + (p2.y - p0.y) * 0.15;
    d += ` C ${cp1x},${cp1y} ${cp2x},${cp2y} ${p2.x},${p2.y}`;
  }
  return d;
}

function intersectX(p1: { x: number; y: number }, p2: { x: number; y: number }, baselineY: number): number | null {
  if (p1.y === p2.y) return null;
  if ((p1.y < baselineY && p2.y < baselineY) || (p1.y > baselineY && p2.y > baselineY)) return null;
  const t = (baselineY - p1.y) / (p2.y - p1.y);
  if (t <= 0 || t >= 1) return null;
  return p1.x + t * (p2.x - p1.x);
}

export default function PerformanceChart({
  data, baseline, height = 240, unit = '', title, description, yLabel, mode = 'absolute',
}: PerformanceChartProps) {
  const normalized: DataPoint[] = Array.isArray(data) && data.length > 0
    ? typeof data[0] === 'number'
      ? (data as number[]).map((v, i) => ({ label: `P${i + 1}`, value: v }))
      : data as DataPoint[]
    : [];
  if (normalized.length < 2) return null;

  const firstVal = normalized[0].value;
  const bl = mode === 'return' ? 0 : (baseline ?? 0);

  const processed = useMemo(() => {
    return normalized.map((d) => {
      const v = mode === 'return' && firstVal !== 0
        ? ((d.value - firstVal) / firstVal) * 100
        : d.value;
      return { ...d, displayValue: v };
    });
  }, [normalized, mode, firstVal]);

  const values = processed.map(d => d.displayValue);

  const min = Math.min(...values, bl);
  const max = Math.max(...values, bl);
  const range = max - min || 1;
  const pad = range * 0.1;
  const chartMin = min - pad;
  const chartMax = max + pad;
  const chartRange = chartMax - chartMin;

  const WIDTH = 700;
  const padding = { top: 12, bottom: 28, left: 48, right: 16 };
  const plotW = WIDTH - padding.left - padding.right;
  const plotH = height - padding.top - padding.bottom;

  function xPos(i: number): number {
    return padding.left + (i / (normalized.length - 1 || 1)) * plotW;
  }

  function yPos(v: number): number {
    return padding.top + (1 - (v - chartMin) / chartRange) * plotH;
  }

  const baselineY = yPos(bl);
  const points = processed.map((d, i) => ({ x: xPos(i), y: yPos(d.displayValue), value: d.value, displayValue: d.displayValue, label: d.label }));

  const fillPoints = useMemo(() => {
    if (points.length < 2) return '';
    const firstX = points[0].x;
    const lastX = points[points.length - 1].x;
    const start = `M ${firstX},${baselineY}`;
    const segments: string[] = [];
    for (let i = 0; i < points.length - 1; i++) {
      const p1 = points[i];
      const p2 = points[i + 1];
      const xi = intersectX(p1, p2, baselineY);
      if (xi !== null) {
        segments.push(`L ${p1.x},${p1.y} L ${xi},${baselineY}`);
      } else {
        segments.push(`L ${p1.x},${p1.y}`);
      }
    }
    segments.push(`L ${lastX},${baselineY} Z`);
    return start + segments.join(' ');
  }, [points, baselineY]);

  const segmentsAbove: string[] = [];
  const segmentsBelow: string[] = [];

  for (let i = 0; i < points.length - 1; i++) {
    const p1 = points[i];
    const p2 = points[i + 1];
    const xi = intersectX(p1, p2, baselineY);

    if (xi === null) {
      const seg = `M ${p1.x},${p1.y} L ${p2.x},${p2.y}`;
      if (p1.y <= baselineY) segmentsAbove.push(seg);
      else segmentsBelow.push(seg);
    } else {
      const above1 = p1.y <= baselineY;
      const xa = xi;
      if (above1) {
        segmentsAbove.push(`M ${p1.x},${p1.y} L ${xa},${baselineY}`);
        segmentsBelow.push(`M ${xa},${baselineY} L ${p2.x},${p2.y}`);
      } else {
        segmentsBelow.push(`M ${p1.x},${p1.y} L ${xa},${baselineY}`);
        segmentsAbove.push(`M ${xa},${baselineY} L ${p2.x},${p2.y}`);
      }
    }
  }

  const yTicks = useMemo(() => {
    const ticks: number[] = [];
    const tickCount = 5;
    for (let i = 0; i <= tickCount; i++) {
      ticks.push(chartMin + (chartRange * i) / tickCount);
    }
    return ticks;
  }, [chartMin, chartRange]);

  const xLabels = useMemo(() => {
    const maxLabels = Math.min(normalized.length, 8);
    const step = Math.max(1, Math.floor((normalized.length - 1) / (maxLabels - 1)));
    const indices: number[] = [];
    for (let i = 0; i < normalized.length; i += step) indices.push(i);
    if (indices[indices.length - 1] !== normalized.length - 1) indices.push(normalized.length - 1);
    return indices.map(i => ({ index: i, label: normalized[i].label }));
  }, [normalized]);

  const lastDisplay = values[values.length - 1];
  const firstDisplay = values[0];
  const isUp = lastDisplay >= bl;
  const changeFromFirst = mode === 'return' ? lastDisplay : (firstVal !== 0 ? ((lastDisplay - firstDisplay) / Math.abs(firstDisplay)) * 100 : 0);

  function formatYVal(v: number): string {
    if (mode === 'return') {
      return `${v >= 0 ? '+' : ''}${v.toFixed(1)}%`;
    }
    const abs = Math.abs(v);
    if (abs >= 1_00_00_000) return `${unit}${(v / 1_00_00_000).toFixed(1)}Cr`;
    if (abs >= 1_00_000) return `${unit}${(v / 1_00_000).toFixed(1)}L`;
    if (abs >= 1_000) return `${unit}${(v / 1_000).toFixed(1)}k`;
    return `${unit}${Math.round(v).toLocaleString()}`;
  }

  return (
    <div className="bg-surface-50 border border-surface-300/40 rounded-lg p-4">
      {(title || description) && (
        <div className="mb-3">
          {title && <p className="text-[13px] font-semibold text-surface-white">{title}</p>}
          {description && <p className="text-[11px] text-surface-700">{description}</p>}
        </div>
      )}

      <div className="flex items-center gap-4 mb-3 text-[11px]">
        <div className="flex items-center gap-1.5">
          <span className="text-surface-600">Start:</span>
          <span className="font-semibold text-surface-white">{unit}{firstVal.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-surface-600">Current:</span>
          <span className={`font-semibold ${isUp ? 'text-success' : 'text-danger'}`}>
            {unit}{normalized[normalized.length - 1].value.toLocaleString()}
          </span>
        </div>
        <div className={`flex items-center gap-1 font-semibold ${isUp ? 'text-success' : 'text-danger'}`}>
          {isUp ? '▲' : '▼'} {Math.abs(changeFromFirst).toFixed(1)}%
        </div>
      </div>

      <svg
        viewBox={`0 0 ${WIDTH} ${height}`}
        className="w-full h-auto"
        preserveAspectRatio="xMidYMid meet"
        role="img"
        aria-label={title || 'Performance chart'}
      >
        <defs>
          <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#38bdf8" stopOpacity="0.04" />
          </linearGradient>
        </defs>

        {yTicks.map((tick, i) => (
          <g key={i}>
            <line
              x1={padding.left} y1={yPos(tick)}
              x2={WIDTH - padding.right} y2={yPos(tick)}
              stroke="currentColor"
              className="text-surface-300/40"
              strokeWidth="1"
            />
            <text
              x={padding.left - 6} y={yPos(tick) + 3}
              textAnchor="end"
              className="fill-surface-600"
              fontSize="9"
              fontFamily="inherit"
            >
              {formatYVal(tick)}
            </text>
          </g>
        ))}

        {/* Baseline */}
        <line
          x1={padding.left} y1={baselineY}
          x2={WIDTH - padding.right} y2={baselineY}
          stroke="currentColor"
          className="text-surface-500"
          strokeWidth="1"
          strokeDasharray="4,3"
        />
        <text
          x={WIDTH - padding.right + 4} y={baselineY + 3}
          className="fill-surface-500"
          fontSize="8"
          fontFamily="inherit"
        >
          {mode === 'return' ? '0% (Start)' : (yLabel || 'Baseline')}
        </text>

        {/* Gradient fill area */}
        {fillPoints && (
          <path
            d={fillPoints}
            fill="url(#areaGrad)"
            className="transition-all duration-300"
          />
        )}

        {/* Line segments above baseline (green) */}
        {segmentsAbove.map((seg, i) => (
          <path
            key={`above-${i}`}
            d={seg}
            fill="none"
            stroke="#22c55e"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="transition-all duration-300"
          />
        ))}

        {/* Line segments below baseline (red) */}
        {segmentsBelow.map((seg, i) => (
          <path
            key={`below-${i}`}
            d={seg}
            fill="none"
            stroke="#ef4444"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="transition-all duration-300"
          />
        ))}

        {/* Data point dots */}
        {points.map((p, i) => (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r="2.5"
            className={`stroke-surface-100 stroke-[1.5] ${p.y <= baselineY ? 'fill-success' : 'fill-danger'}`}
          />
        ))}

        {/* X-axis labels */}
        {xLabels.map(({ index, label }) => (
          <text
            key={index}
            x={xPos(index)}
            y={height - 4}
            textAnchor="middle"
            className="fill-surface-600"
            fontSize="8"
            fontFamily="inherit"
          >
            {label}
          </text>
        ))}
      </svg>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-2 text-[10px] text-surface-600">
        <span className="inline-flex items-center gap-1">
          <span className="w-3 h-0.5 rounded bg-success" />
          Above baseline
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="w-3 h-0.5 rounded bg-danger" />
          Below baseline
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="w-3 h-2 rounded-sm opacity-30" style={{ backgroundColor: '#38bdf8' }} />
          Area fill
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="w-3 h-px border-t border-dashed" style={{ borderColor: 'currentColor' }} />
          {mode === 'return' ? '0% Return' : (yLabel || 'Baseline')}
        </span>
      </div>
    </div>
  );
}
