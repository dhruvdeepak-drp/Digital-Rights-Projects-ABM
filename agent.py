"""
Agent: data structure for a single case in the ABM.

Each agent carries three layers:
  Layer 1: Condition scores (internal + external) and condition categories
  Layer 2: Characteristics (org type, sector, location, scope, maturity, derived)
  Layer 3: Production rule (case equation rows)

Plus outcome scores, outcome categories, sovereignty profile,
D-A-S pathway (Phase 4), and relational profile (second model).
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProductionRuleRow:
    """One row of a case equation: condition(s) → outcome(s) with mechanism."""
    condition_type: str          # e.g., "GV"
    condition_name: str          # e.g., "Worker Ownership Structures"
    condition_codes: list        # e.g., ["GV2"] — resolved from categorical matrix
    mechanism_type: str          # e.g., "structural"
    outcome_group: str           # e.g., "CV"
    outcome_name: str            # e.g., "Worker-owned alternative..."
    outcome_codes: list          # e.g., ["CV1"] — resolved from categorical matrix
    description: str             # Full qualitative description from Phase_1A
    challenge: str               # Challenge addressed


@dataclass
class RelationalProfile:
    """Second model addition: partnership and relational data."""
    partner_types_engaged: list = field(default_factory=list)      # e.g., [1, 3, 5, 10]
    relationship_types: list = field(default_factory=list)         # e.g., ["PT1", "PT3"]
    partner_diversity: int = 0             # D1 raw (0-12)
    partner_diversity_norm: float = 0.0    # D1 normalized
    relationship_type_range: int = 0       # D2 raw (0-6)
    relationship_type_range_norm: float = 0.0  # D2 normalized
    network_reach: int = 0                 # D3 raw (1-3)
    network_reach_norm: float = 0.0        # D3 normalized
    network_reach_description: str = ""
    inter_case_connectivity: int = 0       # D4 raw (0-3)
    inter_case_connectivity_norm: float = 0.0  # D4 normalized
    inter_case_description: str = ""
    composite_score: float = 0.0           # 0-4
    direct_partners: list = field(default_factory=list)   # canonical names
    latent_clusters: list = field(default_factory=list)    # cluster names


@dataclass
class Agent:
    """A single case in the ABM. All 43 cases are instantiated as Agents."""

    # ── Identity ──────────────────────────────────────────────────────
    name: str                              # Canonical name
    org_type: str                          # "DSO", "DC", "PG", "PP"
    economic_sector: str = ""
    location: str = ""
    geographic_scope: str = ""
    maturity: str = ""

    # ── Layer 1: Condition Scores ─────────────────────────────────────
    # Internal conditions: {type_code: score_or_None}
    # e.g., {"TP": 0.75, "RS": None, "GV": 0.25, ...}
    internal_condition_scores: dict = field(default_factory=dict)
    # External conditions: {type_code: score_or_None}
    external_condition_scores: dict = field(default_factory=dict)
    # Condition categories active: {type_code: [cat_codes]}
    # e.g., {"GV": ["GV2", "GV4"], "TP": ["TP1"], ...}
    condition_categories: dict = field(default_factory=dict)

    # ── Layer 2: Derived Characteristics ──────────────────────────────
    condition_diversity: int = 0           # Count of active condition types (2-7)
    outcome_breadth: int = 0              # Count of outcome groups achieved (1-4)
    relational_density: float = 0.0       # Composite score (0-4)

    # ── Layer 3: Production Rule ──────────────────────────────────────
    production_rule: list = field(default_factory=list)  # list[ProductionRuleRow]
    # Appendix 3 enrichment: qualitative narratives from case equations
    condition_interactions: str = ""    # How conditions work together
    synthesis: str = ""                # How conditions combine to produce outcomes
    compact_equation: str = ""          # Shorthand equation

    # ── Outcomes ──────────────────────────────────────────────────────
    # Outcome group scores: {"DP": 0.60, "CV": None, ...}
    outcome_scores: dict = field(default_factory=dict)
    # Outcome categories achieved: {"DP": ["DP6", "DP7"], ...}
    outcome_categories: dict = field(default_factory=dict)
    outcome_total: float = 0.0

    # ── D-A-S Pathway (populated in Phase 4) ──────────────────────────
    # Recursive D-A-S patterns (17 types, replaces 6-type pathway classification)
    # Binary assignment: list of pattern IDs this case participates in
    recursive_patterns: list = field(default_factory=list)       # sorted pattern IDs
    dominant_patterns: list = field(default_factory=list)         # same as recursive_patterns (binary)
    dominant_pattern_names: list = field(default_factory=list)    # pattern names

    # ── Sovereignty Profile ───────────────────────────────────────────
    # {dimension: score} — computed from outcome categories
    sovereignty_profile: dict = field(default_factory=dict)
    # {dimension: score} — computed from condition types (Bridge B: terrain)
    sovereignty_terrain: dict = field(default_factory=dict)

    # ── Second Model: Relational Profile ──────────────────────────────
    relational_profile: Optional[RelationalProfile] = None

    # ── Computed Properties ───────────────────────────────────────────

    @property
    def all_condition_scores(self) -> dict:
        """Combined internal + external condition scores."""
        return {**self.internal_condition_scores, **self.external_condition_scores}

    @property
    def active_condition_types(self) -> list:
        """List of condition types with non-None scores."""
        return [k for k, v in self.all_condition_scores.items() if v is not None]

    @property
    def active_outcome_groups(self) -> list:
        """List of outcome groups with non-None scores."""
        return [k for k, v in self.outcome_scores.items() if v is not None]

    @property
    def all_active_condition_codes(self) -> list:
        """All active condition category codes across all types."""
        codes = []
        for cat_list in self.condition_categories.values():
            codes.extend(cat_list)
        return codes

    @property
    def all_active_outcome_codes(self) -> list:
        """All active outcome category codes across all groups."""
        codes = []
        for cat_list in self.outcome_categories.values():
            codes.extend(cat_list)
        return codes

    def get_mechanism_types(self) -> list:
        """Mechanism types present in this agent's production rule."""
        return list(set(row.mechanism_type for row in self.production_rule))

    def get_dominant_mechanism(self) -> Optional[str]:
        """Most frequent mechanism type in production rule."""
        if not self.production_rule:
            return None
        from collections import Counter
        mechs = []
        for row in self.production_rule:
            # Handle compound mechanisms like "protective+connective"
            for m in row.mechanism_type.split("+"):
                mechs.append(m.strip())
        counts = Counter(mechs)
        return counts.most_common(1)[0][0] if counts else None

    def summary(self) -> str:
        """Brief text summary of this agent."""
        active_ct = len(self.active_condition_types)
        active_og = len(self.active_outcome_groups)
        pr_rows = len(self.production_rule)
        patterns = ", ".join(self.dominant_pattern_names[:2]) if self.dominant_pattern_names else "not assigned"
        return (
            f"{self.name} ({self.org_type}) | "
            f"Conditions: {active_ct} types | "
            f"Outcomes: {active_og} groups | "
            f"Production rule: {pr_rows} rows | "
            f"D-A-S patterns: {patterns}"
        )

    def __repr__(self):
        return f"Agent('{self.name}', org_type='{self.org_type}')"
