import { useState } from "react";
import { Header } from "./components/Header";
import { GoalSelector, GOAL_PRESETS } from "./components/GoalSelector";
import { PhotoUploader } from "./components/PhotoUploader";
import { AgentTerminal } from "./components/AgentTerminal";
import { BeforeAfterSlider } from "./components/BeforeAfterSlider";
import { RecipeCard } from "./components/RecipeCard";
import { GovernanceModal } from "./components/GovernanceModal";
import { InteractiveFeedbackChat } from "./components/InteractiveFeedbackChat";
import type { AgentStepEvent, MakeupRecipeItem, GovernanceAuditCertificate, StylingPlan } from "./types";
import { Play, RotateCcw, Sparkles, ShieldAlert, ShieldCheck } from "lucide-react";

export function App() {
  const [selectedGoal, setSelectedGoal] = useState<string>("midface_shortening");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // エージェント実行ステート
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [events, setEvents] = useState<AgentStepEvent[]>([]);
  const [currentScore, setCurrentScore] = useState<number>(0);
  const [currentIteration, setCurrentIteration] = useState<number>(1);
  const [isConverged, setIsConverged] = useState<boolean>(false);
  const [sessionId, setSessionId] = useState<string>("");
  const [currentPlan, setCurrentPlan] = useState<StylingPlan | null>(null);

  // 最終結果ステート
  const [finalImage, setFinalImage] = useState<string | null>(null);
  const [recipes, setRecipes] = useState<MakeupRecipeItem[] | null>(null);
  const [auditCert, setAuditCert] = useState<GovernanceAuditCertificate | null>(null);
  const [isGovernanceOpen, setIsGovernanceOpen] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleFileSelect = (file: File, preview: string) => {
    setSelectedFile(file);
    setPreviewUrl(preview);
    setFinalImage(null);
    setRecipes(null);
    setAuditCert(null);
    setCurrentPlan(null);
    setEvents([]);
    setCurrentScore(0);
    setIsConverged(false);
    setErrorMessage(null);
  };

  const handleStartOptimization = async () => {
    if (!selectedFile) {
      setErrorMessage("顔写真を選択またはサンプル写真を読み込んでください。");
      return;
    }

    setIsRunning(true);
    setEvents([]);
    setCurrentScore(0);
    setCurrentIteration(1);
    setIsConverged(false);
    setFinalImage(null);
    setRecipes(null);
    setAuditCert(null);
    setErrorMessage(null);

    const formData = new FormData();
    formData.append("goal", selectedGoal);
    formData.append("image", selectedFile);

    try {
      const response = await fetch("/api/agent/optimize", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`サーバーエラー: ${response.status} ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error("ストリーミングレスポンスを受信できませんでした。");
      }

      await parseSSEStream(response.body);
    } catch (err: any) {
      console.error(err);
      setErrorMessage(err.message || "最適化処理中に通信エラーが発生しました。");
    } finally {
      setIsRunning(false);
    }
  };

  // ユーザー対話型の微調整Replanハンドラー (Human-in-the-Loop)
  const handleFeedbackReplan = async (userFeedback: string) => {
    if (!currentPlan) return;

    setIsRunning(true);
    setErrorMessage(null);

    const formData = new FormData();
    formData.append("session_id", sessionId || "session_default");
    formData.append("goal", selectedGoal);
    formData.append("current_plan_json", JSON.stringify(currentPlan));
    formData.append("user_feedback", userFeedback);
    if (selectedFile) {
      formData.append("image", selectedFile);
    }

    try {
      const response = await fetch("/api/agent/feedback-replan", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`サーバーエラー: ${response.status} ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error("ストリーミングレスポンスを受信できませんでした。");
      }

      await parseSSEStream(response.body);
    } catch (err: any) {
      console.error(err);
      setErrorMessage(err.message || "微調整処理中に通信エラーが発生しました。");
    } finally {
      setIsRunning(false);
    }
  };

  // SSEストリーム共通パーサー
  const parseSSEStream = async (readableStream: ReadableStream<Uint8Array>) => {
    const reader = readableStream.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith("data:")) {
          const jsonStr = trimmed.replace(/^data:\s*/, "");
          try {
            const eventData: AgentStepEvent = JSON.parse(jsonStr);
            setEvents((prev) => [...prev, eventData]);

            if (eventData.session_id) {
              setSessionId(eventData.session_id);
            }

            if (eventData.plan) {
              setCurrentPlan(eventData.plan);
            }

            if (eventData.iteration) {
              setCurrentIteration(eventData.iteration);
            }

            if (eventData.score !== undefined) {
              setCurrentScore(eventData.score);
            }

            if (eventData.type === "converged") {
              setIsConverged(true);
            }

            if (eventData.type === "final_result") {
              if (eventData.simulated_image) {
                setFinalImage(eventData.simulated_image);
              }
              if (eventData.recipe) {
                setRecipes(eventData.recipe);
              }
              if (eventData.audit_certificate) {
                setAuditCert(eventData.audit_certificate);
              }
              if (eventData.final_score !== undefined) {
                setCurrentScore(eventData.final_score);
              }
              if (eventData.plan) {
                setCurrentPlan(eventData.plan);
              }
            }

            if (eventData.type === "error") {
              setErrorMessage(eventData.message || "エラーが発生しました。");
            }
          } catch (err) {
            console.error("SSE parse error", err);
          }
        }
      }
    }
  };

  const currentGoalObj = GOAL_PRESETS.find((g) => g.id === selectedGoal);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Header onOpenGovernance={() => setIsGovernanceOpen(true)} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* エラーアラート */}
        {errorMessage && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0" />
              <span className="text-sm font-medium">{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-xs text-rose-400 hover:text-white underline cursor-pointer"
            >
              閉じる
            </button>
          </div>
        )}

        {/* コントロールパネル: 写真入力 & Goal選択 */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 bg-slate-900/40 p-6 rounded-3xl border border-slate-800/80 shadow-xl">
          <div className="lg:col-span-5 space-y-4">
            <PhotoUploader
              previewUrl={previewUrl}
              onFileSelect={handleFileSelect}
              disabled={isRunning}
            />
          </div>

          <div className="lg:col-span-7 flex flex-col justify-between space-y-5">
            <GoalSelector
              selectedGoal={selectedGoal}
              onSelectGoal={(id) => {
                setSelectedGoal(id);
                setFinalImage(null);
                setRecipes(null);
                setAuditCert(null);
                setCurrentPlan(null);
              }}
              disabled={isRunning}
            />

            {/* アクション起動ボタン */}
            <div className="pt-2 flex flex-col sm:flex-row items-center gap-3">
              <button
                type="button"
                onClick={handleStartOptimization}
                disabled={isRunning || !previewUrl}
                className={`w-full sm:flex-1 py-3.5 px-6 rounded-xl font-bold text-sm flex items-center justify-center gap-2 shadow-lg transition-all ${
                  isRunning || !previewUrl
                    ? "bg-slate-800 text-slate-500 cursor-not-allowed shadow-none"
                    : "bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-400 hover:to-purple-500 text-white shadow-pink-500/25 hover:shadow-pink-500/40 cursor-pointer"
                }`}
              >
                {isRunning ? (
                  <>
                    <Sparkles className="w-4 h-4 animate-spin text-pink-300" />
                    <span>AIエージェント自律探索中...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-current" />
                    <span>エージェント最適化を開始（OODA Loop）</span>
                  </>
                )}
              </button>

              {events.length > 0 && !isRunning && (
                <button
                  type="button"
                  onClick={() => {
                    setEvents([]);
                    setFinalImage(null);
                    setRecipes(null);
                    setAuditCert(null);
                    setCurrentPlan(null);
                    setCurrentScore(0);
                  }}
                  className="w-full sm:w-auto px-4 py-3.5 rounded-xl border border-slate-700 bg-slate-800/80 hover:bg-slate-800 text-slate-300 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>リセット</span>
                </button>
              )}
            </div>
          </div>
        </section>

        {/* 思考プロセス & リアルタイムシミュレーションエリア */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* 左側: エージェントターミナル（Thought/Action/Observation/Score） */}
          <div className="lg:col-span-7">
            <AgentTerminal
              events={events}
              currentScore={currentScore}
              currentIteration={currentIteration}
              isRunning={isRunning}
              isConverged={isConverged}
            />
          </div>

          {/* 右側: Before / After スライダー（または待機・暫定プレビュー） */}
          <div className="lg:col-span-5 flex flex-col justify-center">
            {finalImage && previewUrl ? (
              <BeforeAfterSlider
                beforeImage={previewUrl}
                afterImage={finalImage}
                score={currentScore}
              />
            ) : (
              <div className="h-[520px] rounded-2xl border border-slate-800/80 bg-slate-900/30 flex flex-col items-center justify-center p-6 text-center text-slate-500 space-y-3">
                <div className="p-4 rounded-full bg-slate-800/60 border border-slate-700 text-slate-400">
                  <Sparkles className="w-8 h-8 text-pink-400/60" />
                </div>
                <h4 className="text-sm font-semibold text-slate-300">
                  Before / After 比較プレビュー
                </h4>
                <p className="text-xs text-slate-400 max-w-xs">
                  エージェントの試行錯誤が完了すると、骨格を変えず錯視だけで変化したBefore/After比較スライダーが表示されます。
                </p>
              </div>
            )}
          </div>
        </section>

        {/* ユーザー対話型微調整Replanエリア (Human-in-the-Loop) */}
        {currentPlan && (
          <section className="animate-in fade-in duration-500">
            <InteractiveFeedbackChat
              currentPlan={currentPlan}
              isRunning={isRunning}
              onSubmitFeedback={handleFeedbackReplan}
            />
          </section>
        )}

        {/* 最終レシピ表示エリア（完了時） */}
        {recipes && recipes.length > 0 && (
          <section className="animate-in fade-in duration-500 space-y-4">
            <RecipeCard
              recipes={recipes}
              goalTitle={currentGoalObj ? currentGoalObj.name : "美容目標"}
              beforeImage={previewUrl}
              afterImage={finalImage}
              score={currentScore}
            />

            {/* 監査証明書クイックアクセスバナー */}
            <div className="p-4 rounded-2xl bg-emerald-950/20 border border-emerald-500/20 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2.5 text-emerald-400">
                <ShieldCheck className="w-5 h-5 shrink-0" />
                <span>
                  本シミュレーションは **Google Cloud Responsible AI ガバナンス規程**（反ルッキズム・骨格歪曲0%・生体データRAM限定）に完全適合しています。
                </span>
              </div>
              <button
                type="button"
                onClick={() => setIsGovernanceOpen(true)}
                className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 font-semibold border border-emerald-500/30 transition-colors whitespace-nowrap cursor-pointer"
              >
                監査証明書を確認 →
              </button>
            </div>
          </section>
        )}
      </main>

      {/* ガバナンス監査証明書モーダル */}
      <GovernanceModal
        isOpen={isGovernanceOpen}
        onClose={() => setIsGovernanceOpen(false)}
        certificate={auditCert}
      />

      {/* フッター */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <p>
          Beauty Goal Agent &copy; 2026. Built with Google Cloud Run, Gemini 2.0 / 1.5, and YouCam MCP.
        </p>
        <p className="mt-1 text-[11px] text-slate-400">
          ※本システムは他者基準の顔採点・評価を行わず、ユーザー自らが定めた錯視効果の最適化のみを自律的に探索します。
        </p>
      </footer>
    </div>
  );
}

export default App;
