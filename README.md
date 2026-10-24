# WindLens — UK Wind Forecast Accuracy Dashboard

WindLens is a full-stack data analytics dashboard that compares UK wind generation forecasts with actual generation data for January 2026. It helps users explore forecast errors, understand model performance, and inspect hourly data.

## Live Demo

- **Dashboard:** https://windlens-7k4m2q.vercel.app
- **API:** https://windlens-7k4m2q.onrender.com
- **API Documentation:** https://windlens-7k4m2q.onrender.com/docs

## Features

- Forecast versus actual wind generation analysis
- Interactive charts and hourly data exploration
- Forecast accuracy metrics: MAE, RMSE, and bias
- FastAPI backend endpoints for dashboard data
- Responsive React and TypeScript frontend

## Tech Stack

**Frontend:** React, TypeScript, Vite, Recharts

**Backend:** Python, FastAPI, pandas

**Data source:** Elexon BMRS API

**Deployment:** Vercel (frontend), Render (backend)

## Dataset and Methodology

The current prototype analyses January 2026 data. Forecast observations are matched with actual generation for corresponding delivery periods.

The analysis uses a 12-hour forecast lead-time cutoff as a prototype assumption.

The dashboard reports:

- **MAE:** Mean Absolute Error
- **RMSE:** Root Mean Squared Error
- **Bias:** Mean signed forecast error

For this dataset, the analysis contains 744 matched hourly periods.

## Local Development

### Backend

From the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend runs at `http://127.0.0.1:8000`.

### Frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL=http://127.0.0.1:8000` in `frontend/.env.local` for local development.

The frontend runs at `http://localhost:5173`.

## API Endpoints

| Endpoint | Purpose |
|---|---|
| `/api/health` | Health check |
| `/api/overview` | Summary metrics |
| `/api/series?limit=24` | Time-series data |
| `/api/periods?limit=24` | Matched delivery periods |

## Future Improvements

- Support configurable date ranges
- Add forecast lead-time comparisons
- Improve automated data updates and validation
- Add tests for API endpoints and data-processing logic

## Author

**Tejasv Rathore**

GitHub: https://github.com/Tejasv1910
for implementation guidance, debugging, documentation, and project workflow support. The project should be reviewed and understood by its author before submission.
