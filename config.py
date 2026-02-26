"""
Configuration: canonical names, code mappings, sovereignty mappings.

All reference data for the Digital Rights Projects ABM lives here.
Data files are in /mnt/project/.
"""

import os

# ── File Paths ────────────────────────────────────────────────────────
# Auto-detect: use /mnt/project in container, otherwise same dir as this script
if os.path.exists("/mnt/project"):
    DATA_DIR = "/mnt/project"
else:
    DATA_DIR = os.path.dirname(os.path.abspath(__file__))

FILES = {
    "phase_1a": os.path.join(DATA_DIR, "Phase_1A_Master_final.xlsx"),
    "phase_3a_quant": os.path.join(DATA_DIR, "Phase_3A_Quantitative_Matrix_VERIFIED.xlsx"),
    "phase_3b_qual": os.path.join(DATA_DIR, "Phase_3B_Qualitative_Matrix_FINAL.xlsx"),
    "condition_mapping": os.path.join(DATA_DIR, "Phase_3A_Condition_Mapping.xlsx"),
    "outcome_mapping": os.path.join(DATA_DIR, "Phase_3A_Outcome_Mapping.xlsx"),
    "phase_4b": os.path.join(DATA_DIR, "Phase_4B_Complete.xlsx"),
    "phase_4d": os.path.join(DATA_DIR, "Phase_4D_Outcome_Positioning.xlsx"),
    "relational_density": os.path.join(DATA_DIR, "Relational_Density.xlsx"),
    "partnerships": os.path.join(DATA_DIR, "9_Partnerships.docx"),
}


# ── Canonical Case Names ──────────────────────────────────────────────
# Phase_4B names are canonical. This maps every variant to canonical.
CASE_NAME_MAP = {
    # Phase_1A full names → canonical
    "Australian Research Data Commons": "ARDC",
    "CLEAR (Civic Laboratory for Environmental Action Research)": "CLEAR",
    "DAIR (Distributed AI Research Institute)": "DAIR",
    "Detroit Community Technology Project (CTC)": "Detroit CTC",
    "Digital Empowerment Foundation": "DEF",
    "First Nations Information Governance Centre (FNIGC)": "FNIGC",
    "Global Indigenous Data Alliance (GIDA)": "GIDA",
    "MAIAM NAYRI WINGARA": "MAIAM NAYRI WINGARA",
    "Open Mobility Foundation": "Open Mobility Foundation",
    "Research Data Alliance": "RDA",
    "Slum Dwellers International": "SDI",
    "Stop LAPD Spying Coalition": "Stop LAPD Spying Coalition",
    "Telecomunicaciones Indígenas Comunitarias (TIC A.C.)": "TIC A.C.",
    "The Drivers Cooperative": "The Drivers Cooperative",
    "Worker Algorithm Observatory (WAO)": "WAO",
    "Nea Guinea/Tzoumakers": "Nea Guinea/Tzoumakers",
    "Fairbnb.coop": "Fairbnb.coop",
    # Relational Density variants → canonical
    "CTC": "Detroit CTC",
    "Drivers Cooperative": "The Drivers Cooperative",
    "Fairbnb": "Fairbnb.coop",
    "Nea Guinea": "Nea Guinea/Tzoumakers",
    "OMF": "Open Mobility Foundation",
    "Stop LAPD Spying": "Stop LAPD Spying Coalition",
    "Maiam Nayri Wingara": "MAIAM NAYRI WINGARA",
    # Identity mappings (already canonical)
    "ARDC": "ARDC",
    "CLEAR": "CLEAR",
    "CoopCycle": "CoopCycle",
    "DAIR": "DAIR",
    "DECODE": "DECODE",
    "DEF": "DEF",
    "Detroit CTC": "Detroit CTC",
    "Enspiral": "Enspiral",
    "FNIGC": "FNIGC",
    "GIDA": "GIDA",
    "Groupmuse": "Groupmuse",
    "Guifi.net": "Guifi.net",
    "Les Mercedes": "Les Mercedes",
    "Linux Foundation": "Linux Foundation",
    "Loomio": "Loomio",
    "Masakhane": "Masakhane",
    "Matrix": "Matrix",
    "MiData": "MiData",
    "Monlam AI": "Monlam AI",
    "Namma Yatri": "Namma Yatri",
    "OpenAgriNet": "OpenAgriNet",
    "OpenSAFELY": "OpenSAFELY",
    "OpenStreetMap": "OpenStreetMap",
    "P2P Foundation": "P2P Foundation",
    "Participatory Brazil": "Participatory Brazil",
    "RDA": "RDA",
    "SDI": "SDI",
    "SOLshare": "SOLshare",
    "Sensorica": "Sensorica",
    "Solar Commons": "Solar Commons",
    "Som Energia": "Som Energia",
    "TIC A.C.": "TIC A.C.",
    "Te Hiku Media": "Te Hiku Media",
    "Te Mana Raraunga": "Te Mana Raraunga",
    "WAO": "WAO",
    "WikiHouse": "WikiHouse",
    "Zenzeleni": "Zenzeleni",
}

# All 43 canonical names
CANONICAL_CASES = sorted(set(CASE_NAME_MAP.values()))


# ── Organization Type Codes ───────────────────────────────────────────
ORG_TYPE_MAP = {
    "Data Sovereignty and Digital Rights": "DSO",
    "Digital Cooperative": "DC",
    "Participatory Governance": "PG",
    "Peer Production": "PP",
    # Short codes map to themselves
    "DSO": "DSO",
    "DC": "DC",
    "PG": "PG",
    "PP": "PP",
}

ORG_TYPE_NAMES = {
    "DSO": "Data Sovereignty Organization",
    "DC": "Digital Cooperative",
    "PG": "Participatory Governance Organization",
    "PP": "Peer Production System",
}


# ── Condition Type Codes ──────────────────────────────────────────────
# Maps Phase_1A condition type names to codes
CONDITION_TYPE_MAP = {
    "Technology Practices": "TP",
    "Resources": "RS",
    "Governance": "GV",
    "Technology, Tools, Data, Products and Customers": "TT",
    "Technology Tools": "TT",
    "Partners": "PT",
    "Purpose": "PU",
    "Org Info": "OI",
    "Organizational Information": "OI",
    "Politics": "PO",
    "Regulation": "RG",
    "Social Context": "SC",
    "Problem": "PR",
}

# Internal vs External condition types
INTERNAL_CONDITION_TYPES = ["TP", "RS", "GV", "TT", "PT", "PU", "OI"]
EXTERNAL_CONDITION_TYPES = ["PO", "RG", "SC", "PR"]
ALL_CONDITION_TYPES = INTERNAL_CONDITION_TYPES + EXTERNAL_CONDITION_TYPES

CONDITION_TYPE_NAMES = {
    "TP": "Technology Practices",
    "RS": "Resources",
    "GV": "Governance",
    "TT": "Technology Tools",
    "PT": "Partners",
    "PU": "Purpose",
    "OI": "Organizational Information",
    "PO": "Politics",
    "RG": "Regulation",
    "SC": "Social Context",
    "PR": "Problem",
}

# Column names in Phase_4B (for matching)
CONDITION_COL_NAMES = {
    "Technology Practices": "TP",
    "Resources": "RS",
    "Governance": "GV",
    "Technology Tools": "TT",
    "Partners": "PT",
    "Purpose": "PU",
    "Organizational Information": "OI",
    "Politics": "PO",
    "Regulation": "RG",
    "Social Context": "SC",
    "Problem": "PR",
}


# ── Condition Categories ──────────────────────────────────────────────
# Full 57 condition categories (56 documented + potential extras)
CONDITION_CATEGORIES = {
    "TP": {
        "TP1": "Democratic Data Authority",
        "TP2": "Open Development and Transparency",
        "TP3": "Multi-Scale Architecture Design",
        "TP4": "Community-Centered Design Processes",
        "TP5": "Culturally-Grounded Development",
        "TP6": "Commons Resource Stewardship",
    },
    "RS": {
        "RS1": "Community Capacity Development",
        "RS2": "Access and Skills Democratization",
        "RS3": "Economic Value Redistribution",
        "RS4": "Alternative Economic Experimentation",
        "RS5": "Sustainable Resourcing Models",
        "RS6": "Values-Aligned Resource Allocation",
    },
    "GV": {
        "GV1": "Decentralized Authority Distribution",
        "GV2": "Ownership-Based Democratic Control",
        "GV3": "Federated Multi-Scale Coordination",
        "GV4": "Democratic Scaling Strategies",
        "GV5": "Inclusive Expertise Integration",
        "GV6": "Democratization of External Processes",
    },
    "TT": {
        "TT1": "Community-Controlled Physical Infrastructure",
        "TT2": "Culturally-Grounded Technology Artifacts",
        "TT3": "Indigenous Data Sovereignty Infrastructure",
        "TT4": "Participatory Design Platforms",
        "TT5": "Digital Commons Resources",
        "TT6": "Algorithmic Transparency Infrastructure",
        "TT7": "Decentralized Technical Architecture",
    },
    "PT": {
        "PT1": "Reciprocal Knowledge Exchange",
        "PT2": "Multi-Network Strategic Positioning",
        "PT3": "Community Sovereignty Protection in Partnerships",
        "PT4": "Expertise-Community Knowledge Integration",
        "PT5": "Cross-Sector Collaboration Networks",
    },
    "PU": {
        "PU1": "Indigenous Epistemological Centering",
        "PU2": "Cultural Preservation and Linguistic Sovereignty",
        "PU3": "Value System Reconceptualization",
        "PU4": "Resistance-Construction Integration",
        "PU5": "Ecological and Social Transformation",
        "PU6": "Democratic Citizenship Obligation",
    },
    "OI": {
        "OI1": "Worker/Community Ownership Models",
        "OI2": "Decentralized Governance Architectures",
        "OI3": "Anti-Extractive Value Circulation",
        "OI4": "Commons-Based Production Models",
        "OI5": "Local-Global Scalar Positioning",
        "OI6": "Municipal/Public Digital Governance",
    },
    "PO": {
        "PO1": "Policy and Systemic Transformation Advocacy",
        "PO2": "Resistance-Opposition Integration",
        "PO3": "Strategic Institutional Navigation",
    },
    "RG": {
        "RG1": "Legal Innovation for Sovereignty Protection",
        "RG2": "Ethical Governance Framework Development",
        "RG3": "Strategic Regulatory Navigation",
        "RG4": "Self-Determined Sovereignty Assertion",
    },
    "SC": {
        "SC1": "Inclusive Participation Structures",
        "SC2": "Movement and Network Embeddedness",
        "SC3": "Climate Crisis and Ecological Response",
    },
    "PR": {
        "PR1": "Infrastructure and Access Deficits",
        "PR2": "Colonial and Western-Centric Knowledge Domination",
        "PR3": "Cultural Erasure and Heritage Threat",
        "PR4": "Algorithmic Opacity and Asymmetric Power",
    },
}

# Flat lookup: code → name
ALL_CONDITION_CODES = {}
for type_code, cats in CONDITION_CATEGORIES.items():
    ALL_CONDITION_CODES.update(cats)


# ── Outcome Groups and Categories ─────────────────────────────────────
OUTCOME_GROUPS = ["DP", "CV", "BL", "IM"]

OUTCOME_GROUP_NAMES = {
    "DP": "Democratic Practices",
    "CV": "Community Value",
    "BL": "Balance",
    "IM": "Impact",
}

# Column names in Phase_4D (for matching)
OUTCOME_COL_NAMES = {
    "Democratic Practices": "DP",
    "Community Value": "CV",
    "Balance": "BL",
    "Impact": "IM",
}

OUTCOME_CATEGORIES = {
    "DP": {
        "DP1": "Decentralized Organizational Governance",
        "DP2": "Community Data Sovereignty and Control",
        "DP3": "Community-Controlled Infrastructure",
        "DP4": "Inclusive Participation and Representation",
        "DP5": "Open Access and Transparent Systems",
        "DP6": "Indigenous and Cultural Governance Integration",
        "DP7": "Legal and Institutional Protection",
        "DP8": "Resistance and Accountability Mechanisms",
        "DP9": "Local Capacity and Self-Governance",
    },
    "CV": {
        "CV1": "Worker and Member Economic Benefits",
        "CV2": "Open Knowledge and Technology Commons",
        "CV3": "Community Infrastructure and Capacity Assets",
        "CV4": "Culturally-Specific Technology and Knowledge",
        "CV5": "Alternative Economic Models and Structures",
    },
    "BL": {
        "BL1": "Federated Multi-Scale Governance",
        "BL2": "Multi-Network Coordination and Solidarity",
        "BL3": "Bidirectional Knowledge and Resource Exchange",
        "BL4": "Community Sovereignty Protection in External Engagement",
        "BL5": "Global-Local Standards Navigation",
    },
    "IM": {
        "IM1": "Policy and Regulatory Change",
        "IM2": "Community Capacity Building",
        "IM3": "Cultural and Linguistic Sovereignty",
        "IM4": "Economic Value Transformation",
        "IM5": "Governance and Institutional Transformation",
        "IM6": "Climate and Ecological Transformation",
    },
}

ALL_OUTCOME_CODES = {}
for group_code, cats in OUTCOME_CATEGORIES.items():
    ALL_OUTCOME_CODES.update(cats)


# ── Sovereignty Dimensions ────────────────────────────────────────────
SOVEREIGNTY_DIMENSIONS = [
    "technical",          # Capacity to develop, configure, and control critical technologies
    "infrastructure",     # Ownership, governance, and maintenance of physical/logical backbones
    "territorial",        # Legal and jurisdictional layer, codifying conditions for data/service flows
    "economic",           # Ownership and control of digital means of production (includes data sovereignty)
    "ecological",         # Material dimension — resource consumption, hardware dependencies, twin extractivism
    "collective_rights",  # Individual and popular sovereignty — human rights adapted to digital age
    "epistemic",          # Multiple ways of knowing, decolonial orientation, community authority
]

# Merging rules from 10 → 7 dimensions:
#   "political" + "collective_rights" + "relational" → collective_rights
#   "economic" + "data" → economic
#   "legal" → territorial (legal/jurisdictional)
#   "social" → distributed across collective_rights and ecological
#   "technical", "infrastructure", "epistemic" remain unchanged

# Outcome category → sovereignty dimension mappings (Bridge D)
# Derived from Chapter 7 "Outcomes as Sovereignty Capacity"
# Each outcome category can contribute to multiple sovereignty dimensions.
OUTCOME_SOVEREIGNTY_MAP = {
    # Democratic Practices → collective_rights, technical, epistemic
    "DP1": ["collective_rights"],                        # Decentralized Organizational Governance
    "DP2": ["collective_rights", "economic"],             # Community Data Sovereignty and Control
    "DP3": ["technical", "infrastructure"],               # Community-Controlled Infrastructure
    "DP4": ["collective_rights", "epistemic"],             # Inclusive Participation and Representation
    "DP5": ["technical", "epistemic"],                     # Open Access and Transparent Systems
    "DP6": ["epistemic", "collective_rights"],             # Indigenous and Cultural Governance Integration
    "DP7": ["territorial", "collective_rights"],           # Legal and Institutional Protection
    "DP8": ["collective_rights"],                          # Resistance and Accountability Mechanisms
    "DP9": ["collective_rights"],                          # Local Capacity and Self-Governance
    # Community Value → economic, infrastructure, epistemic
    "CV1": ["economic"],                                   # Worker and Member Economic Benefits
    "CV2": ["economic", "epistemic"],                      # Open Knowledge and Technology Commons
    "CV3": ["infrastructure", "economic"],                 # Community Infrastructure and Capacity Assets
    "CV4": ["epistemic", "economic"],                      # Culturally-Specific Technology and Knowledge
    "CV5": ["economic"],                                   # Alternative Economic Models and Structures
    # Balance → collective_rights, territorial
    "BL1": ["collective_rights"],                          # Federated Multi-Scale Governance
    "BL2": ["collective_rights"],                          # Multi-Network Coordination and Solidarity
    "BL3": ["collective_rights", "epistemic"],             # Bidirectional Knowledge and Resource Exchange
    "BL4": ["collective_rights", "territorial"],           # Community Sovereignty Protection
    "BL5": ["collective_rights", "territorial"],           # Global-Local Standards Navigation
    # Impact → collective_rights, ecological
    "IM1": ["collective_rights", "territorial"],           # Policy and Regulatory Change
    "IM2": ["collective_rights", "epistemic"],             # Community Capacity Building
    "IM3": ["epistemic", "collective_rights"],             # Cultural and Linguistic Sovereignty
    "IM4": ["economic", "ecological"],                     # Economic Value Transformation
    "IM5": ["collective_rights", "territorial"],           # Governance and Institutional Transformation
    "IM6": ["ecological"],                                 # Climate and Ecological Transformation
}

# Outcome group → primary sovereignty dimensions (higher level)
OUTCOME_GROUP_SOVEREIGNTY = {
    "DP": ["collective_rights", "technical", "epistemic"],
    "CV": ["economic", "infrastructure", "epistemic"],
    "BL": ["collective_rights", "territorial"],
    "IM": ["collective_rights", "ecological"],
}


# ── Bridge B: Condition-to-Sovereignty Terrain ────────────────────────
# Maps condition types to the sovereignty dimensions they operate ON
# (the terrain conditions traverse), distinct from the sovereignty
# dimensions outcomes CONSTRUCT (Bridge D / OUTCOME_SOVEREIGNTY_MAP).
# From Chapter 7: "Structural relationship between conditions and
# sovereignty terrain."
CONDITION_SOVEREIGNTY_TERRAIN = {
    "TP": ["technical", "infrastructure"],          # Technology Practices
    "TT": ["technical", "infrastructure"],          # Technology Tools
    "GV": ["territorial", "collective_rights"],     # Governance
    "RS": ["economic"],                             # Resources
    "PT": ["collective_rights", "economic", "epistemic"],  # Partners (multi-dimensional)
    "PU": ["epistemic"],                            # Purpose
    "OI": ["economic", "collective_rights"],         # Organizational Information (context-dependent)
    "PO": ["collective_rights", "territorial"],     # Politics
    "RG": ["territorial"],                          # Regulation
    "SC": ["collective_rights", "ecological"],      # Social Context
    "PR": ["collective_rights", "ecological"],       # Problem (context-dependent)
}


# ── Mechanism Types ───────────────────────────────────────────────────
MECHANISM_TYPES = ["structural", "enabling", "connective", "protective", "legitimizing"]

# Condition type → dominant mechanism
CONDITION_MECHANISM_MAP = {
    "TP": "enabling",
    "RS": "enabling",
    "GV": "structural",
    "TT": "enabling",
    "PT": "connective",
    "PU": "legitimizing",
    "OI": "enabling",  # "Positioning" in Pattern Summary; closest standard type
    "PO": "legitimizing",
    "RG": "protective",
    "SC": "enabling",
    "PR": "enabling",  # "Mixed" in Pattern Summary
}


# ── 17 Recursive D-A-S Patterns ───────────────────────────────────────
# From Appendix 11, Part 1: Inventory of Recursive Logic Patterns.
# Corrected to match Appendix exactly: Social (not Epistemic/Cultural),
# Environmental (not Infrastructure), Policy Advocacy (not Civil Society).
# Assigned at agent level via mechanism-constrained mapping.
# Assignment is BINARY: a case either participates in a pattern or not.
RECURSIVE_PATTERNS = {
    # Dimensions (1-6)
    1: "Political Sovereignty",
    2: "Economic Sovereignty",
    3: "Technical Sovereignty",
    4: "Legal Sovereignty",
    5: "Social Sovereignty",
    6: "Environmental Sovereignty",
    # Sovereignty Claimants (7-11)
    7: "States as Claimants",
    8: "Corporations as Claimants",
    9: "Academia as Claimants",
    10: "Policy Advocacy as Claimants",
    11: "Community-based Claimants",
    # Sovereignty Debates (12-17)
    12: "State vs. Corporate Control",
    13: "Individual vs. Collective Rights",
    14: "Localization vs. Free Flow",
    15: "Determinism vs. Construction",
    16: "Reform vs. Transformation",
    17: "Open vs. Closed Systems",
}

# Mechanism type → reachable recursive patterns
# Each mechanism can only trigger patterns in its reachable set.
# From Appendix 11 Part 3 (Convergence), grounded in how each mechanism
# type engages sovereignty dynamics.
MECHANISM_RECURSIVE_MAP = {
    "structural": [1, 2, 7, 8, 12, 16],   # Political, Economic, States, Corporations, State vs. Corporate, Reform vs. Transform
    "enabling": [2, 3, 5, 6, 11, 15],      # Economic, Technical, Social, Environmental, Community-based, Determinism vs. Construction
    "connective": [10, 11, 13, 14],         # Policy Advocacy, Community-based, Individual vs. Collective, Localization vs. Free Flow
    "protective": [4, 7, 12, 17],           # Legal, States, State vs. Corporate, Open vs. Closed
    "legitimizing": [1, 5, 9, 10, 16],      # Political, Social, Academia, Policy Advocacy, Reform vs. Transform
}

# Condition type + outcome group → specific recursive patterns (from mechanism's reachable set)
# Each entry draws ONLY from its mechanism's reachable patterns.
RECURSIVE_PATTERN_REFINEMENT = {
    # ── structural (GV) ──────────────────────────────────────────────
    ("GV", "DP"): [1],            # Authority restructuring = Political
    ("GV", "CV"): [2, 8],         # Governance of value distribution, contesting corporate extraction
    ("GV", "BL"): [12, 16],       # Navigating state-corporate tension, reform vs. transformation
    ("GV", "IM"): [1, 16],        # Systemic governance impact
    # ── enabling: TP ─────────────────────────────────────────────────
    ("TP", "DP"): [3, 15],        # Alternative architectures asserting constructivism
    ("TP", "CV"): [2, 3],         # Technology enabling alternative value models
    ("TP", "BL"): [3, 15],        # Technical practice navigating design choices
    ("TP", "IM"): [3, 15],        # Technical capacity for systemic alternatives
    # ── enabling: TT ─────────────────────────────────────────────────
    ("TT", "DP"): [3, 5],         # Infrastructure democratization as counter-design
    ("TT", "CV"): [2, 3],         # Infrastructure enabling alternative economies
    ("TT", "IM"): [3, 6],         # Infrastructure design and environmental externalities
    # ── enabling: RS ─────────────────────────────────────────────────
    ("RS", "CV"): [2, 11],        # Resource redistribution as community wealth
    ("RS", "DP"): [11, 15],       # Community capacity for democratic assertion
    ("RS", "IM"): [2, 11],        # Economic transformation through community resources
    # ── enabling: OI ─────────────────────────────────────────────────
    ("OI", "DP"): [5, 11],        # Organizational positioning for inclusion
    ("OI", "IM"): [11, 15],       # Organizational impact asserting construction
    # ── enabling: SC ─────────────────────────────────────────────────
    ("SC", "BL"): [5, 6],         # Social/environmental context conditions
    ("SC", "DP"): [5, 11],        # Social context enabling democratic participation
    # ── enabling: PR ─────────────────────────────────────────────────
    ("PR", "CV"): [2, 11],        # Problem of extraction, community alternative
    # ── connective (PT) ──────────────────────────────────────────────
    ("PT", "BL"): [13, 14],       # Partnership navigates rights and flow tensions
    ("PT", "DP"): [11, 13],       # Partnership enables collective governance
    ("PT", "IM"): [10, 14],       # Networks for advocacy, challenging incumbents
    # ── protective (RG) ──────────────────────────────────────────────
    ("RG", "DP"): [4, 7],         # Legal mandates shape participation
    ("RG", "BL"): [12, 17],       # Regulatory openness/closure, state-corporate negotiation
    ("RG", "IM"): [4, 7],         # Legal frameworks enabling systemic impact
    # ── legitimizing: PU ─────────────────────────────────────────────
    ("PU", "DP"): [5],            # Cultural perspectives informing design
    ("PU", "CV"): [5],            # Cultural value creation
    ("PU", "IM"): [5, 10],        # Purpose-driven impact and advocacy cycles
    # ── legitimizing: PO ─────────────────────────────────────────────
    ("PO", "DP"): [1, 10],        # Political advocacy for democratic governance
    ("PO", "IM"): [10, 16],       # Advocacy cycles, reform vs. transformation
}


# ── Necessary Conditions (Revision 4.4) ──────────────────────────────
# 100% coverage relationships from Chapter 7 condition-outcome analysis.
# When a necessary condition is absent, the corresponding outcome
# CANNOT be produced — enforced in counter-case/sensitivity operations.
NECESSARY_CONDITIONS = {
    "TT1": ["DP3"],   # Physical Infrastructure → Community-Controlled Infrastructure (100%)
    "PU1": ["DP6"],   # Indigenous Epistemology → Cultural Governance Integration (100%)
    "PU2": ["IM3"],   # Cultural Preservation → Linguistic Sovereignty (100%)
    "RS3": ["IM4"],   # Economic Value Redistribution → Economic Transformation (100%)
    "PT2": ["BL2"],   # Multi-Network Positioning → Network Coordination (100%)
}

# Near-necessary (75%+) — flagged but not enforced as hard constraints
NEAR_NECESSARY_CONDITIONS = {
    "TP1": ["DP2"],   # Democratic Data Authority → Data Sovereignty (75%)
}


# ── Outcome Co-occurrence (Revision 4.5) ─────────────────────────────
# From Chapter 7: DP and CV co-occur at 71%, reflecting mutual
# constitution of political and economic sovereignty.
OUTCOME_COOCCURRENCE = {
    ("DP", "CV"): 0.71,   # Democratic Practices ↔ Community Value
    ("CV", "DP"): 0.71,   # Symmetric
    ("DP", "BL"): 0.55,   # Approximate from empirical patterns
    ("BL", "DP"): 0.55,
    ("DP", "IM"): 0.48,
    ("IM", "DP"): 0.48,
    ("CV", "BL"): 0.42,
    ("BL", "CV"): 0.42,
    ("CV", "IM"): 0.38,
    ("IM", "CV"): 0.38,
    ("BL", "IM"): 0.35,
    ("IM", "BL"): 0.35,
}

# Intra-group connection pathways (from Appendix 10)
OUTCOME_INTRA_GROUP_PATHWAYS = {
    "DP": "Foundation→Practice→Protection; Authority→Accountability; Universal→Culturally-Specific",
    "CV": "Economic value → knowledge commons → cultural value (integrated system)",
    "BL": "Structural solutions (federated governance) + relational solutions (reciprocal partnerships)",
    "IM": "Capacity→Policy→Institution; Cultural→Economic Integration; Local→Systemic Amplification",
}


# ── Condition Classification (Revision 4.7) ──────────────────────────
# From Chapter 7 condition-outcome relationships section.
# Transversal: high resonance, broad connections across outcome groups
# Specialist: low resonance, high consistency, narrow scope
# Necessary: 100% coverage (see NECESSARY_CONDITIONS above)
CONDITION_CLASSIFICATION = {
    # Transversal conditions (high resonance, broad connections)
    "PO1": "transversal",   # 41 connections, all 4 outcome groups
    "RS1": "transversal",   # 29 connections, strong in DP (12) and IM (13)
    "PT2": "transversal",   # 28 connections, focused on BL (10) and IM (7)
    "TP2": "transversal",   # 22 connections, distributed across DP (8) and CV (8)
    # Specialist conditions (low resonance, high consistency)
    "TP5": "specialist",    # 3 cases, 100% coverage for specific outcomes
    "TT1": "specialist",    # 5 cases, 100% for DP3 (also necessary)
    "PU1": "specialist",    # 4 cases, 100% for DP6 (also necessary)
    "PU2": "specialist",    # Cultural Preservation, 100% for IM3 (also necessary)
    "RS3": "specialist",    # Economic Value Redistribution (also necessary)
    "PT2": "transversal",   # Multi-Network Positioning (transversal + near-necessary for BL2)
    # Necessary conditions (100% coverage)
    "TT1": "necessary",     # TT1 → DP3 (overrides specialist)
    "PU1": "necessary",     # PU1 → DP6 (overrides specialist)
    "PU2": "necessary",     # PU2 → IM3 (overrides specialist)
    "RS3": "necessary",     # RS3 → IM4 (overrides specialist)
    "PT2": "necessary",     # PT2 → BL2 (overrides transversal — dual classification)
}

# Transversal condition resonance scores (connection counts from cross-impact matrix)
TRANSVERSAL_RESONANCE = {
    "PO1": {"total": 41, "DP": 10, "CV": 8, "BL": 10, "IM": 13},
    "RS1": {"total": 29, "DP": 12, "CV": 4, "BL": 0, "IM": 13},
    "PT2": {"total": 28, "DP": 4, "CV": 7, "BL": 10, "IM": 7},
    "TP2": {"total": 22, "DP": 8, "CV": 8, "BL": 3, "IM": 3},
}


# ── Partner Types (Second Model) ──────────────────────────────────────
PARTNER_TYPES = {
    1: "Indigenous Governance Bodies",
    2: "Community and Grassroots Organizations",
    3: "Academic and Research Institutions",
    4: "Government Agencies and Public Institutions",
    5: "International and Multilateral Organizations",
    6: "Philanthropic and Development Funders",
    7: "Corporate and Technology Entities",
    8: "Cooperative and Solidarity Economy Networks",
    9: "Labor and Worker Organizations",
    10: "Digital Rights and Open Technology Organizations",
    11: "Social Movement and Advocacy Networks",
    12: "Cultural, Religious, and Knowledge Institutions",
}

# Relationship Types (PT1-PT6)
RELATIONSHIP_TYPES = {
    "PT1": "Reciprocal Knowledge Exchange",
    "PT2": "Multi-Network Strategic Positioning",
    "PT3": "Community Sovereignty Protection",
    "PT4": "Expertise-Community Knowledge Integration",
    "PT5": "Cross-Sector Collaboration Networks",
    "PT6": "Generative Partnering",
}

# Inter-case direct partnerships
DIRECT_PARTNERSHIPS = [
    ("GIDA", "Te Mana Raraunga"),
    ("GIDA", "MAIAM NAYRI WINGARA"),
    ("GIDA", "FNIGC"),
    ("Te Hiku Media", "Te Mana Raraunga"),
    ("Enspiral", "Loomio"),  # PT6: spawned
]

# Latent clusters (shared organizational spaces, no direct partnerships)
LATENT_CLUSTERS = {
    "Platform Cooperatives": ["CoopCycle", "Fairbnb.coop", "The Drivers Cooperative", "Les Mercedes"],
    "Spanish Cooperative Infrastructure": ["Guifi.net", "Som Energia"],
    "Community Network Builders": ["Detroit CTC", "Zenzeleni", "TIC A.C.", "Guifi.net"],
    "Open Knowledge Commons": ["P2P Foundation", "Sensorica", "WikiHouse", "Nea Guinea/Tzoumakers"],
    "Research Data Governance": ["ARDC", "RDA"],
    "Algorithmic Accountability": ["DAIR", "WAO", "Stop LAPD Spying Coalition"],
}


# ── Helper Functions ──────────────────────────────────────────────────

def canonicalize_case_name(name: str) -> str:
    """Resolve any case name variant to canonical form."""
    name = name.strip()
    if name in CASE_NAME_MAP:
        return CASE_NAME_MAP[name]
    # Fallback: try case-insensitive match
    name_lower = name.lower()
    for variant, canonical in CASE_NAME_MAP.items():
        if variant.lower() == name_lower:
            return canonical
    raise ValueError(f"Unknown case name: '{name}'")


def canonicalize_condition_type(name: str) -> str:
    """Resolve condition type name to code."""
    name = name.strip()
    if name in CONDITION_TYPE_MAP:
        return CONDITION_TYPE_MAP[name]
    if name in ALL_CONDITION_TYPES:
        return name
    raise ValueError(f"Unknown condition type: '{name}'")


def canonicalize_org_type(name: str) -> str:
    """Resolve org type name to code."""
    name = name.strip()
    if name in ORG_TYPE_MAP:
        return ORG_TYPE_MAP[name]
    raise ValueError(f"Unknown org type: '{name}'")


def get_outcome_group(code: str) -> str:
    """Get outcome group from category code (e.g., 'DP1' → 'DP')."""
    for group, cats in OUTCOME_CATEGORIES.items():
        if code in cats:
            return group
    raise ValueError(f"Unknown outcome code: '{code}'")


def get_condition_type(code: str) -> str:
    """Get condition type from category code (e.g., 'GV1' → 'GV')."""
    for ctype, cats in CONDITION_CATEGORIES.items():
        if code in cats:
            return ctype
    raise ValueError(f"Unknown condition code: '{code}'")
