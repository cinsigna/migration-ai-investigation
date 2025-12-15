# Migration Mismatch Investigation Dashboard

A lightweight dashboard to analyse migration payloads, identify mismatches, quantify customer impact, and generate AI-assisted root cause insights. Designed to support incident triage and remediation during utility billing migrations.

---

## Overview

This project demonstrates an AI powered approach to investigating utility billing migration issues.
It ingests SI migration payloads, identifies mismatches between legacy and migrated products, quantifies customer impact, and generates a structured root cause analysis with remediation guidance.

The goal is to reduce manual investigation time and provide delivery teams with clear, client ready insights to support incident triage and migration remediation.

## Presentation

The case study presentation and supporting materials are included in the docs folder.
These slides are used to walk through the approach, the prototype, and the investigation flow during the interview.

---

## Main Capabilities

### Mismatch detection
Compares `legacy_product` and `migrated_product` fields and flags mismatches.

### Customer impact
Aggregates affected customer IDs per pattern.
Exports:

output/impacted_customers.csv  
output/impacted_customers_by_pattern.csv  

### Visual summary
Horizontal bar chart showing mismatch counts by SI reason code.

### AI-generated RCA
Structured summary produced using the OpenAI API.
Includes likely cause, remediation suggestion, systematic vs isolated classification, and list of impacted customers.

---

## Folder Structure

CDL - Case study/
│
├── data/                     sample migration payloads  
├── output/                   exported analysis files  
│   ├── ai_mismatch_analysis.txt  
│   ├── impacted_customers.csv  
│   └── impacted_customers_by_pattern.csv  
│
├── src/  
│   └── mismatch_dashboard.py    main analysis + Gradio app  
│
├── notebooks/  
│   └── RCA.ipynb                exploratory analysis  
│
├── docs/ or presentation/       slide deck for the case study  
│
├── requirements.txt  
└── README.md  

---

## Setup

Install dependencies:

pip install -r requirements.txt

Set your OpenAI key:

export OPENAI_API_KEY="your_key_here"

Launch the dashboard:

python src/mismatch_dashboard.py

A local Gradio UI will open in your browser.

---

## Outputs

The dashboard automatically generates:

output/ai_mismatch_analysis.txt  
output/impacted_customers.csv  
output/impacted_customers_by_pattern.csv  

These can be shared with engineering, delivery teams, or clients.

---

## Core Logic

- Pandas for mismatch grouping and KPI calculations  
- Matplotlib for graphical insight  
- OpenAI for structured RCA generation  
- Gradio for interactive UI  
- CSV-based workflow aligned with standard SI payload formats  

---

## Intended Use

Supports:

- early stage identification of migration issues  
- quantification of customer impact  
- preparation of client-ready RCA summaries  
- alignment between configured products and SI outputs  

---

## Future Extensions

- multi-file comparison to track migration improvements  
- automated rule validation for mapping logic  
- PDF export of RCA  
- additional visualisation layers  

---
