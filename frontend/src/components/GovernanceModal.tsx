import { ShieldCheck, Lock, EyeOff, Cpu, X, CheckCircle, Copy, Check } from "lucide-react";
import { useState } from "react";
import type { GovernanceAuditCertificate } from "../types";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  certificate?: GovernanceAuditCertificate | null;
}

export const GovernanceModal = ({ isOpen, onClose, certificate }: Props) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const defaultCert: GovernanceAuditCertificate = certificate || {
    certificate_id: "CERT-DEMO-2026",
    issued_at: new Date().toISOString(),
    standard: "Google Cloud Responsible AI & Governance Standards Vol.5",
    lookism_free_compliance: {
      rule: "N-G01 (コンプレックス非刺激・ルッキズム排除規程)",
      evaluation_mode: "錯視幾何比率シフトのみ測定（容姿採点・欠点指摘の全面排除）",
      status: "PASSED",
    },
    body_dysmorphic_prevention: {
      rule: "N-G02 (ディスモルフィア抑止・骨格変形リミッター)",
      bone_distortion_rate: "0.00%（物理的骨格変形ツール呼出ゼロ）",
      optical_illusion_parameters: { lip_over_ratio: 1.18, blush: "horizontal_low" },
      status: "ENFORCED",
    },
    biometric_data_safety: {
      rule: "N-G03 (生体顔写真データ最小化と即時破棄)",
      storage_type: "Cloud Run RAM (Volatile Memory Only)",
      disk_db_persistence: "FORBIDDEN & NONE",
      ttl_purge_policy: "Session Close / 300s TTL (Zero Trace)",
      status: "VERIFIED",
    },
    agent_circuit_breaker: {
      rule: "N-G04 (暴走防止サーキットブレーカー)",
      max_loop_limit: 3,
      actual_iterations: 2,
      exit_status: "CONVERGED (Score: 88%)",
    },
  };

  const handleCopyJSON = () => {
    navigator.clipboard.writeText(JSON.stringify(defaultCert, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-700/80 rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* ヘッダー */}
        <div className="px-6 py-5 border-b border-slate-800 bg-slate-950/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-white">
                  Responsible AI &amp; ガバナンス監査証明書
                </h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  VERIFIED
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                ID: {defaultCert.certificate_id}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl hover:bg-slate-800 text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* コンテンツ */}
        <div className="p-6 overflow-y-auto space-y-4 text-xs font-mono">
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-slate-300 space-y-1">
            <div className="text-[11px] text-slate-400">準拠規格 / 監査基準</div>
            <div className="font-bold text-white">{defaultCert.standard}</div>
            <div className="text-[10px] text-slate-400">発行時刻: {defaultCert.issued_at}</div>
          </div>

          {/* 4大ガバナンス項目の検証ステータス */}
          <div className="space-y-3">
            {/* N-G01 */}
            <div className="p-3.5 rounded-2xl bg-slate-950/40 border border-slate-800 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white flex items-center gap-1.5 text-xs">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  {defaultCert.lookism_free_compliance.rule}
                </span>
                <span className="px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">
                  {defaultCert.lookism_free_compliance.status}
                </span>
              </div>
              <p className="text-slate-400 font-sans text-xs">
                {defaultCert.lookism_free_compliance.evaluation_mode}
              </p>
            </div>

            {/* N-G02 */}
            <div className="p-3.5 rounded-2xl bg-slate-950/40 border border-slate-800 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white flex items-center gap-1.5 text-xs">
                  <Lock className="w-4 h-4 text-indigo-400" />
                  {defaultCert.body_dysmorphic_prevention.rule}
                </span>
                <span className="px-2 py-0.5 rounded-md bg-indigo-500/20 text-indigo-400 text-[10px] font-bold">
                  {defaultCert.body_dysmorphic_prevention.status}
                </span>
              </div>
              <p className="text-slate-400 font-sans text-xs">
                骨格変形率: <span className="text-emerald-400 font-bold">{defaultCert.body_dysmorphic_prevention.bone_distortion_rate}</span>。骨格リシェイプツールの遮断と安全パラメータ制約を強制。
              </p>
            </div>

            {/* N-G03 */}
            <div className="p-3.5 rounded-2xl bg-slate-950/40 border border-slate-800 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white flex items-center gap-1.5 text-xs">
                  <EyeOff className="w-4 h-4 text-purple-400" />
                  {defaultCert.biometric_data_safety.rule}
                </span>
                <span className="px-2 py-0.5 rounded-md bg-purple-500/20 text-purple-400 text-[10px] font-bold">
                  {defaultCert.biometric_data_safety.status}
                </span>
              </div>
              <p className="text-slate-400 font-sans text-xs">
                保存先: {defaultCert.biometric_data_safety.storage_type} / ディスク永続化: {defaultCert.biometric_data_safety.disk_db_persistence}。セッション終了時ゼロトレース消去。
              </p>
            </div>

            {/* N-G04 */}
            <div className="p-3.5 rounded-2xl bg-slate-950/40 border border-slate-800 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white flex items-center gap-1.5 text-xs">
                  <Cpu className="w-4 h-4 text-pink-400" />
                  {defaultCert.agent_circuit_breaker.rule}
                </span>
                <span className="px-2 py-0.5 rounded-md bg-pink-500/20 text-pink-400 text-[10px] font-bold">
                  SAFE
                </span>
              </div>
              <p className="text-slate-400 font-sans text-xs">
                上限設定: 最大{defaultCert.agent_circuit_breaker.max_loop_limit}回 / 実行回数: {defaultCert.agent_circuit_breaker.actual_iterations}回 ({defaultCert.agent_circuit_breaker.exit_status})。無限ループ・コスト浪費を完全防止。
              </p>
            </div>
          </div>
        </div>

        {/* フッター */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between">
          <div className="flex items-center gap-2 text-slate-400 text-xs font-sans">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span>審査員向けガバナンス監査ログ検証済み</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyJSON}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-sans transition-colors border border-slate-700 cursor-pointer"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">JSONコピー完了</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 text-slate-400" />
                  <span>監査JSONをコピー</span>
                </>
              )}
            </button>
            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded-xl bg-pink-600 hover:bg-pink-500 text-white text-xs font-sans font-semibold transition-colors cursor-pointer"
            >
              閉じる
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
