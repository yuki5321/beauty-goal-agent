import { Sparkles, ShieldCheck, Lock, EyeOff, FileCheck } from "lucide-react";

interface Props {
  onOpenGovernance?: () => void;
}

export const Header = ({ onOpenGovernance }: Props) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-gradient-to-br from-pink-500 to-purple-600 text-white shadow-lg shadow-pink-500/20">
                <Sparkles className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                  Beauty Goal Agent
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-pink-500/10 text-pink-400 border border-pink-500/20 font-medium">
                    Autonomous OODA Loop
                  </span>
                </h1>
                <p className="text-xs text-slate-400 mt-0.5">
                  「似合う」を押し付けない。あなたの「なりたい顔」へ、AIが試行錯誤で伴走する自律型メイク・スタイリング最適化
                </p>
              </div>
            </div>
          </div>

          {/* ガバナンス・Responsible AI バッジ & 監査証モーダルトリガー */}
          <div className="flex items-center gap-2 flex-wrap">
            <button
              type="button"
              onClick={onOpenGovernance}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 text-emerald-400 text-xs font-medium transition-colors cursor-pointer group"
              title="クリックしてガバナンス監査証明書を表示"
            >
              <ShieldCheck className="w-3.5 h-3.5 group-hover:scale-110 transition-transform" />
              <span>反ルッキズム・非採点規程</span>
              <FileCheck className="w-3 h-3 text-emerald-400/70 ml-1" />
            </button>

            <button
              type="button"
              onClick={onOpenGovernance}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 text-indigo-400 text-xs font-medium transition-colors cursor-pointer group"
              title="クリックしてガバナンス監査証明書を表示"
            >
              <Lock className="w-3.5 h-3.5 group-hover:scale-110 transition-transform" />
              <span>骨格変形リミッター（錯視限定）</span>
            </button>

            <button
              type="button"
              onClick={onOpenGovernance}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/20 text-purple-400 text-xs font-medium transition-colors cursor-pointer group"
              title="クリックしてガバナンス監査証明書を表示"
            >
              <EyeOff className="w-3.5 h-3.5 group-hover:scale-110 transition-transform" />
              <span>RAM限定・生体データ即時破棄</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
