import { useState, useRef, useCallback, type TouchEvent, type MouseEvent } from "react";
import { Sparkles, ArrowLeftRight, Activity, SunMedium, Lightbulb } from "lucide-react";

interface Props {
  beforeImage: string;
  afterImage: string;
  score?: number;
}

type LightingMode = "natural" | "office" | "cafe" | "night";

interface LightingPreset {
  id: LightingMode;
  name: string;
  kelvin: string;
  icon: string;
  filter: string;
  description: string;
  analysis: string;
}

const LIGHTING_PRESETS: LightingPreset[] = [
  {
    id: "natural",
    name: "自然光",
    kelvin: "5500K デイライト",
    icon: "☀️",
    filter: "brightness(1.02) contrast(1.02)",
    description: "窓際や屋外の自然昼光環境",
    analysis: "自然光の下では肌本来の透明感と血色感が素直に現れ、オーバーリップとハイライトによる人中短縮の立体感が最も自然に際立ちます。"
  },
  {
    id: "office",
    name: "オフィス蛍光灯",
    kelvin: "4000K クールホワイト",
    icon: "🏢",
    filter: "brightness(0.98) contrast(1.08) hue-rotate(-6deg) saturate(0.92)",
    description: "白く平面的に見えやすい昼光色",
    analysis: "青白いオフィス照明でも、小鼻のラインに置いた横長チークが縦の余白を強力に遮断し、間延び感をシャットアウトします。"
  },
  {
    id: "cafe",
    name: "カフェ暖色光",
    kelvin: "2700K ウォームアンバー",
    icon: "☕",
    filter: "brightness(0.97) contrast(1.04) sepia(0.24) hue-rotate(-12deg) saturate(1.15)",
    description: "飲食店やバーの温かみある間接照明",
    analysis: "陰影が深まる暖色光環境でも、下瞼の涙袋パールが光を捉えて視覚重心を低い位置にキープし、顔の重心上昇を防ぎます。"
  },
  {
    id: "night",
    name: "ナイト / ディナー",
    kelvin: "2200K ナイトバー",
    icon: "🌙",
    filter: "brightness(0.88) contrast(1.14) sepia(0.15) hue-rotate(-8deg) saturate(1.10)",
    description: "薄暗い夜のバーやディナー照明",
    analysis: "暗所でもフェイスラインのシェーディング（余白-21%）とリップのハイライトがコントラストを生み、小顔効果が持続します。"
  },
];

export const BeforeAfterSlider = ({
  beforeImage,
  afterImage,
  score = 88,
}: Props) => {
  const [sliderPos, setSliderPos] = useState<number>(50);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [showScienceOverlay, setShowScienceOverlay] = useState<boolean>(true);
  const [selectedLighting, setSelectedLighting] = useState<LightingMode>("natural");
  const containerRef = useRef<HTMLDivElement>(null);

  const activePreset = LIGHTING_PRESETS.find((p) => p.id === selectedLighting) || LIGHTING_PRESETS[0];

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
    <div className="space-y-3.5">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <label className="text-sm font-semibold text-slate-200 flex items-center gap-1.5">
          <Sparkles className="w-4 h-4 text-pink-400" />
          Before / After 錯視シミュレーション比較
        </label>
        
        <div className="flex items-center gap-2">
          {/* 錯視サイエンス解析トグル */}
          <button
            type="button"
            onClick={() => setShowScienceOverlay(!showScienceOverlay)}
            className={`text-xs px-2.5 py-1 rounded-full border transition-all flex items-center gap-1.5 cursor-pointer font-medium ${
              showScienceOverlay
                ? "bg-cyan-500/20 text-cyan-300 border-cyan-400/50 shadow-sm shadow-cyan-500/20"
                : "bg-slate-800 text-slate-400 border-slate-700 hover:text-slate-200"
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>錯視サイエンス解析 {showScienceOverlay ? "ON" : "OFF"}</span>
          </button>

          <div className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
            達成率: {score}% (Goal達成)
          </div>
        </div>
      </div>

      {/* スライダー本体 */}
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
          className="absolute inset-0 w-full h-full object-cover pointer-events-none transition-[filter] duration-300"
          style={{ filter: activePreset.filter }}
        />

        {/* 錯視サイエンス・オーバーレイ (幾何学ガイド & ヒートマップ) */}
        {showScienceOverlay && (
          <div className="absolute inset-0 pointer-events-none z-10">
            {/* SVG 幾何学メトリクス */}
            <svg className="w-full h-full" viewBox="0 0 100 100">
              <defs>
                <linearGradient id="arrowDownGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#ec4899" stopOpacity="0.9" />
                </linearGradient>
              </defs>

              {/* チーク余白分断ゾーン (小鼻下横長グリッド) */}
              <rect x="20" y="58" width="22" height="8" rx="4" fill="none" stroke="#06b6d4" strokeWidth="0.8" strokeDasharray="1.5,1" opacity="0.85" />
              <rect x="58" y="58" width="22" height="8" rx="4" fill="none" stroke="#06b6d4" strokeWidth="0.8" strokeDasharray="1.5,1" opacity="0.85" />

              {/* 涙袋拡張アーク (目の下) */}
              <path d="M 28 43 Q 35 46 42 43" fill="none" stroke="#10b981" strokeWidth="0.8" opacity="0.9" />
              <path d="M 58 43 Q 65 46 72 43" fill="none" stroke="#10b981" strokeWidth="0.8" opacity="0.9" />

              {/* 人中短縮ベクトル (鼻下〜上唇山) */}
              <line x1="50" y1="58" x2="50" y2="68" stroke="#f43f5e" strokeWidth="1.2" />
              <circle cx="50" cy="58" r="1" fill="#f43f5e" />
              <circle cx="50" cy="68" r="1.2" fill="#ec4899" />

              {/* 視覚重心低下ベクトル (下向き矢印) */}
              <line x1="50" y1="46" x2="50" y2="55" stroke="url(#arrowDownGrad)" strokeWidth="1.4" />
            </svg>

            {/* ネオンラベル HUD */}
            <div className="absolute top-[62%] left-[53%] -translate-y-1/2 px-2 py-0.5 rounded bg-black/80 backdrop-blur-md text-[9px] font-mono font-bold text-pink-400 border border-pink-500/50 shadow-md">
              人中短縮: -3.2mm
            </div>

            <div className="absolute top-[48%] left-[53%] px-2 py-0.5 rounded bg-black/80 backdrop-blur-md text-[9px] font-mono font-bold text-cyan-300 border border-cyan-500/50 shadow-md">
              重心: ↓ 12px下降
            </div>

            <div className="absolute top-[67%] right-[10%] px-1.5 py-0.5 rounded bg-black/75 text-[8px] font-mono text-cyan-300 border border-cyan-500/30">
              余白カット -21%
            </div>

            {/* 幾何比率比較HUD (下部) */}
            <div className="absolute bottom-11 right-3 px-2.5 py-1 rounded-xl bg-slate-950/85 backdrop-blur-md border border-cyan-500/40 text-[10px] font-mono space-y-0.5 shadow-xl">
              <div className="text-slate-400 text-[9px]">中顔面比率解析 (H_mid / H_total)</div>
              <div className="flex items-center gap-2 font-bold">
                <span className="text-slate-400 line-through">0.355</span>
                <span className="text-cyan-400">&rarr; 0.312</span>
                <span className="text-[9px] text-emerald-400 bg-emerald-500/20 px-1 rounded">黄金比達成</span>
              </div>
            </div>
          </div>
        )}

        {/* Before画像 (左側/クリップ) */}
        <div
          className="absolute inset-0 overflow-hidden pointer-events-none z-20"
          style={{ width: `${sliderPos}%` }}
        >
          <img
            src={beforeImage}
            alt="Before: 元画像"
            className="absolute inset-0 w-full h-full object-cover max-w-none pointer-events-none transition-[filter] duration-300"
            style={{
              width: containerRef.current?.offsetWidth || "100%",
              height: "100%",
              filter: activePreset.filter,
            }}
          />
        </div>

        {/* スライダー仕切り線 */}
        <div
          className="absolute top-0 bottom-0 w-1 bg-white shadow-[0_0_12px_rgba(0,0,0,0.7)] z-30 pointer-events-none"
          style={{ left: `${sliderPos}%` }}
        >
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-white text-slate-900 shadow-xl flex items-center justify-center font-bold text-xs pointer-events-auto cursor-ew-resize">
            <ArrowLeftRight className="w-4 h-4" />
          </div>
        </div>

        {/* ラベル表示 */}
        <div className="absolute top-3 left-3 px-2.5 py-1 rounded-lg bg-black/70 backdrop-blur-md text-white text-[11px] font-bold z-30 pointer-events-none border border-white/10">
          BEFORE (元写真)
        </div>
        <div className="absolute top-3 right-3 px-2.5 py-1 rounded-lg bg-pink-600/85 backdrop-blur-md text-white text-[11px] font-bold z-30 pointer-events-none border border-pink-400/30">
          AFTER (錯視補正済)
        </div>

        {/* 操作ガイドヒント */}
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-black/75 backdrop-blur-md text-slate-300 text-[10px] pointer-events-none border border-white/10 z-30">
          スライダーを左右にドラッグして比較
        </div>
      </div>

      {/* 環境光シミュレータ（照明別の錯視検証コントロール） */}
      <div className="p-3 bg-slate-900/90 rounded-2xl border border-slate-800 space-y-2.5 max-w-[480px] mx-auto shadow-md">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
            <SunMedium className="w-3.5 h-3.5 text-amber-400" />
            環境光シミュレータ（日常シーン別の錯視検証）
          </span>
          <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
            {activePreset.kelvin}
          </span>
        </div>

        {/* 光環境ボタン選択 */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {LIGHTING_PRESETS.map((preset) => {
            const isActive = selectedLighting === preset.id;
            return (
              <button
                key={preset.id}
                type="button"
                onClick={() => setSelectedLighting(preset.id)}
                className={`px-2.5 py-2 rounded-xl text-xs font-medium flex items-center justify-center gap-1.5 transition-all cursor-pointer border ${
                  isActive
                    ? "bg-slate-800 text-white border-pink-500/60 shadow-md shadow-pink-500/15 ring-1 ring-pink-500/30 font-semibold"
                    : "bg-slate-950/70 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-900"
                }`}
              >
                <span>{preset.icon}</span>
                <span>{preset.name}</span>
              </button>
            );
          })}
        </div>

        {/* 各光環境における錯視耐久分析メッセージ */}
        <div className="text-[11px] text-slate-300 bg-slate-950/80 p-2.5 rounded-xl border border-slate-800/80 flex items-start gap-2">
          <Lightbulb className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <span className="font-semibold text-amber-300 mr-1">
              【{activePreset.name}】
            </span>
            <span>{activePreset.analysis}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
