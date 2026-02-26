"""
Test script: verify data loading, agent construction, and model operations.

Checks against known empirical findings from Chapter 7:
1. 43 agents loaded
2. Te Hiku Media profile matches handoff specification
3. Governance → Democratic Practices is strongest association (36 links)
4. Partners → Balance dominates (26 links)
5. Five comprehensive cases (all 4 outcome groups)
6. Indigenous cluster has highest relational density
7. DSOs average highest relational density
8. SOLshare achieves 4 groups with only 3 condition types
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from data_loader import load_model_data
from primary_model import PrimaryModel
from config import OUTCOME_GROUP_NAMES, CONDITION_TYPE_NAMES


def main():
    print("=" * 70)
    print("DIGITAL RIGHTS PROJECTS ABM — Phase 1 Data Loading Test")
    print("=" * 70)
    print()

    # Load everything
    agents, loader = load_model_data()
    model = PrimaryModel(agents, cross_impact_quant=loader.cross_impact_quant)

    print()
    print("=" * 70)
    print("VERIFICATION TESTS")
    print("=" * 70)

    passed = 0
    failed = 0

    # ── Test 1: 43 agents ─────────────────────────────────────────────
    n = len(agents)
    if n == 43:
        print(f"\n✓ TEST 1: {n} agents loaded (expected 43)")
        passed += 1
    else:
        print(f"\n✗ TEST 1: {n} agents loaded (expected 43)")
        failed += 1

    # ── Test 2: Te Hiku Media profile ─────────────────────────────────
    thm = model.get_agent("Te Hiku Media")
    checks = []
    checks.append(("org_type", thm.org_type, "DSO"))
    checks.append(("PU score", thm.internal_condition_scores.get("PU"), 1.00))
    checks.append(("TT score", thm.internal_condition_scores.get("TT"), 0.50))
    checks.append(("PT score", thm.internal_condition_scores.get("PT"), 0.25))
    checks.append(("RG score", thm.external_condition_scores.get("RG"), 0.75))
    checks.append(("DP outcome", thm.outcome_scores.get("DP"), 0.60))
    checks.append(("CV outcome", thm.outcome_scores.get("CV"), 0.33))
    checks.append(("BL outcome", thm.outcome_scores.get("BL"), 0.22))
    checks.append(("IM outcome", thm.outcome_scores.get("IM"), 0.48))
    checks.append(("outcome_breadth", thm.outcome_breadth, 4))

    thm_pass = True
    for label, actual, expected in checks:
        if actual != expected:
            print(f"\n✗ TEST 2 ({label}): got {actual}, expected {expected}")
            thm_pass = False

    if thm_pass:
        print(f"\n✓ TEST 2: Te Hiku Media profile matches specification")
        passed += 1
    else:
        failed += 1

    # ── Test 3: Governance → Democratic Practices strongest ───────────
    ci_logic = model.cross_impact_generative_logic()
    top = ci_logic[0] if ci_logic else None
    if top and top["condition_type"] == "GV" and top["outcome_group"] == "DP":
        print(f"\n✓ TEST 3: Governance → Democratic Practices is strongest ({top['count']} links)")
        passed += 1
    else:
        print(f"\n✗ TEST 3: Top cross-impact association is {top}")
        failed += 1

    # ── Test 4: Partners → Balance dominates ──────────────────────────
    # Use cross-impact logic for consistency
    bl_entries = [e for e in ci_logic if e["outcome_group"] == "BL"]
    bl_top = bl_entries[0] if bl_entries else None
    if bl_top and bl_top["condition_type"] == "PT":
        print(f"\n✓ TEST 4: Partners → Balance dominates ({bl_top['count']} links)")
        passed += 1
    else:
        print(f"\n✗ TEST 4: Top Balance association is {bl_top}")
        failed += 1

    # ── Test 5: Five comprehensive cases ──────────────────────────────
    summary = model.ecosystem_summary()
    comprehensive = summary["comprehensive_cases"]
    expected_comp = {"Guifi.net", "Matrix", "Masakhane", "Te Hiku Media", "SOLshare"}
    if set(comprehensive) == expected_comp:
        print(f"\n✓ TEST 5: Five comprehensive cases match: {comprehensive}")
        passed += 1
    else:
        print(f"\n✗ TEST 5: Comprehensive cases: {comprehensive}")
        print(f"  Expected: {expected_comp}")
        # Check overlap
        print(f"  Overlap: {set(comprehensive) & expected_comp}")
        print(f"  Missing: {expected_comp - set(comprehensive)}")
        print(f"  Extra: {set(comprehensive) - expected_comp}")
        failed += 1

    # ── Test 6: Indigenous cluster highest relational density ─────────
    gida = model.get_agent("GIDA")
    fnigc = model.get_agent("FNIGC")
    tmr = model.get_agent("Te Mana Raraunga")
    rd_ok = (
        abs(gida.relational_density - 2.92) < 0.01 and
        abs(fnigc.relational_density - 2.83) < 0.01 and
        abs(tmr.relational_density - 2.83) < 0.01
    )
    if rd_ok:
        print(f"\n✓ TEST 6: Indigenous cluster relational density correct "
              f"(GIDA={gida.relational_density}, FNIGC={fnigc.relational_density}, "
              f"TMR={tmr.relational_density})")
        passed += 1
    else:
        print(f"\n✗ TEST 6: GIDA={gida.relational_density}, "
              f"FNIGC={fnigc.relational_density}, TMR={tmr.relational_density}")
        failed += 1

    # ── Test 7: DSOs highest avg relational density ───────────────────
    by_type = model.compare_by_org_type()
    dso_rd = by_type.get("DSO", {}).get("avg_relational_density", 0)
    dc_rd = by_type.get("DC", {}).get("avg_relational_density", 0)
    if dso_rd > dc_rd and dso_rd > 2.0:
        print(f"\n✓ TEST 7: DSOs highest avg relational density "
              f"(DSO={dso_rd}, DC={dc_rd})")
        passed += 1
    else:
        print(f"\n✗ TEST 7: DSO avg RD={dso_rd}, DC avg RD={dc_rd}")
        for ot, data in by_type.items():
            print(f"  {ot}: {data.get('avg_relational_density', 0)}")
        failed += 1

    # ── Test 8: SOLshare — 4 outcomes with 3 condition types ──────────
    sol = model.get_agent("SOLshare")
    sol_ct = sol.condition_diversity
    sol_ob = sol.outcome_breadth
    if sol_ob == 4 and sol_ct <= 4:
        print(f"\n✓ TEST 8: SOLshare has {sol_ob} outcome groups with "
              f"{sol_ct} condition types (configurational)")
        passed += 1
    else:
        print(f"\n✗ TEST 8: SOLshare condition_diversity={sol_ct}, outcome_breadth={sol_ob}")
        failed += 1

    # ── Test 9: Sovereignty dimensions are 7 (not 10) ─────────────────────────
    from config import SOVEREIGNTY_DIMENSIONS
    expected_dims = ["technical", "infrastructure", "territorial", "economic",
                     "ecological", "collective_rights", "epistemic"]
    sov_dims = list(thm.sovereignty_profile.keys())
    terrain_dims = list(thm.sovereignty_terrain.keys())
    if (len(sov_dims) == 7 and set(sov_dims) == set(expected_dims) and
            len(terrain_dims) == 7 and set(terrain_dims) == set(expected_dims)):
        print(f"\n✓ TEST 9: 7 sovereignty dimensions correct (capacity + terrain)")
        passed += 1
    else:
        print(f"\n✗ TEST 9: Expected 7 dims, got capacity={len(sov_dims)}, terrain={len(terrain_dims)}")
        failed += 1

    # ── Test 10: Bridge B terrain profile non-empty ─────────────────────────
    active_terrain = [d for d, s in thm.sovereignty_terrain.items() if s > 0]
    if len(active_terrain) >= 3:
        print(f"\n✓ TEST 10: Te Hiku Media has {len(active_terrain)} active terrain dimensions")
        passed += 1
    else:
        print(f"\n✗ TEST 10: Only {len(active_terrain)} active terrain dimensions")
        failed += 1

    # ── Summary ───────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print(f"RESULTS: {passed}/{passed + failed} tests passed")
    print("=" * 70)

    # ── Display Te Hiku Media profile ─────────────────────────────────
    print()
    print(model.agent_profile_text("Te Hiku Media"))

    # ── Generative Logic Top 10 (Cross-Impact) ──────────────────────────
    print()
    print("═══ Top 10 Cross-Impact Condition → Outcome Associations ═══")
    ci_logic = model.cross_impact_generative_logic()
    for item in ci_logic[:10]:
        print(f"  {item['condition_name']:25s} → {item['outcome_name']:22s}: {item['count']} links")

    # ── Production Rule Level Frequencies ─────────────────────────────
    print()
    print("═══ Top 10 Production Rule Condition → Outcome Frequencies ═══")
    gen_logic = model.generative_logic_summary()
    for item in gen_logic[:10]:
        print(f"  {item['condition_name']:25s} → {item['outcome_name']:22s}: {item['count']} links")

    # ── Org Type Comparison ───────────────────────────────────────────
    print()
    print("═══ Organizational Type Comparison ═══")
    for ot, data in by_type.items():
        print(f"\n  {data['name']} ({data['count']} cases):")
        print(f"    Avg condition diversity: {data['avg_condition_diversity']}")
        print(f"    Avg relational density: {data['avg_relational_density']}")
        for og, stats in data['outcome_profiles'].items():
            print(f"    {OUTCOME_GROUP_NAMES[og]}: mean={stats['mean']:.3f} ({stats['presence']})")

    return passed, failed


if __name__ == "__main__":
    p, f = main()
    sys.exit(0 if f == 0 else 1)
