import { useRef } from "react";
import { Upload, Sparkles, CheckCircle2 } from "lucide-react";

interface Props {
  previewUrl: string | null;
  onFileSelect: (file: File, preview: string) => void;
  disabled?: boolean;
}

export const PhotoUploader: React.FC<Props> = ({
  previewUrl,
  onFileSelect,
  disabled,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        onFileSelect(file, reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // デモ用の正面顔写真をCanvasで高解像度生成するヘルパー
  const loadDemoSamplePhoto = () => {
    const canvas = document.createElement("canvas");
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // 背景（自然な肌色トーンのスタジオ背景）
    const grad = ctx.createLinearGradient(0, 0, 0, 512);
    grad.addColorStop(0, "#f8fafc");
    grad.addColorStop(1, "#cbd5e1");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 512, 512);

    // 輪郭（卵型の顔輪郭）
    ctx.fillStyle = "#faebd7";
    ctx.beginPath();
    ctx.ellipse(256, 260, 130, 170, 0, 0, Math.PI * 2);
    ctx.fill();

    // 髪（ロングダークブラウン）
    ctx.fillStyle = "#2d2424";
    ctx.beginPath();
    ctx.arc(256, 210, 145, Math.PI, 0);
    ctx.lineTo(410, 480);
    ctx.lineTo(370, 490);
    ctx.lineTo(360, 320);
    ctx.lineTo(152, 320);
    ctx.lineTo(142, 490);
    ctx.lineTo(102, 480);
    ctx.closePath();
    ctx.fill();

    // 額（前髪なしのおでこ）
    ctx.fillStyle = "#faebd7";
    ctx.beginPath();
    ctx.ellipse(256, 190, 110, 70, 0, 0, Math.PI * 2);
    ctx.fill();

    // 目（左右）
    const drawEye = (cx: number) => {
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.ellipse(cx, 210, 24, 12, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#3e2723";
      ctx.beginPath();
      ctx.arc(cx, 210, 9, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.arc(cx - 3, 207, 3, 0, Math.PI * 2);
      ctx.fill();
    };
    drawEye(195);
    drawEye(317);

    // 眉（高めのアーチ眉）
    ctx.strokeStyle = "#4a3728";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(170, 185);
    ctx.quadraticCurveTo(195, 175, 225, 186);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(287, 186);
    ctx.quadraticCurveTo(317, 175, 342, 185);
    ctx.stroke();

    // 鼻（すっきりとした鼻筋・小鼻）
    ctx.strokeStyle = "#e2b89c";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(256, 215);
    ctx.lineTo(256, 290);
    ctx.quadraticCurveTo(248, 298, 242, 295);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(256, 290);
    ctx.quadraticCurveTo(264, 298, 270, 295);
    ctx.stroke();

    // 唇（ナチュラルピンク、薄めの唇）
    ctx.fillStyle = "#e07a7a";
    ctx.beginPath();
    ctx.ellipse(256, 350, 28, 9, 0, 0, Math.PI * 2);
    ctx.fill();

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], "demo_sample_face.jpg", { type: "image/jpeg" });
        const dataUrl = canvas.toDataURL("image/jpeg");
        onFileSelect(file, dataUrl);
      }
    }, "image/jpeg", 0.95);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold text-slate-200 flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-pink-500"></span>
          正面の顔写真（自撮り）を入力
        </label>
        <button
          type="button"
          disabled={disabled}
          onClick={loadDemoSamplePhoto}
          className="text-xs text-pink-400 hover:text-pink-300 font-medium flex items-center gap-1 underline underline-offset-2 transition-colors cursor-pointer"
        >
          <Sparkles className="w-3.5 h-3.5" />
          デモ用サンプル写真を読み込む
        </button>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileChange}
        disabled={disabled}
      />

      <div
        onClick={() => !disabled && fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-6 text-center transition-all ${
          previewUrl
            ? "border-pink-500/50 bg-slate-900/40"
            : "border-slate-800 bg-slate-900/30 hover:border-slate-700 hover:bg-slate-900/50"
        } ${disabled ? "cursor-not-allowed opacity-60" : "cursor-pointer"}`}
      >
        {previewUrl ? (
          <div className="flex flex-col items-center">
            <div className="relative w-36 h-36 rounded-2xl overflow-hidden border-2 border-pink-500 shadow-xl shadow-pink-500/20 mb-3 group">
              <img
                src={previewUrl}
                alt="アップロードプレビュー"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-semibold">
                写真を変更
              </div>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
              <CheckCircle2 className="w-4 h-4" />
              <span>顔写真が正常にセットされました</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">
              クリックすると別の写真を選択できます（RAM上のみで処理され保存されません）
            </p>
          </div>
        ) : (
          <div className="py-4 flex flex-col items-center">
            <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700 text-slate-400 mb-3">
              <Upload className="w-8 h-8 text-pink-400" />
            </div>
            <p className="text-sm font-semibold text-white mb-1">
              クリックまたは写真をドラッグ＆ドロップ
            </p>
            <p className="text-xs text-slate-400 max-w-xs">
              JPG / PNG 形式（正面向き・前髪や輪郭がわかりやすい写真が最適です）
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
