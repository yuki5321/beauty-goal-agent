import { useState } from "react";
import { MessageSquarePlus, Send, Sparkles, Wand2 } from "lucide-react";
import type { StylingPlan } from "../types";

interface Props {
  currentPlan: StylingPlan | null;
  isRunning: boolean;
  onSubmitFeedback: (feedback: string) => void;
}

export const InteractiveFeedbackChat = ({
  currentPlan,
  isRunning,
  onSubmitFeedback,
}: Props) => {
  const [feedbackInput, setFeedbackInput] = useState("");

  const quickPresets = [
    "リップをもう少しナチュラルに落ち着かせたい",
    "前髪なし（額出し）のバランスも試したい",
    "涙袋のラメ・影をさらに強調したい",
    "チークを少し高めにして大人っぽさをプラスしたい",
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!feedbackInput.trim() || isRunning) return;
    onSubmitFeedback(feedbackInput.trim());
    setFeedbackInput("");
  };

  const handleQuickClick = (text: string) => {
    if (isRunning) return;
    onSubmitFeedback(text);
  };

  if (!currentPlan) return null;

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-4 shadow-xl">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <MessageSquarePlus className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              エージェントと対話して微調整する
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-mono">
                Human-in-the-Loop Replan
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              「もう少しリップを薄く」「前髪なしも試したい」など、あなたのこだわりを伝えるとAIが自律的に再調整します
            </p>
          </div>
        </div>
      </div>

      {/* クイックサジェストボタン */}
      <div className="space-y-1.5">
        <span className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
          <Wand2 className="w-3 h-3 text-pink-400" />
          よくある追加リクエスト（ワンクリックで試せます）:
        </span>
        <div className="flex flex-wrap gap-2">
          {quickPresets.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              disabled={isRunning}
              onClick={() => handleQuickClick(preset)}
              className="text-xs px-3 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-300 hover:text-white transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {preset}
            </button>
          ))}
        </div>
      </div>

      {/* 入力フォーム */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={feedbackInput}
          onChange={(e) => setFeedbackInput(e.target.value)}
          placeholder="例: チークをもっと自然なコーラルにして、前髪はシースルーバングのままで"
          disabled={isRunning}
          className="flex-1 px-4 py-3 rounded-xl bg-slate-950 border border-slate-700 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-pink-500 transition-colors"
        />
        <button
          type="submit"
          disabled={isRunning || !feedbackInput.trim()}
          className="px-5 py-3 rounded-xl bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-400 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-bold flex items-center gap-1.5 transition-all shadow-md shadow-pink-500/20 cursor-pointer"
        >
          {isRunning ? (
            <>
              <Sparkles className="w-3.5 h-3.5 animate-spin" />
              <span>再調整中...</span>
            </>
          ) : (
            <>
              <Send className="w-3.5 h-3.5" />
              <span>AIに依頼</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};
