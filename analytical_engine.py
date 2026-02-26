"""
Analytical Operations: the generative engine of the primary model.

Production rules formalize documented condition-outcome relationships.
They become GENERATIVE when conditions are varied: the production rule
determines how changes to conditions affect outcomes, based on the
empirically grounded relationships it encodes.

Operations:
  1. Condition sensitivity analysis (vary conditions, observe outcome effects)
  2. Cross-impact alignment (compare against Phase 3A/3B benchmarks)
  3. Generative logic testing (verify domain-level patterns computationally)
  4. Counter-case testing (opposite condition configurations)
  5. Agent feature analysis (patterns across org type, maturity, etc.)
  6. Sovereignty pathway tracing (conditions → outcomes → sovereignty)
  7. Reverse analysis (desired outcomes → required conditions)
  8. Hypothetical case creation (user-specified condition profiles)
  9. Validation tests (consistency, input response, cross-impact alignment)
"""

import copy
from collections import defaultdict, Counter
from config import (
    ALL_CONDITION_TYPES, INTERNAL_CONDITION_TYPES, EXTERNAL_CONDITION_TYPES,
    OUTCOME_GROUPS, OUTCOME_GROUP_NAMES, CONDITION_TYPE_NAMES,
    SOVEREIGNTY_DIMENSIONS, ORG_TYPE_NAMES,
    OUTCOME_SOVEREIGNTY_MAP, OUTCOME_CATEGORIES, CONDITION_CATEGORIES,
    CONDITION_MECHANISM_MAP,
    CONDITION_SOVEREIGNTY_TERRAIN, OUTCOME_GROUP_SOVEREIGNTY,
    NECESSARY_CONDITIONS, NEAR_NECESSARY_CONDITIONS,
    OUTCOME_COOCCURRENCE,
    CONDITION_CLASSIFICATION, TRANSVERSAL_RESONANCE,
    RECURSIVE_PATTERNS, MECHANISM_RECURSIVE_MAP, RECURSIVE_PATTERN_REFINEMENT,
)
from agent import Agent, ProductionRuleRow


class AnalyticalEngine:
    """
    Analytical operations for the primary model.

    The engine operates on agents and cross-impact data to perform
    sensitivity analysis, counterfactual scenarios, and pattern detection.
    """

    def __init__(self, model):
        """
        Args:
            model: PrimaryModel instance with agents and cross_impact_quant
        """
        self.model = model
        self.agents = model.agents
        self.cross_impact = model.cross_impact_quant

        # Precompute connection matrices per agent
        self._connection_cache = {}

    # ══════════════════════════════════════════════════════════════════
    # 1. CONDITION SENSITIVITY ANALYSIS
    # ══════════════════════════════════════════════════════════════════

    def condition_sensitivity(self, case_name: str, condition_type: str,
                              delta: float = 0.25) -> dict:
        """
        Vary a single condition type's score and compute outcome effects.

        Uses two weight sources:
        1. Production rule connections (case-level: which CT→OG links exist)
        2. Cross-impact matrix (ecosystem-level: how strongly CT relates to OG)

        When a condition is varied, connected outcomes change proportionally
        to the condition-outcome connection strength.
        """
        agent = self.model.get_agent(case_name)
        pr_connections = self._get_condition_outcome_connections(agent)

        # Get baseline score
        baseline_score = agent.all_condition_scores.get(condition_type)
        if baseline_score is None:
            return {
                "case": case_name,
                "condition_type": condition_type,
                "status": "not_active",
                "message": f"{condition_type} is not active for {case_name}",
                "outcome_effects": {og: {"baseline": None, "modified": None,
                                          "change": 0, "connected": False}
                                    for og in OUTCOME_GROUPS},
            }

        # Compute new score (clamped to 0-1)
        new_score = max(0.0, min(1.0, baseline_score + delta))
        actual_delta = new_score - baseline_score

        # If at boundary and delta goes further, use the full delta for
        # computing effects but note the score is clamped
        effective_delta = delta if actual_delta == 0 and delta != 0 else actual_delta

        results = {
            "case": case_name,
            "condition_type": condition_type,
            "condition_name": CONDITION_TYPE_NAMES.get(condition_type, condition_type),
            "baseline_score": baseline_score,
            "new_score": round(new_score, 3),
            "delta_applied": round(actual_delta, 3),
            "delta_effective": round(effective_delta, 3),
            "clamped": actual_delta != delta,
            "outcome_effects": {},
        }

        # Get cross-impact connection weights for this condition type
        ci_weights = self._cross_impact_weights(condition_type)

        for og in OUTCOME_GROUPS:
            baseline_outcome = agent.outcome_scores.get(og)
            if baseline_outcome is None:
                results["outcome_effects"][og] = {
                    "baseline": None,
                    "modified": None,
                    "change": 0,
                    "connected": False,
                }
                continue

            # Check if production rule links this CT to this OG
            pr_linked = pr_connections.get((condition_type, og), 0) > 0

            # Cross-impact weight (normalized)
            ci_weight = ci_weights.get(og, 0)

            if not pr_linked and ci_weight == 0:
                results["outcome_effects"][og] = {
                    "baseline": round(baseline_outcome, 3),
                    "modified": round(baseline_outcome, 3),
                    "change": 0,
                    "connection_strength": 0,
                    "connected": False,
                }
                continue

            # Connection strength: blend production rule (case-specific)
            # with cross-impact (ecosystem-level)
            # PR gives binary signal; CI gives magnitude
            if pr_linked:
                connection_strength = ci_weight
            else:
                # Cross-impact says there's a relationship even if this
                # case's production rule doesn't have a direct link
                connection_strength = ci_weight * 0.3  # attenuated

            # Outcome change proportional to delta × connection strength
            outcome_delta = effective_delta * connection_strength
            modified_outcome = max(0.0, min(1.0, baseline_outcome + outcome_delta))

            results["outcome_effects"][og] = {
                "baseline": round(baseline_outcome, 3),
                "modified": round(modified_outcome, 3),
                "change": round(modified_outcome - baseline_outcome, 4),
                "connection_strength": round(connection_strength, 3),
                "pr_linked": pr_linked,
                "ci_weight": round(ci_weight, 3),
                "connected": True,
            }

        # ── Necessary condition enforcement (Revision 4.4) ──────────────
        # If removing a condition that is necessary for specific outcomes,
        # those outcomes MUST be set to 0 regardless of proportional reduction.
        if effective_delta < 0:
            agent_condition_codes = agent.condition_categories.get(condition_type, [])
            for cond_code in agent_condition_codes:
                required_outcomes = NECESSARY_CONDITIONS.get(cond_code, [])
                for req_oc in required_outcomes:
                    req_og = None
                    for grp, cats in OUTCOME_CATEGORIES.items():
                        if req_oc in cats:
                            req_og = grp
                            break
                    if req_og and req_og in results["outcome_effects"]:
                        eff = results["outcome_effects"][req_og]
                        if isinstance(eff, dict) and eff.get("baseline") is not None:
                            # Check if condition would be fully removed
                            if new_score <= 0:
                                if req_oc in agent.outcome_categories.get(req_og, []):
                                    eff["necessary_condition_violated"] = True
                                    eff["necessary_pair"] = f"{cond_code} -> {req_oc}"
                                    eff["modified"] = 0.0
                                    eff["change"] = round(-eff["baseline"], 4)

        # ── Outcome co-occurrence propagation (Revision 4.5) ─────────
        # After computing primary effects, propagate to co-occurring outcomes
        cooccurrence_effects = {}
        for og, eff in results["outcome_effects"].items():
            if isinstance(eff, dict) and eff.get("change", 0) != 0:
                primary_change = eff["change"]
                for (og1, og2), rate in OUTCOME_COOCCURRENCE.items():
                    if og1 == og and og2 != og:
                        secondary_change = round(primary_change * rate, 4)
                        if og2 not in cooccurrence_effects:
                            cooccurrence_effects[og2] = 0.0
                        cooccurrence_effects[og2] += secondary_change
        if cooccurrence_effects:
            results["cooccurrence_effects"] = {
                og: round(val, 4) for og, val in cooccurrence_effects.items()
            }

        # ── Condition classification annotation (Revision 4.7) ────────
        cond_codes = agent.condition_categories.get(condition_type, [])
        classifications = set()
        for cc in cond_codes:
            cls = CONDITION_CLASSIFICATION.get(cc)
            if cls:
                classifications.add(cls)
        if classifications:
            results["condition_classifications"] = sorted(classifications)
            # Add resonance data for transversal conditions
            for cc in cond_codes:
                if cc in TRANSVERSAL_RESONANCE:
                    results["transversal_resonance"] = TRANSVERSAL_RESONANCE[cc]
                    break

        return results

    def _cross_impact_weights(self, condition_type: str) -> dict:
        """
        Compute normalized cross-impact weights for a condition type
        across outcome groups. Uses the quantitative matrix subtotals.
        """
        from config import CONDITION_CATEGORIES, OUTCOME_CATEGORIES

        # Sum cross-impact frequencies: condition_type → each outcome group
        ct_codes = list(CONDITION_CATEGORIES.get(condition_type, {}).keys())

        og_totals = defaultdict(int)
        for ocode, cond_counts in self.cross_impact.items():
            # Determine outcome group
            ogroup = None
            for grp, cats in OUTCOME_CATEGORIES.items():
                if ocode in cats:
                    ogroup = grp
                    break
            if not ogroup:
                continue
            for ccode in ct_codes:
                og_totals[ogroup] += cond_counts.get(ccode, 0)

        # Normalize: divide by max to get 0-1 range
        if not og_totals:
            return {}
        max_val = max(og_totals.values()) if og_totals else 1
        if max_val == 0:
            return {}
        return {og: total / max_val for og, total in og_totals.items()}

    def ecosystem_sensitivity(self, condition_type: str,
                               delta: float = 0.25) -> dict:
        """
        Vary a condition type across ALL agents that have it active.
        Returns aggregated outcome effects across the ecosystem.
        """
        results = {
            "condition_type": condition_type,
            "condition_name": CONDITION_TYPE_NAMES.get(condition_type, condition_type),
            "delta": delta,
            "cases_affected": 0,
            "cases_with_condition": 0,
            "outcome_effects": {og: {"total_change": 0, "avg_change": 0,
                                      "cases_connected": 0, "direction": ""}
                                for og in OUTCOME_GROUPS},
        }

        case_results = []
        for name, agent in self.agents.items():
            if agent.all_condition_scores.get(condition_type) is not None:
                results["cases_with_condition"] += 1
                r = self.condition_sensitivity(name, condition_type, delta)
                if r.get("status") != "not_active":
                    case_results.append(r)

        results["cases_affected"] = len(case_results)

        for og in OUTCOME_GROUPS:
            changes = []
            for r in case_results:
                eff = r["outcome_effects"].get(og, {})
                if eff.get("connected"):
                    changes.append(eff["change"])

            if changes:
                total = sum(changes)
                avg = total / len(changes)
                results["outcome_effects"][og] = {
                    "total_change": round(total, 4),
                    "avg_change": round(avg, 4),
                    "cases_connected": len(changes),
                    "max_change": round(max(changes, key=abs), 4),
                    "direction": "increase" if avg > 0 else "decrease" if avg < 0 else "none",
                }

        return results

    def full_sensitivity_matrix(self, delta: float = 0.25) -> dict:
        """
        Run ecosystem sensitivity for ALL condition types.
        Returns the complete condition-type × outcome-group sensitivity matrix.
        """
        matrix = {}
        for ct in ALL_CONDITION_TYPES:
            matrix[ct] = self.ecosystem_sensitivity(ct, delta)
        return matrix

    def condition_importance_ranking(self, outcome_group: str,
                                      delta: float = 0.25) -> list:
        """
        Rank condition types by their importance for a specific outcome group.
        Importance = average outcome change when the condition is varied.
        """
        rankings = []
        for ct in ALL_CONDITION_TYPES:
            result = self.ecosystem_sensitivity(ct, delta)
            eff = result["outcome_effects"].get(outcome_group, {})
            avg_change = abs(eff.get("avg_change", 0))
            rankings.append({
                "condition_type": ct,
                "condition_name": CONDITION_TYPE_NAMES.get(ct, ct),
                "avg_change": avg_change,
                "cases_connected": eff.get("cases_connected", 0),
                "direction": eff.get("direction", ""),
            })
        rankings.sort(key=lambda x: x["avg_change"], reverse=True)
        return rankings

    # ══════════════════════════════════════════════════════════════════
    # 2. CROSS-IMPACT ALIGNMENT
    # ══════════════════════════════════════════════════════════════════

    def cross_impact_alignment(self, delta: float = 0.25) -> dict:
        """
        Compare sensitivity analysis results against Phase 3A cross-impact
        matrix frequencies. Tests whether conditions that co-occur most
        frequently with outcomes also produce the largest sensitivity effects.

        Returns alignment assessment per outcome group.
        """
        # Get cross-impact frequencies (condition type → outcome group)
        ci_logic = self.model.cross_impact_generative_logic()

        # Get sensitivity rankings
        alignment = {}
        for og in OUTCOME_GROUPS:
            og_name = OUTCOME_GROUP_NAMES[og]

            # Cross-impact ranking
            ci_ranked = sorted(
                [e for e in ci_logic if e["outcome_group"] == og],
                key=lambda x: x["count"], reverse=True
            )

            # Sensitivity ranking
            sens_ranked = self.condition_importance_ranking(og, delta)

            # Compare top-3
            ci_top3 = [e["condition_type"] for e in ci_ranked[:3]]
            sens_top3 = [e["condition_type"] for e in sens_ranked[:3]]

            overlap = set(ci_top3) & set(sens_top3)

            alignment[og] = {
                "outcome_group": og,
                "outcome_name": og_name,
                "cross_impact_top3": ci_top3,
                "sensitivity_top3": sens_top3,
                "overlap": list(overlap),
                "alignment_score": len(overlap) / 3,
                "cross_impact_details": ci_ranked[:5],
                "sensitivity_details": sens_ranked[:5],
            }

        return alignment

    # ══════════════════════════════════════════════════════════════════
    # 3. GENERATIVE LOGIC TESTING
    # ══════════════════════════════════════════════════════════════════

    def test_generative_logic(self, delta: float = 0.25) -> dict:
        """
        Test ten domain-level generative logic claims derived from
        the dissertation's empirical analysis. Each claim posits that
        a specific condition type is among the top-3 drivers of a
        specific outcome group.

        Method: For each claim, run ecosystem-wide sensitivity analysis
        (+delta on the claimed condition), measure the average outcome
        effect, then rank all 11 condition types by their effect on
        the target outcome. A claim "holds" if the condition ranks
        in the top 3.

        Returns dict with claims list, method description, and summary.
        """
        claims = [
            # Original 4 claims
            {"claim": "Governance structures Democratic Practices",
             "condition": "GV", "outcome": "DP", "mechanism": "structural"},
            {"claim": "Technology creates affordances for Community Value",
             "condition": "TP", "outcome": "CV", "mechanism": "enabling"},
            {"claim": "Partners enable Balance",
             "condition": "PT", "outcome": "BL", "mechanism": "connective"},
            {"claim": "Politics drives Impact",
             "condition": "PO", "outcome": "IM", "mechanism": "legitimizing"},
            # 6 additional claims
            {"claim": "Technology Practices enable Democratic Practices",
             "condition": "TP", "outcome": "DP", "mechanism": "enabling"},
            {"claim": "Purpose orients Democratic Practices",
             "condition": "PU", "outcome": "DP", "mechanism": "legitimizing"},
            {"claim": "Resources sustain Community Value",
             "condition": "RS", "outcome": "CV", "mechanism": "enabling"},
            {"claim": "Resources drive Impact",
             "condition": "RS", "outcome": "IM", "mechanism": "enabling"},
            {"claim": "Technology Tools create Democratic Practices",
             "condition": "TT", "outcome": "DP", "mechanism": "enabling"},
            {"claim": "Purpose drives Impact",
             "condition": "PU", "outcome": "IM", "mechanism": "legitimizing"},
        ]

        results = []
        for claim in claims:
            eco_result = self.ecosystem_sensitivity(claim["condition"], delta)
            target_effect = eco_result["outcome_effects"].get(claim["outcome"], {})

            ranking = self.condition_importance_ranking(claim["outcome"], delta)
            top_condition = ranking[0]["condition_type"] if ranking else None

            claim_rank = next(
                (i + 1 for i, r in enumerate(ranking)
                 if r["condition_type"] == claim["condition"]),
                len(ranking)
            )

            results.append({
                "claim": claim["claim"],
                "condition_type": claim["condition"],
                "condition_name": CONDITION_TYPE_NAMES.get(claim["condition"], claim["condition"]),
                "outcome_group": claim["outcome"],
                "outcome_name": OUTCOME_GROUP_NAMES.get(claim["outcome"], claim["outcome"]),
                "expected_mechanism": claim["mechanism"],
                "avg_effect": target_effect.get("avg_change", 0),
                "cases_connected": target_effect.get("cases_connected", 0),
                "rank_among_conditions": claim_rank,
                "top_condition": top_condition,
                "top_condition_name": CONDITION_TYPE_NAMES.get(top_condition, ""),
                "holds": claim_rank <= 3,
                "strongest": claim_rank == 1,
            })

        holds_count = sum(1 for r in results if r["holds"])

        return {
            "method_description": (
                f"Each claim is tested by applying a +{delta} perturbation to the "
                f"claimed condition type across all cases where it is active, measuring "
                f"the average effect on the target outcome group, then ranking all 11 "
                f"condition types by their effect. A claim 'holds' if the condition "
                f"ranks in the top 3 for its target outcome."
            ),
            "n_claims": len(claims),
            "holds_count": holds_count,
            "delta": delta,
            "claims": results,
        }

    # ══════════════════════════════════════════════════════════════════
    # 4. COUNTER-CASE TESTING
    # ══════════════════════════════════════════════════════════════════

    def counter_case(self, case_name: str, condition_type: str,
                     new_value: float = 0.0) -> dict:
        """
        Set a condition to a specific value (typically 0 or opposite extreme)
        and compute the resulting outcome profile.

        This tests whether the production rule's encoded relationships
        hold under stress: removing a condition should reduce connected
        outcomes; adding a condition should increase them.
        """
        agent = self.model.get_agent(case_name)
        baseline_score = agent.all_condition_scores.get(condition_type)

        if baseline_score is None:
            # Condition not active: test adding it
            delta = new_value  # adding from 0
        else:
            delta = new_value - baseline_score

        result = self.condition_sensitivity(case_name, condition_type, delta)
        result["counter_case_type"] = "removal" if new_value == 0 else "addition" if baseline_score is None else "modification"
        result["new_value"] = new_value
        return result

    def remove_condition(self, case_name: str, condition_type: str) -> dict:
        """Remove a condition entirely (set to 0). Convenience wrapper."""
        return self.counter_case(case_name, condition_type, 0.0)

    def maximize_condition(self, case_name: str, condition_type: str) -> dict:
        """Set a condition to maximum (1.0). Convenience wrapper."""
        return self.counter_case(case_name, condition_type, 1.0)

    def swap_org_type_profile(self, case_name: str,
                               target_org_type: str) -> dict:
        """
        Replace a case's condition profile with the average profile of
        another organizational type. Tests whether org type is a genuine
        moderator or a correlate of typical condition profiles.
        """
        agent = self.model.get_agent(case_name)
        target_agents = self.model.get_agents_by_type(target_org_type)

        if not target_agents:
            return {"error": f"No agents of type {target_org_type}"}

        # Compute average condition scores for target type
        avg_scores = {}
        for ct in ALL_CONDITION_TYPES:
            scores = [a.all_condition_scores.get(ct) for a in target_agents
                      if a.all_condition_scores.get(ct) is not None]
            avg_scores[ct] = round(sum(scores) / len(scores), 3) if scores else None

        # Compute deltas from current profile
        results = {
            "case": case_name,
            "original_org_type": agent.org_type,
            "target_org_type": target_org_type,
            "condition_changes": {},
            "outcome_effects": {og: 0.0 for og in OUTCOME_GROUPS},
        }

        for ct in ALL_CONDITION_TYPES:
            current = agent.all_condition_scores.get(ct)
            target = avg_scores.get(ct)
            if current is not None and target is not None:
                delta = target - current
                if abs(delta) > 0.01:
                    sens = self.condition_sensitivity(case_name, ct, delta)
                    results["condition_changes"][ct] = {
                        "original": current,
                        "target": round(target, 3),
                        "delta": round(delta, 3),
                    }
                    for og in OUTCOME_GROUPS:
                        eff = sens["outcome_effects"].get(og, {})
                        results["outcome_effects"][og] += eff.get("change", 0)

        for og in OUTCOME_GROUPS:
            results["outcome_effects"][og] = round(results["outcome_effects"][og], 4)

        return results

    def external_counter_case(self, condition_profile: dict,
                               name: str = "Counter-Case") -> dict:
        """
        Create an entirely new hypothetical case with specified conditions.
        Tests what outcomes the production rules would predict for
        configurations that no empirical case exhibits.

        condition_profile: {condition_type_code: score} e.g., {"GV": 0.8, "TP": 0.9}
        """
        return self.hypothetical_case(condition_profile, name)

    # ══════════════════════════════════════════════════════════════════
    # 5. AGENT FEATURE ANALYSIS
    # ══════════════════════════════════════════════════════════════════

    # Economic sector umbrella mapping (keyed to actual Phase_1A values)
    # Plan §1.3 specifies 5 umbrella categories + Other Sectors
    SECTOR_MAP = {
        # Technology & Software (plan's list + closest fits)
        "Software / Technology services": "Technology & Software",
        "Internet communications protocol": "Technology & Software",
        "Internet service provider": "Technology & Software",
        "Commmunity wireless internet commons/internet infrastructure": "Technology & Software",
        "Community centered AI research institute": "Technology & Software",
        "Technology research for digital sovereignty": "Technology & Software",
        "Open source maps (maps as a commons)": "Technology & Software",
        "Open source digital fabrication system for modular house construction": "Technology & Software",
        "Demonstration of centering data sovereignty in how we use the internet": "Technology & Software",
        "Open source platform for electronic health records": "Technology & Software",
        "Indigenous telecommunications provider": "Technology & Software",
        # Advocacy & Rights
        "Advocacy network - indigenous data rights": "Advocacy & Rights",
        "Advocacy group for digital rights": "Advocacy & Rights",
        "Advocacy group - commons-based society": "Advocacy & Rights",
        "Algorithmic justice group": "Advocacy & Rights",
        "Data rights - cultural preservation": "Advocacy & Rights",
        "Police watchdog": "Advocacy & Rights",
        "Digital literacy": "Advocacy & Rights",
        "Slum data for advocacy": "Advocacy & Rights",
        # Research & Knowledge
        "Research as a Commons": "Research & Knowledge",
        "Community driven data infrastructure for sharing": "Research & Knowledge",
        "Crowd-sourced open science for fourth industrial revolution tech": "Research & Knowledge",
        "Environmental Action Research Lab": "Research & Knowledge",
        # Energy & Climate
        "Climate Technology / Energy Marketplace": "Energy & Climate",
        "Renewable energy": "Energy & Climate",
        "Solar energy as a commons - climate tech": "Energy & Climate",
        # Transportation & Logistics
        "Ride-hailing platform - mobility / transportation": "Transportation & Logistics",
        "Federation of logistics messengers / cooperatives": "Transportation & Logistics",
        "Delivery service": "Transportation & Logistics",
        "Mobility": "Transportation & Logistics",
        # Other Sectors (remaining cases mapped to closest fit)
        "Media organization nurturing Maori language and culture": "Other Sectors",
        "Data cooperative for health data": "Other Sectors",
        "Community-centred vacation rental platform (tourism booking)": "Other Sectors",
        "Community music events platform": "Other Sectors",
        "Maker space for developing sustainability tools, skills, and production systems": "Other Sectors",
        "Digital technology for agriculture / agritech": "Other Sectors",
        "Government administration": "Other Sectors",
        "Collaboration platform for mutual aid": "Other Sectors",
    }

    def feature_outcome_correlation(self, feature: str) -> dict:
        """
        Analyze how a specific agent feature correlates with outcome
        and sovereignty profiles. Supports custom groupings for
        condition_diversity (individual values), outcome_breadth
        (individual values), and economic_sector (umbrella categories).
        """
        agents = list(self.agents.values())

        # Custom groupings for specific features
        if feature == "condition_diversity":
            return self._custom_grouped_analysis(agents, feature, individual=True)
        elif feature == "outcome_breadth":
            return self._custom_grouped_analysis(agents, feature, individual=True)
        elif feature == "economic_sector":
            return self._sector_analysis(agents)
        elif feature in ("relational_density",):
            return self._numeric_feature_analysis(agents, feature)
        else:
            return self._categorical_feature_analysis(agents, feature)

    def _custom_grouped_analysis(self, agents: list, feature: str,
                                  individual: bool = False) -> dict:
        """Analyze by custom discrete groupings."""
        if feature == "condition_diversity":
            # 3-group split per plan: Low (2-3), Medium (4-5), High (6-7)
            group_map = {}
            for a in agents:
                val = getattr(a, feature, 0)
                if val <= 3:
                    group_map.setdefault("Low (2-3)", []).append(a)
                elif val <= 5:
                    group_map.setdefault("Medium (4-5)", []).append(a)
                else:
                    group_map.setdefault("High (6-7)", []).append(a)
            group_order = ["Low (2-3)", "Medium (4-5)", "High (6-7)"]
        elif feature == "outcome_breadth":
            # 4 individual groups
            group_map = defaultdict(list)
            for a in agents:
                val = getattr(a, feature, 0)
                group_map[str(val)].append(a)
            group_order = sorted(group_map.keys())
        else:
            group_map = defaultdict(list)
            for a in agents:
                val = getattr(a, feature, 0)
                if val is not None:
                    group_map[str(val)].append(a)
            group_order = sorted(group_map.keys())

        result = {"feature": feature, "type": "custom_grouped", "groups": {}}
        for key in group_order:
            group = group_map.get(key, [])
            if not group:
                continue
            avg_outcomes = {}
            for og in OUTCOME_GROUPS:
                scores = [a.outcome_scores.get(og) for a in group
                          if a.outcome_scores.get(og) is not None]
                avg_outcomes[og] = round(sum(scores) / len(scores), 3) if scores else 0

            avg_sov = {}
            for dim in SOVEREIGNTY_DIMENSIONS:
                vals = [a.sovereignty_profile.get(dim, 0) for a in group]
                avg_sov[dim] = round(sum(vals) / len(vals), 3)

            result["groups"][key] = {
                "count": len(group),
                "avg_outcomes": avg_outcomes,
                "avg_sovereignty": avg_sov,
                "cases": [a.name for a in group],
            }

        return result

    def _sector_analysis(self, agents: list) -> dict:
        """Analyze by economic sector using umbrella categories."""
        groups = defaultdict(list)
        for a in agents:
            raw_sector = a.economic_sector
            umbrella = self.SECTOR_MAP.get(raw_sector, "Other")
            groups[umbrella].append(a)

        result = {"feature": "economic_sector", "type": "sector_mapped", "groups": {}}
        for sector in sorted(groups.keys()):
            group = groups[sector]
            avg_outcomes = {}
            for og in OUTCOME_GROUPS:
                scores = [a.outcome_scores.get(og) for a in group
                          if a.outcome_scores.get(og) is not None]
                avg_outcomes[og] = round(sum(scores) / len(scores), 3) if scores else 0

            avg_sov = {}
            for dim in SOVEREIGNTY_DIMENSIONS:
                vals = [a.sovereignty_profile.get(dim, 0) for a in group]
                avg_sov[dim] = round(sum(vals) / len(vals), 3)

            result["groups"][sector] = {
                "count": len(group),
                "avg_outcomes": avg_outcomes,
                "avg_sovereignty": avg_sov,
                "cases": [a.name for a in group],
            }

        return result

    def _numeric_feature_analysis(self, agents: list, feature: str) -> dict:
        """Analyze correlation between a numeric feature and outcomes/sovereignty."""
        values = [getattr(a, feature, 0) for a in agents]
        values_sorted = sorted(values)
        median = values_sorted[len(values_sorted) // 2]

        high = [a for a in agents if getattr(a, feature, 0) > median]
        low = [a for a in agents if getattr(a, feature, 0) <= median]

        result = {
            "feature": feature,
            "type": "numeric",
            "median": median,
            "groups": {},
        }

        for label, group in [("high", high), ("low", low)]:
            if not group:
                continue
            avg_outcomes = {}
            for og in OUTCOME_GROUPS:
                scores = [a.outcome_scores.get(og) for a in group
                          if a.outcome_scores.get(og) is not None]
                avg_outcomes[og] = round(sum(scores) / len(scores), 3) if scores else 0

            avg_sov = {}
            for dim in SOVEREIGNTY_DIMENSIONS:
                vals = [a.sovereignty_profile.get(dim, 0) for a in group]
                avg_sov[dim] = round(sum(vals) / len(vals), 3)

            result["groups"][label] = {
                "count": len(group),
                "avg_outcomes": avg_outcomes,
                "avg_sovereignty": avg_sov,
            }

        if "high" in result["groups"] and "low" in result["groups"]:
            result["differences"] = {}
            result["sovereignty_differences"] = {}
            for og in OUTCOME_GROUPS:
                h = result["groups"]["high"]["avg_outcomes"].get(og, 0)
                l = result["groups"]["low"]["avg_outcomes"].get(og, 0)
                result["differences"][og] = round(h - l, 3)
            for dim in SOVEREIGNTY_DIMENSIONS:
                h = result["groups"]["high"]["avg_sovereignty"].get(dim, 0)
                l = result["groups"]["low"]["avg_sovereignty"].get(dim, 0)
                result["sovereignty_differences"][dim] = round(h - l, 3)

        return result

    def _categorical_feature_analysis(self, agents: list, feature: str) -> dict:
        """Analyze outcome profiles across categories of a feature."""
        groups = defaultdict(list)
        for a in agents:
            val = getattr(a, feature, None)
            if val:
                groups[val].append(a)

        result = {"feature": feature, "type": "categorical", "groups": {}}
        for val, group in groups.items():
            avg_outcomes = {}
            for og in OUTCOME_GROUPS:
                scores = [a.outcome_scores.get(og) for a in group
                          if a.outcome_scores.get(og) is not None]
                avg_outcomes[og] = round(sum(scores) / len(scores), 3) if scores else 0

            avg_sov = {}
            for dim in SOVEREIGNTY_DIMENSIONS:
                vals = [a.sovereignty_profile.get(dim, 0) for a in group]
                avg_sov[dim] = round(sum(vals) / len(vals), 3)

            result["groups"][val] = {
                "count": len(group),
                "avg_outcomes": avg_outcomes,
                "avg_sovereignty": avg_sov,
            }

        return result

    # ══════════════════════════════════════════════════════════════════
    # 6. SOVEREIGNTY PATHWAY TRACING
    # ══════════════════════════════════════════════════════════════════

    def trace_sovereignty_pathway(self, case_name: str) -> list:
        """
        Trace the full condition → mechanism → outcome → sovereignty pathway
        for a specific case. Makes the computational link visible.
        """
        agent = self.model.get_agent(case_name)
        pathways = []

        for row in agent.production_rule:
            # Get sovereignty dimensions from outcome categories
            outcome_cats = agent.outcome_categories.get(row.outcome_group, [])
            sov_dims = set()
            for oc in outcome_cats:
                sov_dims.update(OUTCOME_SOVEREIGNTY_MAP.get(oc, []))

            pathways.append({
                "condition_type": row.condition_type,
                "condition_name": row.condition_name,
                "mechanism": row.mechanism_type,
                "outcome_group": row.outcome_group,
                "outcome_name": row.outcome_name,
                "sovereignty_dimensions": sorted(sov_dims),
                "description": row.description,
            })

        return pathways

    def sovereignty_sensitivity(self, case_name: str, condition_type: str,
                                 delta: float = 0.25) -> dict:
        """
        Trace how varying a condition affects sovereignty dimensions
        (through outcome changes). Extends condition_sensitivity to the
        sovereignty layer.
        """
        sens = self.condition_sensitivity(case_name, condition_type, delta)
        agent = self.model.get_agent(case_name)

        sov_effects = {dim: 0.0 for dim in SOVEREIGNTY_DIMENSIONS}

        for og, eff in sens.get("outcome_effects", {}).items():
            if not eff.get("connected"):
                continue
            change = eff.get("change", 0)
            if change == 0:
                continue

            # Map outcome group categories to sovereignty dimensions
            outcome_cats = agent.outcome_categories.get(og, [])
            dims_affected = set()
            for oc in outcome_cats:
                dims_affected.update(OUTCOME_SOVEREIGNTY_MAP.get(oc, []))

            # Distribute change across affected dimensions
            if dims_affected:
                per_dim = change / len(dims_affected)
                for dim in dims_affected:
                    sov_effects[dim] += per_dim

        sens["sovereignty_effects"] = {
            dim: round(val, 4) for dim, val in sov_effects.items() if val != 0
        }
        return sens

    # ══════════════════════════════════════════════════════════════════
    # 7. REVERSE ANALYSIS
    # ══════════════════════════════════════════════════════════════════

    def reverse_analysis_outcome(self, target_outcome_group: str,
                                  min_score: float = 0.5) -> dict:
        """
        Starting from a desired outcome group, identify which conditions
        are most important for achieving it and which cases demonstrate it.

        This is the "what conditions do I need?" question.
        """
        # Cases that achieve the target outcome
        achievers = []
        for name, agent in self.agents.items():
            score = agent.outcome_scores.get(target_outcome_group)
            if score is not None and score >= min_score:
                achievers.append({
                    "case": name,
                    "org_type": agent.org_type,
                    "score": score,
                    "active_conditions": agent.active_condition_types,
                    "condition_diversity": agent.condition_diversity,
                })

        # Condition frequency among achievers
        cond_freq = Counter()
        for a in achievers:
            for ct in a["active_conditions"]:
                cond_freq[ct] += 1

        # Condition importance from sensitivity
        importance = self.condition_importance_ranking(target_outcome_group)

        return {
            "target_outcome": target_outcome_group,
            "target_name": OUTCOME_GROUP_NAMES.get(target_outcome_group, ""),
            "min_score": min_score,
            "achiever_count": len(achievers),
            "achievers": sorted(achievers, key=lambda x: x["score"], reverse=True),
            "condition_frequency_among_achievers": dict(cond_freq.most_common()),
            "condition_importance": importance[:5],
        }

    def reverse_analysis_sovereignty(self, target_dimension: str) -> dict:
        """
        Starting from a desired sovereignty dimension, identify which
        outcomes contribute to it, which conditions drive those outcomes,
        and which cases demonstrate capacity in this dimension.

        Mirrors reverse_analysis_outcome structure with:
        - condition_importance (sensitivity-based ranking)
        - condition_frequency_among_achievers
        - full achiever list with active conditions
        """
        # Find outcome categories that map to this dimension
        contributing_outcomes = []
        for oc, dims in OUTCOME_SOVEREIGNTY_MAP.items():
            if target_dimension in dims:
                contributing_outcomes.append(oc)

        # Find which outcome GROUPS contain the contributing outcome categories
        contributing_groups = set()
        for oc in contributing_outcomes:
            for og in OUTCOME_GROUPS:
                if oc.startswith(og):
                    contributing_groups.add(og)

        # Cases with capacity in this dimension (achievers)
        achievers = []
        for name, agent in self.agents.items():
            dim_score = agent.sovereignty_profile.get(target_dimension, 0)
            if dim_score > 0:
                achievers.append({
                    "case": name,
                    "org_type": agent.org_type,
                    "dimension_score": round(dim_score, 3),
                    "contributing_outcomes": [
                        oc for oc in contributing_outcomes
                        if oc in agent.all_active_outcome_codes
                    ],
                    "active_conditions": agent.active_condition_types,
                    "condition_diversity": agent.condition_diversity,
                })

        achievers.sort(key=lambda x: x["dimension_score"], reverse=True)

        # Condition frequency among achievers
        cond_freq = Counter()
        for a in achievers:
            for ct in a["active_conditions"]:
                cond_freq[ct] += 1

        # Condition importance: aggregate sensitivity across contributing outcome groups
        importance_scores = defaultdict(lambda: {"total_effect": 0, "cases_connected": 0})
        for og in contributing_groups:
            ranking = self.condition_importance_ranking(og)
            for r in ranking:
                ct = r["condition_type"]
                importance_scores[ct]["total_effect"] += r.get("avg_change", 0)
                importance_scores[ct]["cases_connected"] = max(
                    importance_scores[ct]["cases_connected"],
                    r.get("cases_connected", 0)
                )

        condition_importance = []
        for ct, data in importance_scores.items():
            condition_importance.append({
                "condition_type": ct,
                "condition_name": CONDITION_TYPE_NAMES.get(ct, ct),
                "avg_change": round(data["total_effect"] / len(contributing_groups), 4) if contributing_groups else 0,
                "cases_connected": data["cases_connected"],
            })
        condition_importance.sort(key=lambda x: abs(x["avg_change"]), reverse=True)

        return {
            "target_dimension": target_dimension,
            "contributing_outcome_codes": contributing_outcomes,
            "contributing_outcome_groups": sorted(contributing_groups),
            "cases_with_capacity": len(achievers),
            "condition_importance": condition_importance[:7],
            "condition_frequency_among_achievers": dict(cond_freq.most_common()),
            "top_cases": achievers[:10],
        }

    # ══════════════════════════════════════════════════════════════════
    # 8. HYPOTHETICAL CASE CREATION
    # ══════════════════════════════════════════════════════════════════

    def hypothetical_case(self, condition_profile: dict,
                           name: str = "Hypothetical",
                           org_type: str = "DSO") -> dict:
        """
        Create a hypothetical case with user-specified conditions.
        Uses the ecosystem's generative logic to predict outcomes.

        condition_profile: {condition_type: score}
        e.g., {"GV": 0.8, "TP": 0.6, "PT": 0.4, "PO": 0.7}
        """
        # Find the most similar empirical cases
        similarities = []
        for cname, agent in self.agents.items():
            overlap = 0
            for ct, score in condition_profile.items():
                agent_score = agent.all_condition_scores.get(ct)
                if agent_score is not None:
                    overlap += 1 - abs(agent_score - score)
            similarity = overlap / max(len(condition_profile), 1)
            similarities.append((cname, similarity, agent))

        similarities.sort(key=lambda x: x[1], reverse=True)
        top_similar = similarities[:5]

        # Predict outcomes using weighted average of similar cases
        predicted_outcomes = {}
        for og in OUTCOME_GROUPS:
            weighted_sum = 0
            weight_total = 0
            for cname, sim, agent in top_similar:
                score = agent.outcome_scores.get(og)
                if score is not None:
                    weighted_sum += score * sim
                    weight_total += sim
            if weight_total > 0:
                predicted_outcomes[og] = round(weighted_sum / weight_total, 3)
            else:
                predicted_outcomes[og] = None

        # Predict sovereignty profile
        predicted_sovereignty = {dim: 0.0 for dim in SOVEREIGNTY_DIMENSIONS}
        for cname, sim, agent in top_similar:
            for dim in SOVEREIGNTY_DIMENSIONS:
                predicted_sovereignty[dim] += agent.sovereignty_profile.get(dim, 0) * sim
        total_sim = sum(s[1] for s in top_similar)
        if total_sim > 0:
            for dim in SOVEREIGNTY_DIMENSIONS:
                predicted_sovereignty[dim] = round(
                    predicted_sovereignty[dim] / total_sim, 3
                )

        return {
            "name": name,
            "org_type": org_type,
            "condition_profile": condition_profile,
            "predicted_outcomes": predicted_outcomes,
            "predicted_sovereignty": predicted_sovereignty,
            "similar_cases": [
                {"case": c, "similarity": round(s, 3)}
                for c, s, _ in top_similar
            ],
            "method": "weighted_average_of_5_most_similar_cases",
        }

    # ══════════════════════════════════════════════════════════════════
    # 9. VALIDATION TESTS
    # ══════════════════════════════════════════════════════════════════

    def validate_consistency(self, n_runs: int = 3) -> dict:
        """
        Test 1: Consistency across identical runs.
        The model is deterministic, so identical inputs must produce
        identical outputs every time.
        """
        results = []
        test_case = "Te Hiku Media"

        for i in range(n_runs):
            sens = self.condition_sensitivity(test_case, "PU", 0.25)
            results.append(sens)

        # Compare all runs
        consistent = True
        for i in range(1, len(results)):
            for og in OUTCOME_GROUPS:
                eff_0 = results[0]["outcome_effects"].get(og, {})
                eff_i = results[i]["outcome_effects"].get(og, {})
                if eff_0.get("change") != eff_i.get("change"):
                    consistent = False
                    break

        return {
            "test": "consistency",
            "n_runs": n_runs,
            "case": test_case,
            "consistent": consistent,
            "status": "PASS" if consistent else "FAIL",
        }

    def validate_input_response(self) -> dict:
        """
        Test 2: Appropriate response to input changes.
        Increasing a condition connected to an outcome should increase
        that outcome (positive delta → positive effect).
        Decreasing should decrease.
        """
        test_cases = [
            ("Te Hiku Media", "PU", "IM", 0.25, "increase"),
            ("Te Hiku Media", "PU", "IM", -0.25, "decrease"),
            ("Guifi.net", "GV", "DP", 0.25, "increase"),
            ("Guifi.net", "GV", "DP", -0.25, "decrease"),
            ("Masakhane", "PT", "BL", 0.25, "increase"),
        ]

        results = []
        for case, ct, og, delta, expected_dir in test_cases:
            sens = self.condition_sensitivity(case, ct, delta)
            eff = sens["outcome_effects"].get(og, {})
            change = eff.get("change", 0)

            actual_dir = "increase" if change > 0 else "decrease" if change < 0 else "none"
            passed = actual_dir == expected_dir

            results.append({
                "case": case,
                "condition": ct,
                "outcome": og,
                "delta": delta,
                "expected": expected_dir,
                "actual": actual_dir,
                "change": change,
                "status": "PASS" if passed else "FAIL",
            })

        all_pass = all(r["status"] == "PASS" for r in results)
        return {
            "test": "input_response",
            "n_tests": len(results),
            "all_pass": all_pass,
            "details": results,
            "status": "PASS" if all_pass else "FAIL",
        }

    def validate_cross_impact_alignment(self) -> dict:
        """
        Test 3: Cross-impact alignment.
        Case-level production rules, when aggregated, should reproduce
        independently documented ecosystem-level patterns from the
        Phase 3A cross-impact matrix.
        """
        alignment = self.cross_impact_alignment()

        # Overall alignment score
        total_score = sum(a["alignment_score"] for a in alignment.values())
        avg_score = total_score / len(alignment) if alignment else 0

        return {
            "test": "cross_impact_alignment",
            "avg_alignment": round(avg_score, 2),
            "per_outcome": {
                og: {
                    "alignment_score": data["alignment_score"],
                    "cross_impact_top3": data["cross_impact_top3"],
                    "sensitivity_top3": data["sensitivity_top3"],
                    "overlap": data["overlap"],
                }
                for og, data in alignment.items()
            },
            "status": "PASS" if avg_score >= 0.5 else "PARTIAL" if avg_score > 0 else "FAIL",
        }

    def run_all_validation(self, comprehensive: bool = False) -> dict:
        """Run validation tests. If comprehensive=True, use expanded tests."""
        if comprehensive:
            return {
                "consistency": self.comprehensive_consistency_test(),
                "input_response": self.comprehensive_input_response_test(),
                "cross_impact_alignment": self.validate_cross_impact_alignment(),
                "qualitative_alignment": self.qualitative_computational_alignment(),
            }
        return {
            "consistency": self.validate_consistency(),
            "input_response": self.validate_input_response(),
            "cross_impact_alignment": self.validate_cross_impact_alignment(),
        }

    # ── Comprehensive Validation Methods (Phase 5A) ───────────────────

    def comprehensive_consistency_test(self, n_runs: int = 10) -> dict:
        """
        Test 1 (Comprehensive): Run full model n_runs times for all 43 agents.
        Record every agent's outcome scores and sovereignty capacity.
        Compare across runs. Model is deterministic → all must be identical.
        """
        # Collect per-run snapshots
        run_snapshots = []
        for _ in range(n_runs):
            snapshot = {}
            for name, agent in self.agents.items():
                # Re-run sensitivity at delta=0 to exercise the pipeline
                sens = self.condition_sensitivity(name, agent.active_condition_types[0], 0.0)
                outcome_vals = tuple(
                    round(agent.outcome_scores.get(og, 0) or 0, 10)
                    for og in OUTCOME_GROUPS
                )
                sov_vals = tuple(
                    round(agent.sovereignty_profile.get(d, 0) or 0, 10)
                    for d in SOVEREIGNTY_DIMENSIONS
                )
                snapshot[name] = (outcome_vals, sov_vals)
            run_snapshots.append(snapshot)

        # Compare all runs against first
        baseline = run_snapshots[0]
        max_outcome_dev = 0.0
        max_sov_dev = 0.0
        identical_outcomes = 0
        identical_sov = 0
        total_comparisons = 0

        for run_idx in range(1, n_runs):
            for name in baseline:
                total_comparisons += 1
                b_out, b_sov = baseline[name]
                r_out, r_sov = run_snapshots[run_idx][name]

                out_dev = max(abs(a - b) for a, b in zip(b_out, r_out))
                sov_dev = max(abs(a - b) for a, b in zip(b_sov, r_sov))

                max_outcome_dev = max(max_outcome_dev, out_dev)
                max_sov_dev = max(max_sov_dev, sov_dev)

                if out_dev < 1e-10:
                    identical_outcomes += 1
                if sov_dev < 1e-10:
                    identical_sov += 1

        pct_identical_out = (identical_outcomes / total_comparisons * 100) if total_comparisons else 100
        pct_identical_sov = (identical_sov / total_comparisons * 100) if total_comparisons else 100

        return {
            "test": "consistency",
            "n_runs": n_runs,
            "agents_tested": len(self.agents),
            "consistent": max_outcome_dev < 1e-10 and max_sov_dev < 1e-10,
            "status": "PASS" if (max_outcome_dev < 1e-10 and max_sov_dev < 1e-10) else "FAIL",
            "metrics": {
                "outcome_scores": {
                    "mean_std_across_runs": 0.0 if max_outcome_dev < 1e-10 else round(max_outcome_dev, 12),
                    "pct_identical_profiles": round(pct_identical_out, 1),
                    "max_deviation": round(max_outcome_dev, 12),
                },
                "sovereignty_capacity": {
                    "mean_std_across_runs": 0.0 if max_sov_dev < 1e-10 else round(max_sov_dev, 12),
                    "pct_identical_profiles": round(pct_identical_sov, 1),
                    "max_deviation": round(max_sov_dev, 12),
                },
            },
        }

    def comprehensive_input_response_test(self) -> dict:
        """
        Test 2 (Comprehensive): 20 hardcoded test rows spanning 7 cases,
        all 4 org types, 8+ condition types, deltas from -0.5 to +0.5.
        Returns both directional results and companion qualitative data.
        """
        test_specs = [
            # (case, condition_type, outcome_group, delta, expected_direction)
            # Te Hiku Media (DSO) — PU, TT, RG
            ("Te Hiku Media", "PU", "DP", 0.25, "increase"),
            ("Te Hiku Media", "PU", "IM", -0.25, "decrease"),
            ("Te Hiku Media", "TT", "DP", 0.5, "increase"),
            ("Te Hiku Media", "RG", "BL", 0.25, "increase"),
            # FNIGC (DSO) — GV, RS
            ("FNIGC", "GV", "DP", 0.25, "increase"),
            ("FNIGC", "GV", "IM", -0.25, "decrease"),
            ("FNIGC", "RS", "IM", 0.25, "increase"),
            # Guifi.net (DC) — GV, TP, RS
            ("Guifi.net", "GV", "DP", 0.25, "increase"),
            ("Guifi.net", "TP", "CV", 0.5, "increase"),
            ("Guifi.net", "RS", "CV", -0.5, "decrease"),
            # CoopCycle (DC) — GV, RS
            ("CoopCycle", "GV", "DP", -0.25, "decrease"),
            ("CoopCycle", "RS", "CV", 0.25, "increase"),
            # Participatory Brazil (PG) — GV, SC, TT
            ("Participatory Brazil", "GV", "DP", -0.25, "decrease"),
            ("Participatory Brazil", "SC", "IM", 0.25, "increase"),
            ("Participatory Brazil", "TT", "IM", 0.25, "increase"),
            # Matrix (PP) — TP, GV, PO
            ("Matrix", "TP", "CV", 0.25, "increase"),
            ("Matrix", "GV", "DP", -0.5, "decrease"),
            ("Matrix", "PO", "IM", 0.25, "increase"),
            # Masakhane (DSO) — PU, PT
            ("Masakhane", "PU", "DP", 0.5, "increase"),
            ("Masakhane", "PT", "BL", -0.25, "decrease"),
        ]

        details = []
        companion = []
        pass_count = 0

        for case, ct, og, delta, expected_dir in test_specs:
            agent = self.agents.get(case)
            if not agent:
                continue

            # Check condition is active for this case
            if agent.all_condition_scores.get(ct) is None:
                # Condition not active — skip gracefully
                details.append({
                    "case": case, "condition": ct,
                    "condition_name": CONDITION_TYPE_NAMES.get(ct, ct),
                    "outcome": og, "delta": delta,
                    "expected": expected_dir, "actual": "n/a",
                    "change": 0, "status": "SKIP",
                })
                companion.append({
                    "case": case, "condition": ct,
                    "condition_name": CONDITION_TYPE_NAMES.get(ct, ct),
                    "delta": delta, "descriptor": "condition not active",
                    "mechanism": "n/a", "affected_outcomes": [],
                    "outcome_changes": {},
                })
                continue

            sens = self.condition_sensitivity(case, ct, delta)
            eff = sens["outcome_effects"].get(og, {})
            change = eff.get("change", 0)
            actual_dir = "increase" if change > 0 else "decrease" if change < 0 else "none"
            passed = actual_dir == expected_dir
            if passed:
                pass_count += 1

            details.append({
                "case": case,
                "condition": ct,
                "condition_name": CONDITION_TYPE_NAMES.get(ct, ct),
                "outcome": og,
                "delta": delta,
                "expected": expected_dir,
                "actual": actual_dir,
                "change": round(change, 4),
                "status": "PASS" if passed else "FAIL",
            })

            # Build companion: qualitative descriptor + mechanism + full outcome vector
            pr_descriptors = []
            pr_mechanisms = set()
            for row in agent.production_rule:
                if row.condition_type == ct:
                    pr_descriptors.append(row.description[:60] if row.description else "")
                    pr_mechanisms.add(row.mechanism_type)

            outcome_changes = {}
            for o_grp in OUTCOME_GROUPS:
                o_eff = sens["outcome_effects"].get(o_grp, {})
                o_change = o_eff.get("change", 0)
                if o_change != 0:
                    outcome_changes[o_grp] = round(o_change, 4)

            companion.append({
                "case": case,
                "condition": ct,
                "condition_name": CONDITION_TYPE_NAMES.get(ct, ct),
                "delta": delta,
                "descriptor": "; ".join(d for d in pr_descriptors if d)[:200],
                "mechanism": "+".join(sorted(pr_mechanisms)) if pr_mechanisms else "unknown",
                "affected_outcomes": list(outcome_changes.keys()),
                "outcome_changes": outcome_changes,
            })

        active_tests = [d for d in details if d["status"] != "SKIP"]
        active_pass = sum(1 for d in active_tests if d["status"] == "PASS")
        n_active = len(active_tests)

        return {
            "test": "input_response",
            "n_tests": n_active,
            "pass_count": active_pass,
            "all_pass": active_pass == n_active,
            "details": details,
            "companion": companion,
            "status": "PASS" if active_pass == n_active else "FAIL",
        }

    def qualitative_computational_alignment(self) -> dict:
        """
        Test 4: Compare model's aggregated mechanism-descriptor patterns
        against Phase 3B's qualitative characterizations.
        For each condition type, check whether the computationally dominant
        mechanism matches the qualitatively documented mechanism.
        """
        # Phase 3B qualitative characterizations (hardcoded from Pattern Summary)
        PHASE_3B = {
            "TP": {"mechanism": "enabling", "actions": "enable, ground, design"},
            "RS": {"mechanism": "enabling", "actions": "build, support, align"},
            "GV": {"mechanism": "structural", "actions": "structure, distribute, govern"},
            "TT": {"mechanism": "enabling", "actions": "facilitate, instantiate, operationalize"},
            "PT": {"mechanism": "connective", "actions": "exchange, connect, coordinate"},
            "PU": {"mechanism": "legitimizing", "actions": "orient, ground, motivate"},
            "OI": {"mechanism": "positioning", "actions": "define, position, embody"},
            "PO": {"mechanism": "legitimizing", "actions": "advocate, legitimize, drive"},
            "RG": {"mechanism": "protective", "actions": "formalize, assert, protect"},
            "SC": {"mechanism": "enabling", "actions": "embed, respond, enable"},
            "PR": {"mechanism": "mixed", "actions": "counter, motivate, drive"},
        }

        # Aggregate mechanism types from production rules
        from collections import Counter
        mech_by_ct = defaultdict(Counter)
        total_rules = 0
        for agent in self.agents.values():
            for row in agent.production_rule:
                if row.condition_type and row.mechanism_type:
                    for m in row.mechanism_type.split("+"):
                        mech_by_ct[row.condition_type][m.strip()] += 1
                    total_rules += 1

        per_condition = []
        aligned_count = 0
        for ct_code in ALL_CONDITION_TYPES:
            counts = mech_by_ct.get(ct_code, Counter())
            computational_dominant = counts.most_common(1)[0][0] if counts else "none"
            computational_count = counts.most_common(1)[0][1] if counts else 0

            qual = PHASE_3B.get(ct_code, {})
            qual_mechanism = qual.get("mechanism", "unknown")
            qual_actions = qual.get("actions", "")

            # Determine alignment
            if qual_mechanism == computational_dominant:
                alignment = "ALIGNED"
                aligned_count += 1
            elif qual_mechanism in ("mixed", "positioning"):
                # These don't map directly to the five mechanism types
                alignment = "PARTIAL"
            elif computational_dominant in qual_mechanism or qual_mechanism in computational_dominant:
                alignment = "PARTIAL"
            else:
                alignment = "DIVERGENT"

            per_condition.append({
                "condition_type": ct_code,
                "condition_name": CONDITION_TYPE_NAMES.get(ct_code, ct_code),
                "qualitative_mechanism": qual_mechanism,
                "qualitative_actions": qual_actions,
                "computational_mechanism": computational_dominant,
                "computational_count": computational_count,
                "total_rules": sum(counts.values()),
                "alignment": alignment,
            })

        # Per-mechanism summary
        mechanism_totals = Counter()
        mechanism_cts = defaultdict(list)
        for ct_code, counts in mech_by_ct.items():
            for m, c in counts.items():
                mechanism_totals[m] += c
                if ct_code not in mechanism_cts[m]:
                    mechanism_cts[m].append(ct_code)

        per_mechanism = []
        for mech, count in mechanism_totals.most_common():
            per_mechanism.append({
                "mechanism": mech,
                "computational_count": count,
                "pct_of_total": round(count / total_rules * 100, 1) if total_rules else 0,
                "condition_types": sorted(mechanism_cts[mech]),
            })

        alignment_rate = aligned_count / len(ALL_CONDITION_TYPES) if ALL_CONDITION_TYPES else 0
        partial_count = sum(1 for pc in per_condition if pc["alignment"] == "PARTIAL")

        return {
            "test": "qualitative_computational_alignment",
            "status": "PASS" if alignment_rate >= 0.7 else "PARTIAL" if alignment_rate >= 0.5 else "FAIL",
            "alignment_rate": round(alignment_rate, 2),
            "aligned": aligned_count,
            "partial": partial_count,
            "divergent": len(ALL_CONDITION_TYPES) - aligned_count - partial_count,
            "total_condition_types": len(ALL_CONDITION_TYPES),
            "per_condition": per_condition,
            "per_mechanism": per_mechanism,
        }

    # ══════════════════════════════════════════════════════════════════
    # INTERNAL HELPERS
    # ══════════════════════════════════════════════════════════════════

    def _get_condition_outcome_connections(self, agent: Agent) -> dict:
        """
        Build a connection matrix for an agent: {(cond_type, outcome_group): count}.
        Cached per agent.
        """
        if agent.name in self._connection_cache:
            return self._connection_cache[agent.name]

        connections = defaultdict(int)
        for row in agent.production_rule:
            if row.condition_type and row.outcome_group:
                connections[(row.condition_type, row.outcome_group)] += 1

        self._connection_cache[agent.name] = dict(connections)
        return dict(connections)

    # ══════════════════════════════════════════════════════════════════
    # 10. CONDITION INTERACTION ANALYSIS (Revision 4.6)
    # ══════════════════════════════════════════════════════════════════

    def condition_interaction_analysis(self, cond_type_1: str, cond_type_2: str,
                                        outcome_group: str = None) -> dict:
        """
        Analyze interaction effects between two condition types.

        Compares outcome profiles across three groups:
        - Both conditions active
        - Only condition 1 active
        - Only condition 2 active
        - Neither active

        Reports whether the combination produces effects different
        from either alone (configurational logic interpretation).
        """
        both = []
        only_1 = []
        only_2 = []
        neither = []

        for name, agent in self.agents.items():
            has_1 = agent.all_condition_scores.get(cond_type_1) is not None
            has_2 = agent.all_condition_scores.get(cond_type_2) is not None

            if has_1 and has_2:
                both.append(agent)
            elif has_1 and not has_2:
                only_1.append(agent)
            elif not has_1 and has_2:
                only_2.append(agent)
            else:
                neither.append(agent)

        def avg_outcomes(group):
            if not group:
                return {og: None for og in OUTCOME_GROUPS}
            result = {}
            for og in OUTCOME_GROUPS:
                scores = [a.outcome_scores.get(og) for a in group
                          if a.outcome_scores.get(og) is not None]
                result[og] = round(sum(scores) / len(scores), 3) if scores else None
            return result

        both_outcomes = avg_outcomes(both)
        only1_outcomes = avg_outcomes(only_1)
        only2_outcomes = avg_outcomes(only_2)
        neither_outcomes = avg_outcomes(neither)

        # Compute interaction effects
        interaction_effects = {}
        target_groups = [outcome_group] if outcome_group else OUTCOME_GROUPS
        for og in target_groups:
            b = both_outcomes.get(og)
            o1 = only1_outcomes.get(og)
            o2 = only2_outcomes.get(og)
            n = neither_outcomes.get(og)

            if b is not None and o1 is not None and o2 is not None and n is not None:
                # Expected additive effect: (effect of 1 alone) + (effect of 2 alone)
                # Effect of 1 alone = o1 - n; Effect of 2 alone = o2 - n
                additive_expected = (o1 - n) + (o2 - n) + n
                actual = b
                interaction_term = round(actual - additive_expected, 4)
                interaction_effects[og] = {
                    "both": b,
                    "only_1": o1,
                    "only_2": o2,
                    "neither": n,
                    "additive_expected": round(additive_expected, 3),
                    "actual": actual,
                    "interaction_effect": interaction_term,
                    "interaction_type": (
                        "synergistic" if interaction_term > 0.05
                        else "antagonistic" if interaction_term < -0.05
                        else "additive"
                    ),
                }
            else:
                interaction_effects[og] = {
                    "both": b, "only_1": o1, "only_2": o2, "neither": n,
                    "interaction_effect": None,
                    "interaction_type": "insufficient_data",
                }

        return {
            "condition_1": cond_type_1,
            "condition_2": cond_type_2,
            "condition_1_name": CONDITION_TYPE_NAMES.get(cond_type_1, cond_type_1),
            "condition_2_name": CONDITION_TYPE_NAMES.get(cond_type_2, cond_type_2),
            "group_sizes": {
                "both": len(both),
                "only_1": len(only_1),
                "only_2": len(only_2),
                "neither": len(neither),
            },
            "interaction_effects": interaction_effects,
        }

    # ══════════════════════════════════════════════════════════════════
    # 11. BRIDGE B: TERRAIN-CAPACITY GAP ANALYSIS (Revision 4.2)
    # ══════════════════════════════════════════════════════════════════

    def terrain_capacity_gap(self, case_name: str = None) -> dict:
        """
        Analyze the gap between sovereignty terrain (conditions operate on)
        and sovereignty capacity (outcomes construct).

        Positive gap = terrain without constructed capacity (unrealized)
        Negative gap = capacity exceeds terrain engagement (emergent)

        If case_name given, returns single case analysis.
        If None, returns ecosystem-level analysis.
        """
        if case_name:
            agent = self.model.get_agent(case_name)
            gap = {}
            for dim in SOVEREIGNTY_DIMENSIONS:
                terrain = agent.sovereignty_terrain.get(dim, 0)
                capacity = agent.sovereignty_profile.get(dim, 0)
                gap[dim] = {
                    "terrain": terrain,
                    "capacity": capacity,
                    "gap": round(terrain - capacity, 3),
                    "interpretation": (
                        "unrealized" if terrain - capacity > 0.1
                        else "emergent" if capacity - terrain > 0.1
                        else "aligned"
                    ),
                }
            return {
                "case": case_name,
                "dimensions": gap,
                "unrealized_dimensions": [d for d, v in gap.items()
                                           if v["interpretation"] == "unrealized"],
                "emergent_dimensions": [d for d, v in gap.items()
                                        if v["interpretation"] == "emergent"],
            }
        else:
            # Ecosystem-level: average gap across all agents
            avg_gap = {dim: {"terrain": 0, "capacity": 0, "gap": 0}
                       for dim in SOVEREIGNTY_DIMENSIONS}
            count = len(self.agents)
            for agent in self.agents.values():
                for dim in SOVEREIGNTY_DIMENSIONS:
                    avg_gap[dim]["terrain"] += agent.sovereignty_terrain.get(dim, 0)
                    avg_gap[dim]["capacity"] += agent.sovereignty_profile.get(dim, 0)
            for dim in SOVEREIGNTY_DIMENSIONS:
                avg_gap[dim]["terrain"] = round(avg_gap[dim]["terrain"] / count, 3)
                avg_gap[dim]["capacity"] = round(avg_gap[dim]["capacity"] / count, 3)
                avg_gap[dim]["gap"] = round(
                    avg_gap[dim]["terrain"] - avg_gap[dim]["capacity"], 3
                )
            return {
                "ecosystem": True,
                "agent_count": count,
                "avg_dimensions": avg_gap,
            }

    # ══════════════════════════════════════════════════════════════════
    # 12. RECURSIVE PATTERN ASSIGNMENT (Revision 4.3)
    # ══════════════════════════════════════════════════════════════════

    def assign_recursive_patterns(self, case_name: str = None) -> dict:
        """
        Assign 17 recursive D-A-S patterns (BINARY).

        Each production rule row has a mechanism type constraining which
        patterns are reachable. Condition-outcome context selects specific
        patterns. Assignment is binary: a case either participates in a
        pattern or not, regardless of how many rows trigger it.
        """
        def assign_row_patterns(row):
            """Assign recursive patterns to a single production rule row."""
            mechanism = row.mechanism_type.split("+")[0].strip()
            # Try refinement based on condition type + outcome group
            key = (row.condition_type, row.outcome_group)
            refined = RECURSIVE_PATTERN_REFINEMENT.get(key)
            if refined:
                return refined
            return MECHANISM_RECURSIVE_MAP.get(mechanism, [])

        if case_name:
            agent = self.model.get_agent(case_name)
            rows = []
            pattern_set = set()
            for row in agent.production_rule:
                patterns = assign_row_patterns(row)
                pattern_set.update(patterns)
                rows.append({
                    "condition": f"{row.condition_type} ({', '.join(row.condition_codes)})",
                    "mechanism": row.mechanism_type,
                    "outcome": f"{row.outcome_group} ({', '.join(row.outcome_codes)})",
                    "recursive_patterns": patterns,
                    "pattern_names": [RECURSIVE_PATTERNS.get(p, f"#{p}") for p in patterns],
                })

            sorted_patterns = sorted(pattern_set)
            return {
                "case": case_name,
                "rows": rows,
                "patterns": sorted_patterns,
                "pattern_names": [RECURSIVE_PATTERNS.get(p, f"#{p}") for p in sorted_patterns],
                "pattern_count": len(sorted_patterns),
            }
        else:
            # Ecosystem-level: how many cases participate in each pattern (binary)
            pattern_cases = defaultdict(set)  # pattern_id → set of case names
            case_patterns = {}  # case_name → sorted list of pattern IDs
            for name, agent in self.agents.items():
                case_set = set()
                for row in agent.production_rule:
                    patterns = assign_row_patterns(row)
                    case_set.update(patterns)
                    for p in patterns:
                        pattern_cases[p].add(name)
                case_patterns[name] = sorted(case_set)

            return {
                "ecosystem": True,
                "total_cases": len(self.agents),
                "pattern_frequency": {
                    p: {"cases": len(cases), "name": RECURSIVE_PATTERNS.get(p, f"#{p}")}
                    for p, cases in sorted(pattern_cases.items(),
                                           key=lambda x: -len(x[1]))
                },
                "most_common_patterns": [
                    {"id": p, "name": RECURSIVE_PATTERNS.get(p, f"#{p}"),
                     "cases": len(cases),
                     "case_names": sorted(cases)}
                    for p, cases in sorted(pattern_cases.items(),
                                           key=lambda x: -len(x[1]))[:5]
                ],
                "case_patterns": case_patterns,
            }

    # ══════════════════════════════════════════════════════════════════
    # 13. OUTCOME CO-OCCURRENCE ANALYSIS (Revision 4.5)
    # ══════════════════════════════════════════════════════════════════

    def outcome_cooccurrence_analysis(self) -> dict:
        """
        Analyze empirical outcome co-occurrence patterns across 43 cases.
        Validates the documented 71% DP-CV co-occurrence rate and reports
        all pairwise co-occurrence frequencies.
        """
        group_presence = defaultdict(set)
        for name, agent in self.agents.items():
            for og in OUTCOME_GROUPS:
                if agent.outcome_scores.get(og) is not None:
                    group_presence[og].add(name)

        cooccurrence = {}
        for i, og1 in enumerate(OUTCOME_GROUPS):
            for og2 in OUTCOME_GROUPS[i + 1:]:
                both = group_presence[og1] & group_presence[og2]
                either = group_presence[og1] | group_presence[og2]
                cases_with_og1 = len(group_presence[og1])
                rate = len(both) / cases_with_og1 if cases_with_og1 > 0 else 0
                cooccurrence[f"{og1}-{og2}"] = {
                    "both_present": len(both),
                    "either_present": len(either),
                    "og1_total": cases_with_og1,
                    "og2_total": len(group_presence[og2]),
                    "cooccurrence_rate": round(rate, 3),
                    "jaccard_similarity": round(
                        len(both) / len(either), 3) if either else 0,
                    "cases": sorted(both),
                }

        return {
            "pairwise": cooccurrence,
            "dp_cv_rate": cooccurrence.get("DP-CV", {}).get("cooccurrence_rate", 0),
            "documented_dp_cv_rate": 0.71,
        }
