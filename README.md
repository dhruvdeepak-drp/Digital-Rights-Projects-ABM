# Digital Rights Projects: Agent-Based Model and Interactive Observatory

This repository contains the complete source code and data files for the agent-based model (ABM) developed as part of the doctoral dissertation *Digital Rights Projects: Collective Capacities for Democratizing Technology* (Dhruv Deepak, George Mason University, Department of Sociology, 2026).

## What This Is

The model computationally operationalizes findings from a qualitative content analysis of 43 community-led digital initiatives across four organizational types: Data Sovereignty Organizations, Digital Cooperatives, Participatory Governance Organizations, and Peer Production Systems. It traces how condition configurations produce outcomes and construct sovereignty capacity across seven interdependent dimensions.

The interactive observatory provides a browser-based interface for exploring the model's analytical capabilities, including sensitivity analysis, counterfactual simulation, case construction, relational density analysis, and cross-case pattern detection.

## Live Observatory

The interactive observatory is deployed at: **[deployment URL]**

Access requires a PIN provided in the dissertation.

## Repository Structure

| File | Description |
|------|-------------|
| `config.py` | Constants, mappings, sovereignty dimension definitions, Bridge B and Bridge D mappings, D-A-S pattern definitions |
| `data_loader.py` | Reads empirical data from Excel files and instantiates 43 agents |
| `agent.py` | Agent class carrying condition configurations, outcomes, sovereignty profiles, and relational characteristics |
| `primary_model.py` | Primary model engine: production rule evaluation, outcome prediction, case construction |
| `analytical_engine.py` | Analytical operations: sensitivity, counterfactuals, sovereignty pathways, cross-case patterns |
| `relational_engine.py` | Second model engine: varies partnership configurations while holding conditions constant |
| `app.py` | Flask web application exposing 34 API endpoints |
| `index.html` | Single-page interactive observatory interface |
| `test_loading.py` | Data loading validation (10 tests) |
| `test_analytical.py` | Primary model and analytical engine tests (17 tests) |
| `test_relational.py` | Relational engine tests (7 tests) |

The six Excel data files in this repository are outputs of Stage 1 (qualitative content analysis and cross-impact assessment) and are required for the model to run.

## Running Locally

**Requirements:** Python 3.10 or later.

```bash
# Install dependencies
pip install flask openpyxl gunicorn

# Run the application
python app.py
```

The application starts on `http://localhost:5000`. All outputs are deterministic — running locally produces identical results to the deployed observatory.

## Relationship to the Dissertation

The model implements the dissertation's four-bridge theoretical architecture:

- **Bridge A (Genealogical):** The analytical vocabulary in `config.py` reflects the synthesis of seven strands of digital commonwealth scholarship into a digital sovereignty framework.
- **Bridge B (Structural):** `CONDITION_SOVEREIGNTY_TERRAIN` maps each condition type to the sovereignty dimensions it engages, establishing the terrain on which sovereignty construction occurs.
- **Bridge C (Mechanistic):** The 17 recursive D-A-S patterns and mechanism type assignments characterize how conditions produce outcomes through design-affordance-sovereignty cycles.
- **Bridge D (Conceptual):** `OUTCOME_SOVEREIGNTY_MAP` maps each outcome category to the sovereignty dimensions it constructs as capacity.

Chapters 7 and 8 of the dissertation describe the model's design, construction, and analytical findings. Appendix 15 provides a detailed codebase overview.

## Citation

Deepak, D. (2026). *Digital Rights Projects: Collective Capacities for Democratizing Technology* [Doctoral dissertation, George Mason University].

## License

This code is shared for academic review and research purposes. Please contact the author regarding reuse.
