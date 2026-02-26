"""
Relational Analytical Engine: the second model.

Holds primary model's condition-outcome-sovereignty relationships constant.
Varies data relations (partner types, relationship types, relational density)
as the independent variable to observe how relational context shapes outcomes.

Operations:
  1. Relational density sensitivity (vary D1-D4 dimensions)
  2. Partner type effects (add/remove partner types)
  3. Relationship type effects (vary PT1-PT6 profiles)
  4. Agent-agent interactions (7 directly partnered cases)
  5. Cluster analysis (Indigenous Data Sovereignty, Enspiral-Loomio)
  6. Latent cluster activation (simulate formalizing indirect connections)
  7. Relational density as moderator (high vs low density, same conditions)
"""

from collections import defaultdict, Counter
from config import (
    OUTCOME_GROUPS, OUTCOME_GROUP_NAMES, SOVEREIGNTY_DIMENSIONS,
    PARTNER_TYPES, RELATIONSHIP_TYPES, ORG_TYPE_NAMES,
    DIRECT_PARTNERSHIPS, LATENT_CLUSTERS,
)


class RelationalEngine:
    """
    Analytical operations for the second model.

    All primary model variables (conditions, outcomes, production rules,
    sovereignty) are held constant. Data relations vary.
    """

    def __init__(self, model, analytical_engine=None):
        """
        Args:
            model: PrimaryModel instance
            analytical_engine: AnalyticalEngine (for sovereignty computations)
        """
        self.model = model
        self.agents = model.agents
        self.analytical = analytical_engine

    # ══════════════════════════════════════════════════════════════════
    # 1. RELATIONAL DENSITY SENSITIVITY
    # ══════════════════════════════════════════════════════════════════

    def density_dimension_sensitivity(self, dimension: str) -> dict:
        """
        Test what happens to outcome profiles when a single relational
        density dimension is varied while all other variables remain constant.

        Dimensions: D1 (partner_diversity), D2 (relationship_type_range),
                    D3 (network_reach), D4 (inter_case_connectivity)

        Groups agents into high/low on the dimension and compares outcomes.
        """
        dim_map = {
            "D1": "partner_diversity",
            "D2": "relationship_type_range",
            "D3": "network_reach",
            "D4": "inter_case_connectivity",
        }
        attr = dim_map.get(dimension)
        if not attr:
            return {"error": f"Unknown dimension: {dimension}"}

        # Get dimension values
        values = []
        for name, agent in self.agents.items():
            rp = agent.relational_profile
            if rp:
                val = getattr(rp, attr, 0) or 0
                values.append((name, agent, val))

        if not values:
            return {"error": "No relational profiles loaded"}

        # Split at median; handle edge case where all values ≤ median
        sorted_vals = sorted(v[2] for v in values)
        median = sorted_vals[len(sorted_vals) // 2]

        high = [(n, a) for n, a, v in values if v > median]
        low = [(n, a) for n, a, v in values if v <= median]

        # If one group is empty, split by index at midpoint
        if not high or not low:
            sorted_by_val = sorted(values, key=lambda x: x[2])
            mid = len(sorted_by_val) // 2
            low = [(n, a) for n, a, v in sorted_by_val[:mid]]
            high = [(n, a) for n, a, v in sorted_by_val[mid:]]

        result = {
            "dimension": dimension,
            "attribute": attr,
            "median": median,
            "high_group": self._group_outcomes(high),
            "low_group": self._group_outcomes(low),
            "differences": {},
        }

        # Compute differences
        for og in OUTCOME_GROUPS:
            h = result["high_group"]["avg_outcomes"].get(og, 0)
            l = result["low_group"]["avg_outcomes"].get(og, 0)
            result["differences"][og] = {
                "high_avg": h,
                "low_avg": l,
                "delta": round(h - l, 4),
                "direction": "high > low" if h > l else "low > high" if l > h else "equal",
            }

        # Sovereignty differences
        result["sovereignty_differences"] = {}
        for dim in SOVEREIGNTY_DIMENSIONS:
            h = result["high_group"]["avg_sovereignty"].get(dim, 0)
            l = result["low_group"]["avg_sovereignty"].get(dim, 0)
            result["sovereignty_differences"][dim] = {
                "delta": round(h - l, 4),
                "direction": "high > low" if h > l else "low > high" if l > h else "equal",
            }

        return result

    def full_density_sensitivity(self) -> dict:
        """Run density sensitivity for all four dimensions."""
        return {d: self.density_dimension_sensitivity(d) for d in ["D1", "D2", "D3", "D4"]}

    # ══════════════════════════════════════════════════════════════════
    # 2. PARTNER TYPE EFFECTS
    # ══════════════════════════════════════════════════════════════════

    def partner_type_effect(self, partner_type_id: int) -> dict:
        """
        Compare outcome and sovereignty profiles between cases that have
        a specific partner type versus those that do not.
        """
        pt_name = PARTNER_TYPES.get(partner_type_id, f"Type {partner_type_id}")

        has_pt = []
        lacks_pt = []
        for name, agent in self.agents.items():
            rp = agent.relational_profile
            if rp and partner_type_id in (rp.partner_types_engaged or []):
                has_pt.append((name, agent))
            else:
                lacks_pt.append((name, agent))

        result = {
            "partner_type": partner_type_id,
            "partner_type_name": pt_name,
            "has_count": len(has_pt),
            "lacks_count": len(lacks_pt),
            "has_group": self._group_outcomes(has_pt),
            "lacks_group": self._group_outcomes(lacks_pt),
            "outcome_differences": {},
            "sovereignty_differences": {},
        }

        for og in OUTCOME_GROUPS:
            h = result["has_group"]["avg_outcomes"].get(og, 0)
            l = result["lacks_group"]["avg_outcomes"].get(og, 0)
            result["outcome_differences"][og] = {
                "has_avg": h, "lacks_avg": l,
                "delta": round(h - l, 4),
            }

        for dim in SOVEREIGNTY_DIMENSIONS:
            h = result["has_group"]["avg_sovereignty"].get(dim, 0)
            l = result["lacks_group"]["avg_sovereignty"].get(dim, 0)
            result["sovereignty_differences"][dim] = {
                "delta": round(h - l, 4),
            }

        return result

    def all_partner_type_effects(self) -> dict:
        """Run partner type effect analysis for all 12 partner types."""
        return {pt: self.partner_type_effect(pt) for pt in PARTNER_TYPES}

    def partner_type_combination_effect(self, pt_ids: list) -> dict:
        """
        Test whether specific partner type combinations produce different
        outcomes than either type alone. Mirrors the primary model's
        configurational logic applied to relational territory.
        """
        # Cases with ALL specified partner types
        has_all = []
        has_some = []
        has_none = []

        for name, agent in self.agents.items():
            rp = agent.relational_profile
            engaged = set(rp.partner_types_engaged or []) if rp else set()

            if set(pt_ids).issubset(engaged):
                has_all.append((name, agent))
            elif engaged & set(pt_ids):
                has_some.append((name, agent))
            else:
                has_none.append((name, agent))

        return {
            "partner_types": pt_ids,
            "partner_type_names": [PARTNER_TYPES.get(pt, f"Type {pt}") for pt in pt_ids],
            "has_all": self._group_outcomes(has_all),
            "has_some": self._group_outcomes(has_some),
            "has_none": self._group_outcomes(has_none),
            "combinatorial_effect": self._compute_combinatorial_effect(
                has_all, has_some, has_none
            ),
        }

    def _compute_combinatorial_effect(self, has_all, has_some, has_none):
        """Compute whether combination exceeds individual effects."""
        if not has_all or not has_some:
            return {"status": "insufficient_data"}

        effects = {}
        for og in OUTCOME_GROUPS:
            all_avg = self._avg_outcome(has_all, og)
            some_avg = self._avg_outcome(has_some, og)
            none_avg = self._avg_outcome(has_none, og)
            effects[og] = {
                "all_avg": all_avg,
                "some_avg": some_avg,
                "none_avg": none_avg,
                "combinatorial_premium": round(all_avg - some_avg, 4),
                "synergy": all_avg > some_avg > none_avg,
            }
        return effects

    # ══════════════════════════════════════════════════════════════════
    # 3. RELATIONSHIP TYPE EFFECTS
    # ══════════════════════════════════════════════════════════════════

    def relationship_type_effect(self, rel_type: str) -> dict:
        """
        Compare outcome profiles between cases exhibiting a specific
        relationship type (PT1-PT6) versus those that do not.
        """
        has_rt = []
        lacks_rt = []
        for name, agent in self.agents.items():
            rp = agent.relational_profile
            if rp and rel_type in (rp.relationship_types or []):
                has_rt.append((name, agent))
            else:
                lacks_rt.append((name, agent))

        rel_name = RELATIONSHIP_TYPES.get(rel_type, rel_type)
        result = {
            "relationship_type": rel_type,
            "relationship_name": rel_name,
            "has_count": len(has_rt),
            "lacks_count": len(lacks_rt),
            "has_group": self._group_outcomes(has_rt),
            "lacks_group": self._group_outcomes(lacks_rt),
            "outcome_differences": {},
            "sovereignty_differences": {},
        }

        for og in OUTCOME_GROUPS:
            h = result["has_group"]["avg_outcomes"].get(og, 0)
            l = result["lacks_group"]["avg_outcomes"].get(og, 0)
            result["outcome_differences"][og] = {
                "has_avg": h, "lacks_avg": l,
                "delta": round(h - l, 4),
            }

        for dim in SOVEREIGNTY_DIMENSIONS:
            h = result["has_group"]["avg_sovereignty"].get(dim, 0)
            l = result["lacks_group"]["avg_sovereignty"].get(dim, 0)
            result["sovereignty_differences"][dim] = round(h - l, 4)

        return result

    def all_relationship_type_effects(self) -> dict:
        """Run relationship type effect analysis for PT1-PT6."""
        return {rt: self.relationship_type_effect(rt) for rt in RELATIONSHIP_TYPES}

    def relationship_combination_effect(self, rel_types: list) -> dict:
        """
        Test whether specific relationship type combinations (e.g.,
        PT1+PT3 vs PT1+PT5) produce distinctive outcome profiles.
        """
        has_combo = []
        lacks_combo = []

        for name, agent in self.agents.items():
            rp = agent.relational_profile
            engaged = set(rp.relationship_types or []) if rp else set()
            if set(rel_types).issubset(engaged):
                has_combo.append((name, agent))
            else:
                lacks_combo.append((name, agent))

        return {
            "relationship_types": rel_types,
            "names": [RELATIONSHIP_TYPES.get(rt, rt) for rt in rel_types],
            "has_combo": self._group_outcomes(has_combo),
            "lacks_combo": self._group_outcomes(lacks_combo),
        }

    # ══════════════════════════════════════════════════════════════════
    # 4. AGENT-AGENT INTERACTIONS
    # ══════════════════════════════════════════════════════════════════

    def agent_agent_analysis(self) -> dict:
        """
        Analyze the 7 directly partnered cases as functioning relational
        ecosystems. Tests whether shared partnerships produce convergent
        or divergent outcome profiles.
        """
        # Build adjacency dict from partnership pairs
        partnerships = defaultdict(set)
        for a, b in DIRECT_PARTNERSHIPS:
            partnerships[a].add(b)
            partnerships[b].add(a)

        results = {}
        for case_name, partner_names in partnerships.items():
            agent = self.model.get_agent(case_name)
            if not agent:
                continue

            partner_agents = []
            for pname in partner_names:
                pa = self.model.get_agent(pname)
                if pa:
                    partner_agents.append(pa)

            if not partner_agents:
                continue

            # Compare outcome profiles
            outcome_convergence = {}
            for og in OUTCOME_GROUPS:
                case_score = agent.outcome_scores.get(og)
                partner_scores = [pa.outcome_scores.get(og)
                                  for pa in partner_agents
                                  if pa.outcome_scores.get(og) is not None]
                if case_score is not None and partner_scores:
                    avg_partner = sum(partner_scores) / len(partner_scores)
                    diff = abs(case_score - avg_partner)
                    outcome_convergence[og] = {
                        "case_score": round(case_score, 3),
                        "partner_avg": round(avg_partner, 3),
                        "difference": round(diff, 3),
                        "convergent": diff < 0.2,
                    }

            # Compare sovereignty profiles
            sov_convergence = {}
            for dim in SOVEREIGNTY_DIMENSIONS:
                case_val = agent.sovereignty_profile.get(dim, 0)
                partner_vals = [pa.sovereignty_profile.get(dim, 0)
                                for pa in partner_agents]
                if partner_vals:
                    avg_partner = sum(partner_vals) / len(partner_vals)
                    sov_convergence[dim] = {
                        "case_val": round(case_val, 3),
                        "partner_avg": round(avg_partner, 3),
                        "convergent": abs(case_val - avg_partner) < 0.15,
                    }

            # Shared partner types
            case_pts = set(agent.relational_profile.partner_types_engaged or [])
            shared_pts = set()
            for pa in partner_agents:
                pa_pts = set(pa.relational_profile.partner_types_engaged or [])
                shared_pts.update(case_pts & pa_pts)

            results[case_name] = {
                "partners": sorted(partner_names),
                "n_partners": len(partner_agents),
                "outcome_convergence": outcome_convergence,
                "sovereignty_convergence": sov_convergence,
                "shared_partner_types": sorted(shared_pts),
                "org_types": [agent.org_type] + [pa.org_type for pa in partner_agents],
            }

        return results

    # ══════════════════════════════════════════════════════════════════
    # 5. CLUSTER ANALYSIS
    # ══════════════════════════════════════════════════════════════════

    def cluster_analysis(self, cluster_name: str) -> dict:
        """
        Analyze a named cluster (e.g., 'Indigenous Data Sovereignty',
        'Enspiral-Loomio') as a functioning relational ecosystem.

        Computes collective density, shared patterns, and whether the
        cluster exhibits emergent properties not visible case-by-case.
        """
        # Find cluster members
        members = []
        if cluster_name in LATENT_CLUSTERS:
            for case in LATENT_CLUSTERS[cluster_name]:
                agent = self.model.get_agent(case)
                if agent:
                    members.append((case, agent))

        # Also check direct partnerships that form clusters
        if cluster_name == "Indigenous Data Sovereignty":
            for case in ["GIDA", "Te Mana Raraunga", "MAIAM NAYRI WINGARA",
                          "FNIGC", "Te Hiku Media"]:
                agent = self.model.get_agent(case)
                if agent and case not in [m[0] for m in members]:
                    members.append((case, agent))
        elif cluster_name == "Enspiral-Loomio":
            for case in ["Enspiral", "Loomio"]:
                agent = self.model.get_agent(case)
                if agent and case not in [m[0] for m in members]:
                    members.append((case, agent))

        if not members:
            return {"error": f"No members found for cluster '{cluster_name}'"}

        # Collective metrics
        densities = [a.relational_profile.composite_score
                     for _, a in members
                     if a.relational_profile and a.relational_profile.composite_score]
        sum_individual = sum(densities) if densities else 0
        avg_individual = sum_individual / len(densities) if densities else 0

        # Outcome profiles
        cluster_outcomes = self._group_outcomes(members)

        # Sovereignty profiles
        all_partner_types = set()
        all_rel_types = set()
        for _, a in members:
            rp = a.relational_profile
            if rp:
                all_partner_types.update(rp.partner_types_engaged or [])
                all_rel_types.update(rp.relationship_types or [])

        # Compare to non-cluster cases
        non_members = [(n, a) for n, a in self.agents.items()
                       if n not in [m[0] for m in members]]
        non_cluster_outcomes = self._group_outcomes(non_members)

        return {
            "cluster": cluster_name,
            "members": [m[0] for m in members],
            "n_members": len(members),
            "avg_relational_density": round(avg_individual, 3),
            "sum_densities": round(sum_individual, 3),
            "cluster_outcomes": cluster_outcomes,
            "non_cluster_outcomes": non_cluster_outcomes,
            "outcome_differences": {
                og: round(
                    cluster_outcomes["avg_outcomes"].get(og, 0) -
                    non_cluster_outcomes["avg_outcomes"].get(og, 0), 4
                )
                for og in OUTCOME_GROUPS
            },
            "collective_partner_types": sorted(all_partner_types),
            "collective_relationship_types": sorted(all_rel_types),
            "emergent_properties": self._detect_emergent(members, non_members),
        }

    def _detect_emergent(self, members, non_members):
        """Detect whether cluster exhibits properties not visible case-by-case."""
        if not members or not non_members:
            return {"status": "insufficient_data"}

        # Check if cluster outcome breadth exceeds average member breadth
        member_breadths = [a.outcome_breadth for _, a in members]
        avg_member_breadth = sum(member_breadths) / len(member_breadths) if member_breadths else 0

        # Collective breadth: union of all outcome groups across members
        collective_groups = set()
        for _, a in members:
            collective_groups.update(a.active_outcome_groups)
        collective_breadth = len(collective_groups)

        # Non-cluster average breadth
        nc_breadths = [a.outcome_breadth for _, a in non_members]
        avg_nc_breadth = sum(nc_breadths) / len(nc_breadths) if nc_breadths else 0

        # Sovereignty coverage: how many dimensions > 0
        member_sov_counts = []
        for _, a in members:
            active_dims = sum(1 for d in SOVEREIGNTY_DIMENSIONS
                              if a.sovereignty_profile.get(d, 0) > 0)
            member_sov_counts.append(active_dims)
        avg_member_sov = sum(member_sov_counts) / len(member_sov_counts) if member_sov_counts else 0

        # Collective sovereignty coverage
        collective_sov = set()
        for _, a in members:
            for dim in SOVEREIGNTY_DIMENSIONS:
                if a.sovereignty_profile.get(dim, 0) > 0:
                    collective_sov.add(dim)

        return {
            "avg_member_outcome_breadth": round(avg_member_breadth, 2),
            "collective_outcome_breadth": collective_breadth,
            "breadth_emergence": collective_breadth > avg_member_breadth,
            "avg_member_sovereignty_dimensions": round(avg_member_sov, 2),
            "collective_sovereignty_dimensions": len(collective_sov),
            "sovereignty_emergence": len(collective_sov) > avg_member_sov,
            "avg_non_cluster_breadth": round(avg_nc_breadth, 2),
            "cluster_exceeds_non_cluster": avg_member_breadth > avg_nc_breadth,
        }

    # ══════════════════════════════════════════════════════════════════
    # 6. LATENT CLUSTER ACTIVATION
    # ══════════════════════════════════════════════════════════════════

    def simulate_cluster_activation(self, cluster_name: str) -> dict:
        """
        Simulate what would happen if cases in a latent cluster formalized
        their indirect connections into direct partnerships.

        Uses the layered prediction engine to estimate outcome and sovereignty
        changes for each member based on increased inter-case connectivity
        and shared partner type expansion.
        """
        current = self.cluster_analysis(cluster_name)
        if "error" in current:
            return current

        members = current["members"]
        member_agents = [(n, self.model.get_agent(n)) for n in members]
        member_agents = [(n, a) for n, a in member_agents if a and a.relational_profile]

        if not member_agents:
            return {"error": "No members with relational profiles"}

        # Compute collective partner types across all members
        collective_pts = set()
        for _, a in member_agents:
            collective_pts.update(a.relational_profile.partner_types_engaged or [])

        # Use convergence data from existing partnerships to estimate direction
        existing_interactions = self.agent_agent_analysis()
        avg_convergence = {og: [] for og in OUTCOME_GROUPS}
        for case_data in existing_interactions.values():
            for og, conv in case_data.get("outcome_convergence", {}).items():
                if conv.get("convergent"):
                    avg_convergence[og].append(conv["difference"])

        convergence_direction = {}
        for og in OUTCOME_GROUPS:
            vals = avg_convergence[og]
            if vals:
                convergence_direction[og] = round(sum(vals) / len(vals), 4)
            else:
                convergence_direction[og] = 0

        # For each member, predict effects of activation
        simulated_effects = {
            "cluster": cluster_name,
            "members": members,
            "n_members": len(member_agents),
            "current_avg_density": current["avg_relational_density"],
            "collective_partner_types": sorted(collective_pts),
            "convergence_direction": convergence_direction,
            "member_predictions": {},
        }

        outcome_predictions_sum = {og: 0 for og in OUTCOME_GROUPS}
        sov_predictions_sum = {dim: 0 for dim in SOVEREIGNTY_DIMENSIONS}

        for case_name, agent in member_agents:
            rp = agent.relational_profile
            current_d4 = rp.inter_case_connectivity or 0
            current_pts = set(rp.partner_types_engaged or [])

            # Simulate: each member gains access to collective partner types
            # and increases D4 by the number of new within-cluster connections
            potential_new_connections = len(member_agents) - 1
            new_d4 = min(4, current_d4 + min(potential_new_connections, 3))
            new_pts = sorted(current_pts | collective_pts)

            # Run prediction
            pred = self.relational_sensitivity(
                case_name,
                modified_partner_types=new_pts,
                modified_d4=new_d4,
            )

            if "error" not in pred:
                member_pred = {
                    "current_D4": current_d4,
                    "simulated_D4": new_d4,
                    "pt_gained": sorted(set(new_pts) - current_pts),
                    "outcome_effects": pred["outcome_effects"],
                    "sovereignty_effects": pred["sovereignty_effects"],
                    "density_change": round(
                        pred["modified_profile"]["composite"] -
                        pred["original_profile"]["composite"], 3
                    ),
                }
                simulated_effects["member_predictions"][case_name] = member_pred

                for og in OUTCOME_GROUPS:
                    outcome_predictions_sum[og] += pred["outcome_effects"][og]["predicted"]
                for dim in SOVEREIGNTY_DIMENSIONS:
                    sov_predictions_sum[dim] += pred["sovereignty_effects"][dim]["predicted"]

        n = len(simulated_effects["member_predictions"])
        if n > 0:
            simulated_effects["avg_predicted_outcomes"] = {
                og: round(outcome_predictions_sum[og] / n, 3) for og in OUTCOME_GROUPS
            }
            simulated_effects["avg_predicted_sovereignty"] = {
                dim: round(sov_predictions_sum[dim] / n, 3) for dim in SOVEREIGNTY_DIMENSIONS
            }
            # Compare to current cluster averages
            simulated_effects["outcome_change"] = {
                og: round(
                    simulated_effects["avg_predicted_outcomes"][og] -
                    current["cluster_outcomes"]["avg_outcomes"].get(og, 0), 3
                ) for og in OUTCOME_GROUPS
            }
            simulated_effects["sovereignty_change"] = {
                dim: round(
                    simulated_effects["avg_predicted_sovereignty"][dim] -
                    current["cluster_outcomes"]["avg_sovereignty"].get(dim, 0), 3
                ) for dim in SOVEREIGNTY_DIMENSIONS
            }

        return simulated_effects

    # ══════════════════════════════════════════════════════════════════
    # 7. RELATIONAL DENSITY AS MODERATOR
    # ══════════════════════════════════════════════════════════════════

    def density_as_moderator(self) -> dict:
        """
        Test whether relational density moderates condition-outcome
        relationships. Cases with similar condition profiles but different
        relational density should produce different outcomes if density
        is a genuine moderator.
        """
        # Split into high/low density
        agents_with_density = []
        for name, agent in self.agents.items():
            rp = agent.relational_profile
            if rp and rp.composite_score is not None:
                agents_with_density.append((name, agent, rp.composite_score))

        agents_with_density.sort(key=lambda x: x[2])
        mid = len(agents_with_density) // 2
        low_density = agents_with_density[:mid]
        high_density = agents_with_density[mid:]

        # Compare condition diversity → outcome relationships
        result = {
            "high_density": {
                "count": len(high_density),
                "avg_density": round(sum(x[2] for x in high_density) / len(high_density), 3),
                "avg_outcomes": {},
                "avg_condition_diversity": round(
                    sum(a.condition_diversity for _, a, _ in high_density) / len(high_density), 2
                ),
            },
            "low_density": {
                "count": len(low_density),
                "avg_density": round(sum(x[2] for x in low_density) / len(low_density), 3),
                "avg_outcomes": {},
                "avg_condition_diversity": round(
                    sum(a.condition_diversity for _, a, _ in low_density) / len(low_density), 2
                ),
            },
            "moderation_evidence": {},
        }

        for og in OUTCOME_GROUPS:
            h_scores = [a.outcome_scores.get(og) for _, a, _ in high_density
                        if a.outcome_scores.get(og) is not None]
            l_scores = [a.outcome_scores.get(og) for _, a, _ in low_density
                        if a.outcome_scores.get(og) is not None]
            h_avg = sum(h_scores) / len(h_scores) if h_scores else 0
            l_avg = sum(l_scores) / len(l_scores) if l_scores else 0
            result["high_density"]["avg_outcomes"][og] = round(h_avg, 3)
            result["low_density"]["avg_outcomes"][og] = round(l_avg, 3)
            result["moderation_evidence"][og] = {
                "difference": round(h_avg - l_avg, 4),
                "direction": "density_amplifies" if h_avg > l_avg else "density_constrains" if l_avg > h_avg else "no_effect",
            }

        # Find "matched pairs" — cases with similar condition diversity
        # but different density
        matched = self._find_matched_pairs(agents_with_density)
        result["matched_pairs"] = matched

        return result

    def _find_matched_pairs(self, agents_sorted_by_density):
        """Find pairs with similar conditions but different density."""
        pairs = []
        n = len(agents_sorted_by_density)

        for i in range(n):
            for j in range(i + 1, n):
                name_i, agent_i, d_i = agents_sorted_by_density[i]
                name_j, agent_j, d_j = agents_sorted_by_density[j]

                # Similar condition diversity (within 1)
                if abs(agent_i.condition_diversity - agent_j.condition_diversity) <= 1:
                    # Different density (at least 0.5 apart)
                    if abs(d_i - d_j) >= 0.5:
                        # Compare outcomes
                        outcome_diffs = {}
                        for og in OUTCOME_GROUPS:
                            s_i = agent_i.outcome_scores.get(og)
                            s_j = agent_j.outcome_scores.get(og)
                            if s_i is not None and s_j is not None:
                                outcome_diffs[og] = round(s_j - s_i, 3)
                            else:
                                outcome_diffs[og] = 0.0

                        pairs.append({
                            "low": name_i,
                            "high": name_j,
                            "low_density": round(d_i, 2),
                            "high_density": round(d_j, 2),
                            "condition_diversity_low": agent_i.condition_diversity,
                            "condition_diversity_high": agent_j.condition_diversity,
                            "outcome_differences": outcome_diffs,
                        })

        # Return most illustrative pairs (largest density gap)
        pairs.sort(key=lambda x: abs(x["high_density"] - x["low_density"]), reverse=True)
        return pairs[:10]

    # ══════════════════════════════════════════════════════════════════
    # COMPREHENSIVE SECOND MODEL REPORT
    # ══════════════════════════════════════════════════════════════════

    def full_report(self) -> dict:
        """Generate the complete second model analysis."""
        return {
            "density_sensitivity": self.full_density_sensitivity(),
            "partner_type_effects": self.all_partner_type_effects(),
            "relationship_type_effects": self.all_relationship_type_effects(),
            "agent_agent_interactions": self.agent_agent_analysis(),
            "indigenous_cluster": self.cluster_analysis("Indigenous Data Sovereignty"),
            "enspiral_loomio": self.cluster_analysis("Enspiral-Loomio"),
            "density_moderation": self.density_as_moderator(),
        }

    # ══════════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════════

    def _group_outcomes(self, case_list) -> dict:
        """Compute average outcomes and sovereignty for a group of cases."""
        if not case_list:
            return {"count": 0, "avg_outcomes": {}, "avg_sovereignty": {}}

        avg_outcomes = {}
        for og in OUTCOME_GROUPS:
            scores = [a.outcome_scores.get(og) for _, a in case_list
                      if a.outcome_scores.get(og) is not None]
            avg_outcomes[og] = round(sum(scores) / len(scores), 3) if scores else 0

        avg_sov = {}
        for dim in SOVEREIGNTY_DIMENSIONS:
            vals = [a.sovereignty_profile.get(dim, 0) for _, a in case_list]
            avg_sov[dim] = round(sum(vals) / len(vals), 3)

        return {
            "count": len(case_list),
            "cases": [n for n, _ in case_list],
            "avg_outcomes": avg_outcomes,
            "avg_sovereignty": avg_sov,
        }

    def _avg_outcome(self, case_list, og):
        """Average outcome score for a group."""
        scores = [a.outcome_scores.get(og) for _, a in case_list
                  if a.outcome_scores.get(og) is not None]
        return round(sum(scores) / len(scores), 3) if scores else 0

    # ══════════════════════════════════════════════════════════════════
    # 8. DENSITY DISTRIBUTION (actual scores, no high/low split)
    # ══════════════════════════════════════════════════════════════════

    def density_distribution(self) -> dict:
        """
        Return every case's actual relational density scores (composite + 4
        dimensions) alongside their outcome scores and sovereignty profiles.
        No median split — the frontend renders correlations from raw data.
        """
        cases = []
        for name, agent in self.agents.items():
            rp = agent.relational_profile
            if not rp:
                continue
            entry = {
                "name": name,
                "org_type": agent.org_type,
                "composite": round(rp.composite_score, 3) if rp.composite_score else 0,
                "D1": rp.partner_diversity or 0,
                "D1_norm": round(rp.partner_diversity_norm, 3),
                "D2": rp.relationship_type_range or 0,
                "D2_norm": round(rp.relationship_type_range_norm, 3),
                "D3": rp.network_reach or 0,
                "D3_norm": round(rp.network_reach_norm, 3),
                "D4": rp.inter_case_connectivity or 0,
                "D4_norm": round(rp.inter_case_connectivity_norm, 3),
                "outcomes": {
                    og: round(agent.outcome_scores.get(og), 3)
                    for og in OUTCOME_GROUPS
                    if agent.outcome_scores.get(og) is not None
                },
                "sovereignty": {
                    dim: round(agent.sovereignty_profile.get(dim, 0), 3)
                    for dim in SOVEREIGNTY_DIMENSIONS
                },
            }
            cases.append(entry)

        # Compute correlations (Pearson-like) for composite and each dimension
        correlations = {}
        composite_vals = [c["composite"] for c in cases]
        for metric in ["composite", "D1_norm", "D2_norm", "D3_norm", "D4_norm"]:
            vals = [c[metric] for c in cases]
            metric_corrs = {}
            for og in OUTCOME_GROUPS:
                og_vals = [c["outcomes"].get(og, 0) for c in cases]
                metric_corrs[og] = self._pearson(vals, og_vals)
            for dim in SOVEREIGNTY_DIMENSIONS:
                sov_vals = [c["sovereignty"].get(dim, 0) for c in cases]
                metric_corrs[f"sov_{dim}"] = self._pearson(vals, sov_vals)
            correlations[metric] = metric_corrs

        return {
            "cases": sorted(cases, key=lambda x: x["composite"], reverse=True),
            "correlations": correlations,
            "n_cases": len(cases),
        }

    @staticmethod
    def _pearson(x, y):
        """Simple Pearson correlation coefficient."""
        n = len(x)
        if n < 3:
            return 0.0
        mx = sum(x) / n
        my = sum(y) / n
        num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
        dx = (sum((xi - mx) ** 2 for xi in x)) ** 0.5
        dy = (sum((yi - my) ** 2 for yi in y)) ** 0.5
        if dx == 0 or dy == 0:
            return 0.0
        return round(num / (dx * dy), 4)


    # ══════════════════════════════════════════════════════════════════
    # 9. RELATIONAL SENSITIVITY PREDICTION (Layered Effects Engine)
    # ══════════════════════════════════════════════════════════════════

    def _compute_learned_effects(self):
        """
        Pre-compute cross-case learned effects from all analytical tabs.
        Returns a dict of effect tables used by the prediction engine.
        Called once per engine lifetime, cached.
        """
        if hasattr(self, '_learned_cache'):
            return self._learned_cache

        # --- Partner type effects ---
        pt_effects = {}
        for pt_id in PARTNER_TYPES:
            eff = self.partner_type_effect(pt_id)
            pt_effects[pt_id] = {
                "outcomes": {
                    og: eff["outcome_differences"][og]["delta"]
                    for og in OUTCOME_GROUPS
                },
                "sovereignty": {
                    dim: eff["sovereignty_differences"][dim]["delta"]
                    for dim in SOVEREIGNTY_DIMENSIONS
                },
                "has_count": eff["has_count"],
                "lacks_count": eff["lacks_count"],
            }

        # --- Relationship type effects ---
        rt_effects = {}
        for rt in RELATIONSHIP_TYPES:
            eff = self.relationship_type_effect(rt)
            rt_effects[rt] = {
                "outcomes": {
                    og: eff["outcome_differences"][og]["delta"]
                    for og in OUTCOME_GROUPS
                },
                "sovereignty": {
                    dim: eff["sovereignty_differences"].get(dim, {}).get("delta", 0)
                    if isinstance(eff["sovereignty_differences"].get(dim), dict)
                    else eff["sovereignty_differences"].get(dim, 0)
                    for dim in SOVEREIGNTY_DIMENSIONS
                },
                "has_count": eff["has_count"],
                "lacks_count": eff["lacks_count"],
            }

        # --- Network reach (D3) correlations ---
        dd = self.density_distribution()
        d3_correlations = {}
        for og in OUTCOME_GROUPS:
            d3_correlations[og] = dd["correlations"]["D3_norm"].get(og, 0)
        for dim in SOVEREIGNTY_DIMENSIONS:
            d3_correlations[f"sov_{dim}"] = dd["correlations"]["D3_norm"].get(f"sov_{dim}", 0)

        # --- Inter-case connectivity (D4) effect ---
        has_d4 = []
        lacks_d4 = []
        for name, agent in self.agents.items():
            rp = agent.relational_profile
            if not rp:
                continue
            if (rp.inter_case_connectivity or 0) > 0:
                has_d4.append((name, agent))
            else:
                lacks_d4.append((name, agent))
        d4_effects = {"outcomes": {}, "sovereignty": {}}
        has_grp = self._group_outcomes(has_d4)
        lacks_grp = self._group_outcomes(lacks_d4)
        for og in OUTCOME_GROUPS:
            d4_effects["outcomes"][og] = round(
                has_grp["avg_outcomes"].get(og, 0) - lacks_grp["avg_outcomes"].get(og, 0), 4
            )
        for dim in SOVEREIGNTY_DIMENSIONS:
            d4_effects["sovereignty"][dim] = round(
                has_grp["avg_sovereignty"].get(dim, 0) - lacks_grp["avg_sovereignty"].get(dim, 0), 4
            )
        d4_effects["has_count"] = len(has_d4)
        d4_effects["lacks_count"] = len(lacks_d4)

        # --- Matched-pairs density coefficient ---
        pairs = self.enriched_matched_pairs()
        density_coefficients = {"outcomes": {}, "sovereignty": {}}
        if pairs:
            for og in OUTCOME_GROUPS:
                weighted_rates = []
                for p in pairs:
                    gap = p["density_gap"]
                    od = p["outcome_diffs"].get(og)
                    if od and gap > 0.1:
                        weighted_rates.append(od["delta"] / gap)
                density_coefficients["outcomes"][og] = (
                    round(sum(weighted_rates) / len(weighted_rates), 4)
                    if weighted_rates else 0
                )
            for dim in SOVEREIGNTY_DIMENSIONS:
                weighted_rates = []
                for p in pairs:
                    gap = p["density_gap"]
                    sd = p["sovereignty_diffs"].get(dim)
                    if sd and gap > 0.1:
                        weighted_rates.append(sd["delta"] / gap)
                density_coefficients["sovereignty"][dim] = (
                    round(sum(weighted_rates) / len(weighted_rates), 4)
                    if weighted_rates else 0
                )

        self._learned_cache = {
            "pt_effects": pt_effects,
            "rt_effects": rt_effects,
            "d3_correlations": d3_correlations,
            "d4_effects": d4_effects,
            "density_coefficients": density_coefficients,
        }
        return self._learned_cache

    def relational_sensitivity(self, case_name: str,
                                modified_partner_types: list = None,
                                modified_relationship_types: list = None,
                                modified_d3: int = None,
                                modified_d4: int = None) -> dict:
        """
        Layered prediction engine: predict outcome and sovereignty effects
        when a case's relational profile is modified.

        Layers learned effects from:
          1. Partner type differentials (50% attenuation)
          2. Relationship type differentials (50% attenuation)
          3. Network reach (D3) correlation-based adjustment
          4. Inter-case connectivity (D4) effect
          5. Matched-pairs density calibration (dampening check)

        D1 and D2 are auto-computed from partner types and relationship
        types, not user-modifiable.
        """
        agent = self.model.get_agent(case_name)
        if not agent or not agent.relational_profile:
            return {"error": f"Case '{case_name}' not found or has no relational profile"}

        learned = self._compute_learned_effects()
        rp = agent.relational_profile
        ATTENUATION = 0.5

        # --- Original profile ---
        orig_pts = set(rp.partner_types_engaged or [])
        orig_rts = set(rp.relationship_types or [])
        orig_d3 = rp.network_reach or 0
        orig_d4 = rp.inter_case_connectivity or 0
        orig_d1 = rp.partner_diversity or 0
        orig_d2 = rp.relationship_type_range or 0

        # --- Modified profile ---
        mod_pts = set(modified_partner_types) if modified_partner_types is not None else set(orig_pts)
        mod_rts = set(modified_relationship_types) if modified_relationship_types is not None else set(orig_rts)
        mod_d3 = modified_d3 if modified_d3 is not None else orig_d3
        mod_d4 = modified_d4 if modified_d4 is not None else orig_d4
        mod_d1 = len(mod_pts)
        mod_d2 = len(mod_rts)

        # --- Original scores (baseline) ---
        orig_outcomes = {
            og: round(agent.outcome_scores.get(og) or 0, 4) for og in OUTCOME_GROUPS
        }
        orig_sovereignty = {
            dim: round(agent.sovereignty_profile.get(dim, 0), 4)
            for dim in SOVEREIGNTY_DIMENSIONS
        }

        # --- Layer 1: Partner type effects ---
        pt_added = sorted(mod_pts - orig_pts)
        pt_removed = sorted(orig_pts - mod_pts)
        pt_outcome_delta = {og: 0.0 for og in OUTCOME_GROUPS}
        pt_sov_delta = {dim: 0.0 for dim in SOVEREIGNTY_DIMENSIONS}

        for pt_id in pt_added:
            eff = learned["pt_effects"].get(pt_id, {})
            for og in OUTCOME_GROUPS:
                pt_outcome_delta[og] += (eff.get("outcomes", {}).get(og, 0) * ATTENUATION)
            for dim in SOVEREIGNTY_DIMENSIONS:
                pt_sov_delta[dim] += (eff.get("sovereignty", {}).get(dim, 0) * ATTENUATION)
        for pt_id in pt_removed:
            eff = learned["pt_effects"].get(pt_id, {})
            for og in OUTCOME_GROUPS:
                pt_outcome_delta[og] -= (eff.get("outcomes", {}).get(og, 0) * ATTENUATION)
            for dim in SOVEREIGNTY_DIMENSIONS:
                pt_sov_delta[dim] -= (eff.get("sovereignty", {}).get(dim, 0) * ATTENUATION)

        # --- Layer 2: Relationship type effects ---
        rt_added = sorted(mod_rts - orig_rts)
        rt_removed = sorted(orig_rts - mod_rts)
        rt_outcome_delta = {og: 0.0 for og in OUTCOME_GROUPS}
        rt_sov_delta = {dim: 0.0 for dim in SOVEREIGNTY_DIMENSIONS}

        for rt in rt_added:
            eff = learned["rt_effects"].get(rt, {})
            for og in OUTCOME_GROUPS:
                rt_outcome_delta[og] += (eff.get("outcomes", {}).get(og, 0) * ATTENUATION)
            for dim in SOVEREIGNTY_DIMENSIONS:
                rt_sov_delta[dim] += (eff.get("sovereignty", {}).get(dim, 0) * ATTENUATION)
        for rt in rt_removed:
            eff = learned["rt_effects"].get(rt, {})
            for og in OUTCOME_GROUPS:
                rt_outcome_delta[og] -= (eff.get("outcomes", {}).get(og, 0) * ATTENUATION)
            for dim in SOVEREIGNTY_DIMENSIONS:
                rt_sov_delta[dim] -= (eff.get("sovereignty", {}).get(dim, 0) * ATTENUATION)

        # --- Layer 3: Network reach (D3) correlation-based ---
        d3_outcome_delta = {og: 0.0 for og in OUTCOME_GROUPS}
        d3_sov_delta = {dim: 0.0 for dim in SOVEREIGNTY_DIMENSIONS}
        d3_change = mod_d3 - orig_d3
        if d3_change != 0:
            d3_norm_change = d3_change / 2.0
            d3_corrs = learned["d3_correlations"]
            for og in OUTCOME_GROUPS:
                corr = d3_corrs.get(og, 0)
                d3_outcome_delta[og] = corr * d3_norm_change * 0.15
            for dim in SOVEREIGNTY_DIMENSIONS:
                corr = d3_corrs.get(f"sov_{dim}", 0)
                d3_sov_delta[dim] = corr * d3_norm_change * 0.15

        # --- Layer 4: Inter-case connectivity (D4) effect ---
        d4_outcome_delta = {og: 0.0 for og in OUTCOME_GROUPS}
        d4_sov_delta = {dim: 0.0 for dim in SOVEREIGNTY_DIMENSIONS}
        d4_change = mod_d4 - orig_d4
        if d4_change != 0:
            d4_eff = learned["d4_effects"]
            d4_frac = d4_change / 4.0
            for og in OUTCOME_GROUPS:
                d4_outcome_delta[og] = d4_eff["outcomes"].get(og, 0) * d4_frac * ATTENUATION
            for dim in SOVEREIGNTY_DIMENSIONS:
                d4_sov_delta[dim] = d4_eff["sovereignty"].get(dim, 0) * d4_frac * ATTENUATION

        # --- Sum component effects ---
        raw_outcome_delta = {}
        raw_sov_delta = {}
        for og in OUTCOME_GROUPS:
            raw_outcome_delta[og] = (
                pt_outcome_delta[og] + rt_outcome_delta[og] +
                d3_outcome_delta[og] + d4_outcome_delta[og]
            )
        for dim in SOVEREIGNTY_DIMENSIONS:
            raw_sov_delta[dim] = (
                pt_sov_delta[dim] + rt_sov_delta[dim] +
                d3_sov_delta[dim] + d4_sov_delta[dim]
            )

        # --- Layer 5: Matched-pairs density calibration ---
        orig_composite = (orig_d1 / 12 + orig_d2 / 6 + orig_d3 / 3 + orig_d4 / 4)
        mod_composite = (mod_d1 / 12 + mod_d2 / 6 + mod_d3 / 3 + mod_d4 / 4)
        density_change = mod_composite - orig_composite

        density_coeff = learned["density_coefficients"]
        dampening = 1.0
        if abs(density_change) > 0.1:
            divergence_count = 0
            for og in OUTCOME_GROUPS:
                coeff_pred = density_coeff["outcomes"].get(og, 0) * density_change
                comp_pred = raw_outcome_delta[og]
                if abs(comp_pred) > 0.01 and abs(coeff_pred) > 0.001:
                    ratio = abs(comp_pred) / abs(coeff_pred) if coeff_pred != 0 else 1
                    if ratio > 2.0:
                        divergence_count += 1
            if divergence_count >= 2:
                dampening = 0.7

        # --- Compute final predictions ---
        outcome_effects = {}
        for og in OUTCOME_GROUPS:
            orig_val = orig_outcomes[og]
            delta = round(raw_outcome_delta[og] * dampening, 4)
            pred = round(max(0, min(1, orig_val + delta)), 3)
            pct = round(delta / orig_val * 100, 1) if orig_val > 0.01 else 0
            outcome_effects[og] = {
                "original": round(orig_val, 3),
                "predicted": pred,
                "delta": delta,
                "pct_change": pct,
            }

        sovereignty_effects = {}
        for dim in SOVEREIGNTY_DIMENSIONS:
            orig_val = orig_sovereignty[dim]
            delta = round(raw_sov_delta[dim] * dampening, 4)
            pred = round(max(0, orig_val + delta), 3)
            pct = round(delta / orig_val * 100, 1) if orig_val > 0.01 else 0
            sovereignty_effects[dim] = {
                "original": round(orig_val, 3),
                "predicted": pred,
                "delta": delta,
                "pct_change": pct,
            }

        # --- Effect layers breakdown ---
        layers = {
            "partner_types": {
                "outcomes": {og: round(pt_outcome_delta[og], 4) for og in OUTCOME_GROUPS},
                "sovereignty": {dim: round(pt_sov_delta[dim], 4) for dim in SOVEREIGNTY_DIMENSIONS},
            },
            "relationship_types": {
                "outcomes": {og: round(rt_outcome_delta[og], 4) for og in OUTCOME_GROUPS},
                "sovereignty": {dim: round(rt_sov_delta[dim], 4) for dim in SOVEREIGNTY_DIMENSIONS},
            },
            "network_reach": {
                "outcomes": {og: round(d3_outcome_delta[og], 4) for og in OUTCOME_GROUPS},
                "sovereignty": {dim: round(d3_sov_delta[dim], 4) for dim in SOVEREIGNTY_DIMENSIONS},
            },
            "inter_case_connectivity": {
                "outcomes": {og: round(d4_outcome_delta[og], 4) for og in OUTCOME_GROUPS},
                "sovereignty": {dim: round(d4_sov_delta[dim], 4) for dim in SOVEREIGNTY_DIMENSIONS},
            },
            "dampening_applied": dampening,
        }

        # --- Similar cases (for reference) ---
        similarities = []
        for other_name, other_agent in self.agents.items():
            orp = other_agent.relational_profile
            if not orp:
                continue
            other_pts = set(orp.partner_types_engaged or [])
            other_rts = set(orp.relationship_types or [])
            pt_union = mod_pts | other_pts
            pt_sim = len(mod_pts & other_pts) / len(pt_union) if pt_union else 1.0
            rt_union = mod_rts | other_rts
            rt_sim = len(mod_rts & other_rts) / len(rt_union) if rt_union else 1.0
            dim_diffs = []
            for dk, mx, mod_v, attr in [
                ("D1", 12, mod_d1, "partner_diversity"),
                ("D2", 6, mod_d2, "relationship_type_range"),
                ("D3", 3, mod_d3, "network_reach"),
                ("D4", 4, mod_d4, "inter_case_connectivity"),
            ]:
                other_v = getattr(orp, attr) or 0
                dim_diffs.append(((mod_v / mx) - (other_v / mx)) ** 2)
            dim_sim = max(0, 1 - (sum(dim_diffs) / 4) ** 0.5)
            composite_sim = 0.35 * pt_sim + 0.25 * rt_sim + 0.40 * dim_sim
            similarities.append((other_name, other_agent, round(composite_sim, 4)))
        similarities.sort(key=lambda x: x[2], reverse=True)
        top_k = similarities[:7]

        # --- Changes summary ---
        dim_changes = {}
        if mod_d1 != orig_d1:
            dim_changes["D1"] = {"original": orig_d1, "modified": mod_d1, "delta": mod_d1 - orig_d1}
        if mod_d2 != orig_d2:
            dim_changes["D2"] = {"original": orig_d2, "modified": mod_d2, "delta": mod_d2 - orig_d2}
        if mod_d3 != orig_d3:
            dim_changes["D3"] = {"original": orig_d3, "modified": mod_d3, "delta": mod_d3 - orig_d3}
        if mod_d4 != orig_d4:
            dim_changes["D4"] = {"original": orig_d4, "modified": mod_d4, "delta": mod_d4 - orig_d4}

        return {
            "case": case_name,
            "changes": {
                "partner_types_added": pt_added,
                "partner_types_removed": pt_removed,
                "relationship_types_added": rt_added,
                "relationship_types_removed": rt_removed,
                "dimension_changes": dim_changes,
            },
            "modified_profile": {
                "partner_types": sorted(mod_pts),
                "relationship_types": sorted(mod_rts),
                "D1": mod_d1, "D2": mod_d2, "D3": mod_d3, "D4": mod_d4,
                "composite": round(mod_composite, 3),
            },
            "original_profile": {
                "partner_types": sorted(orig_pts),
                "relationship_types": sorted(orig_rts),
                "D1": orig_d1, "D2": orig_d2, "D3": orig_d3, "D4": orig_d4,
                "composite": round(orig_composite, 3),
            },
            "outcome_effects": outcome_effects,
            "sovereignty_effects": sovereignty_effects,
            "effect_layers": layers,
            "similar_cases": [
                {
                    "name": n,
                    "similarity": s,
                    "org_type": a.org_type,
                    "partner_types": sorted(a.relational_profile.partner_types_engaged or []),
                    "relationship_types": sorted(a.relational_profile.relationship_types or []),
                    "density": round(a.relational_profile.composite_score, 3) if a.relational_profile.composite_score else 0,
                }
                for n, a, s in top_k
            ],
        }

    # ══════════════════════════════════════════════════════════════════
    # 9b. HAS/LACKS PARTNERSHIP COMPARISON
    # ══════════════════════════════════════════════════════════════════

    def has_lacks_comparison(self) -> dict:
        """
        Aggregate outcome and sovereignty comparison: cases with direct
        partnerships vs cases without.
        """
        partnered_names = set()
        for a, b in DIRECT_PARTNERSHIPS:
            partnered_names.add(a)
            partnered_names.add(b)

        has_partners = []
        lacks_partners = []
        for name, agent in self.agents.items():
            if name in partnered_names:
                has_partners.append((name, agent))
            else:
                lacks_partners.append((name, agent))

        has_grp = self._group_outcomes(has_partners)
        lacks_grp = self._group_outcomes(lacks_partners)

        outcome_diffs = {}
        for og in OUTCOME_GROUPS:
            h_val = has_grp["avg_outcomes"].get(og, 0)
            l_val = lacks_grp["avg_outcomes"].get(og, 0)
            pct = round((h_val - l_val) / l_val * 100, 1) if l_val > 0.01 else 0
            outcome_diffs[og] = {
                "has_avg": h_val, "lacks_avg": l_val,
                "delta": round(h_val - l_val, 4), "pct_diff": pct,
                "name": OUTCOME_GROUP_NAMES.get(og, og),
            }

        sov_diffs = {}
        for dim in SOVEREIGNTY_DIMENSIONS:
            h_val = has_grp["avg_sovereignty"].get(dim, 0)
            l_val = lacks_grp["avg_sovereignty"].get(dim, 0)
            pct = round((h_val - l_val) / l_val * 100, 1) if l_val > 0.01 else 0
            sov_diffs[dim] = {
                "has_avg": h_val, "lacks_avg": l_val,
                "delta": round(h_val - l_val, 4), "pct_diff": pct,
            }

        return {
            "has_count": len(has_partners),
            "lacks_count": len(lacks_partners),
            "has_cases": sorted(partnered_names),
            "lacks_cases": sorted(set(self.agents.keys()) - partnered_names),
            "outcome_diffs": outcome_diffs,
            "sovereignty_diffs": sov_diffs,
            "has_avg_density": round(
                sum(a.relational_profile.composite_score for _, a in has_partners
                    if a.relational_profile and a.relational_profile.composite_score) / len(has_partners), 3
            ) if has_partners else 0,
            "lacks_avg_density": round(
                sum(a.relational_profile.composite_score for _, a in lacks_partners
                    if a.relational_profile and a.relational_profile.composite_score) / len(lacks_partners), 3
            ) if lacks_partners else 0,
        }

    # ══════════════════════════════════════════════════════════════════
    # 10. ENRICHED CLUSTER ANALYSIS
    # ══════════════════════════════════════════════════════════════════

    def enriched_cluster_analysis(self, cluster_name: str) -> dict:
        """
        Extended cluster analysis with named outcomes/dimensions in emergent
        properties, percentage differentials, and average member counts.
        """
        base = self.cluster_analysis(cluster_name)
        if "error" in base:
            return base

        members = [(n, self.model.get_agent(n)) for n in base["members"]]
        members = [(n, a) for n, a in members if a]

        # Percentage differentials instead of raw deltas
        pct_outcome_diffs = {}
        for og in OUTCOME_GROUPS:
            cluster_avg = base["cluster_outcomes"]["avg_outcomes"].get(og, 0)
            nc_avg = base["non_cluster_outcomes"]["avg_outcomes"].get(og, 0)
            if nc_avg > 0.01:
                pct = round((cluster_avg - nc_avg) / nc_avg * 100, 1)
            else:
                pct = 0
            pct_outcome_diffs[og] = {
                "cluster_avg": cluster_avg,
                "non_cluster_avg": nc_avg,
                "pct_diff": pct,
                "name": OUTCOME_GROUP_NAMES.get(og, og),
            }

        pct_sovereignty_diffs = {}
        for dim in SOVEREIGNTY_DIMENSIONS:
            cluster_avg = base["cluster_outcomes"]["avg_sovereignty"].get(dim, 0)
            nc_avg = base["non_cluster_outcomes"]["avg_sovereignty"].get(dim, 0)
            if nc_avg > 0.01:
                pct = round((cluster_avg - nc_avg) / nc_avg * 100, 1)
            else:
                pct = 0
            pct_sovereignty_diffs[dim] = {
                "cluster_avg": cluster_avg,
                "non_cluster_avg": nc_avg,
                "pct_diff": pct,
            }

        # Enriched emergent properties with named outcomes and dimensions
        ep = base.get("emergent_properties", {})
        # Which outcome groups are active collectively?
        collective_ogs = set()
        member_ogs = {}
        for n, a in members:
            case_ogs = set(a.active_outcome_groups)
            member_ogs[n] = sorted(case_ogs)
            collective_ogs.update(case_ogs)

        # Which sovereignty dimensions are active collectively?
        collective_sov_dims = set()
        member_sov_dims = {}
        for n, a in members:
            active = [d for d in SOVEREIGNTY_DIMENSIONS if a.sovereignty_profile.get(d, 0) > 0]
            member_sov_dims[n] = active
            collective_sov_dims.update(active)

        ep["collective_outcome_names"] = [OUTCOME_GROUP_NAMES.get(og, og) for og in sorted(collective_ogs)]
        ep["collective_sovereignty_names"] = sorted(collective_sov_dims)
        ep["member_outcome_breadths"] = {n: len(ogs) for n, ogs in member_ogs.items()}
        ep["member_sovereignty_counts"] = {n: len(dims) for n, dims in member_sov_dims.items()}

        # Average member partner types and relationship types
        avg_pt_count = sum(
            len(a.relational_profile.partner_types_engaged or [])
            for _, a in members if a.relational_profile
        ) / len(members) if members else 0
        avg_rt_count = sum(
            len(a.relational_profile.relationship_types or [])
            for _, a in members if a.relational_profile
        ) / len(members) if members else 0

        base["pct_outcome_diffs"] = pct_outcome_diffs
        base["pct_sovereignty_diffs"] = pct_sovereignty_diffs
        base["emergent_properties"] = ep
        base["avg_member_partner_types"] = round(avg_pt_count, 1)
        base["avg_member_relationship_types"] = round(avg_rt_count, 1)
        base["collective_partner_type_count"] = len(base["collective_partner_types"])
        base["collective_relationship_type_count"] = len(base["collective_relationship_types"])

        # Named partner types and relationship types
        base["collective_partner_type_names"] = [
            PARTNER_TYPES.get(pt, f"Type {pt}") for pt in base["collective_partner_types"]
        ]
        base["collective_relationship_type_names"] = [
            RELATIONSHIP_TYPES.get(rt, rt) for rt in base["collective_relationship_types"]
        ]

        # Member details for the table
        base["member_details"] = []
        for n, a in members:
            rp = a.relational_profile
            base["member_details"].append({
                "name": n,
                "org_type": a.org_type,
                "composite_density": round(rp.composite_score, 3) if rp and rp.composite_score else 0,
                "partner_count": len(rp.partner_types_engaged or []) if rp else 0,
                "relationship_count": len(rp.relationship_types or []) if rp else 0,
                "network_reach": rp.network_reach if rp else 0,
                "D1": rp.partner_diversity if rp else 0,
                "D2": rp.relationship_type_range if rp else 0,
                "D3": rp.network_reach if rp else 0,
                "D4": rp.inter_case_connectivity if rp else 0,
                "outcomes": {
                    og: round(a.outcome_scores.get(og) or 0, 3) for og in OUTCOME_GROUPS
                },
                "sovereignty": {
                    dim: round(a.sovereignty_profile.get(dim, 0), 3)
                    for dim in SOVEREIGNTY_DIMENSIONS
                },
            })

        # Network reach distribution across members
        nr_dist = {"Local": 0, "National": 0, "Transnational": 0}
        nr_labels = {1: "Local", 2: "National", 3: "Transnational"}
        for n, a in members:
            rp = a.relational_profile
            if rp and rp.network_reach:
                label = nr_labels.get(rp.network_reach, "Unknown")
                nr_dist[label] = nr_dist.get(label, 0) + 1
        base["network_reach_distribution"] = nr_dist

        return base

    # ══════════════════════════════════════════════════════════════════
    # 11. ENRICHED AGENT-AGENT INTERACTIONS
    # ══════════════════════════════════════════════════════════════════

    def enriched_agent_interactions(self) -> dict:
        """
        Agent-agent analysis showing BOTH numeric convergence AND shared
        outcomes/sovereignty qualitatively between directly partnered cases.
        """
        partnerships = defaultdict(set)
        for a, b in DIRECT_PARTNERSHIPS:
            partnerships[a].add(b)
            partnerships[b].add(a)

        results = {}
        for case_name, partner_names in partnerships.items():
            agent = self.model.get_agent(case_name)
            if not agent:
                continue

            partner_agents = []
            for pname in partner_names:
                pa = self.model.get_agent(pname)
                if pa:
                    partner_agents.append((pname, pa))

            if not partner_agents:
                continue

            # --- Numeric convergence (outcome + sovereignty) ---
            outcome_convergence = {}
            for og in OUTCOME_GROUPS:
                case_score = agent.outcome_scores.get(og)
                partner_scores = [pa.outcome_scores.get(og)
                                  for _, pa in partner_agents
                                  if pa.outcome_scores.get(og) is not None]
                if case_score is not None and partner_scores:
                    avg_partner = sum(partner_scores) / len(partner_scores)
                    diff = case_score - avg_partner
                    outcome_convergence[og] = {
                        "case_score": round(case_score, 3),
                        "partner_avg": round(avg_partner, 3),
                        "difference": round(diff, 3),
                        "abs_difference": round(abs(diff), 3),
                        "convergent": abs(diff) < 0.2,
                        "group_name": OUTCOME_GROUP_NAMES.get(og, og),
                    }

            sov_convergence = {}
            for dim in SOVEREIGNTY_DIMENSIONS:
                case_val = agent.sovereignty_profile.get(dim, 0)
                partner_vals = [pa.sovereignty_profile.get(dim, 0) for _, pa in partner_agents]
                if partner_vals:
                    avg_partner = sum(partner_vals) / len(partner_vals)
                    diff = case_val - avg_partner
                    sov_convergence[dim] = {
                        "case_val": round(case_val, 3),
                        "partner_avg": round(avg_partner, 3),
                        "difference": round(diff, 3),
                        "convergent": abs(diff) < 0.15,
                    }

            # --- Qualitative: shared outcome categories ---
            case_outcome_cats = {}
            for og in OUTCOME_GROUPS:
                case_outcome_cats[og] = set(agent.outcome_categories.get(og, []))

            shared_outcomes = {}
            for og in OUTCOME_GROUPS:
                case_cats = case_outcome_cats[og]
                for pname, pa in partner_agents:
                    partner_cats = set(pa.outcome_categories.get(og, []))
                    common = case_cats & partner_cats
                    if common:
                        if og not in shared_outcomes:
                            shared_outcomes[og] = {
                                "group_name": OUTCOME_GROUP_NAMES.get(og, og),
                                "shared_categories": {},
                            }
                        for code in common:
                            from config import OUTCOME_CATEGORIES
                            cat_name = OUTCOME_CATEGORIES.get(og, {}).get(code, code)
                            shared_outcomes[og]["shared_categories"][code] = cat_name

            # Shared sovereignty dimensions (both > 0)
            shared_sovereignty = []
            for dim in SOVEREIGNTY_DIMENSIONS:
                case_val = agent.sovereignty_profile.get(dim, 0)
                partner_vals = [pa.sovereignty_profile.get(dim, 0) for _, pa in partner_agents]
                if case_val > 0 and any(v > 0 for v in partner_vals):
                    shared_sovereignty.append(dim)

            # Shared partner types
            case_pts = set(agent.relational_profile.partner_types_engaged or [])
            shared_pts = set()
            for _, pa in partner_agents:
                pa_pts = set(pa.relational_profile.partner_types_engaged or [])
                shared_pts.update(case_pts & pa_pts)

            results[case_name] = {
                "partners": sorted(partner_names),
                "n_partners": len(partner_agents),
                "org_type": agent.org_type,
                "outcome_convergence": outcome_convergence,
                "sovereignty_convergence": sov_convergence,
                "shared_outcomes": shared_outcomes,
                "shared_sovereignty": shared_sovereignty,
                "shared_partner_types": sorted(shared_pts),
                "shared_partner_type_names": [
                    PARTNER_TYPES.get(pt, f"Type {pt}") for pt in sorted(shared_pts)
                ],
                "case_density": round(
                    agent.relational_profile.composite_score, 3
                ) if agent.relational_profile and agent.relational_profile.composite_score else 0,
            }

        return results

    # ══════════════════════════════════════════════════════════════════
    # 12. ENRICHED MATCHED PAIRS
    # ══════════════════════════════════════════════════════════════════

    def enriched_matched_pairs(self) -> list:
        """
        Matched pairs with full condition details — which conditions are
        shared, to what extent, and how outcomes/sovereignty differ.
        """
        from config import CONDITION_TYPE_NAMES

        agents_with_density = []
        for name, agent in self.agents.items():
            rp = agent.relational_profile
            if rp and rp.composite_score is not None:
                agents_with_density.append((name, agent, rp.composite_score))

        agents_with_density.sort(key=lambda x: x[2])
        pairs = []
        n = len(agents_with_density)

        for i in range(n):
            for j in range(i + 1, n):
                name_i, agent_i, d_i = agents_with_density[i]
                name_j, agent_j, d_j = agents_with_density[j]

                # Similar condition diversity (within 1)
                if abs(agent_i.condition_diversity - agent_j.condition_diversity) > 1:
                    continue
                # Different density (at least 0.5 apart)
                if abs(d_i - d_j) < 0.5:
                    continue

                # Find shared conditions and their scores
                shared_conditions = []
                all_cts_i = set(agent_i.internal_condition_scores.keys()) | set(agent_i.external_condition_scores.keys())
                all_cts_j = set(agent_j.internal_condition_scores.keys()) | set(agent_j.external_condition_scores.keys())
                common_cts = all_cts_i & all_cts_j

                for ct in sorted(common_cts):
                    score_i = agent_i.internal_condition_scores.get(ct) or agent_i.external_condition_scores.get(ct)
                    score_j = agent_j.internal_condition_scores.get(ct) or agent_j.external_condition_scores.get(ct)
                    if score_i is not None and score_j is not None:
                        shared_conditions.append({
                            "condition": ct,
                            "name": CONDITION_TYPE_NAMES.get(ct, ct),
                            "score_low": round(score_i, 2),
                            "score_high": round(score_j, 2),
                            "similar": abs(score_i - score_j) <= 0.25,
                        })

                n_shared = len(shared_conditions)
                # Require at least 2 shared condition types for a meaningful pair
                if n_shared < 2:
                    continue
                n_similar = sum(1 for c in shared_conditions if c["similar"])

                # Outcome differences with names and percentages
                outcome_diffs = {}
                for og in OUTCOME_GROUPS:
                    s_i = agent_i.outcome_scores.get(og)
                    s_j = agent_j.outcome_scores.get(og)
                    if s_i is not None and s_j is not None:
                        delta = round(s_j - s_i, 3)
                        pct = round((s_j - s_i) / s_i * 100, 1) if s_i > 0.01 else 0
                        outcome_diffs[og] = {
                            "low_score": round(s_i, 3),
                            "high_score": round(s_j, 3),
                            "delta": delta,
                            "pct_diff": pct,
                            "name": OUTCOME_GROUP_NAMES.get(og, og),
                        }

                # Sovereignty differences
                sov_diffs = {}
                for dim in SOVEREIGNTY_DIMENSIONS:
                    v_i = agent_i.sovereignty_profile.get(dim, 0)
                    v_j = agent_j.sovereignty_profile.get(dim, 0)
                    if v_i > 0 or v_j > 0:
                        sov_diffs[dim] = {
                            "low_val": round(v_i, 3),
                            "high_val": round(v_j, 3),
                            "delta": round(v_j - v_i, 3),
                        }

                pairs.append({
                    "low_density_case": name_i,
                    "high_density_case": name_j,
                    "low_density": round(d_i, 3),
                    "high_density": round(d_j, 3),
                    "density_gap": round(d_j - d_i, 3),
                    "condition_diversity_low": agent_i.condition_diversity,
                    "condition_diversity_high": agent_j.condition_diversity,
                    "shared_conditions": shared_conditions,
                    "n_shared": n_shared,
                    "n_similar_scores": n_similar,
                    "outcome_diffs": outcome_diffs,
                    "sovereignty_diffs": sov_diffs,
                })

        # Sort by density gap, take top 10
        pairs.sort(key=lambda x: x["density_gap"], reverse=True)
        return pairs[:12]
