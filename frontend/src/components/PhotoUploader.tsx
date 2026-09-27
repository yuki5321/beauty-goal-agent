import { useRef, useState, useEffect } from "react";
import { Upload, Sparkles, CheckCircle2, Camera, X } from "lucide-react";

interface Props {
  previewUrl: string | null;
  onFileSelect: (file: File, preview: string) => void;
  disabled?: boolean;
}

export const PhotoUploader = ({
  previewUrl,
  onFileSelect,
  disabled,
}: Props) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);

  // カメラの起動
  const startCamera = async () => {
    setCameraError(null);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 720 },
          height: { ideal: 720 },
        },
      });
      setStream(mediaStream);
      setIsCameraOpen(true);
    } catch (err: any) {
      console.error("Camera access error:", err);
      setCameraError(
        "カメラの起動に失敗しました。カメラへのアクセスを許可してください（または通常アップロードをご利用ください）。"
      );
    }
  };

  // カメラの停止
  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
    setIsCameraOpen(false);
  };

  useEffect(() => {
    if (isCameraOpen && videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [isCameraOpen, stream]);

  // 写真の撮影 (スナップショット)
  const capturePhoto = () => {
    if (!videoRef.current) return;

    const video = videoRef.current;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 512;
    canvas.height = video.videoHeight || 512;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // 鏡のように左右反転して描画
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], `selfie_${Date.now()}.jpg`, {
          type: "image/jpeg",
        });
        const dataUrl = canvas.toDataURL("image/jpeg");
        onFileSelect(file, dataUrl);
        stopCamera();
      }
    }, "image/jpeg", 0.95);
  };

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
        const file = new File([blob], "demo_sample_face.jpg", {
          type: "image/jpeg",
        });
        const dataUrl = canvas.toDataURL("image/jpeg");
        onFileSelect(file, dataUrl);
      }
    }, "image/jpeg", 0.95);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <label className="text-sm font-semibold text-slate-200 flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-pink-500"></span>
          正面の顔写真（自撮り）を入力
        </label>
        
        <div className="flex items-center gap-3">
          {/* スマートミラー：インカメラ起動ボタン */}
          <button
            type="button"
            disabled={disabled}
            onClick={startCamera}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1 transition-colors cursor-pointer bg-cyan-950/40 px-2.5 py-1 rounded-lg border border-cyan-500/30"
          >
            <Camera className="w-3.5 h-3.5" />
            <span>カメラで撮影</span>
          </button>

          <button
            type="button"
            disabled={disabled}
            onClick={loadDemoSamplePhoto}
            className="text-xs text-pink-400 hover:text-pink-300 font-medium flex items-center gap-1 underline underline-offset-2 transition-colors cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>デモ用サンプル</span>
          </button>
        </div>
      </div>

      {cameraError && (
        <div className="text-xs text-rose-400 bg-rose-500/10 p-2.5 rounded-xl border border-rose-500/20">
          {cameraError}
        </div>
      )}

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
              JPG / PNG 形式（右上の「カメラで撮影」からインカメラ自撮りも可能）
            </p>
          </div>
        )}
      </div>

      {/* スマートミラー撮影モーダル */}
      {isCameraOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-in fade-in duration-200">
          <div className="relative w-full max-w-md bg-slate-900 border border-cyan-500/40 rounded-3xl overflow-hidden shadow-2xl flex flex-col">
            <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2 text-cyan-400 font-semibold text-sm">
                <Camera className="w-4 h-4" />
                <span>スマートミラー：正面顔撮影</span>
              </div>
              <button
                onClick={stopCamera}
                className="p-1 rounded-lg text-slate-400 hover:text-white transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="relative aspect-square w-full bg-black overflow-hidden flex items-center justify-center">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover -scale-x-100"
              />
              {/* 正面ガイド枠 */}
              <div className="absolute inset-8 rounded-full border-2 border-dashed border-cyan-400/50 pointer-events-none flex items-center justify-center">
                <span className="text-[11px] text-cyan-300/80 bg-black/50 px-2 py-0.5 rounded-full font-mono">
                  枠内に顔を合わせてください
                </span>
              </div>
            </div>

            <div className="p-5 bg-slate-950 flex items-center justify-center gap-4">
              <button
                type="button"
                onClick={capturePhoto}
                className="flex items-center gap-2 px-8 py-3.5 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-sm shadow-lg shadow-cyan-500/25 cursor-pointer transition-all scale-100 hover:scale-105 active:scale-95"
              >
                <Camera className="w-4 h-4" />
                <span>パシャッと撮影する</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
