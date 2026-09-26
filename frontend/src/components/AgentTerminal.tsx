import { useEffect, useRef } from "react";
import { Terminal, Cpu, CheckCircle, AlertTriangle, Sparkles } from "lucide-react";
import type { AgentStepEvent } from "../types";

interface Props {
  events: AgentStepEvent[];
  currentScore: number;
  currentIteration: number;
  isRunning: boolean;
  isConverged?: boolean;
}

export const AgentTerminal: React.FC<Props> = ({
  events,
  currentScore,
  currentIteration,
  isRunning,
  isConverged = false,
}) => {
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950 overflow-hidden shadow-2xl flex flex-col h-[520px]">
      {/* ターミナルヘッダー */}
      <div className="bg-slate-900 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <span className="w-3 h-3 rounded-full bg-rose-500/80 inline-block"></span>
            <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block"></span>
            <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block"></span>
          </div>
          <div className="h-4 w-px bg-slate-700 mx-1"></div>
          <div className="flex items-center gap-1.5 text-xs font-mono text-slate-300">
            <Terminal className="w-3.5 h-3.5 text-pink-400" />
            <span>BeautyGoalAgent :: OODA Autonomous Loop</span>
          </div>
        </div>

        {/* スコアインジケーター */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-mono">Loop:</span>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-200 font-mono font-bold">
              #{currentIteration || 1} / 3
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-mono">Goal Score:</span>
            <div className="flex items-center gap-1.5 bg-slate-800/80 px-2.5 py-1 rounded-lg border border-slate-700">
              <span
                className={`text-sm font-bold font-mono ${
                  currentScore >= 85 || isConverged
                    ? "text-emerald-400"
                    : currentScore > 0
                    ? "text-pink-400"
                    : "text-slate-400"
                }`}
              >
                {currentScore}%
              </span>
              <span className="text-[10px] text-slate-400">(目標: 85%以上)</span>
            </div>
          </div>
        </div>
      </div>

      {/* ターミナル本体ログストリーム */}
      <div className="flex-1 p-4 overflow-y-auto font-mono text-xs space-y-3.5">
        {events.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-2">
            <Cpu className="w-8 h-8 text-slate-600 animate-pulse" />
            <p>写真を選択して「エージェント最適化を開始」を押すと、OODA推論ループが始まります。</p>
          </div>
        )}

        {events.map((ev, idx) => {
          if (ev.type === "step") {
            return (
              <div key={idx} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1.5">
                <div className="flex items-center gap-2 text-pink-400 font-semibold">
                  <span className="px-1.5 py-0.5 rounded bg-pink-500/20 text-[10px] uppercase">
                    {ev.step_name}
                  </span>
                  <span>{ev.title}</span>
                </div>
                {ev.thought && (
                  <p className="text-slate-300 leading-relaxed pl-2 border-l-2 border-slate-700">
                    <span className="text-slate-500">Thought: </span>{ev.thought}
                  </p>
                )}
                {ev.action && (
                  <p className="text-cyan-400 pl-2">
                    <span className="text-slate-500">Action: </span>{ev.action}
                  </p>
                )}
              </div>
            );
          }

          if (ev.type === "observation") {
            return (
              <div key={idx} className="p-3 rounded-xl bg-slate-900/50 border border-slate-800/60 pl-4 border-l-cyan-500 text-slate-300 space-y-1">
                <div className="text-[11px] text-cyan-400 font-semibold">Observation:</div>
                <p className="leading-relaxed">{ev.observation}</p>
              </div>
            );
          }

          if (ev.type === "evaluation_result") {
            return (
              <div
                key={idx}
                className={`p-3.5 rounded-xl border ${
                  ev.score && ev.score >= 85
                    ? "bg-emerald-950/30 border-emerald-500/30 text-emerald-300"
                    : "bg-amber-950/20 border-amber-500/30 text-amber-300"
                } space-y-2`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4" />
                    Gemini 批評・達成度判定 (Critic Agent)
                  </span>
                  <span className="text-base font-extrabold font-mono">
                    Score: {ev.score}% {ev.score && ev.score >= 85 ? "🎉 GOAL達成" : "⚠️ 未達（Replan必要）"}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{ev.critic_feedback}</p>
              </div>
            );
          }

          if (ev.type === "converged") {
            return (
              <div key={idx} className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
                <span className="font-bold">{ev.message}</span>
              </div>
            );
          }

          if (ev.type === "circuit_breaker") {
            return (
              <div key={idx} className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                <span>{ev.message}</span>
              </div>
            );
          }

          if (ev.type === "status") {
            return (
              <div key={idx} className="text-slate-400 text-[11px] italic">
                &gt; {ev.message}
              </div>
            );
          }

          if (ev.type === "error") {
            return (
              <div key={idx} className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 space-y-1">
                <div className="font-bold flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4" />
                  ガバナンス検知 / エラー
                </div>
                <p>{ev.message}</p>
              </div>
            );
          }

          return null;
        })}

        {isRunning && (
          <div className="flex items-center gap-2 text-pink-400 text-xs py-2">
            <span className="w-2 h-2 rounded-full bg-pink-500 animate-ping"></span>
            <span>Agent 推論 &amp; MCP ツール呼び出し中...</span>
          </div>
        )}

        <div ref={terminalEndRef} />
      </div>
    </div>
  );
};
