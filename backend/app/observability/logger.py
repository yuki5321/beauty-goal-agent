import json
import logging
import sys
from typing import List, Dict, Any, Optional

class StructuredAgentLogger:
    def __init__(self, component: str = "BeautyGoalAgent"):
        self.component = component
        self.logger = logging.getLogger(component)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            self.logger.addHandler(handler)

    def log_step(
        self,
        session_id: str,
        iteration_count: int,
        goal: str,
        thought_process: str,
        mcp_tools_called: List[str],
        evaluation_score: int,
        status: str,
        governance_check: Optional[Dict[str, Any]] = None,
        severity: str = "INFO"
    ) -> Dict[str, Any]:
        """Cloud Logging形式で構造化ログを出力し、辞書としても返す"""
        log_payload = {
            "severity": severity,
            "component": self.component,
            "session_id": session_id,
            "iteration_count": iteration_count,
            "goal": goal,
            "thought_process": thought_process,
            "mcp_tools_called": mcp_tools_called,
            "evaluation_score": evaluation_score,
            "status": status,
            "governance_check": governance_check or {
                "body_dysmorphic_risk": "SAFE",
                "prompt_injection_detected": False,
                "pii_masked": True
            }
        }
        # 標準出力へJSONとして出力（Cloud Logging が自動で構造化パースする形式）
        print(json.dumps(log_payload, ensure_ascii=False), flush=True)
        return log_payload

agent_logger = StructuredAgentLogger()
