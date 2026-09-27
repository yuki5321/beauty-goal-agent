import os
from PIL import Image, ImageDraw, ImageFont

def generate_png():
    width = 1600
    height = 900
    img = Image.new("RGB", (width, height), color=(11, 15, 25))
    draw = ImageDraw.Draw(img)

    # 背景装飾ライン
    for y in range(150, 900, 150):
        draw.line([(0, y), (1600, y)], fill=(30, 41, 59), width=1)
    for x in range(200, 1600, 200):
        draw.line([(x, 0), (x, 900)], fill=(30, 41, 59), width=1)

    # ヘッダー
    draw.rectangle([0, 0, 1600, 120], fill=(15, 23, 42))
    draw.line([(0, 120), (1600, 120)], fill=(51, 65, 85), width=2)
    draw.text((60, 30), "Beauty Goal Agent :: System Architecture", fill=(244, 114, 182))
    draw.text((60, 70), "第5回 Agentic AI Hackathon with Google Cloud  |  Google Cloud Run x Gemini 2.0 / 1.5 x YouCam MCP", fill=(148, 163, 184))

    # ガバナンスバッジ
    draw.rounded_rectangle([1080, 35, 1540, 85], radius=15, fill=(6, 78, 59), outline=(16, 185, 129), width=2)
    draw.text((1110, 50), "Responsible AI & Governance Verified (N-G01 - N-G04)", fill=(52, 211, 153))

    # --- 1. Frontend ---
    draw.rounded_rectangle([60, 150, 380, 840], radius=20, fill=(15, 23, 42), outline=(71, 85, 105), width=2)
    draw.rounded_rectangle([60, 150, 380, 205], radius=20, fill=(30, 41, 59))
    draw.text((80, 168), "Client App (React / Vite)", fill=(248, 250, 252))

    # Frontend Boxes
    draw.rounded_rectangle([80, 220, 360, 310], radius=12, fill=(30, 41, 59), outline=(244, 63, 94), width=1)
    draw.text((95, 235), "1. Goal Selection & Photo Upload", fill=(251, 113, 133))
    draw.text((95, 260), "- Midface Shortening / Small Face", fill=(203, 213, 225))
    draw.text((95, 280), "- Biometric Photo Safe Upload", fill=(148, 163, 184))

    draw.rounded_rectangle([80, 325, 360, 435], radius=12, fill=(30, 41, 59), outline=(6, 182, 212), width=2)
    draw.text((95, 340), "2. Real-time OODA Stream", fill=(34, 211, 238))
    draw.text((95, 365), "- Server-Sent Events (SSE) Client", fill=(203, 213, 225))
    draw.text((95, 385), "- Thought / Action / Critic Feed", fill=(203, 213, 225))
    draw.text((95, 405), "- Score Progress (72% -> 88%)", fill=(165, 243, 252))

    draw.rounded_rectangle([80, 450, 360, 560], radius=12, fill=(30, 41, 59), outline=(168, 85, 247), width=2)
    draw.text((95, 465), "3. Before/After & Recipes", fill=(192, 132, 252))
    draw.text((95, 490), "- Drag Comparison Slider", fill=(203, 213, 225))
    draw.text((95, 510), "- Real Cosmetics Recs (KATE etc)", fill=(203, 213, 225))
    draw.text((95, 530), "- Download Prescription PNG Card", fill=(233, 213, 255))

    draw.rounded_rectangle([80, 575, 360, 680], radius=12, fill=(30, 41, 59), outline=(236, 72, 153), width=2)
    draw.text((95, 590), "4. Human-in-the-Loop Chat", fill=(244, 114, 182))
    draw.text((95, 615), "- Interactive Custom Replan", fill=(203, 213, 225))
    draw.text((95, 635), "- e.g. Natural Lip, Bangs None", fill=(203, 213, 225))

    draw.rounded_rectangle([80, 695, 360, 815], radius=12, fill=(6, 78, 59), outline=(16, 185, 129), width=1)
    draw.text((95, 715), "5. Trust & Governance Panel", fill=(52, 211, 153))
    draw.text((95, 740), "- Biometric Memory Purge Proof", fill=(167, 243, 208))
    draw.text((95, 760), "- Bone Distortion Rate: 0.00%", fill=(167, 243, 208))
    draw.text((95, 780), "- Audit Certificate Modal", fill=(167, 243, 208))

    # --- 2. Google Cloud Run ---
    draw.rounded_rectangle([420, 150, 1080, 840], radius=20, fill=(15, 23, 42), outline=(66, 133, 244), width=3)
    draw.rounded_rectangle([420, 150, 1080, 205], radius=20, fill=(30, 58, 138))
    draw.text((445, 168), "Google Cloud Run :: Agent Core (FastAPI on Port 8080)", fill=(255, 255, 255))
    draw.text((880, 168), "Region: asia-northeast1 (Scale to 0)", fill=(147, 197, 253))

    # Cloud Run Sub-layers
    draw.rounded_rectangle([445, 225, 1055, 315], radius=14, fill=(15, 23, 42), outline=(16, 185, 129), width=2)
    draw.text((465, 245), "Layer 1: Security & Ethics Guardrail (N-G01 / N-G02)", fill=(52, 211, 153))
    draw.text((465, 270), "- Lookism Filter: Physically block offensive rating terms & scores", fill=(203, 213, 225))
    draw.text((465, 290), "- Bone Distortion Limiter: Block AI_Face_Reshape, hard limit optical illusion", fill=(203, 213, 225))

    draw.rounded_rectangle([445, 330, 1055, 410], radius=14, fill=(15, 23, 42), outline=(139, 92, 246), width=2)
    draw.text((465, 345), "Layer 2: In-Memory Biometric Buffer (N-G03 Data Minimization)", fill=(192, 132, 252))
    draw.text((465, 370), "- RAM-only processing in Cloud Run volatile memory (Disk/DB write FORBIDDEN)", fill=(203, 213, 225))
    draw.text((465, 390), "- Instant zero-trace purge on session close or 300s TTL expiration", fill=(167, 139, 250))

    # OODA Orchestrator
    draw.rounded_rectangle([445, 425, 1055, 695], radius=16, fill=(11, 17, 32), outline=(244, 63, 94), width=2)
    draw.text((465, 445), "Layer 3: Autonomous Agent Orchestrator (OODA & Replan Loop)", fill=(251, 113, 133))

    # Step Boxes
    steps = [
        ("Step 1: OBSERVE", "Analyze Face Ratio", "Midface: 0.355", (56, 189, 248)),
        ("Step 2: ORIENT", "Goal Gap Analysis", "Identify Center", (192, 132, 252)),
        ("Step 3: DECIDE", "Styling Planning", "Formulate Plan A", (244, 114, 182)),
        ("Step 4: ACT", "MCP Tool Calls", "Virtual Try-On", (250, 204, 21)),
    ]
    for i, (st, desc1, desc2, col) in enumerate(steps):
        sx = 465 + i * 145
        draw.rounded_rectangle([sx, 480, sx + 135, 565], radius=10, fill=(30, 41, 59), outline=col, width=1)
        draw.text((sx + 10, 495), st, fill=col)
        draw.text((sx + 10, 520), desc1, fill=(226, 232, 240))
        draw.text((sx + 10, 540), desc2, fill=(148, 163, 184))

    # Step 5 & 6
    draw.rounded_rectangle([465, 580, 745, 680], radius=12, fill=(30, 41, 59), outline=(16, 185, 129), width=2)
    draw.text((480, 595), "Step 5: EVALUATE (Gemini Critic)", fill=(52, 211, 153))
    draw.text((480, 620), "- Multimodal comparison: Score 72%", fill=(226, 232, 240))
    draw.text((480, 640), "- Critic: Blush too high, teardrop missing", fill=(248, 113, 113))
    draw.text((480, 660), "- Status: Replan required (<85%)", fill=(250, 204, 21))

    draw.rounded_rectangle([765, 580, 1035, 680], radius=12, fill=(30, 41, 59), outline=(236, 72, 153), width=2)
    draw.text((780, 595), "Step 6: REPLAN (Plan B / 88%)", fill=(244, 114, 182))
    draw.text((780, 620), "- Reflect Critic & lower blush, add shadow", fill=(226, 232, 240))
    draw.text((780, 640), "- Re-simulation -> Score 88% (GOAL MET!)", fill=(52, 211, 153))
    draw.text((780, 660), "- Circuit Breaker: Max 3 Loops Safely Exit", fill=(147, 197, 253))

    # Observability Layer
    draw.rounded_rectangle([445, 710, 1055, 815], radius=14, fill=(15, 23, 42), outline=(14, 165, 233), width=2)
    draw.text((465, 725), "Layer 4: Observability (Google Cloud Logging & Trace)", fill=(56, 189, 248))
    draw.text((465, 750), "- Cloud Logging structured JSON: Thought, Action, Observation, Score & Audit", fill=(203, 213, 225))
    draw.text((465, 770), "- Real-time SSE Streaming endpoints (/api/agent/optimize, /api/agent/feedback-replan)", fill=(203, 213, 225))
    draw.text((465, 790), "- End-to-End latency tracing (avg 4.2s per optimization loop)", fill=(2, 132, 199))

    # --- 3. External Services ---
    draw.rounded_rectangle([1120, 150, 1540, 840], radius=20, fill=(15, 23, 42), outline=(71, 85, 105), width=2)
    draw.rounded_rectangle([1120, 150, 1540, 205], radius=20, fill=(30, 41, 59))
    draw.text((1150, 168), "AI Foundation & Support Sponsors", fill=(248, 250, 252))

    # Gemini API Box
    draw.rounded_rectangle([1145, 225, 1515, 480], radius=16, fill=(30, 27, 75), outline=(129, 140, 248), width=2)
    draw.text((1165, 250), "Google Gemini API", fill=(199, 210, 254))
    draw.text((1165, 275), "Gemini 2.0 Flash / Gemini 1.5 Pro", fill=(165, 180, 252))

    draw.rounded_rectangle([1165, 305, 1495, 370], radius=8, fill=(15, 23, 42))
    draw.text((1180, 325), "Planning Agent", fill=(224, 231, 255))
    draw.text((1180, 345), "- Formulate initial optical styling plan", fill=(148, 163, 184))

    draw.rounded_rectangle([1165, 385, 1495, 465], radius=8, fill=(15, 23, 42), outline=(165, 243, 252), width=1)
    draw.text((1180, 400), "Visual Critic Agent (Multimodal)", fill=(165, 243, 252))
    draw.text((1180, 420), "- Image-to-Image visual inspection", fill=(203, 213, 225))
    draw.text((1180, 440), "- Goal ratio shift (0-100%) & reflection", fill=(203, 213, 225))

    # YouCam MCP Box
    draw.rounded_rectangle([1145, 500, 1515, 815], radius=16, fill=(59, 7, 100), outline=(244, 63, 94), width=2)
    draw.text((1165, 525), "YouCam MCP Server", fill=(253, 164, 175))
    draw.text((1165, 550), "Perfect Corp. API (Support Sponsor)", fill=(254, 205, 211))

    mcp_tools = [
        ("analyze_face", "Face Proportion & Landmarks"),
        ("apply_blush", "Lower Horizontal Cheek Overlay"),
        ("apply_lipstick", "Upper Overlip (Philtrum Shorten)"),
        ("apply_eye_makeup", "Lower Eyelid Teardrop Shadow"),
    ]
    for j, (tool, tdesc) in enumerate(mcp_tools):
        ty = 580 + j * 50
        draw.rounded_rectangle([1165, ty, 1495, ty + 42], radius=8, fill=(30, 27, 75))
        draw.text((1180, ty + 12), tool + ":", fill=(251, 207, 232))
        draw.text((1290, ty + 12), tdesc, fill=(226, 232, 240))

    # 矢印ライン (Client <-> Cloud Run <-> External)
    draw.line([(380, 360), (420, 360)], fill=(6, 182, 212), width=3)
    draw.line([(420, 380), (380, 380)], fill=(236, 72, 153), width=3)
    draw.text((388, 340), "HTTP/SSE", fill=(6, 182, 212))

    draw.line([(1080, 350), (1120, 350)], fill=(129, 140, 248), width=3)
    draw.text((1083, 330), "GenAI", fill=(129, 140, 248))

    draw.line([(1080, 650), (1120, 650)], fill=(244, 63, 94), width=3)
    draw.text((1083, 630), "MCP", fill=(244, 63, 94))

    out_path = os.path.join(os.path.dirname(__file__), "architecture_diagram.png")
    img.save(out_path, format="PNG")
    print(f"Architecture diagram PNG generated at {out_path}")

if __name__ == "__main__":
    generate_png()
