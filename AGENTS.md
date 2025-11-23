# Repository Guidelines

## Project Structure & Module Organization
- `app.py`: Streamlit entry point with tabs for results, Monte Carlo, ruin, and presets.
- `src/`: Core package.
  - `config.py`: Defaults (risk, preset dir, sims).
  - `models/`: Trade and TradeResult dataclasses.
  - `data/`: CSV loader for trades.
  - `risk/`: Position sizing, metrics, ruin calculator.
  - `simulation/`: Sequential engine and Monte Carlo driver.
  - `presets/`: JSON preset persistence.
  - `ui/`: Sidebar layout and reusable components.
- `requirements.txt`: Python dependencies.
- `presets_data/`: Created at runtime to store saved presets.

## Build, Test, and Development Commands
- Install deps: `pip install -r requirements.txt`
- Run app locally: `streamlit run app.py`
- Quick syntax check: `python -m compileall app.py src`

## Coding Style & Naming Conventions
- Language: Python 3; prefer type hints and dataclasses for models/settings.
- Indent with 4 spaces; keep lines reasonably short (~99 chars).
- Module/filename naming: `snake_case.py`; classes in `CamelCase`; variables/functions `snake_case`.
- Keep UI labels/user-facing text in Japanese (current UI language).
- Avoid non-ASCII unless already present in UI text.

## Testing Guidelines
- No formal test suite yet; add `pytest` tests alongside modules (e.g., `tests/test_risk.py`).
- Use small deterministic trade fixtures to verify equity curves, R multiples, drawdowns, and ruin calculations.
- For UI changes, at least exercise `streamlit run app.py` locally to ensure pages render and uploads parse.

## Commit & Pull Request Guidelines
- Commit messages: short imperative summary (e.g., "Add fractional Kelly sizing clamp").
- PRs should include: summary of changes, impacted modules, screenshots/GIFs for UI, and any new CLI commands.
- Link to related issues when applicable; call out breaking changes or new config requirements (`config.py`, presets).

## Security & Configuration Tips
- Presets are stored as JSON under `presets_data/`; avoid committing sensitive sample data.
- CSV uploads are parsed with pandas; validate required headers before simulating.
- Network access is not required for core logic (yfinance is not wired yet); keep the app offline by default.
