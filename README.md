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
