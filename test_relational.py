"""
Test script: verify second model (relational) operations.

Tests against Chapter 7.9 specifications:
1. Relational density sensitivity produces directionally meaningful results
2. Partner type effects differentiate cases
3. Relationship type effects show distinctive profiles
4. Agent-agent interactions identify convergence in partnered cases
5. Indigenous Data Sovereignty cluster exhibits emergent properties
6. Relational density moderates condition-outcome relationships
7. 17 recursive D-A-S patterns assigned for all 43 cases
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from data_loader import load_model_data
from primary_model import PrimaryModel
from analytical_engine import AnalyticalEngine
from relational_engine import RelationalEngine
from config import (
    OUTCOME_GROUP_NAMES, PARTNER_TYPES, RELATIONSHIP_TYPES,
    RECURSIVE_PATTERNS,
)


def main():
    print("=" * 70)
    print("DIGITAL RIGHTS PROJECTS ABM — Phase 4 Second Model Test")
    print("=" * 70)
    print()

    # Load
    agents, loader = load_model_data()
    model = PrimaryModel(agents, cross_impact_quant=loader.cross_impact_quant)
    engine = AnalyticalEngine(model)
    relational = RelationalEngine(model, analytical_engine=engine)

    passed = 0
    failed = 0

    # ══════════════════════════════════════════════════════════════════
    # TEST 1: RECURSIVE D-A-S PATTERN ASSIGNMENT (17 patterns)
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("RECURSIVE D-A-S PATTERN ASSIGNMENT")
    print("=" * 70)

    from collections import Counter
    # Patterns are already assigned during data loading
    all_assigned = True
    all_pattern_counts = Counter()
    for name, agent in agents.items():
        if not agent.recursive_patterns:
            all_assigned = False
        all_pattern_counts.update(agent.recursive_patterns)

    if all_assigned:
        print(f"\n✓ All 43 agents assigned recursive D-A-S patterns")
        passed += 1
    else:
        unassigned = [n for n, a in agents.items() if not a.recursive_patterns]
        print(f"\n✗ {len(unassigned)} agents missing patterns: {unassigned[:5]}...")
        failed += 1

    print("  Pattern distribution (cases participating per pattern):")
    for pid, count in all_pattern_counts.most_common(8):
        pname = RECURSIVE_PATTERNS.get(pid, f"#{pid}")
        print(f"    #{pid:2d} {pname:40s}: {count} cases")

    # Check specific cases
    thm = model.get_agent("Te Hiku Media")
    gida = model.get_agent("GIDA")
    print(f"\n  Te Hiku Media: {', '.join(thm.dominant_pattern_names)} (dominant mechanism: {thm.get_dominant_mechanism()})")
    print(f"  GIDA:          {', '.join(gida.dominant_pattern_names)} (dominant mechanism: {gida.get_dominant_mechanism()})")

    # Verify enrichment loaded
    if thm.synthesis and thm.condition_interactions:
        print(f"  Enrichment loaded: synthesis={len(thm.synthesis)} chars, interactions={len(thm.condition_interactions)} chars")
    else:
        print(f"  Warning: enrichment not loaded for Te Hiku Media")

    # ══════════════════════════════════════════════════════════════════
    # TEST 2: RELATIONAL DENSITY SENSITIVITY
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("RELATIONAL DENSITY SENSITIVITY")
    print("=" * 70)

    density_results = relational.full_density_sensitivity()

    has_effect = False
    for dim_code, result in density_results.items():
        if "error" in result:
            print(f"\n  {dim_code}: ERROR — {result['error']}")
            continue

        print(f"\n  {dim_code} ({result['attribute']}) — median={result['median']}")
        print(f"    High group: {result['high_group']['count']} cases | "
              f"Low group: {result['low_group']['count']} cases")
        for og in ["DP", "CV", "BL", "IM"]:
            d = result["differences"][og]
            print(f"    {OUTCOME_GROUP_NAMES[og]:25s}: Δ={d['delta']:+.4f} ({d['direction']})")
            if abs(d["delta"]) > 0.01:
                has_effect = True

    if has_effect:
        print(f"\n✓ Density dimensions show differential outcome effects")
        passed += 1
    else:
        print(f"\n✗ No meaningful density effects detected")
        failed += 1

    # ══════════════════════════════════════════════════════════════════
    # TEST 3: PARTNER TYPE EFFECTS — Indigenous governance vs Corporate
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("PARTNER TYPE EFFECTS")
    print("=" * 70)

    # Partner type 1: Indigenous Governance and Tribal Bodies
    pt1_result = relational.partner_type_effect(1)
    print(f"\n  PT 1: {PARTNER_TYPES[1]}")
    print(f"    Has: {pt1_result['has_count']} cases | Lacks: {pt1_result['lacks_count']} cases")
    for og in ["DP", "CV", "BL", "IM"]:
        d = pt1_result["outcome_differences"][og]
        print(f"    {OUTCOME_GROUP_NAMES[og]:25s}: Δ={d['delta']:+.4f}")

    # Partner type 6: Corporate and Technology Entities
    pt6_result = relational.partner_type_effect(6)
    print(f"\n  PT 6: {PARTNER_TYPES[6]}")
    print(f"    Has: {pt6_result['has_count']} cases | Lacks: {pt6_result['lacks_count']} cases")
    for og in ["DP", "CV", "BL", "IM"]:
        d = pt6_result["outcome_differences"][og]
        print(f"    {OUTCOME_GROUP_NAMES[og]:25s}: Δ={d['delta']:+.4f}")

    # Test: Indigenous governance should show stronger sovereignty effects
    pt1_sov = pt1_result["sovereignty_differences"]
    has_sov_diff = any(abs(v.get("delta", 0)) > 0.01 for v in pt1_sov.values())
    if has_sov_diff:
        print(f"\n✓ Partner types produce differential sovereignty profiles")
        passed += 1
    else:
        print(f"\n✗ No sovereignty differentiation by partner type")
        failed += 1

    # Combinatorial test
    print(f"\n  Combination: Academic (2) + Community/Grassroots (4)")
    combo = relational.partner_type_combination_effect([2, 4])
    print(f"    All: {combo['has_all']['count']} cases | "
          f"Some: {combo['has_some']['count']} | None: {combo['has_none']['count']}")
    ce = combo.get("combinatorial_effect", {})
    if isinstance(ce, dict) and "DP" in ce:
        synergies = sum(1 for og in ["DP", "CV", "BL", "IM"]
                        if ce.get(og, {}).get("synergy", False))
        print(f"    Synergies detected: {synergies}/4 outcome groups")

    # ══════════════════════════════════════════════════════════════════
    # TEST 4: RELATIONSHIP TYPE EFFECTS
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("RELATIONSHIP TYPE EFFECTS")
    print("=" * 70)

    for rt in ["PT1", "PT3", "PT5"]:
        rt_result = relational.relationship_type_effect(rt)
        print(f"\n  {rt}: {RELATIONSHIP_TYPES[rt]}")
        print(f"    Has: {rt_result['has_count']} | Lacks: {rt_result['lacks_count']}")
        for og in ["DP", "CV", "BL", "IM"]:
            d = rt_result["outcome_differences"][og]
            print(f"    {OUTCOME_GROUP_NAMES[og]:25s}: Δ={d['delta']:+.4f}")

    # PT3 should differentiate Balance
    pt3_result = relational.relationship_type_effect("PT3")
    bl_diff = pt3_result["outcome_differences"].get("BL", {}).get("delta", 0)
    if abs(bl_diff) > 0.01:
        print(f"\n✓ PT3 (Sovereignty Protection) differentiates Balance (Δ={bl_diff:+.4f})")
        passed += 1
    else:
        print(f"\n✗ PT3 does not differentiate Balance")
        failed += 1

    # ══════════════════════════════════════════════════════════════════
    # TEST 5: AGENT-AGENT INTERACTIONS
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("AGENT-AGENT INTERACTIONS")
    print("=" * 70)

    aa = relational.agent_agent_analysis()
    print(f"\n  Directly partnered cases: {len(aa)}")

    convergent_count = 0
    for case, data in aa.items():
        convergences = sum(1 for og, conv in data["outcome_convergence"].items()
                           if conv.get("convergent", False))
        total = len(data["outcome_convergence"])
        if convergences > 0:
            convergent_count += 1
        print(f"  {case:25s} → {data['partners']} "
              f"| {convergences}/{total} convergent outcomes "
              f"| shared PTs: {data['shared_partner_types']}")

    if convergent_count > 0:
        print(f"\n✓ {convergent_count} partnered cases show outcome convergence")
        passed += 1
    else:
        print(f"\n✗ No convergence detected in partnered cases")
        failed += 1

    # ══════════════════════════════════════════════════════════════════
    # TEST 6: INDIGENOUS DATA SOVEREIGNTY CLUSTER
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("CLUSTER ANALYSIS — Indigenous Data Sovereignty")
    print("=" * 70)

    ids_cluster = relational.cluster_analysis("Indigenous Data Sovereignty")
    if "error" not in ids_cluster:
        print(f"\n  Members: {ids_cluster['members']}")
        print(f"  Avg density: {ids_cluster['avg_relational_density']}")
        print(f"  Outcome differences (cluster vs rest):")
        for og in ["DP", "CV", "BL", "IM"]:
            d = ids_cluster["outcome_differences"][og]
            print(f"    {OUTCOME_GROUP_NAMES[og]:25s}: Δ={d:+.4f}")

        emg = ids_cluster["emergent_properties"]
        print(f"\n  Emergent properties:")
        print(f"    Outcome breadth: avg member={emg['avg_member_outcome_breadth']}, "
              f"collective={emg['collective_outcome_breadth']} "
              f"(emergence={emg['breadth_emergence']})")
        print(f"    Sovereignty dims: avg member={emg['avg_member_sovereignty_dimensions']}, "
              f"collective={emg['collective_sovereignty_dimensions']} "
              f"(emergence={emg['sovereignty_emergence']})")

        if emg.get("sovereignty_emergence") or emg.get("breadth_emergence"):
            print(f"\n✓ Indigenous cluster exhibits emergent properties")
            passed += 1
        else:
            print(f"\n✗ No emergence detected")
            failed += 1
    else:
        print(f"\n✗ Cluster analysis failed: {ids_cluster['error']}")
        failed += 1

    # ══════════════════════════════════════════════════════════════════
    # TEST 7: RELATIONAL DENSITY AS MODERATOR
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("RELATIONAL DENSITY AS MODERATOR")
    print("=" * 70)

    mod = relational.density_as_moderator()
    print(f"\n  High density: {mod['high_density']['count']} cases "
          f"(avg={mod['high_density']['avg_density']}, "
          f"cond_div={mod['high_density']['avg_condition_diversity']})")
    print(f"  Low density:  {mod['low_density']['count']} cases "
          f"(avg={mod['low_density']['avg_density']}, "
          f"cond_div={mod['low_density']['avg_condition_diversity']})")

    moderation_found = False
    for og in ["DP", "CV", "BL", "IM"]:
        me = mod["moderation_evidence"][og]
        print(f"    {OUTCOME_GROUP_NAMES[og]:25s}: Δ={me['difference']:+.4f} "
              f"({me['direction']})")
        if abs(me["difference"]) > 0.02:
            moderation_found = True

    print(f"\n  Matched pairs (similar conditions, different density): {len(mod['matched_pairs'])}")
    for pair in mod["matched_pairs"][:3]:
        print(f"    {pair['low']:20s} (d={pair['low_density']}) vs "
              f"{pair['high']:20s} (d={pair['high_density']})")
        for og in ["DP", "BL"]:
            print(f"      {OUTCOME_GROUP_NAMES[og]}: Δ={pair['outcome_differences'][og]:+.3f}")

    if moderation_found:
        print(f"\n✓ Relational density moderates outcome profiles")
        passed += 1
    else:
        print(f"\n✗ No moderation effect detected")
        failed += 1

    # ══════════════════════════════════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed}/{passed + failed} tests passed")
    print("=" * 70)

    return passed, failed


if __name__ == "__main__":
    p, f = main()
    sys.exit(0 if f == 0 else 1)
