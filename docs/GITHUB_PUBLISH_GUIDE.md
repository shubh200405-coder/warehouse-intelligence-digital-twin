# GitHub publishing and Streamlit deployment

## Repository identity

**Repository name**

`warehouse-intelligence-digital-twin`

**Display name**

`Warehouse Intelligence | Digital Twin & Operations Analytics`

**GitHub description**

Interactive warehouse operations analytics built with Python and Streamlit, featuring inventory intelligence, CSV-based analysis, rack-level drill-down, synchronized 2D floor plans and 3D warehouse visualization, exception monitoring, and simulated equipment activity.

**Suggested topics**

`python` `streamlit` `pandas` `plotly` `threejs` `digital-twin` `warehouse-management` `inventory-analytics` `supply-chain-analytics` `data-visualization`

## Repository root

Upload the contents of this project folder, not the enclosing ZIP folder. `app.py` and `requirements.txt` must sit at the repository root.

```text
warehouse-intelligence-digital-twin/
├── app.py
├── digital_twin.py
├── requirements.txt
├── requirements-dev.txt
├── run_windows.bat
├── pytest.ini
├── .gitignore
├── .env.example
├── .streamlit/
│   └── config.toml
├── data/
│   └── sample_inventory.csv
├── static/
│   ├── digital_twin.html
│   ├── digital_twin.css
│   ├── floorplan.js
│   └── three_scene.js
├── database/
│   └── schema.sql
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_DICTIONARY.md
│   ├── KPI_DEFINITIONS.md
│   ├── PROJECT_AUDIT.md
│   ├── USER_GUIDE.md
│   ├── PROJECT_EXPLANATION_HINGLISH.md
│   └── VIDEO_OVERVIEW_SCRIPT_HINGLISH.md
├── powerbi/
│   ├── measures.dax
│   ├── data-model.md
│   └── power-query-notes.md
└── tests/
    ├── test_demo_model.py
    └── test_digital_twin.py
```

## Before pushing

- Keep the included synthetic `data/sample_inventory.csv`.
- Do not upload real warehouse/customer exports unless you have permission and have removed confidential fields.
- Do not upload `.venv/`, `__pycache__/`, `.pytest_cache/`, `.env`, or `.streamlit/secrets.toml`. The included `.gitignore` excludes these.
- Do not put API keys, passwords, access tokens, or database credentials in source files or README.

## Publish using VS Code

1. Extract the ZIP.
2. In VS Code select **File → Open Folder** and open the inner `Warehouse_Intelligence_English_UI` folder (the folder that directly contains `app.py`).
3. Select the **Source Control** icon in the left activity bar.
4. Click **Initialize Repository**.
5. Review the changed files. Make sure `.venv`, `.env`, secrets, and private datasets are not listed.
6. Enter commit message `Initial release: Warehouse Intelligence` and click **Commit**.
7. Select **Publish Branch** or **Publish to GitHub**, sign in to GitHub, and create the repository named `warehouse-intelligence-digital-twin`.
8. Choose **Public** for a portfolio project only if the repository contains no confidential data.

If VS Code does not show the GitHub publishing option, use the terminal from the project root:

```powershell
git init
git add .
git commit -m "Initial release: Warehouse Intelligence"
git branch -M main
git remote add origin https://github.com/YOUR-GITHUB-USERNAME/warehouse-intelligence-digital-twin.git
git push -u origin main
```

Replace `YOUR-GITHUB-USERNAME` with your actual GitHub username. Git may ask you to sign in through your browser. If Git is not installed, install Git for Windows first, restart VS Code, and retry.

## Deploy on Streamlit Community Cloud

1. Open [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
2. Select **Create app**.
3. Choose repository `YOUR-GITHUB-USERNAME/warehouse-intelligence-digital-twin`.
4. Choose branch `main`.
5. Set **Main file path** to `app.py`.
6. Optionally set the app subdomain to `warehouse-intelligence-digital-twin` if available.
7. Select **Deploy** and wait for the build logs to finish.

The root `requirements.txt` is used to install dependencies. The `.streamlit/config.toml` file must remain in the repository at that exact path. Keep `static/` and `data/` in the repository because the application reads those assets locally.

The 3D view imports browser modules from `esm.sh`, so it needs internet access in the browser. The 2D floor plan is the fallback if WebGL is unavailable.

## After publishing

Every future change should be committed and pushed to the same branch. Streamlit Community Cloud detects repository updates and redeploys the app. Check app logs in the Streamlit workspace if the deployment fails.

## Important note about uploaded data

This app supports uploading an inventory CSV for analysis. Do not use sensitive business or customer data in a public demo. The included sample file is synthetic. If a real dataset is necessary, make sure the app's audience, data handling, and hosting access are appropriate before uploading it.
