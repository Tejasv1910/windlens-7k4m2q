# WindLens — UK Wind Forecast Accuracy Dashboard

WindLens is a full-stack dashboard for evaluating Great Britain's wind power forecasts against actual generation during January 2026. It is designed to help electricity-market analysts understand forecast errors and assess forecast quality before delivery.

## Features

- Forecast-versus-actual generation time series.
- KPI cards for Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), forecast bias, matched periods, and data coverage.
- Largest forecast-error periods with forecast publication timestamps and lead times.
- A historical dataset covering January 2026.
- A configurable frontend API URL for local development and deployment.

## Technology Stack

**Frontend:** React, TypeScript, Vite, Recharts  
**Backend:** Python, FastAPI, pandas, NumPy  
**Testing:** pytest, HTTPX  
**Data source:** Elexon BMRS API

## Project Structure

```text
windlens/
├── backend/
│   ├── main.py
│   ├── download_january.py
│   ├── analyze_january.py
│   ├── validate_analysis.py
│   ├── inspect_elexon.py
│   └── requirements.txt
├── data/
│   ├── actuals_jan_2026.csv
│   ├── forecasts_jan_2026.csv
│   ├── matched_jan_2026.csv
│   └── metrics_jan_2026.json
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── .gitignore
└── README.md
```

## Data and Methodology

The dashboard uses wind generation actuals and wind forecast records from the Elexon BMRS API.

- **Analysis period:** 1–31 January 2026.
- **Actual generation:** Half-hourly records aggregated into hourly averages for comparison.
- **Forecast selection:** For each delivery hour, select the latest forecast published at least 12 hours before delivery.
- **Cutoff assumption:** The 12-hour decision cutoff is a prototype assumption, not a claim about a specific market rule.
- **Comparison:** Match hourly forecasts with hourly actual generation.

Forecasts published after the selected cutoff are excluded to avoid using information that would not have been available at the assumed decision time.

## Evaluation Metrics

- **MAE:** Average absolute difference between forecast and actual generation, in MW.
- **RMSE:** Square root of the average squared forecast error, in MW.
- **Bias:** Average forecast minus actual generation. Positive bias indicates overforecasting.
- **Coverage:** Percentage of eligible delivery periods successfully matched.
- **Matched periods:** Number of delivery periods included in the comparison.

### January 2026 Results

Using the 12-hour cutoff assumption:

| Metric | Result |
|---|---:|
| Matched hourly periods | 744 |
| Coverage | 100% |
| MAE | 1,907.18 MW |
| RMSE | 2,384.45 MW |
| Bias | +1,704.37 MW |

These results describe forecast error under the stated selection method; they are not, by themselves, a complete electricity procurement or trading recommendation.

## Local Setup

### Prerequisites

Install Python, Node.js with npm, and Git.

### 1. Start the backend

From the project root in PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Backend API: `http://127.0.0.1:8000`  
Interactive API documentation: `http://127.0.0.1:8000/docs`

### 2. Start the frontend

Open a **second terminal** in VS Code:

```powershell
cd frontend
npm install
```

Create `frontend/.env.local` with:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Then run:

```powershell
npm run dev
```

Open `http://localhost:5173`.

### 3. Build the frontend

From the `frontend` directory:

```powershell
npm run build
```

## Configuration and Deployment

The frontend reads its backend URL from `VITE_API_URL`. Set this environment variable to the deployed backend URL when deploying the frontend.

A production deployment also needs a hosted Python backend, suitable CORS settings, and access to the required data files. Update this section with the actual deployed application URL once deployment is complete.

**Live demo:** To be added  
**Public repository:** To be added

## Testing and Validation

The analysis validation script checks for duplicate delivery hours and ensures selected forecasts respect the publication cutoff.

Run the validation script from the backend directory:

```powershell
python validate_analysis.py
```

If tests are added or configured, run them with:

```powershell
python -m pytest
```

## AI Tools Disclosure

AI assistance was used during development for implementation guidance, debugging, documentation, and project workflow support. The project should be reviewed and understood by its author before submission.
