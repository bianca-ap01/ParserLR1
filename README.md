
# LR(1) Toolkit — Labs Library + Fullstack App

This bundle contains:
- `lr1_project/`: labs-style LR(1) generator & parser (pip-installable package `lr1`).
- `lr1_app/`: FastAPI backend + Vite/React frontend that visualizes:
  - LR(1) **closure table** (states/items) and **syntax tables** (ACTION/GOTO)
  - **ε-NFA** from a regex (Thompson), **ε-closure** table
  - **DFA** via subset construction (+ transition table)

## Quick start

### 1) Install the LR(1) library (editable)
```bash
cd lr1_project
python3 -m venv .venv && source .venv/bin/activate
pip install -e ./src
```

### 2) Run the backend
```bash
cd ../lr1_app/backend
source ../.venv/bin/activate  # or create a new venv here
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3) Run the frontend
```bash
cd ../frontend
npm i
npm run dev
```

Open the printed local URL from Vite. Use the Grammar panel to build LR(1) tables, and the Regex panel to build ε‑NFA / DFA tables.