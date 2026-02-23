# Ad Performance Checker

Score your ad creatives and overall ad performance with **Creative Score**, **Ad Score**, **ROAS**, and actionable **Improvements**.

## What you get

- **Creative scoring** — 0–100 score based on CTR, engagement rate, video completion (or copy length), and conversion rate, with a per-metric breakdown.
- **Ad score** — Combined score (50% creative + 50% ROAS) with a letter grade.
- **ROAS** — Return on Ad Spend (Revenue ÷ Spend) with a simple tier (Poor / Average / Good / Excellent).
- **Improvements** — Prioritized suggestions (e.g. boost CTR, improve conversion rate, add CTA) when metrics are below benchmarks.

## Run locally

```bash
cd ad-performance-checker
pip install -r requirements.txt
python main.py
```

Open [http://localhost:8050](http://localhost:8050).

## API

- `POST /api/analyze` — Body: JSON with ad metrics (see below). Returns creative score, ad score, ROAS, and improvements.

### Example request

```json
{
  "ad_spend": 500,
  "revenue": 1200,
  "impressions": 50000,
  "clicks": 750,
  "engagements": 1500,
  "conversions": 45,
  "has_video": false,
  "video_views": 0,
  "video_completion_100": 0,
  "headline": "Summer Sale – 30% Off",
  "primary_text": "Limited time. Free shipping over $50.",
  "cta": "Shop Now"
}
```

### Example response

```json
{
  "creative_score": { "score": 72.5, "grade": "B", "components": [...] },
  "ad_score": { "score": 78.2, "grade": "B", "creative_contribution": 72.5, "roas_contribution": 83.9 },
  "roas": { "roas": 2.4, "formatted": "2.40x", "tier": "average", "label": "Average", "revenue": 1200, "spend": 500 },
  "improvements": [
    { "priority": "high", "category": "Creative", "title": "Boost click-through rate", "detail": "...", "metric": "CTR" }
  ],
  "metrics": { "impressions": 50000, "clicks": 750, "ctr": 1.5, ... }
}
```

## Port

Default port is **8050**. Set `PORT` in the environment to change it.

---

## Deploy on Render

1. Push this repo to GitHub (e.g. [QUICKADSWORK/ad-performance-checker](https://github.com/QUICKADSWORK/ad-performance-checker)).
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**.
3. Connect your GitHub account and select the `ad-performance-checker` repo.
4. Render will read `render.yaml` and create a **Web Service** (build: `pip install -r requirements.txt`, start: `uvicorn main:app --host 0.0.0.0 --port $PORT`).
5. Click **Apply**; after the deploy finishes, your app will be live at `https://<service-name>.onrender.com`.

No env vars or disk are required. The app is stateless.

---

## Push to a new GitHub repo

1. **Create a new repo on GitHub**  
   Go to [github.com/new](https://github.com/new), name it (e.g. `ad-performance-checker`), leave it **empty** (no README, no .gitignore).

2. **Add the remote and push** (replace `YOUR_USERNAME` and `YOUR_REPO` with your GitHub username and repo name):

   ```bash
   cd ad-performance-checker
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

   If you use SSH:

   ```bash
   git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```
