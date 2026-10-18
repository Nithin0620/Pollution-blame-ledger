interface SliderProps {
  label: string;
  value: number;
  onChange: (val: number) => void;
  color: string;
  min?: number;
  max?: number;
  step?: number;
}

export function Slider({
  label,
  value,
  onChange,
  color,
  min = 0,
  max = 100,
  step = 5,
}: SliderProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs">
        <span className="font-bold text-slate-800">{label}</span>
        <span
          className="font-extrabold px-2 py-0.5 rounded-md text-white transition-all text-[11px]"
          style={{ backgroundColor: value > 0 ? color : '#94a3b8' }}
        >
          {value > 0 ? `−${value}%` : '0%'}
        </span>
      </div>
      <div className="relative flex items-center">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={e => onChange(Number(e.target.value))}
          className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400"
          style={{
            accentColor: color,
          }}
        />
      </div>
    </div>
  );
}
