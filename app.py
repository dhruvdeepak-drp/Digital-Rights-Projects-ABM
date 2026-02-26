"""
Digital Rights Projects ABM — Web Interface (Complete)
Run: python app.py → http://localhost:5001

Exposes ALL analytical operations from:
  - PrimaryModel (ecosystem stats, generative logic, org type comparison)
  - AnalyticalEngine (sensitivity, counterfactual, hypothetical, sovereignty, reverse)
  - RelationalEngine (density, partner types, relationship types, clusters, agent-agent)
"""
import os, sys, json
from flask import Flask, jsonify, request, send_from_directory, session, redirect, url_for

sys.path.insert(0, os.path.dirname(__file__))
from data_loader import load_model_data
from primary_model import PrimaryModel
from analytical_engine import AnalyticalEngine
from relational_engine import RelationalEngine
from collections import defaultdict
from config import (
    OUTCOME_GROUPS, OUTCOME_GROUP_NAMES, CONDITION_TYPE_NAMES,
    ALL_CONDITION_TYPES, INTERNAL_CONDITION_TYPES, EXTERNAL_CONDITION_TYPES,
    SOVEREIGNTY_DIMENSIONS, ORG_TYPE_NAMES, RECURSIVE_PATTERNS,
    PARTNER_TYPES, RELATIONSHIP_TYPES, LATENT_CLUSTERS, DIRECT_PARTNERSHIPS,
    CONDITION_CATEGORIES, OUTCOME_CATEGORIES,
    OUTCOME_SOVEREIGNTY_MAP, CONDITION_SOVEREIGNTY_TERRAIN,
    OUTCOME_GROUP_SOVEREIGNTY, CONDITION_MECHANISM_MAP, MECHANISM_TYPES,
    NECESSARY_CONDITIONS, NEAR_NECESSARY_CONDITIONS,
    OUTCOME_COOCCURRENCE,
    MECHANISM_RECURSIVE_MAP, RECURSIVE_PATTERN_REFINEMENT,
)

# ── Initialize models ──────────────────────────────────────────────────
print("Initializing ABM...")
agents, loader = load_model_data()
model = PrimaryModel(agents, cross_impact_quant=loader.cross_impact_quant)
engine = AnalyticalEngine(model)
relational = RelationalEngine(model, analytical_engine=engine)
print(f"Ready: {len(agents)} agents loaded.\n")

# ── Precompute score → category mapping ────────────────────────────
SCORE_CATEGORY_MAP = {}
SCORE_INTERPRETATION = {
    "1.0": "Foundational",
    "0.75": "Strongly Constructive",
    "0.5": "Constructive",
    "0.25": "Enabling",
    "0.0": "Neutral",
    "-0.25": "Navigational",
}
for ct in ALL_CONDITION_TYPES:
    ct_data = defaultdict(lambda: defaultdict(int))
    for a in agents.values():
        s = a.internal_condition_scores.get(ct) or a.external_condition_scores.get(ct)
        if s is not None:
            for cat in a.condition_categories.get(ct, []):
                ct_data[str(round(s, 2))][cat] += 1
    if ct_data:
        SCORE_CATEGORY_MAP[ct] = {
            score: sorted(cats.items(), key=lambda x: -x[1])
            for score, cats in ct_data.items()
        }

# Precompute outcome score → category mapping
OUTCOME_SCORE_CATS = {}
for og in OUTCOME_GROUPS:
    og_data = defaultdict(lambda: defaultdict(int))
    for a in agents.values():
        s = a.outcome_scores.get(og)
        if s is not None:
            for cat in a.outcome_categories.get(og, []):
                og_data[str(round(s, 2))][cat] += 1
    if og_data:
        OUTCOME_SCORE_CATS[og] = og_data

app = Flask(__name__, static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "drp-abm-session-key-2025")

ACCESS_PIN = "1012"

PIN_PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Digital Rights Projects ABM</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0e1117;color:#c9d1d9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
display:flex;align-items:center;justify-content:center;min-height:100vh}
.pin-box{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:2.5rem;text-align:center;max-width:340px;width:90%}
h1{font-size:1.1rem;margin-bottom:0.3rem;color:#e6edf3}
.sub{font-size:0.78rem;color:#8b949e;margin-bottom:1.5rem}
input{background:#0d1117;border:1px solid #30363d;color:#e6edf3;font-size:1.8rem;text-align:center;
letter-spacing:0.6rem;padding:0.7rem;border-radius:8px;width:100%;outline:none;margin-bottom:1rem}
input:focus{border-color:#58a6ff}
button{background:#238636;color:#fff;border:none;padding:0.6rem 2rem;border-radius:6px;font-size:0.9rem;
cursor:pointer;width:100%}
button:hover{background:#2ea043}
.err{color:#f85149;font-size:0.78rem;margin-bottom:0.8rem}
</style></head><body>
<div class="pin-box">
<h1>Digital Rights Projects</h1>
<div class="sub">Agent-Based Model Observatory</div>
ERRMSG
<form method="POST" action="/auth">
<input type="password" name="pin" maxlength="4" pattern="[0-9]{4}" inputmode="numeric" placeholder="----" autofocus required>
<button type="submit">Enter</button>
</form></div></body></html>"""

@app.before_request
def check_auth():
    if request.path == "/auth":
        return None
    if session.get("authenticated"):
        return None
    return PIN_PAGE.replace("ERRMSG", ""), 200

@app.route("/auth", methods=["POST"])
def auth():
    pin = request.form.get("pin", "")
    if pin == ACCESS_PIN:
        session["authenticated"] = True
        session.permanent = True
        return redirect("/")
    return PIN_PAGE.replace("ERRMSG", '<div class="err">Incorrect code</div>'), 200


# ══════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════

def safe(v, default=0):
    """None-safe numeric accessor."""
    return v if v is not None else default

def resolve_name(name):
    """Resolve a URL name to a canonical agent name, with partial matching."""
    if name in agents:
        return name
    for n in agents:
        if name.lower() in n.lower():
            return n
    return None

def agent_to_dict(agent, summary=False):
    """Convert Agent to JSON-serializable dict."""
    d = {
        "name": agent.name,
        "org_type": agent.org_type,
        "org_type_name": ORG_TYPE_NAMES.get(agent.org_type, agent.org_type),
        "economic_sector": agent.economic_sector,
        "location": agent.location,
        "geographic_scope": agent.geographic_scope,
        "maturity": agent.maturity,
        "condition_diversity": agent.condition_diversity,
        "outcome_breadth": agent.outcome_breadth,
        "relational_density": round(agent.relational_density, 3),
        "dominant_patterns": agent.dominant_pattern_names,
    }
    if summary:
        d["total_conditions"] = round(
            sum(safe(v) for v in agent.internal_condition_scores.values()) +
            sum(safe(v) for v in agent.external_condition_scores.values()), 3)
        d["total_outcomes"] = round(
            sum(safe(v) for v in agent.outcome_scores.values()), 3)
        d["sovereignty_profile"] = {
            dim: round(safe(agent.sovereignty_profile.get(dim)), 3)
            for dim in SOVEREIGNTY_DIMENSIONS
        }
        return d

    # ── Full profile ───────────────────────────────────────────────
    d["internal_conditions"] = {
        ct: {
            "name": CONDITION_TYPE_NAMES.get(ct, ct),
            "score": round(safe(agent.internal_condition_scores.get(ct)), 3),
            "categories": agent.condition_categories.get(ct, []),
            "category_names": {
                code: CONDITION_CATEGORIES.get(ct, {}).get(code, code)
                for code in agent.condition_categories.get(ct, [])
            },
            "mechanism": CONDITION_MECHANISM_MAP.get(ct, ""),
            "sovereignty_terrain": CONDITION_SOVEREIGNTY_TERRAIN.get(ct, []),
        }
        for ct in INTERNAL_CONDITION_TYPES
        if agent.internal_condition_scores.get(ct) is not None
    }
    d["external_conditions"] = {
        ct: {
            "name": CONDITION_TYPE_NAMES.get(ct, ct),
            "score": round(safe(agent.external_condition_scores.get(ct)), 3),
            "categories": agent.condition_categories.get(ct, []),
            "category_names": {
                code: CONDITION_CATEGORIES.get(ct, {}).get(code, code)
                for code in agent.condition_categories.get(ct, [])
            },
            "mechanism": CONDITION_MECHANISM_MAP.get(ct, ""),
            "sovereignty_terrain": CONDITION_SOVEREIGNTY_TERRAIN.get(ct, []),
        }
        for ct in EXTERNAL_CONDITION_TYPES
        if agent.external_condition_scores.get(ct) is not None
    }
    d["outcomes"] = {
        og: {
            "name": OUTCOME_GROUP_NAMES.get(og, og),
            "score": round(safe(agent.outcome_scores.get(og)), 3),
            "categories": agent.outcome_categories.get(og, []),
            "category_names": {
                code: OUTCOME_CATEGORIES.get(og, {}).get(code, code)
                for code in agent.outcome_categories.get(og, [])
            },
            "sovereignty_contributions": {
                code: OUTCOME_SOVEREIGNTY_MAP.get(code, [])
                for code in agent.outcome_categories.get(og, [])
            },
        }
        for og in OUTCOME_GROUPS
        if agent.outcome_scores.get(og) is not None
    }

    # Sovereignty: capacity (from outcomes) and terrain (from conditions)
    d["sovereignty_profile"] = {
        dim: round(safe(agent.sovereignty_profile.get(dim)), 3)
        for dim in SOVEREIGNTY_DIMENSIONS
    }
    d["sovereignty_terrain"] = {
        dim: round(safe(agent.sovereignty_terrain.get(dim)), 3)
        for dim in SOVEREIGNTY_DIMENSIONS
    }

    # Recursive D-A-S patterns (binary: list of patterns this case participates in)
    d["recursive_patterns"] = [
        {"id": pid, "name": RECURSIVE_PATTERNS.get(pid, f"#{pid}")}
        for pid in agent.recursive_patterns
    ]

    # Production rule
    d["production_rules"] = [
        {
            "condition_type": r.condition_type,
            "condition_name": r.condition_name,
            "condition_codes": r.condition_codes,
            "mechanism": r.mechanism_type,
            "outcome_group": r.outcome_group,
            "outcome_name": r.outcome_name,
            "outcome_codes": r.outcome_codes,
            "description": r.description,
            "challenge": r.challenge,
        }
        for r in agent.production_rule
    ]

    # Appendix 3 enrichment
    d["condition_interactions"] = agent.condition_interactions
    d["synthesis"] = agent.synthesis
    d["compact_equation"] = agent.compact_equation

    # Relational profile (second model)
    rp = agent.relational_profile
    d["partner_types_engaged"] = rp.partner_types_engaged if rp else []
    d["partner_type_names"] = {
        pt: PARTNER_TYPES.get(pt, f"Type {pt}")
        for pt in (rp.partner_types_engaged if rp else [])
    }
    d["relationship_types"] = rp.relationship_types if rp else []
    d["relationship_type_names"] = {
        rt: RELATIONSHIP_TYPES.get(rt, rt)
        for rt in (rp.relationship_types if rp else [])
    }
    d["relational_dimensions"] = {
        "partner_diversity": rp.partner_diversity if rp else 0,
        "partner_diversity_norm": round(rp.partner_diversity_norm, 3) if rp else 0,
        "relationship_type_range": rp.relationship_type_range if rp else 0,
        "relationship_type_range_norm": round(rp.relationship_type_range_norm, 3) if rp else 0,
        "network_reach": rp.network_reach if rp else 0,
        "network_reach_norm": round(rp.network_reach_norm, 3) if rp else 0,
        "network_reach_description": rp.network_reach_description if rp else "",
        "inter_case_connectivity": rp.inter_case_connectivity if rp else 0,
        "inter_case_connectivity_norm": round(rp.inter_case_connectivity_norm, 3) if rp else 0,
        "inter_case_description": rp.inter_case_description if rp else "",
        "composite_score": round(rp.composite_score, 3) if rp else 0,
    }
    d["direct_partners"] = rp.direct_partners if rp else []
    d["latent_clusters"] = rp.latent_clusters if rp else []

    return d


# ══════════════════════════════════════════════════════════════════════
# STATIC FILE SERVING
# ══════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ══════════════════════════════════════════════════════════════════════
# REFERENCE DATA / CONSTANTS
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/constants")
def api_constants():
    """All reference constants for the frontend."""
    return jsonify({
        "outcome_groups": dict(OUTCOME_GROUP_NAMES),
        "outcome_categories": {
            og: {code: name for code, name in cats.items()}
            for og, cats in OUTCOME_CATEGORIES.items()
        },
        "condition_types": dict(CONDITION_TYPE_NAMES),
        "condition_categories": {
            ct: {code: name for code, name in cats.items()}
            for ct, cats in CONDITION_CATEGORIES.items()
        },
        "internal_conditions": list(INTERNAL_CONDITION_TYPES),
        "external_conditions": list(EXTERNAL_CONDITION_TYPES),
        "all_conditions": list(ALL_CONDITION_TYPES),
        "sovereignty_dimensions": SOVEREIGNTY_DIMENSIONS,
        "org_types": dict(ORG_TYPE_NAMES),
        "recursive_patterns": {str(k): v for k, v in RECURSIVE_PATTERNS.items()},
        "partner_types": {str(k): v for k, v in PARTNER_TYPES.items()},
        "relationship_types": dict(RELATIONSHIP_TYPES),
        "mechanism_types": MECHANISM_TYPES,
        "condition_mechanism_map": dict(CONDITION_MECHANISM_MAP),
        "condition_sovereignty_terrain": {
            ct: dims for ct, dims in CONDITION_SOVEREIGNTY_TERRAIN.items()
        },
        "outcome_sovereignty_map": {
            code: dims for code, dims in OUTCOME_SOVEREIGNTY_MAP.items()
        },
        "outcome_group_sovereignty": {
            og: dims for og, dims in __import__('config').OUTCOME_GROUP_SOVEREIGNTY.items()
        },
        "necessary_conditions": dict(NECESSARY_CONDITIONS),
        "near_necessary_conditions": dict(NEAR_NECESSARY_CONDITIONS),
        "outcome_cooccurrence": {
            f"{k[0]}-{k[1]}": v for k, v in OUTCOME_COOCCURRENCE.items()
        },
        "direct_partnerships": [[a, b] for a, b in DIRECT_PARTNERSHIPS],
        "latent_clusters": dict(LATENT_CLUSTERS),
    })


# ══════════════════════════════════════════════════════════════════════
# SCORE → CATEGORY MAP
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/score-category-map")
def api_score_category_map():
    """
    For each condition type, the empirically observed categories at each
    discrete score level.  Returns {ct: {score: [[code, freq], ...]}}.
    Also includes score interpretation labels.
    """
    return jsonify({
        "map": SCORE_CATEGORY_MAP,
        "interpretations": SCORE_INTERPRETATION,
        "score_levels": [-0.25, 0, 0.25, 0.5, 0.75, 1.0],
    })


# ══════════════════════════════════════════════════════════════════════
# COMPREHENSIVE COUNTERFACTUAL ANALYSIS
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/counterfactual", methods=["POST"])
def api_counterfactual():
    """
    Comprehensive counterfactual analysis for an existing case.

    POST body: {
      "case": "Te Hiku Media",
      "modified_conditions": {
        "PU": 0.75,       # changed score
        "GV": 1.0,        # added new condition
        "TT": null         # removed (N/A)
      }
    }

    Returns condition changes, new production rules / mechanisms / logics,
    predicted outcomes with categories, sovereignty terrain + capacity,
    and D-A-S patterns.
    """
    data = request.get_json(force=True)
    case_name = data.get("case")
    modified = data.get("modified_conditions", {})

    r = resolve_name(case_name)
    if not r:
        return jsonify({"error": f"Case not found: {case_name}"}), 404

    base_agent = agents[r]

    # ── 1. Build original and new condition profiles ──────────────
    original_scores = dict(base_agent.all_condition_scores)
    original_cats = dict(base_agent.condition_categories)
    new_scores = dict(original_scores)  # start from base

    for ct, val in modified.items():
        if val is None:
            # N/A: remove condition entirely
            new_scores.pop(ct, None)
        else:
            new_scores[ct] = float(val)

    # ── 2. Condition change details ───────────────────────────────
    condition_changes = []
    all_cts = set(list(original_scores.keys()) + list(modified.keys()))
    for ct in sorted(all_cts):
        old_score = original_scores.get(ct)
        new_val = modified.get(ct, "unchanged")
        if new_val == "unchanged":
            continue
        new_score = None if new_val is None else float(new_val)

        change_entry = {
            "condition_type": ct,
            "condition_name": CONDITION_TYPE_NAMES.get(ct, ct),
            "old_score": old_score,
            "old_interpretation": SCORE_INTERPRETATION.get(
                str(round(old_score, 2)), "N/A") if old_score is not None else "N/A",
            "new_score": new_score,
            "new_interpretation": SCORE_INTERPRETATION.get(
                str(round(new_score, 2)), "") if new_score is not None else "N/A",
            "old_categories": [],
            "new_categories": [],
            "mechanism": CONDITION_MECHANISM_MAP.get(ct, ""),
            "sovereignty_terrain": CONDITION_SOVEREIGNTY_TERRAIN.get(ct, []),
        }

        # Old categories
        if old_score is not None:
            for code in original_cats.get(ct, []):
                change_entry["old_categories"].append({
                    "code": code,
                    "name": CONDITION_CATEGORIES.get(ct, {}).get(code, code),
                })

        # New categories: from empirical score→category map
        if new_score is not None and ct in SCORE_CATEGORY_MAP:
            score_key = str(round(new_score, 2))
            if score_key in SCORE_CATEGORY_MAP[ct]:
                for code, freq in SCORE_CATEGORY_MAP[ct][score_key]:
                    change_entry["new_categories"].append({
                        "code": code,
                        "name": CONDITION_CATEGORIES.get(ct, {}).get(code, code),
                        "frequency": freq,
                    })
        condition_changes.append(change_entry)

    # ── 3. Find similar cases for prediction ──────────────────────
    active_new = {ct: s for ct, s in new_scores.items() if s is not None}
    similarities = []
    for cname, agent in agents.items():
        overlap = 0
        matched = 0
        for ct, score in active_new.items():
            agent_score = agent.all_condition_scores.get(ct)
            if agent_score is not None:
                overlap += 1 - abs(agent_score - score)
                matched += 1
        # Penalize cases that have conditions the new profile doesn't
        extra = len([ct for ct in agent.all_condition_scores
                     if ct not in active_new and
                     agent.all_condition_scores[ct] is not None])
        similarity = overlap / max(len(active_new), 1) - extra * 0.05
        similarities.append((cname, max(similarity, 0), agent))

    similarities.sort(key=lambda x: x[1], reverse=True)
    top5 = similarities[:5]
    total_sim = sum(s for _, s, _ in top5) or 1

    # ── 4. Predict outcomes with categories ───────────────────────
    predicted_outcomes = {}
    for og in OUTCOME_GROUPS:
        weighted_sum = 0
        weight_total = 0
        cat_votes = defaultdict(float)
        for cname, sim, agent in top5:
            sc = agent.outcome_scores.get(og)
            if sc is not None:
                weighted_sum += sc * sim
                weight_total += sim
                for cat in agent.outcome_categories.get(og, []):
                    cat_votes[cat] += sim
        if weight_total > 0:
            pred_score = round(weighted_sum / weight_total, 3)
            # Pick categories from top-weighted
            sorted_cats = sorted(cat_votes.items(), key=lambda x: -x[1])
            # Take categories that appear in majority of similar cases
            threshold = weight_total * 0.3
            pred_cats = [
                {"code": code, "name": OUTCOME_CATEGORIES.get(og, {}).get(code, code),
                 "sovereignty_contributions": OUTCOME_SOVEREIGNTY_MAP.get(code, []),
                 "weight": round(w, 3)}
                for code, w in sorted_cats if w >= threshold
            ]
            # Baseline
            base_score = base_agent.outcome_scores.get(og)
            base_cats = [
                {"code": code,
                 "name": OUTCOME_CATEGORIES.get(og, {}).get(code, code)}
                for code in base_agent.outcome_categories.get(og, [])
            ] if base_score is not None else []

            predicted_outcomes[og] = {
                "name": OUTCOME_GROUP_NAMES.get(og, og),
                "predicted_score": pred_score,
                "baseline_score": round(base_score, 3) if base_score else None,
                "change": round(pred_score - base_score, 4) if base_score else None,
                "predicted_categories": pred_cats,
                "baseline_categories": base_cats,
            }

    # ── 5. Collect production rules from similar cases ────────────
    rule_votes = defaultdict(lambda: {"count": 0, "weight": 0, "examples": []})
    mechanism_weights = defaultdict(float)
    for cname, sim, agent in top5:
        for rule in agent.production_rule:
            # Only include rules where the condition is active in new profile
            if rule.condition_type in active_new:
                key = f"{rule.condition_type}→{rule.outcome_group}"
                rule_votes[key]["count"] += 1
                rule_votes[key]["weight"] += sim
                if len(rule_votes[key]["examples"]) < 2:
                    rule_votes[key]["examples"].append({
                        "case": cname,
                        "condition_name": rule.condition_name,
                        "condition_codes": rule.condition_codes,
                        "mechanism": rule.mechanism_type,
                        "outcome_name": rule.outcome_name,
                        "outcome_codes": rule.outcome_codes,
                        "description": rule.description,
                    })
                mechanism_weights[rule.mechanism_type] += sim

    predicted_rules = sorted(
        [{"pathway": k, **v} for k, v in rule_votes.items()],
        key=lambda x: -x["weight"]
    )

    # Logic type: generative (from production rules) vs configurational
    generative_pathways = set()
    for rule in base_agent.production_rule:
        generative_pathways.add(f"{rule.condition_type}→{rule.outcome_group}")

    for pr in predicted_rules:
        pr["logic"] = "generative" if pr["pathway"] in generative_pathways \
            else "configurational"

    # ── 6. Sovereignty: terrain from conditions, capacity from outcomes ─
    new_terrain = {dim: 0.0 for dim in SOVEREIGNTY_DIMENSIONS}
    n_terrain_conds = 0
    for ct, score in active_new.items():
        for dim in CONDITION_SOVEREIGNTY_TERRAIN.get(ct, []):
            new_terrain[dim] += score
            n_terrain_conds += 1
    # Normalize terrain
    dim_counts = defaultdict(int)
    for ct in active_new:
        for dim in CONDITION_SOVEREIGNTY_TERRAIN.get(ct, []):
            dim_counts[dim] += 1
    for dim in SOVEREIGNTY_DIMENSIONS:
        if dim_counts[dim] > 0:
            new_terrain[dim] = round(new_terrain[dim] / dim_counts[dim], 3)

    new_capacity = {dim: 0.0 for dim in SOVEREIGNTY_DIMENSIONS}
    dim_out_counts = defaultdict(int)
    for og, odata in predicted_outcomes.items():
        score = odata["predicted_score"]
        for cat_info in odata["predicted_categories"]:
            for dim in cat_info["sovereignty_contributions"]:
                new_capacity[dim] += score
                dim_out_counts[dim] += 1
    for dim in SOVEREIGNTY_DIMENSIONS:
        if dim_out_counts[dim] > 0:
            new_capacity[dim] = round(new_capacity[dim] / dim_out_counts[dim], 3)

    sovereignty = {}
    for dim in SOVEREIGNTY_DIMENSIONS:
        old_terrain = safe(base_agent.sovereignty_terrain.get(dim))
        old_capacity = safe(base_agent.sovereignty_profile.get(dim))
        sovereignty[dim] = {
            "old_terrain": round(old_terrain, 3),
            "new_terrain": new_terrain[dim],
            "terrain_change": round(new_terrain[dim] - old_terrain, 4),
            "old_capacity": round(old_capacity, 3),
            "new_capacity": new_capacity[dim],
            "capacity_change": round(new_capacity[dim] - old_capacity, 4),
        }

    # ── 7. D-A-S patterns from similar cases' production rules ────
    pattern_votes = defaultdict(float)
    for cname, sim, agent in top5:
        for pid in agent.recursive_patterns:
            pattern_votes[pid] += sim  # binary: weight by similarity only

    das_patterns = sorted([
        {"id": pid, "name": RECURSIVE_PATTERNS.get(pid, f"#{pid}"),
         "weight": round(w, 2)}
        for pid, w in pattern_votes.items()
    ], key=lambda x: -x["weight"])

    return jsonify({
        "case": r,
        "condition_changes": condition_changes,
        "predicted_rules": predicted_rules,
        "mechanisms_engaged": sorted(
            [{"type": m, "weight": round(w, 2)}
             for m, w in mechanism_weights.items()],
            key=lambda x: -x["weight"]),
        "predicted_outcomes": predicted_outcomes,
        "sovereignty": sovereignty,
        "das_patterns": das_patterns,
        "similar_cases": [
            {"case": c, "similarity": round(s, 3)} for c, s, _ in top5
        ],
    })


# ══════════════════════════════════════════════════════════════════════
# HYPOTHETICAL CASE CONSTRUCTOR (from scratch)
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/construct-case", methods=["POST"])
def api_construct_case():
    """
    Build a hypothetical case from scratch (no base case required).

    POST body: {
      "conditions": {"GV": 1.0, "TP": 0.75, "PT": 0.5, ...},
      "name": "My Hypothetical",
      "org_type": "DC"
    }

    Uses 5 most similar empirical cases to predict outcomes, mechanisms,
    production rules, sovereignty, and D-A-S patterns.
    """
    data = request.get_json(force=True)
    condition_profile = data.get("conditions", {})
    case_name = data.get("name", "Hypothetical Case")
    org_type = data.get("org_type", "")

    if not condition_profile:
        return jsonify({"error": "No conditions specified"}), 400

    # Find 5 most similar cases
    similarities = []
    for cname, agent in agents.items():
        overlap = 0
        matched = 0
        for ct, score in condition_profile.items():
            agent_score = agent.all_condition_scores.get(ct)
            if agent_score is not None:
                overlap += 1 - abs(agent_score - score)
                matched += 1
        # Bonus for matching org type
        org_bonus = 0.1 if org_type and agent.org_type == org_type else 0
        # Penalize for extra conditions the hypothetical doesn't have
        extra = len([ct for ct in agent.all_condition_scores
                     if ct not in condition_profile and
                     agent.all_condition_scores[ct] is not None])
        sim = (overlap / max(len(condition_profile), 1)) + org_bonus - extra * 0.03
        similarities.append((cname, max(sim, 0), agent))

    similarities.sort(key=lambda x: x[1], reverse=True)
    top5 = similarities[:5]
    total_sim = sum(s for _, s, _ in top5) or 1

    # Condition details with categories
    condition_details = []
    for ct, score in sorted(condition_profile.items()):
        cats = []
        if ct in SCORE_CATEGORY_MAP:
            key = str(round(score, 2))
            for code, freq in SCORE_CATEGORY_MAP.get(ct, {}).get(key, []):
                cats.append({
                    "code": code,
                    "name": CONDITION_CATEGORIES.get(ct, {}).get(code, code),
                    "frequency": freq,
                })
        condition_details.append({
            "condition_type": ct,
            "condition_name": CONDITION_TYPE_NAMES.get(ct, ct),
            "score": score,
            "interpretation": SCORE_INTERPRETATION.get(str(round(score, 2)), ""),
            "mechanism": CONDITION_MECHANISM_MAP.get(ct, ""),
            "sovereignty_terrain": CONDITION_SOVEREIGNTY_TERRAIN.get(ct, []),
            "categories": cats,
        })

    # Predict outcomes
    predicted_outcomes = {}
    for og in OUTCOME_GROUPS:
        weighted_sum = 0
        weight_total = 0
        cat_votes = defaultdict(float)
        for cname, sim, agent in top5:
            sc = agent.outcome_scores.get(og)
            if sc is not None:
                weighted_sum += sc * sim
                weight_total += sim
                for cat in agent.outcome_categories.get(og, []):
                    cat_votes[cat] += sim
        if weight_total > 0:
            pred_score = round(weighted_sum / weight_total, 3)
            threshold = weight_total * 0.3
            pred_cats = [
                {"code": code,
                 "name": OUTCOME_CATEGORIES.get(og, {}).get(code, code),
                 "sovereignty_contributions": OUTCOME_SOVEREIGNTY_MAP.get(code, []),
                 "weight": round(w, 3)}
                for code, w in sorted(cat_votes.items(), key=lambda x: -x[1])
                if w >= threshold
            ]
            predicted_outcomes[og] = {
                "name": OUTCOME_GROUP_NAMES.get(og, og),
                "predicted_score": pred_score,
                "predicted_categories": pred_cats,
            }

    # Production rules from similar cases
    rule_votes = defaultdict(lambda: {"count": 0, "weight": 0, "examples": []})
    mechanism_weights = defaultdict(float)
    for cname, sim, agent in top5:
        for rule in agent.production_rule:
            if rule.condition_type in condition_profile:
                key = f"{rule.condition_type}→{rule.outcome_group}"
                rule_votes[key]["count"] += 1
                rule_votes[key]["weight"] += sim
                if len(rule_votes[key]["examples"]) < 2:
                    rule_votes[key]["examples"].append({
                        "case": cname,
                        "condition_name": rule.condition_name,
                        "mechanism": rule.mechanism_type,
                        "outcome_name": rule.outcome_name,
                        "description": rule.description,
                    })
                mechanism_weights[rule.mechanism_type] += sim

    predicted_rules = sorted(
        [{"pathway": k, **v} for k, v in rule_votes.items()],
        key=lambda x: -x["weight"]
    )

    # Sovereignty
    new_terrain = {dim: 0.0 for dim in SOVEREIGNTY_DIMENSIONS}
    dim_counts = defaultdict(int)
    for ct, score in condition_profile.items():
        for dim in CONDITION_SOVEREIGNTY_TERRAIN.get(ct, []):
            new_terrain[dim] += score
            dim_counts[dim] += 1
    for dim in SOVEREIGNTY_DIMENSIONS:
        if dim_counts[dim] > 0:
            new_terrain[dim] = round(new_terrain[dim] / dim_counts[dim], 3)

    new_capacity = {dim: 0.0 for dim in SOVEREIGNTY_DIMENSIONS}
    dim_out_counts = defaultdict(int)
    for og, odata in predicted_outcomes.items():
        score = odata["predicted_score"]
        for cat_info in odata["predicted_categories"]:
            for dim in cat_info["sovereignty_contributions"]:
                new_capacity[dim] += score
                dim_out_counts[dim] += 1
    for dim in SOVEREIGNTY_DIMENSIONS:
        if dim_out_counts[dim] > 0:
            new_capacity[dim] = round(new_capacity[dim] / dim_out_counts[dim], 3)

    sovereignty = {
        dim: {"terrain": new_terrain[dim], "capacity": new_capacity[dim]}
        for dim in SOVEREIGNTY_DIMENSIONS
    }

    # D-A-S patterns
    pattern_votes = defaultdict(float)
    for cname, sim, agent in top5:
        for pid in agent.recursive_patterns:
            pattern_votes[pid] += sim
    das_patterns = sorted([
        {"id": pid, "name": RECURSIVE_PATTERNS.get(pid, f"#{pid}"),
         "weight": round(w, 2)}
        for pid, w in pattern_votes.items()
    ], key=lambda x: -x["weight"])

    return jsonify({
        "name": case_name,
        "org_type": org_type,
        "condition_details": condition_details,
        "predicted_rules": predicted_rules,
        "mechanisms_engaged": sorted(
            [{"type": m, "weight": round(w, 2)}
             for m, w in mechanism_weights.items()],
            key=lambda x: -x["weight"]),
        "predicted_outcomes": predicted_outcomes,
        "sovereignty": sovereignty,
        "das_patterns": das_patterns,
        "similar_cases": [
            {"case": c, "similarity": round(s, 3)} for c, s, _ in top5
        ],
    })


# ══════════════════════════════════════════════════════════════════════
# D-A-S PATTERN DETAIL
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/das-patterns-detail")
def api_das_patterns_detail():
    """
    Full detail on all 17 recursive D-A-S patterns (binary): which cases
    participate in each, org type distribution, example production rules,
    and pattern groupings by family.
    """
    # Helper: which patterns does a production rule row trigger?
    def row_patterns(row):
        mechanism = row.mechanism_type.split("+")[0].strip()
        key = (row.condition_type, row.outcome_group)
        refined = RECURSIVE_PATTERN_REFINEMENT.get(key)
        if refined:
            return refined
        return MECHANISM_RECURSIVE_MAP.get(mechanism, [])

    patterns = {}
    for pid, pname in RECURSIVE_PATTERNS.items():
        cases_with = []
        org_dist = defaultdict(int)
        example_rules = []

        for cname, agent in agents.items():
            if pid in agent.recursive_patterns:
                cases_with.append({
                    "case": cname,
                    "org_type": agent.org_type,
                })
                org_dist[agent.org_type] += 1

                # Collect example rules that trigger this pattern
                if len(example_rules) < 3:
                    for row in agent.production_rule:
                        rp = row_patterns(row)
                        if pid in rp and len(example_rules) < 3:
                            example_rules.append({
                                "case": cname,
                                "condition": f"{row.condition_type} ({', '.join(row.condition_codes)})",
                                "mechanism": row.mechanism_type,
                                "outcome": f"{row.outcome_group} ({', '.join(row.outcome_codes)})",
                                "description": row.description[:150] if row.description else "",
                            })

        cases_with.sort(key=lambda x: x["case"])
        patterns[pid] = {
            "id": pid,
            "name": pname,
            "case_count": len(cases_with),
            "cases": cases_with,
            "org_type_distribution": dict(org_dist),
            "example_rules": example_rules,
        }

    # Group patterns into families
    return jsonify({
        "patterns": patterns,
        "families": {
            "sovereignty_dimensions": {"label": "Sovereignty Dimensions (#1–6)", "pattern_ids": [1,2,3,4,5,6]},
            "claimant_types": {"label": "Sovereignty Claimants (#7–11)", "pattern_ids": [7,8,9,10,11]},
            "debates": {"label": "Sovereignty Debates (#12–17)", "pattern_ids": [12,13,14,15,16,17]},
        },
        "total_patterns": len(patterns),
        "total_cases": len(agents),
    })


# ══════════════════════════════════════════════════════════════════════
# PRIMARY MODEL: CASE ACCESS
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/cases")
def api_cases():
    """List all 43 cases (summary view)."""
    return jsonify([agent_to_dict(a, summary=True) for a in agents.values()])

@app.route("/api/case/<path:name>")
def api_case(name):
    """Full profile for a single case."""
    r = resolve_name(name)
    if not r:
        return jsonify({"error": f"Case not found: {name}"}), 404
    return jsonify(agent_to_dict(agents[r]))

@app.route("/api/agents")
def api_agents():
    """All 43 agents with relational profiles for the Second Model frontend."""
    result = []
    for name, agent in agents.items():
        rp = agent.relational_profile
        entry = {
            "name": agent.name,
            "org_type": agent.org_type,
            "relational_profile": {
                "composite": round(rp.composite_score, 3) if rp and rp.composite_score else 0,
                "D1": rp.partner_diversity if rp else 0,
                "D1_norm": round(rp.partner_diversity_norm, 3) if rp else 0,
                "D2": rp.relationship_type_range if rp else 0,
                "D2_norm": round(rp.relationship_type_range_norm, 3) if rp else 0,
                "D3": rp.network_reach if rp else 0,
                "D3_norm": round(rp.network_reach_norm, 3) if rp else 0,
                "D4": rp.inter_case_connectivity if rp else 0,
                "D4_norm": round(rp.inter_case_connectivity_norm, 3) if rp else 0,
                "partner_types_engaged": rp.partner_types_engaged if rp else [],
                "relationship_types": rp.relationship_types if rp else [],
                "network_reach": rp.network_reach if rp else 0,
                "inter_case_connectivity": rp.inter_case_connectivity if rp else 0,
                "network_reach_description": rp.network_reach_description if rp else "",
                "direct_partners": rp.direct_partners if rp else [],
                "latent_clusters": rp.latent_clusters if rp else [],
            } if rp else None,
            "outcome_scores": {
                og: round(safe(agent.outcome_scores.get(og)), 3)
                for og in OUTCOME_GROUPS
                if agent.outcome_scores.get(og) is not None
            },
            "outcome_categories": {
                og: agent.outcome_categories.get(og, [])
                for og in OUTCOME_GROUPS
            },
            "sovereignty_profile": {
                dim: round(safe(agent.sovereignty_profile.get(dim)), 3)
                for dim in SOVEREIGNTY_DIMENSIONS
            },
            "sovereignty_terrain": {
                dim: round(safe(agent.sovereignty_terrain.get(dim)), 3)
                for dim in SOVEREIGNTY_DIMENSIONS
            },
        }
        result.append(entry)
    return jsonify(result)


# ══════════════════════════════════════════════════════════════════════
# PRIMARY MODEL: ECOSYSTEM STATISTICS
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/ecosystem")
def api_ecosystem():
    """Ecosystem summary statistics."""
    s = model.ecosystem_summary()
    s["total_production_rules"] = sum(
        len(a.production_rule) for a in agents.values())
    s["pattern_distribution"] = model.recursive_pattern_distribution()
    s["mechanism_distribution"] = model.mechanism_distribution()
    return jsonify(s)

@app.route("/api/generative-logic")
def api_generative_logic():
    """Production rule level condition→outcome frequencies (case-level generative logic)."""
    return jsonify(model.generative_logic_summary())

@app.route("/api/cross-impact-logic")
def api_cross_impact_logic():
    """Cross-impact matrix level condition→outcome frequencies (ecosystem-level)."""
    return jsonify(model.cross_impact_generative_logic())

@app.route("/api/condition-outcome-frequencies")
def api_condition_outcome_freq():
    """Condition type → outcome group co-occurrence matrix. Optional org_type filter."""
    org_type = request.args.get("org_type")
    return jsonify(model.condition_outcome_frequencies(org_type=org_type))

@app.route("/api/mechanism-distribution")
def api_mechanism_distribution():
    """Distribution of mechanism types across all production rules."""
    return jsonify(model.mechanism_distribution())


# ══════════════════════════════════════════════════════════════════════
# PRIMARY MODEL: ORG TYPE COMPARISON
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/org-type/<org_type>")
def api_org_type(org_type):
    """Detailed profile for a single org type with member cases."""
    oa = model.get_agents_by_type(org_type)
    if not oa:
        return jsonify({"error": f"No agents of type {org_type}"}), 404
    n = len(oa)
    avg_out = {}
    for og in OUTCOME_GROUPS:
        scores = [a.outcome_scores.get(og) for a in oa
                  if a.outcome_scores.get(og) is not None]
        avg_out[og] = round(sum(scores) / len(scores), 3) if scores else 0
    avg_sov = {d: round(sum(safe(a.sovereignty_profile.get(d))
               for a in oa) / n, 3) for d in SOVEREIGNTY_DIMENSIONS}
    return jsonify({
        "org_type": org_type,
        "org_type_name": ORG_TYPE_NAMES.get(org_type, org_type),
        "count": n,
        "cases": [agent_to_dict(a, summary=True) for a in oa],
        "avg_outcomes": avg_out,
        "avg_sovereignty": avg_sov,
    })

@app.route("/api/compare-org-types")
def api_compare_org_types():
    """Compare outcome and sovereignty profiles across all 4 org types."""
    return jsonify(model.compare_by_org_type())

@app.route("/api/compare-feature/<feature>")
def api_compare_feature(feature):
    """Compare outcome profiles grouped by any agent feature."""
    return jsonify(model.compare_by_feature(feature))

@app.route("/api/sovereignty-by-type")
def api_sovereignty_by_type():
    """Average sovereignty profiles per organizational type."""
    return jsonify(model.sovereignty_profiles_by_type())


# ══════════════════════════════════════════════════════════════════════
# ANALYTICAL ENGINE: SENSITIVITY ANALYSIS
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/sensitivity/<path:name>")
def api_sensitivity(name):
    """Single-case condition sensitivity (vary one condition, observe outcomes)."""
    r = resolve_name(name)
    if not r:
        return jsonify({"error": "Case not found"}), 404
    ct = request.args.get("condition", "PU")
    delta = float(request.args.get("delta", "0.25"))
    return jsonify(engine.condition_sensitivity(r, ct, delta))

@app.route("/api/sovereignty-sensitivity/<path:name>")
def api_sovereignty_sensitivity(name):
    """Condition sensitivity extended to sovereignty dimensions."""
    r = resolve_name(name)
    if not r:
        return jsonify({"error": "Case not found"}), 404
    ct = request.args.get("condition", "PU")
    delta = float(request.args.get("delta", "0.25"))
    return jsonify(engine.sovereignty_sensitivity(r, ct, delta))

@app.route("/api/ecosystem-sensitivity")
def api_ecosystem_sensitivity():
    """Vary a condition across ALL agents that have it active."""
    ct = request.args.get("condition", "GV")
    delta = float(request.args.get("delta", "0.25"))
    return jsonify(engine.ecosystem_sensitivity(ct, delta))

@app.route("/api/full-sensitivity-matrix")
def api_full_sensitivity_matrix():
    """Complete condition-type × outcome-group sensitivity matrix."""
    delta = float(request.args.get("delta", "0.25"))
    return jsonify(engine.full_sensitivity_matrix(delta))

@app.route("/api/condition-importance/<outcome_group>")
def api_condition_importance(outcome_group):
    """Rank condition types by importance for a specific outcome group."""
    delta = float(request.args.get("delta", "0.25"))
    return jsonify(engine.condition_importance_ranking(outcome_group, delta))


# ══════════════════════════════════════════════════════════════════════
# ANALYTICAL ENGINE: COUNTERFACTUAL / COUNTER-CASE
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/counter-case/<path:name>")
def api_counter_case(name):
    """Set a condition to a specific value and observe effects."""
    r = resolve_name(name)
    if not r:
        return jsonify({"error": "Case not found"}), 404
    ct = request.args.get("condition", "GV")
    val = float(request.args.get("value", "0.0"))
    return jsonify(engine.counter_case(r, ct, val))

@app.route("/api/remove-condition/<path:name>")
def api_remove_condition(name):
    """Remove a condition entirely (set to 0)."""
    r = resolve_name(name)
    if not r:
        return jsonify({"error": "Case not found"}), 404
    ct = request.args.get("condition", "GV")
    return jsonify(engine.remove_condition(r, ct))

@app.route("/api/maximize-condition/<path:name>")
def api_maximize_condition(name):
    """Set a condition to maximum (1.0)."""
    r = resolve_name(name)
    if not r:
        return jsonify({"error": "Case not found"}), 404
    ct = request.args.get("condition", "GV")
    return jsonify(engine.maximize_condition(r, ct))

@app.route("/api/swap-org-type/<path:name>")
def api_swap_org_type(name):
    """Replace a case's condition profile with another org type's average."""
    r = resolve_name(name)
    if not r:
        return jsonify({"error": "Case not found"}), 404
    target = request.args.get("target", "DC")
    return jsonify(engine.swap_org_type_profile(r, target))


# ══════════════════════════════════════════════════════════════════════
# ANALYTICAL ENGINE: HYPOTHETICAL CASE CONSTRUCTOR
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/hypothetical", methods=["POST"])
def api_hypothetical():
    """
    Create a hypothetical case with user-specified conditions.
    POST body: {"conditions": {"GV": 0.8, "TP": 0.6, ...},
                "name": "My Case", "org_type": "DC"}
    """
    data = request.get_json(force=True)
    conditions = data.get("conditions", {})
    name = data.get("name", "Hypothetical")
    org_type = data.get("org_type", "DSO")
    return jsonify(engine.hypothetical_case(conditions, name, org_type))


# ══════════════════════════════════════════════════════════════════════
# ANALYTICAL ENGINE: SOVEREIGNTY PATHWAY TRACING
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/trace-sovereignty/<path:name>")
def api_trace_sovereignty(name):
    """Trace condition → mechanism → outcome → sovereignty pathway for a case."""
    r = resolve_name(name)
    if not r:
        return jsonify({"error": "Case not found"}), 404
    return jsonify(engine.trace_sovereignty_pathway(r))

@app.route("/api/terrain/<path:name>")
def api_terrain(name):
    """Terrain-capacity gap analysis (single case or ecosystem)."""
    r = resolve_name(name)
    if not r:
        return jsonify({"error": "Case not found"}), 404
    return jsonify(engine.terrain_capacity_gap(r))

@app.route("/api/terrain-ecosystem")
def api_terrain_ecosystem():
    """Ecosystem-level terrain-capacity gap analysis."""
    return jsonify(engine.terrain_capacity_gap(None))


# ══════════════════════════════════════════════════════════════════════
# ANALYTICAL ENGINE: REVERSE ANALYSIS
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/reverse-outcome/<outcome_group>")
def api_reverse_outcome(outcome_group):
    """Starting from a desired outcome, find required conditions and cases."""
    min_score = float(request.args.get("min_score", "0.5"))
    return jsonify(engine.reverse_analysis_outcome(outcome_group, min_score))

@app.route("/api/reverse-sovereignty/<dimension>")
def api_reverse_sovereignty(dimension):
    """Starting from a sovereignty dimension, find contributing outcomes/conditions."""
    return jsonify(engine.reverse_analysis_sovereignty(dimension))


# ══════════════════════════════════════════════════════════════════════
# ANALYTICAL ENGINE: GENERATIVE LOGIC TESTING
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/test-generative-logic")
def api_test_generative_logic():
    """Test ten domain-level generative logic claims computationally."""
    delta = float(request.args.get("delta", "0.25"))
    return jsonify(engine.test_generative_logic(delta))

@app.route("/api/cross-impact-alignment")
def api_cross_impact_alignment():
    """Compare sensitivity rankings against cross-impact matrix benchmarks."""
    delta = float(request.args.get("delta", "0.25"))
    return jsonify(engine.cross_impact_alignment(delta))


# ══════════════════════════════════════════════════════════════════════
# ANALYTICAL ENGINE: FEATURE ANALYSIS
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/feature-analysis/<feature>")
def api_feature_analysis(feature):
    """
    Analyze correlation between agent feature and outcome profiles.
    Features: org_type, maturity, geographic_scope, condition_diversity,
              outcome_breadth, relational_density
    """
    return jsonify(engine.feature_outcome_correlation(feature))


# ══════════════════════════════════════════════════════════════════════
# ANALYTICAL ENGINE: CONDITION INTERACTION & CO-OCCURRENCE
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/interaction")
def api_interaction():
    """Analyze interaction effects between two condition types."""
    c1 = request.args.get("cond1", request.args.get("c1", "GV"))
    c2 = request.args.get("cond2", request.args.get("c2", "TP"))
    outcome = request.args.get("outcome", None)
    return jsonify(engine.condition_interaction_analysis(c1, c2, outcome))

@app.route("/api/cooccurrence")
def api_cooccurrence():
    """Outcome co-occurrence analysis across all 43 cases."""
    return jsonify(engine.outcome_cooccurrence_analysis())


# ══════════════════════════════════════════════════════════════════════
# ANALYTICAL ENGINE: RECURSIVE PATTERN ASSIGNMENT
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/recursive-patterns")
def api_recursive_patterns_ecosystem():
    """Ecosystem-level recursive pattern distribution."""
    return jsonify(engine.assign_recursive_patterns(None))

@app.route("/api/recursive-patterns/<path:name>")
def api_recursive_patterns_case(name):
    """Case-level recursive pattern assignment (row-by-row)."""
    r = resolve_name(name)
    if not r:
        return jsonify({"error": "Case not found"}), 404
    return jsonify(engine.assign_recursive_patterns(r))


# ══════════════════════════════════════════════════════════════════════
# ANALYTICAL ENGINE: VALIDATION
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/validation")
def api_validation():
    """Run validation tests. Add ?comprehensive=true for expanded tests."""
    comprehensive = request.args.get("comprehensive", "false").lower() == "true"
    return jsonify(engine.run_all_validation(comprehensive=comprehensive))


# ══════════════════════════════════════════════════════════════════════
# RELATIONAL ENGINE: DENSITY SENSITIVITY
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/relational/density-sensitivity/<dimension>")
def api_density_sensitivity(dimension):
    """
    Vary a single relational density dimension (D1-D4).
    Dimensions: D1 (partner_diversity), D2 (relationship_type_range),
                D3 (network_reach), D4 (inter_case_connectivity)
    """
    return jsonify(relational.density_dimension_sensitivity(dimension))

@app.route("/api/relational/full-density-sensitivity")
def api_full_density_sensitivity():
    """Run density sensitivity for all four dimensions."""
    return jsonify(relational.full_density_sensitivity())


# ══════════════════════════════════════════════════════════════════════
# RELATIONAL ENGINE: PARTNER TYPE EFFECTS
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/relational/partner-types")
def api_rel_partner_types():
    """Effect analysis for all 12 partner types."""
    return jsonify(relational.all_partner_type_effects())

@app.route("/api/relational/partner-type/<int:pt_id>")
def api_rel_partner_type_single(pt_id):
    """Effect analysis for a single partner type."""
    return jsonify(relational.partner_type_effect(pt_id))

@app.route("/api/relational/partner-type-combination", methods=["POST"])
def api_rel_partner_combo():
    """
    Test combinatorial partner type effects.
    POST body: {"partner_types": [1, 3, 10]}
    """
    data = request.get_json(force=True)
    pt_ids = data.get("partner_types", [])
    return jsonify(relational.partner_type_combination_effect(pt_ids))


# ══════════════════════════════════════════════════════════════════════
# RELATIONAL ENGINE: RELATIONSHIP TYPE EFFECTS
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/relational/relationship-types")
def api_rel_relationship_types():
    """Effect analysis for all relationship types (PT1-PT6)."""
    return jsonify(relational.all_relationship_type_effects())

@app.route("/api/relational/relationship-type/<rel_type>")
def api_rel_relationship_type_single(rel_type):
    """Effect analysis for a single relationship type."""
    return jsonify(relational.relationship_type_effect(rel_type))

@app.route("/api/relational/relationship-combination", methods=["POST"])
def api_rel_relationship_combo():
    """
    Test combinatorial relationship type effects.
    POST body: {"relationship_types": ["PT1", "PT3"]}
    """
    data = request.get_json(force=True)
    rt_list = data.get("relationship_types", [])
    return jsonify(relational.relationship_combination_effect(rt_list))


# ══════════════════════════════════════════════════════════════════════
# RELATIONAL ENGINE: CLUSTERS & AGENT-AGENT
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/relational/clusters/<path:cluster_name>")
def api_rel_cluster(cluster_name):
    """Analyze a named cluster as a functioning relational ecosystem."""
    return jsonify(relational.cluster_analysis(cluster_name))

@app.route("/api/relational/simulate-cluster/<path:cluster_name>")
def api_rel_simulate_cluster(cluster_name):
    """Simulate activating a latent cluster (formalizing indirect connections)."""
    return jsonify(relational.simulate_cluster_activation(cluster_name))

@app.route("/api/relational/agent-interactions")
def api_rel_agent_interactions():
    """Analyze the 7 directly partnered cases."""
    return jsonify(relational.agent_agent_analysis())

@app.route("/api/relational/moderation")
def api_rel_moderation():
    """Test relational density as moderator of condition-outcome relationships."""
    return jsonify(relational.density_as_moderator())


# ══════════════════════════════════════════════════════════════════════
# RELATIONAL ENGINE: NEW ENDPOINTS (Phase 4 rebuild)
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/relational/density-distribution")
def api_rel_density_distribution():
    """All cases with actual density scores, outcomes, sovereignty."""
    return jsonify(relational.density_distribution())

@app.route("/api/relational/sensitivity", methods=["POST"])
def api_rel_sensitivity():
    """
    Layered prediction engine: predict outcome/sovereignty effects.
    POST body: {
        "case": "Te Hiku Media",
        "partner_types": [1, 3, 5],
        "relationship_types": ["PT1", "PT3"],
        "d3": 2,
        "d4": 2
    }
    D1 and D2 are auto-computed from partner_types and relationship_types.
    """
    data = request.get_json()
    case_name = data.get("case", "")
    return jsonify(relational.relational_sensitivity(
        case_name=case_name,
        modified_partner_types=data.get("partner_types"),
        modified_relationship_types=data.get("relationship_types"),
        modified_d3=data.get("d3"),
        modified_d4=data.get("d4"),
    ))

@app.route("/api/relational/has-lacks")
def api_rel_has_lacks():
    """Cases with direct partnerships vs cases without."""
    return jsonify(relational.has_lacks_comparison())

@app.route("/api/relational/enriched-cluster/<path:cluster_name>")
def api_rel_enriched_cluster(cluster_name):
    """Enriched cluster analysis with named outcomes/dimensions, pct diffs."""
    return jsonify(relational.enriched_cluster_analysis(cluster_name))

@app.route("/api/relational/enriched-interactions")
def api_rel_enriched_interactions():
    """Agent interactions with qualitative shared outcomes/sovereignty."""
    return jsonify(relational.enriched_agent_interactions())

@app.route("/api/relational/enriched-matched-pairs")
def api_rel_enriched_matched_pairs():
    """Matched pairs with full condition details and pct diffs."""
    return jsonify(relational.enriched_matched_pairs())


# ══════════════════════════════════════════════════════════════════════
# RELATIONAL ENGINE: FULL REPORT
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/relational/full-report")
def api_rel_full_report():
    """Complete second model analysis (all operations)."""
    return jsonify(relational.full_report())


# ══════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=False)
