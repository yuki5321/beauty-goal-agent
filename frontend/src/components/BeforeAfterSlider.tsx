import { useState, useRef, useCallback, type TouchEvent, type MouseEvent } from "react";
import { Sparkles, ArrowLeftRight } from "lucide-react";

interface Props {
  beforeImage: string;
  afterImage: string;
  score?: number;
}

export const BeforeAfterSlider = ({
  beforeImage,
  afterImage,
  score = 88,
}: Props) => {
  const [sliderPos, setSliderPos] = useState<number>(50);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMove = useCallback(
    (clientX: number) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = clientX - rect.left;
      const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
      setSliderPos(percentage);
    },
    []
  );

  const handleTouchMove = (e: TouchEvent) => {
    handleMove(e.touches[0].clientX);
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging) return;
    handleMove(e.clientX);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold text-slate-200 flex items-center gap-1.5">
          <Sparkles className="w-4 h-4 text-pink-400" />
          Before / After 錯視シミュレーション比較
        </label>
        <div className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
          達成率: {score}% (Goal基準達成)
        </div>
      </div>

      <div
        ref={containerRef}
        onMouseDown={() => setIsDragging(true)}
        onMouseUp={() => setIsDragging(false)}
        onMouseLeave={() => setIsDragging(false)}
        onMouseMove={handleMouseMove}
        onTouchMove={handleTouchMove}
        className="relative w-full aspect-square max-w-[480px] mx-auto rounded-2xl overflow-hidden border-2 border-slate-700 shadow-2xl select-none cursor-ew-resize group"
      >
        {/* After画像 (右側/背景) */}
        <img
          src={afterImage}
          alt="After: エージェント最適化"
          className="absolute inset-0 w-full h-full object-cover pointer-events-none"
        />

        {/* Before画像 (左側/クリップ) */}
        <div
          className="absolute inset-0 overflow-hidden pointer-events-none"
          style={{ width: `${sliderPos}%` }}
        >
          <img
            src={beforeImage}
            alt="Before: 元画像"
            className="absolute inset-0 w-full h-full object-cover max-w-none pointer-events-none"
            style={{ width: containerRef.current?.offsetWidth || "100%", height: "100%" }}
          />
        </div>

        {/* スライダー仕切り線 */}
        <div
          className="absolute top-0 bottom-0 w-1 bg-white shadow-[0_0_10px_rgba(0,0,0,0.5)] z-20 pointer-events-none"
          style={{ left: `${sliderPos}%` }}
        >
          {/* 中央ハンドルノブ */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-white text-slate-900 shadow-lg flex items-center justify-center font-bold text-xs pointer-events-auto cursor-ew-resize">
            <ArrowLeftRight className="w-4 h-4" />
          </div>
        </div>

        {/* ラベル表示 */}
        <div className="absolute top-3 left-3 px-2.5 py-1 rounded-lg bg-black/60 backdrop-blur-md text-white text-[11px] font-bold z-10 pointer-events-none border border-white/10">
          BEFORE
        </div>
        <div className="absolute top-3 right-3 px-2.5 py-1 rounded-lg bg-pink-600/80 backdrop-blur-md text-white text-[11px] font-bold z-10 pointer-events-none border border-pink-400/30">
          AFTER (錯視補正済)
        </div>

        {/* 操作ガイドヒント */}
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-black/60 backdrop-blur-md text-slate-300 text-[10px] pointer-events-none border border-white/10">
          スライダーを左右にドラッグして比較
        </div>
      </div>
    </div>
  );
};
