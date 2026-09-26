import { Sparkles, Smile, Eye, Award, Heart } from "lucide-react";
import type { GoalOption } from "../types";

export const GOAL_PRESETS: GoalOption[] = [
  {
    id: "midface_shortening",
    name: "中顔面短縮",
    tagline: "代表ユースケース",
    description: "チークの重心を下げ、上唇オーバーリップと下瞼シャドウで縦の余白を錯視短縮。",
    recommended: true,
  },
  {
    id: "small_face",
    name: "小顔に見せたい",
    tagline: "フェイスライン補正",
    description: "顔周りのレイヤーと外側シェーディングの錯視効果で余白をすっきり整える。",
  },
  {
    id: "vertical_eyes",
    name: "目を縦に大きく",
    tagline: "アイメイク重心操作",
    description: "涙袋ハイライトと黒目上下のポイントカラーで縦幅を強調。",
  },
  {
    id: "mature_chic",
    name: "大人っぽく見せたい",
    tagline: "洗練エレガント",
    description: "直線的な眉と深みのあるリップトーンで知的な立体感を演出。",
  },
  {
    id: "soft_glow",
    name: "やわらかく見せたい",
    tagline: "ふんわり多幸感",
    description: "アーチ眉とまろやかなコーラルチークで丸みと親しみやすさを強調。",
  },
];

interface Props {
  selectedGoal: string;
  onSelectGoal: (goalId: string) => void;
  disabled?: boolean;
}

export const GoalSelector: React.FC<Props> = ({
  selectedGoal,
  onSelectGoal,
  disabled,
}) => {
  const getIcon = (id: string) => {
    switch (id) {
      case "midface_shortening":
        return <Sparkles className="w-4 h-4 text-pink-400" />;
      case "small_face":
        return <Smile className="w-4 h-4 text-amber-400" />;
      case "vertical_eyes":
        return <Eye className="w-4 h-4 text-cyan-400" />;
      case "mature_chic":
        return <Award className="w-4 h-4 text-purple-400" />;
      case "soft_glow":
        return <Heart className="w-4 h-4 text-rose-400" />;
      default:
        return <Sparkles className="w-4 h-4 text-pink-400" />;
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold text-slate-200 flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-pink-500"></span>
          なりたい顔の Goal（美容目標）を選択
        </label>
        <span className="text-xs text-slate-400">※他者採点ではなく、あなた自身の目標</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
        {GOAL_PRESETS.map((goal) => {
          const isSelected = selectedGoal === goal.id;
          return (
            <button
              key={goal.id}
              type="button"
              disabled={disabled}
              onClick={() => onSelectGoal(goal.id)}
              className={`text-left p-3.5 rounded-xl border transition-all relative overflow-hidden ${
                isSelected
                  ? "bg-pink-500/10 border-pink-500 shadow-md shadow-pink-500/10"
                  : "bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-800/40"
              } ${disabled ? "opacity-60 cursor-not-allowed" : "cursor-pointer"}`}
            >
              {goal.recommended && (
                <span className="absolute top-2 right-2 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-pink-500 text-white">
                  推奨
                </span>
              )}
              <div className="flex items-center gap-2 mb-1.5">
                <div className="p-1.5 rounded-lg bg-slate-800/80 border border-slate-700">
                  {getIcon(goal.id)}
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white flex items-center gap-1">
                    {goal.name}
                  </h4>
                  <span className="text-[11px] text-pink-400 font-medium">{goal.tagline}</span>
                </div>
              </div>
              <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                {goal.description}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
};
