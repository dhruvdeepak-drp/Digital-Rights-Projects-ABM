"""
Primary Model: container for 43 agents with analytical operations.

This is the computational core. It holds all agents and provides
methods for querying, comparing, and analyzing across the ecosystem.
Analytical operations (sensitivity, counterfactual, etc.) will be
added in Phase 3.
"""

from collections import Counter, defaultdict
from config import (
    ALL_CONDITION_TYPES, INTERNAL_CONDITION_TYPES, EXTERNAL_CONDITION_TYPES,
    OUTCOME_GROUPS, OUTCOME_GROUP_NAMES, CONDITION_TYPE_NAMES,
    SOVEREIGNTY_DIMENSIONS, ORG_TYPE_NAMES,
    RECURSIVE_PATTERNS, CONDITION_MECHANISM_MAP,
)
from agent import Agent


class PrimaryModel:
    """
    Primary ABM: 43 agents, condition-outcome-sovereignty analysis.
    Agent-agent interactions DISABLED (that's the second model).
    """

    def __init__(self, agents: dict, cross_impact_quant: dict = None):
        """
        Args:
            agents: dict of {canonical_name: Agent}
            cross_impact_quant: dict from DataLoader (outcome_code → {cond_code: count})
        """
        self.agents = agents
        self.cross_impact_quant = cross_impact_quant or {}

    # ── Agent Access ──────────────────────────────────────────────────

    def get_agent(self, name: str) -> Agent:
        """Get agent by canonical name."""
        if name not in self.agents:
            raise KeyError(f"No agent named '{name}'. Available: {list(self.agents.keys())[:5]}...")
        return self.agents[name]

    def get_agents_by_type(self, org_type: str) -> list:
        """Get all agents of a given organizational type."""
        return [a for a in self.agents.values() if a.org_type == org_type]

    def get_agents_by_feature(self, feature: str, value) -> list:
        """Filter agents by any characteristic."""
        results = []
        for a in self.agents.values():
            if feature == "org_type" and a.org_type == value:
                results.append(a)
            elif feature == "geographic_scope" and a.geographic_scope == value:
                results.append(a)
            elif feature == "dominant_pattern" and value in a.dominant_patterns:
                results.append(a)
        return results

    # ── Ecosystem Statistics ──────────────────────────────────────────

    def ecosystem_summary(self) -> dict:
        """Summary statistics across all 43 agents."""
        agents = list(self.agents.values())
        n = len(agents)

        # Org type distribution
        org_counts = Counter(a.org_type for a in agents)

        # Condition diversity
        cond_divs = [a.condition_diversity for a in agents]

        # Outcome breadth
        out_breadths = [a.outcome_breadth for a in agents]

        # Cases achieving all 4 outcome groups
        comprehensive = [a.name for a in agents if a.outcome_breadth == 4]

        # Relational density
        rel_dens = [a.relational_density for a in agents if a.relational_density > 0]

        return {
            "total_agents": n,
            "org_type_distribution": dict(org_counts),
            "condition_diversity": {
                "min": min(cond_divs),
                "max": max(cond_divs),
                "mean": round(sum(cond_divs) / n, 1),
            },
            "outcome_breadth": {
                "min": min(out_breadths),
                "max": max(out_breadths),
                "mean": round(sum(out_breadths) / n, 1),
            },
            "comprehensive_cases": comprehensive,
            "relational_density": {
                "min": round(min(rel_dens), 2) if rel_dens else 0,
                "max": round(max(rel_dens), 2) if rel_dens else 0,
                "mean": round(sum(rel_dens) / len(rel_dens), 2) if rel_dens else 0,
            },
        }

    def condition_outcome_frequencies(self, org_type: str = None) -> dict:
        """
        Compute condition-type → outcome-group co-occurrence frequencies
        across all agents. This is the ecosystem-level generative logic.
        If org_type is specified, filter to only agents of that type.
        """
        freq = defaultdict(lambda: defaultdict(int))
        for agent in self.agents.values():
            if org_type and agent.org_type != org_type:
                continue
            for row in agent.production_rule:
                if row.condition_type and row.outcome_group:
                    freq[row.condition_type][row.outcome_group] += 1
        return {ct: dict(og_counts) for ct, og_counts in freq.items()}

    def generative_logic_summary(self) -> dict:
        """
        Identify dominant condition-type → outcome-group pathways
        from production rules (case-level). Returns sorted by frequency.
        """
        freq = self.condition_outcome_frequencies()
        pairs = []
        for ctype, outcomes in freq.items():
            for ogroup, count in outcomes.items():
                pairs.append({
                    "condition_type": ctype,
                    "condition_name": CONDITION_TYPE_NAMES.get(ctype, ctype),
                    "outcome_group": ogroup,
                    "outcome_name": OUTCOME_GROUP_NAMES.get(ogroup, ogroup),
                    "count": count,
                })
        pairs.sort(key=lambda x: x["count"], reverse=True)
        return pairs

    def cross_impact_generative_logic(self) -> list:
        """
        Compute condition-type → outcome-group frequencies from the
        Phase_3A cross-impact matrix. This is the ecosystem-level
        benchmark (category-level co-occurrences across all 43 cases).
        """
        from config import CONDITION_CATEGORIES, OUTCOME_CATEGORIES

        # Build type-code → condition-type lookup
        code_to_ctype = {}
        for ctype, cats in CONDITION_CATEGORIES.items():
            for code in cats:
                code_to_ctype[code] = ctype

        # Build outcome-code → outcome-group lookup
        code_to_ogroup = {}
        for ogroup, cats in OUTCOME_CATEGORIES.items():
            for code in cats:
                code_to_ogroup[code] = ogroup

        # Sum cross-impact counts by type → group
        from collections import defaultdict
        freq = defaultdict(lambda: defaultdict(int))

        for ocode, cond_counts in self.cross_impact_quant.items():
            ogroup = code_to_ogroup.get(ocode)
            if not ogroup:
                continue
            for ccode, count in cond_counts.items():
                ctype = code_to_ctype.get(ccode)
                if ctype:
                    freq[ctype][ogroup] += count

        pairs = []
        for ctype, outcomes in freq.items():
            for ogroup, count in outcomes.items():
                pairs.append({
                    "condition_type": ctype,
                    "condition_name": CONDITION_TYPE_NAMES.get(ctype, ctype),
                    "outcome_group": ogroup,
                    "outcome_name": OUTCOME_GROUP_NAMES.get(ogroup, ogroup),
                    "count": count,
                    "mechanism": CONDITION_MECHANISM_MAP.get(ctype, ""),
                })
        pairs.sort(key=lambda x: x["count"], reverse=True)
        return pairs

    def mechanism_distribution(self) -> dict:
        """Distribution of mechanism types across all production rules."""
        mechs = Counter()
        for agent in self.agents.values():
            for row in agent.production_rule:
                for m in row.mechanism_type.split("+"):
                    mechs[m.strip()] += 1
        return dict(mechs)

    # ── Comparison Operations ─────────────────────────────────────────

    def compare_by_org_type(self) -> dict:
        """Compare outcome profiles across organizational types."""
        results = {}
        for ot_code, ot_name in ORG_TYPE_NAMES.items():
            agents = self.get_agents_by_type(ot_code)
            if not agents:
                continue
            n = len(agents)

            # Average outcome scores
            avg_outcomes = {}
            for og in OUTCOME_GROUPS:
                scores = [a.outcome_scores.get(og) for a in agents
                          if a.outcome_scores.get(og) is not None]
                avg_outcomes[og] = {
                    "mean": round(sum(scores) / len(scores), 3) if scores else 0,
                    "count": len(scores),
                    "presence": f"{len(scores)}/{n}",
                }

            # Average condition diversity
            avg_cd = round(sum(a.condition_diversity for a in agents) / n, 1)

            # Average relational density
            rd_vals = [a.relational_density for a in agents if a.relational_density > 0]
            avg_rd = round(sum(rd_vals) / len(rd_vals), 2) if rd_vals else 0

            results[ot_code] = {
                "name": ot_name,
                "count": n,
                "avg_condition_diversity": avg_cd,
                "avg_relational_density": avg_rd,
                "outcome_profiles": avg_outcomes,
            }

        return results

    def compare_by_feature(self, feature: str) -> dict:
        """Compare outcome profiles grouped by any agent feature."""
        groups = defaultdict(list)
        for agent in self.agents.values():
            val = getattr(agent, feature, None)
            if val is not None:
                groups[val].append(agent)

        results = {}
        for val, agents in groups.items():
            n = len(agents)
            avg_outcomes = {}
            for og in OUTCOME_GROUPS:
                scores = [a.outcome_scores.get(og) for a in agents
                          if a.outcome_scores.get(og) is not None]
                avg_outcomes[og] = round(sum(scores) / len(scores), 3) if scores else 0
            results[val] = {"count": n, "avg_outcomes": avg_outcomes}

        return results

    # ── Sovereignty Analysis ──────────────────────────────────────────

    def sovereignty_profiles_by_type(self) -> dict:
        """Average sovereignty profiles per organizational type."""
        results = {}
        for ot_code, ot_name in ORG_TYPE_NAMES.items():
            agents = self.get_agents_by_type(ot_code)
            if not agents:
                continue
            avg_profile = {dim: 0.0 for dim in SOVEREIGNTY_DIMENSIONS}
            for agent in agents:
                for dim in SOVEREIGNTY_DIMENSIONS:
                    avg_profile[dim] += agent.sovereignty_profile.get(dim, 0.0)
            for dim in SOVEREIGNTY_DIMENSIONS:
                avg_profile[dim] = round(avg_profile[dim] / len(agents), 3)
            results[ot_code] = {"name": ot_name, "profile": avg_profile}
        return results

    # ── Recursive D-A-S Pattern Summary ─────────────────────────────────

    def recursive_pattern_distribution(self) -> dict:
        """Distribution of 17 recursive patterns across all 43 agents (binary).
        Counts how many cases participate in each pattern."""
        from collections import Counter
        all_counts = Counter()
        for agent in self.agents.values():
            all_counts.update(agent.recursive_patterns)  # list of IDs, each counted once
        return {
            "pattern_counts": {
                p: {"name": RECURSIVE_PATTERNS.get(p, f"#{p}"), "cases": c}
                for p, c in all_counts.most_common()
            },
            "total_cases": len(self.agents),
        }

    # ── Display Helpers ───────────────────────────────────────────────

    def agent_profile_text(self, name: str) -> str:
        """Generate a text profile for an agent (for console/debug)."""
        a = self.get_agent(name)
        lines = [
            f"═══ {a.name} ({ORG_TYPE_NAMES.get(a.org_type, a.org_type)}) ═══",
            f"Sector: {a.economic_sector}",
            f"Location: {a.location} | Scope: {a.geographic_scope}",
            f"Maturity: {a.maturity}",
            "",
            "── Internal Conditions ──",
        ]
        for ct in INTERNAL_CONDITION_TYPES:
            score = a.internal_condition_scores.get(ct)
            cats = a.condition_categories.get(ct, [])
            if score is not None:
                lines.append(f"  {CONDITION_TYPE_NAMES[ct]}: {score:.2f}  [{', '.join(cats)}]")

        lines.append("")
        lines.append("── External Conditions ──")
        for ct in EXTERNAL_CONDITION_TYPES:
            score = a.external_condition_scores.get(ct)
            cats = a.condition_categories.get(ct, [])
            if score is not None:
                lines.append(f"  {CONDITION_TYPE_NAMES[ct]}: {score:.2f}  [{', '.join(cats)}]")

        lines.append("")
        lines.append("── Outcomes ──")
        for og in OUTCOME_GROUPS:
            score = a.outcome_scores.get(og)
            cats = a.outcome_categories.get(og, [])
            if score is not None:
                lines.append(f"  {OUTCOME_GROUP_NAMES[og]}: {score:.2f}  [{', '.join(cats)}]")

        lines.append("")
        lines.append(f"── Derived ──")
        lines.append(f"  Condition diversity: {a.condition_diversity}")
        lines.append(f"  Outcome breadth: {a.outcome_breadth}")
        lines.append(f"  Relational density: {a.relational_density:.2f}")
        patterns_str = ", ".join(a.dominant_pattern_names) if a.dominant_pattern_names else "not assigned"
        lines.append(f"  D-A-S patterns: {patterns_str}")

        lines.append("")
        lines.append("── Production Rule ──")
        for i, row in enumerate(a.production_rule, 1):
            lines.append(
                f"  {i}. [{row.condition_type}] {row.condition_name} "
                f"→ ({row.mechanism_type}) → [{row.outcome_group}] {row.outcome_name}"
            )

        # Enrichment from Appendix 3
        if a.condition_interactions:
            lines.append("")
            lines.append("── Condition Interactions ──")
            lines.append(f"  {a.condition_interactions}")
        if a.synthesis:
            lines.append("")
            lines.append("── Synthesis ──")
            lines.append(f"  {a.synthesis}")
        if a.compact_equation:
            lines.append("")
            lines.append("── Compact Equation ──")
            lines.append(f"  {a.compact_equation}")

        lines.append("")
        lines.append("── Sovereignty Profile ──")
        for dim in SOVEREIGNTY_DIMENSIONS:
            val = a.sovereignty_profile.get(dim, 0.0)
            bar = "█" * int(val * 20)
            lines.append(f"  {dim:20s}: {val:.3f} {bar}")

        lines.append("")
        lines.append("── Sovereignty Terrain (Bridge B) ──")
        for dim in SOVEREIGNTY_DIMENSIONS:
            val = a.sovereignty_terrain.get(dim, 0.0)
            bar = "▒" * int(val * 20)
            lines.append(f"  {dim:20s}: {val:.3f} {bar}")

        # Recursive pattern profile
        if a.recursive_patterns:
            lines.append("")
            lines.append("── Recursive D-A-S Patterns ──")
            for pid in a.recursive_patterns:
                pname = RECURSIVE_PATTERNS.get(pid, f"#{pid}")
                lines.append(f"  #{pid:2d} {pname}")

        return "\n".join(lines)
