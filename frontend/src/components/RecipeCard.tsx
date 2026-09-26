import { useState } from "react";
import { BookOpen, Check, Copy, Sparkles } from "lucide-react";
import type { MakeupRecipeItem } from "../types";

interface Props {
  recipes: MakeupRecipeItem[];
  goalTitle: string;
}

export const RecipeCard: React.FC<Props> = ({ recipes, goalTitle }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const text = recipes
      .map(
        (r) =>
          `【${r.category}】\n手法: ${r.action}\n手順: ${r.instruction}\n効果: ${r.effect}`
      )
      .join("\n\n");

    navigator.clipboard.writeText(
      `💄 Beauty Goal Agent - ${goalTitle} 再現レシピ\n\n` + text
    );
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 space-y-4 shadow-xl">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-pink-500/10 text-pink-400 border border-pink-500/20">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-1.5">
              明日の朝、自分で再現できる最適化レシピ
            </h3>
            <p className="text-xs text-slate-400">
              骨格は変えず、メイクと前髪の錯視だけでゴールを達成する具体的ステップ
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors border border-slate-700 cursor-pointer"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400">コピー完了</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5 text-slate-400" />
              <span>レシピをコピー</span>
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {recipes.map((recipe, idx) => (
          <div
            key={idx}
            className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2 hover:border-slate-700 transition-colors"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-pink-400 bg-pink-500/10 px-2 py-0.5 rounded-md border border-pink-500/20">
                {recipe.category}
              </span>
              <span className="text-[11px] text-slate-400 font-mono">Step #{idx + 1}</span>
            </div>

            <h4 className="text-sm font-semibold text-white">
              {recipe.action}
            </h4>

            <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/40">
              {recipe.instruction}
            </p>

            <div className="flex items-start gap-1.5 text-[11px] text-emerald-400/90 pt-1">
              <Sparkles className="w-3.5 h-3.5 shrink-0 mt-0.5" />
              <span>{recipe.effect}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
