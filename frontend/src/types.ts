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
  type: "step" | "observation" | "evaluation_result" | "iteration_start" | "converged" | "circuit_breaker" | "final_result" | "error" | "status";
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
  recipe?: MakeupRecipeItem[];
  audit_certificate?: GovernanceAuditCertificate;
  governance_status?: {
    body_dysmorphic_risk: string;
    lookism_free_guarantee: boolean;
    biometric_purged_on_close: boolean;
  };
}
