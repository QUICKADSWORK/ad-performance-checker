"""
Ad Performance Checker - FastAPI Application
Creative scoring, ad scoring, ROAS, and improvement suggestions.
"""
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Optional

import scoring

app = FastAPI(
    title="Ad Performance Checker",
    description="Score ad creatives, overall ad performance, ROAS, and get improvement suggestions",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class AdMetricsInput(BaseModel):
    ad_spend: float = Field(0, ge=0, description="Total ad spend")
    revenue: float = Field(0, ge=0, description="Revenue attributed to this ad")
    impressions: int = Field(0, ge=0, description="Impressions")
    clicks: int = Field(0, ge=0, description="Clicks")
    engagements: int = Field(0, ge=0, description="Likes, comments, shares, etc.")
    conversions: int = Field(0, ge=0, description="Conversions")
    video_views: int = Field(0, ge=0, description="Video views (if video ad)")
    video_completion_25: int = Field(0, ge=0, description="25% video completions")
    video_completion_50: int = Field(0, ge=0, description="50% video completions")
    video_completion_75: int = Field(0, ge=0, description="75% video completions")
    video_completion_100: int = Field(0, ge=0, description="100% video completions")
    has_video: bool = Field(False, description="Ad has video creative")
    headline: Optional[str] = Field("", description="Ad headline")
    primary_text: Optional[str] = Field("", description="Primary text / body")
    cta: Optional[str] = Field("", description="Call-to-action button text")

    def to_metrics_dict(self) -> dict:
        return {
            "ad_spend": self.ad_spend,
            "revenue": self.revenue,
            "impressions": self.impressions,
            "clicks": self.clicks,
            "engagements": self.engagements,
            "conversions": self.conversions,
            "video_views": self.video_views,
            "video_completion_25": self.video_completion_25,
            "video_completion_50": self.video_completion_50,
            "video_completion_75": self.video_completion_75,
            "video_completion_100": self.video_completion_100,
            "has_video": self.has_video,
            "headline": self.headline or "",
            "primary_text": self.primary_text or "",
            "cta": self.cta or "",
        }


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the ad performance checker UI."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/analyze")
async def analyze(metrics: AdMetricsInput):
    """Run full ad performance analysis."""
    try:
        result = scoring.run_analysis(metrics.to_metrics_dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8050"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
