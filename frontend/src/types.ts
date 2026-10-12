export interface GoalOption {
  id: string;
  name: string;
  tagline: string;
  description: string;
  recommended?: boolean;
}

export interface StylingPlan {
  blush_placement: string;
  blush_color: string;
  lip_over_ratio: number;
  eyeshadow_lower_intensity: number;
  bangs_style: string;
}

export interface MakeupProductItem {
  brand: string;
  name: string;
  shade: string;
  type: string;
  price?: string;
  grounding_verified?: boolean;
  source_url?: string;
}

export interface MakeupRecipeItem {
  category: string;
  action: string;
  instruction: string;
  effect: string;
  recommended_products?: MakeupProductItem[];
}

export interface GovernanceAuditCertificate {
  certificate_id: string;
  issued_at: string;
  standard: string;
  lookism_free_compliance: {
    rule: string;
    evaluation_mode: string;
    status: string;
  };
  body_dysmorphic_prevention: {
    rule: string;
    bone_distortion_rate: string;
    optical_illusion_parameters: Record<string, any>;
    status: string;
  };
  biometric_data_safety: {
    rule: string;
    storage_type: string;
    disk_db_persistence: string;
    ttl_purge_policy: string;
    external_processing?: string;
    status: string;
  };
  agent_circuit_breaker: {
    rule: string;
    max_loop_limit: number;
    actual_iterations: number;
    exit_status: string;
  };
}

export interface AgentStepEvent {
  type:
    | "step"
    | "observation"
    | "evaluation_result"
    | "iteration_start"
    | "converged"
    | "circuit_breaker"
    | "final_result"
    | "error"
    | "status"
    | "council_debate"
    | "hypothesis_rejected";
  session_id?: string;
  step_name?: string;
  title?: string;
  thought?: string;
  action?: string;
  observation?: string;
  status?: string;
  iteration?: number;
  max_iterations?: number;
  score?: number;
  is_goal_met?: boolean;
  critic_feedback?: string;
  preview_image?: string;
  plan?: StylingPlan;
  message?: string;
  governance_violation?: boolean;
  final_score?: number;
  simulated_image?: string;
  ratio_analysis?: RatioAnalysis;
  bangs_rendered?: boolean;
  element_scores?: ElementScores;
  recipe?: MakeupRecipeItem[];
  audit_certificate?: GovernanceAuditCertificate;
  governance_status?: {
    body_dysmorphic_risk: string;
    lookism_free_guarantee: boolean;
    biometric_purged_on_close: boolean;
    external_processor?: string | null;
  };
  // Multi-Agent Council Debate fields
  speaker?: "optics" | "stylist" | "governance";
  speaker_name?: string;
  argument?: string;
  stance?: "propose" | "critique" | "approve" | "reject";
  // Hypothesis Rejection fields
  rejected_hypothesis?: string;
  rejection_reason?: string;
  pivoted_strategy?: string;
}

export interface RatioAnalysis {
  observed_mid_ratio: number;
  perceived_mid_ratio: number;
  ideal_mid_ratio: number;
}

/** Critic の要素別スコア（0〜100）。前髪は画像に反映されていない場合は含まれない */
export interface ElementScores {
  blush?: number;
  lip?: number;
  under_eye?: number;
  bangs?: number;
}
