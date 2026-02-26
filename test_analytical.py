"""
Test script: verify all analytical operations.

Tests against Chapter 7 specifications:
1. Validation suite (consistency, input response, cross-impact alignment)
2. Sensitivity analysis produces directionally correct results
3. Generative logic claims hold computationally
4. Counter-case testing shows appropriate outcome reduction
5. Reverse analysis identifies correct condition patterns
6. Sovereignty tracing works end-to-end
7. Hypothetical case generation returns plausible results
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from data_loader import load_model_data
from primary_model import PrimaryModel
from analytical_engine import AnalyticalEngine
from config import OUTCOME_GROUP_NAMES, CONDITION_TYPE_NAMES, SOVEREIGNTY_DIMENSIONS


def main():
    print("=" * 70)
    print("DIGITAL RIGHTS PROJECTS ABM — Phase 3 Analytical Operations Test")
    print("=" * 70)
    print()

    # Load
    agents, loader = load_model_data()
    model = PrimaryModel(agents, cross_impact_quant=loader.cross_impact_quant)
    engine = AnalyticalEngine(model)

    passed = 0
    failed = 0

    # ══════════════════════════════════════════════════════════════════
    # TEST 1: VALIDATION SUITE
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("VALIDATION SUITE")
    print("=" * 70)

    validation = engine.run_all_validation()

    # 1a: Consistency
    v1 = validation["consistency"]
    if v1["status"] == "PASS":
        print(f"\n✓ Consistency: {v1['status']} — {v1['n_runs']} identical runs")
        passed += 1
    else:
        print(f"\n✗ Consistency: {v1['status']}")
        failed += 1

    # 1b: Input response
    v2 = validation["input_response"]
    pass_count = sum(1 for d in v2["details"] if d["status"] == "PASS")
    if v2["status"] == "PASS":
        print(f"✓ Input Response: {v2['status']} — {pass_count}/{v2['n_tests']} tests")
        passed += 1
    else:
        print(f"✗ Input Response: {v2['status']} — {pass_count}/{v2['n_tests']} tests")
        for d in v2["details"]:
            if d["status"] == "FAIL":
                print(f"    FAIL: {d['case']} {d['condition']}→{d['outcome']} "
                      f"delta={d['delta']} expected={d['expected']} actual={d['actual']}")
        failed += 1

    # 1c: Cross-impact alignment
    v3 = validation["cross_impact_alignment"]
    print(f"{'✓' if v3['status'] in ('PASS','PARTIAL') else '✗'} Cross-Impact Alignment: "
          f"{v3['status']} — avg alignment={v3['avg_alignment']}")
    for og, data in v3["per_outcome"].items():
        print(f"    {OUTCOME_GROUP_NAMES[og]}: "
              f"CI={data['cross_impact_top3']} | Sens={data['sensitivity_top3']} "
              f"| overlap={data['overlap']}")
    if v3["status"] in ("PASS", "PARTIAL"):
        passed += 1
    else:
        failed += 1

    # ══════════════════════════════════════════════════════════════════
    # TEST 2: CONDITION SENSITIVITY — Te Hiku Media
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("CONDITION SENSITIVITY — Te Hiku Media")
    print("=" * 70)

    thm_sens = engine.condition_sensitivity("Te Hiku Media", "PU", 0.25)
    # PU connects to DP and IM in Te Hiku Media's production rule
    pu_dp = thm_sens["outcome_effects"].get("DP", {})
    pu_im = thm_sens["outcome_effects"].get("IM", {})

    pu_ok = (pu_dp.get("connected", False) and pu_dp.get("change", 0) > 0 and
             pu_im.get("connected", False) and pu_im.get("change", 0) > 0)

    if pu_ok:
        print(f"\n✓ PU +0.25 → DP change={pu_dp['change']:.4f}, IM change={pu_im['change']:.4f}")
        passed += 1
    else:
        print(f"\n✗ PU sensitivity unexpected: DP={pu_dp}, IM={pu_im}")
        failed += 1

    # RG connects to DP in Te Hiku Media
    thm_rg = engine.condition_sensitivity("Te Hiku Media", "RG", -0.25)
    rg_dp = thm_rg["outcome_effects"].get("DP", {})
    rg_ok = rg_dp.get("connected", False) and rg_dp.get("change", 0) < 0
    if rg_ok:
        print(f"✓ RG -0.25 → DP change={rg_dp['change']:.4f} (decrease, as expected)")
        passed += 1
    else:
        print(f"✗ RG sensitivity unexpected: DP={rg_dp}")
        failed += 1

    # ══════════════════════════════════════════════════════════════════
    # TEST 3: ECOSYSTEM SENSITIVITY MATRIX
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("ECOSYSTEM SENSITIVITY — Condition Importance Rankings")
    print("=" * 70)

    for og in ["DP", "CV", "BL", "IM"]:
        ranking = engine.condition_importance_ranking(og, 0.25)
        top3 = ranking[:3]
        print(f"\n  {OUTCOME_GROUP_NAMES[og]} — Top 3 most important conditions:")
        for r in top3:
            print(f"    {r['condition_name']:25s} avg_change={r['avg_change']:.4f} "
                  f"({r['cases_connected']} cases)")

    # Check Partners→Balance is top
    bl_ranking = engine.condition_importance_ranking("BL", 0.25)
    bl_top = bl_ranking[0]["condition_type"] if bl_ranking else None
    if bl_top == "PT":
        print(f"\n✓ Partners is #1 for Balance (consistent with PT→BL=26 links)")
        passed += 1
    else:
        print(f"\n✗ Top for Balance is {bl_top}, expected PT")
        failed += 1

    # ══════════════════════════════════════════════════════════════════
    # TEST 4: GENERATIVE LOGIC CLAIMS
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("GENERATIVE LOGIC TESTING")
    print("=" * 70)

    gl_data = engine.test_generative_logic(0.25)
    gl_holds = 0
    for r in gl_data["claims"]:
        status = "✓ HOLDS" if r["holds"] else "✗ DOES NOT HOLD"
        strongest = " (STRONGEST)" if r["strongest"] else f" (rank #{r['rank_among_conditions']})"
        print(f"\n  {status}: {r['claim']}")
        print(f"    avg effect={r['avg_effect']:.4f}, "
              f"cases={r['cases_connected']}{strongest}")
        if r["holds"]:
            gl_holds += 1

    n_claims = gl_data["n_claims"]
    if gl_holds >= 3:
        print(f"\n✓ {gl_holds}/{n_claims} generative logic claims hold (top-3 threshold)")
        passed += 1
    else:
        print(f"\n✗ Only {gl_holds}/{n_claims} claims hold")
        failed += 1

    # ══════════════════════════════════════════════════════════════════
    # TEST 5: COUNTER-CASE — Remove Purpose from Te Hiku Media
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("COUNTER-CASE TESTING")
    print("=" * 70)

    cc = engine.remove_condition("Te Hiku Media", "PU")
    cc_im = cc["outcome_effects"].get("IM", {})
    cc_dp = cc["outcome_effects"].get("DP", {})

    print(f"\n  Te Hiku Media: Remove Purpose (PU 1.00 → 0.00)")
    for og in ["DP", "CV", "BL", "IM"]:
        eff = cc["outcome_effects"].get(og, {})
        if eff.get("connected"):
            print(f"    {OUTCOME_GROUP_NAMES[og]}: {eff['baseline']:.3f} → "
                  f"{eff['modified']:.3f} (Δ={eff['change']:.4f})")

    cc_ok = cc_im.get("change", 0) < 0 and cc_dp.get("change", 0) < 0
    if cc_ok:
        print(f"  ✓ Removing Purpose reduces DP and IM as predicted")
        passed += 1
    else:
        print(f"  ✗ Unexpected counter-case result")
        failed += 1

    # Org type swap
    print(f"\n  Te Hiku Media: Swap to Peer Production avg profile")
    swap = engine.swap_org_type_profile("Te Hiku Media", "PP")
    for og in ["DP", "CV", "BL", "IM"]:
        eff = swap["outcome_effects"].get(og, 0)
        print(f"    {OUTCOME_GROUP_NAMES[og]}: Δ={eff:.4f}")

    # ══════════════════════════════════════════════════════════════════
    # TEST 6: REVERSE ANALYSIS
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("REVERSE ANALYSIS")
    print("=" * 70)

    # What conditions produce Balance?
    rev_bl = engine.reverse_analysis_outcome("BL", 0.3)
    print(f"\n  Target: Balance (score ≥ 0.3)")
    print(f"  Achievers: {rev_bl['achiever_count']} cases")
    print(f"  Top condition frequencies among achievers:")
    for ct, freq in list(rev_bl["condition_frequency_among_achievers"].items())[:5]:
        print(f"    {CONDITION_TYPE_NAMES.get(ct, ct):25s}: {freq} cases")

    rev_ok = "PT" in list(rev_bl["condition_frequency_among_achievers"].keys())[:3]
    if rev_ok:
        print(f"  ✓ Partners among top conditions for Balance achievers")
        passed += 1
    else:
        print(f"  ✗ Partners not in top 3")
        failed += 1

    # Reverse sovereignty
    rev_sov = engine.reverse_analysis_sovereignty("epistemic")
    print(f"\n  Target Sovereignty: epistemic")
    print(f"  Cases with capacity: {rev_sov['cases_with_capacity']}")
    print(f"  Contributing outcomes: {rev_sov['contributing_outcome_codes']}")
    print(f"  Top 5 cases:")
    for c in rev_sov["top_cases"][:5]:
        print(f"    {c['case']:30s} score={c['dimension_score']:.3f} "
              f"outcomes={c['contributing_outcomes']}")

    # ══════════════════════════════════════════════════════════════════
    # TEST 7: SOVEREIGNTY TRACING
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("SOVEREIGNTY PATHWAY TRACING — Te Hiku Media")
    print("=" * 70)

    pathways = engine.trace_sovereignty_pathway("Te Hiku Media")
    for p in pathways:
        print(f"\n  [{p['condition_type']}] {p['condition_name']}")
        print(f"    → ({p['mechanism']}) → [{p['outcome_group']}] {p['outcome_name']}")
        print(f"    → sovereignty: {', '.join(p['sovereignty_dimensions'])}")

    sov_sens = engine.sovereignty_sensitivity("Te Hiku Media", "PU", 0.25)
    print(f"\n  Sovereignty effects of PU +0.25:")
    for dim, eff in sov_sens.get("sovereignty_effects", {}).items():
        print(f"    {dim:20s}: {eff:+.4f}")

    if sov_sens.get("sovereignty_effects"):
        print(f"  ✓ Sovereignty sensitivity produces non-zero effects")
        passed += 1
    else:
        print(f"  ✗ No sovereignty effects computed")
        failed += 1

    # ══════════════════════════════════════════════════════════════════
    # TEST 8: HYPOTHETICAL CASE
    # ══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("HYPOTHETICAL CASE CREATION")
    print("=" * 70)

    hyp = engine.hypothetical_case(
        {"GV": 0.8, "TP": 0.6, "RS": 0.7, "PT": 0.5},
        name="Strong Governance Digital Cooperative"
    )
    print(f"\n  {hyp['name']}")
    print(f"  Conditions: {hyp['condition_profile']}")
    print(f"  Predicted outcomes:")
    for og in ["DP", "CV", "BL", "IM"]:
        score = hyp["predicted_outcomes"].get(og)
        print(f"    {OUTCOME_GROUP_NAMES[og]:25s}: {score:.3f}" if score else
              f"    {OUTCOME_GROUP_NAMES[og]:25s}: N/A")
    print(f"  Most similar cases:")
    for s in hyp["similar_cases"][:3]:
        print(f"    {s['case']:30s} similarity={s['similarity']:.3f}")

    hyp_ok = hyp["predicted_outcomes"].get("DP") is not None
    if hyp_ok:
        print(f"  ✓ Hypothetical case produces predictions")
        passed += 1
    else:
        print(f"  ✗ No predictions generated")
        failed += 1

    # ======================================================================
    # TEST 12: NECESSARY CONDITION ENFORCEMENT (Revision 4.4)
    # ======================================================================
    print()
    print("=" * 70)
    print("NECESSARY CONDITION ENFORCEMENT")
    print("=" * 70)

    # Te Hiku Media has PU active with PU1 (Indigenous Epistemology)
    # PU1 is necessary for DP6. Removing PU should flag necessary violation.
    nc_test = engine.remove_condition("Te Hiku Media", "PU")
    dp_eff = nc_test["outcome_effects"].get("DP", {})
    nc_violated = dp_eff.get("necessary_condition_violated", False)
    if nc_violated:
        print(f"  ✓ Removing PU from Te Hiku Media flags necessary condition violation")
        print(f"    {dp_eff.get('necessary_pair', '')}")
        passed += 1
    else:
        print(f"  ✗ Necessary condition violation NOT flagged for PU removal")
        failed += 1

    # ======================================================================
    # TEST 13: OUTCOME CO-OCCURRENCE (Revision 4.5)
    # ======================================================================
    print()
    print("=" * 70)
    print("OUTCOME CO-OCCURRENCE PROPAGATION")
    print("=" * 70)

    # Sensitivity analysis should now include cooccurrence_effects
    cooc_test = engine.condition_sensitivity("Te Hiku Media", "PU", 0.25)
    cooc_eff = cooc_test.get("cooccurrence_effects", {})
    if cooc_eff:
        print(f"  Co-occurrence propagation effects:")
        for og, val in cooc_eff.items():
            print(f"    {OUTCOME_GROUP_NAMES.get(og, og):25s}: {val:+.4f}")
        print(f"  ✓ Co-occurrence effects propagated ({len(cooc_eff)} groups affected)")
        passed += 1
    else:
        print(f"  ✗ No co-occurrence effects computed")
        failed += 1

    # Standalone co-occurrence analysis
    cooc_analysis = engine.outcome_cooccurrence_analysis()
    dp_cv_rate = cooc_analysis["dp_cv_rate"]
    print(f"\n  Empirical DP-CV co-occurrence rate: {dp_cv_rate:.3f}")
    print(f"  Documented rate: 0.71")

    # ======================================================================
    # TEST 14: CONDITION INTERACTION ANALYSIS (Revision 4.6)
    # ======================================================================
    print()
    print("=" * 70)
    print("CONDITION INTERACTION ANALYSIS")
    print("=" * 70)

    interaction = engine.condition_interaction_analysis("GV", "TP")
    sizes = interaction["group_sizes"]
    print(f"  Governance × Technology interaction:")
    print(f"    Both active: {sizes['both']} cases")
    print(f"    Only GV: {sizes['only_1']} | Only TP: {sizes['only_2']} | Neither: {sizes['neither']}")
    for og, eff in interaction["interaction_effects"].items():
        itype = eff.get("interaction_type", "N/A")
        ieff = eff.get("interaction_effect")
        if ieff is not None:
            print(f"    {OUTCOME_GROUP_NAMES.get(og, og):25s}: {itype} ({ieff:+.4f})")

    if sizes["both"] > 0 and any(
        e.get("interaction_type") in ("synergistic", "antagonistic", "additive")
        for e in interaction["interaction_effects"].values()
    ):
        print(f"  ✓ Condition interaction analysis produces results")
        passed += 1
    else:
        print(f"  ✗ Condition interaction analysis failed")
        failed += 1

    # ======================================================================
    # TEST 15: BRIDGE B TERRAIN-CAPACITY GAP (Revision 4.2)
    # ======================================================================
    print()
    print("=" * 70)
    print("BRIDGE B: TERRAIN-CAPACITY GAP ANALYSIS")
    print("=" * 70)

    gap = engine.terrain_capacity_gap("Te Hiku Media")
    print(f"  Te Hiku Media terrain-capacity gaps:")
    for dim, vals in gap["dimensions"].items():
        if vals["terrain"] > 0 or vals["capacity"] > 0:
            print(f"    {dim:20s}: terrain={vals['terrain']:.3f} capacity={vals['capacity']:.3f} "
                  f"gap={vals['gap']:+.3f} ({vals['interpretation']})")
    print(f"  Unrealized: {gap['unrealized_dimensions']}")
    print(f"  Emergent: {gap['emergent_dimensions']}")

    if gap["unrealized_dimensions"] or gap["emergent_dimensions"]:
        print(f"  ✓ Terrain-capacity gap analysis identifies meaningful gaps")
        passed += 1
    else:
        print(f"  ✗ No meaningful gaps detected")
        failed += 1

    # Ecosystem-level gap
    eco_gap = engine.terrain_capacity_gap()
    print(f"\n  Ecosystem-level average gaps:")
    for dim, vals in eco_gap["avg_dimensions"].items():
        print(f"    {dim:20s}: terrain={vals['terrain']:.3f} capacity={vals['capacity']:.3f} "
              f"gap={vals['gap']:+.3f}")

    # ======================================================================
    # TEST 16: RECURSIVE PATTERN ASSIGNMENT (Revision 4.3)
    # ======================================================================
    print()
    print("=" * 70)
    print("RECURSIVE PATTERN ASSIGNMENT")
    print("=" * 70)

    rp_thm = engine.assign_recursive_patterns("Te Hiku Media")
    print(f"  Te Hiku Media: {rp_thm['pattern_count']} patterns across "
          f"{len(rp_thm['rows'])} production rule rows")
    for row in rp_thm["rows"]:
        print(f"    {row['condition']:20s} → {row['outcome']:20s} | "
              f"patterns: {row['pattern_names']}")
    print(f"  Patterns: {rp_thm['pattern_names']}")

    # Ecosystem-level
    rp_eco = engine.assign_recursive_patterns()
    top3 = rp_eco["most_common_patterns"][:3]
    print(f"\n  Ecosystem top patterns:")
    for p in top3:
        print(f"    #{p['id']:2d} {p['name']:40s}: {p['cases']} cases")

    if rp_thm["pattern_count"] > 0 and rp_eco["total_cases"] > 0:
        print(f"  ✓ Recursive patterns assigned ({rp_eco['total_cases']} cases)")
        passed += 1
    else:
        print(f"  ✗ Recursive pattern assignment failed")
        failed += 1

    # ======================================================================
    # TEST 17: CONDITION CLASSIFICATION ANNOTATION (Revision 4.7)
    # ======================================================================
    print()
    print("=" * 70)
    print("CONDITION CLASSIFICATION ANNOTATIONS")
    print("=" * 70)

    # Test a case with PU (which has PU1=necessary, PU2=specialist)
    cls_test = engine.condition_sensitivity("Te Hiku Media", "PU", 0.25)
    classifications = cls_test.get("condition_classifications", [])
    if classifications:
        print(f"  PU for Te Hiku Media classified as: {classifications}")
        print(f"  ✓ Condition classification annotation present")
        passed += 1
    else:
        print(f"  ✗ No condition classification annotations")
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
