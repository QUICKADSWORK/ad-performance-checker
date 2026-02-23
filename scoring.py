"""
Ad Performance Scoring Engine
Computes creative score, ad score, ROAS, and improvement suggestions.
"""
from dataclasses import dataclass
from typing import List, Dict, Any

# Industry benchmarks (typical ranges for paid social / display)
BENCHMARKS = {
    "ctr": {"poor": 0.5, "avg": 1.5, "good": 2.5, "excellent": 4.0},  # %
    "engagement_rate": {"poor": 0.5, "avg": 2.0, "good": 4.0, "excellent": 8.0},  # %
    "conversion_rate": {"poor": 0.5, "avg": 2.0, "good": 4.0, "excellent": 8.0},  # %
    "video_completion": {"poor": 25, "avg": 50, "good": 75, "excellent": 90},  # %
    "roas": {"poor": 1.0, "avg": 2.0, "good": 4.0, "excellent": 6.0},  # ratio
}


def _score_from_benchmark(value: float, metric: str) -> tuple:
    """Map a metric value to 0-100 score and tier using benchmarks."""
    bench = BENCHMARKS.get(metric, BENCHMARKS["ctr"])
    poor = bench["poor"]
    avg = bench["avg"]
    good = bench["good"]
    excellent = bench["excellent"]
    if value >= excellent:
        return min(100, 90 + (value - excellent) / max(excellent * 0.1, 0.01)), "excellent"
    if value >= good:
        return 70 + 20 * (value - good) / max(excellent - good, 0.01), "good"
    if value >= avg:
        return 50 + 20 * (value - avg) / max(good - avg, 0.01), "average"
    if value >= poor:
        return 25 + 25 * (value - poor) / max(avg - poor, 0.01), "below_average"
    return max(0, 25 * value / max(poor, 0.01)), "poor"


def _compute_rates(m: dict) -> dict:
    """Compute derived rates (CTR, engagement rate, conversion rate, etc.)."""
    imp = max(m.get("impressions", 0) or 1, 1)
    clicks = m.get("clicks", 0) or 0
    engagements = m.get("engagements", 0) or 0
    conversions = m.get("conversions", 0) or 0
    spend = m.get("ad_spend", 0) or 0
    video_views = m.get("video_views", 0) or 0
    video_completion_100 = m.get("video_completion_100", 0) or 0
    video_completion_75 = m.get("video_completion_75", 0) or 0

    rates = {
        "ctr": 100 * clicks / imp,
        "engagement_rate": 100 * engagements / imp,
        "conversion_rate": 100 * conversions / imp,
        "cpc": spend / clicks if clicks else 0,
        "cpa": spend / conversions if conversions else 0,
    }
    if video_views:
        rates["video_completion_100"] = 100 * video_completion_100 / video_views
        rates["video_completion_75"] = 100 * video_completion_75 / video_views
    else:
        rates["video_completion_100"] = 0
        rates["video_completion_75"] = 0
    return rates


def compute_creative_score(m: dict, rates: dict) -> dict:
    """
    Creative score 0-100 based on CTR, engagement, video completion, and copy signals.
    """
    components = []
    total_weight = 0
    weighted_sum = 0

    ctr_score, ctr_tier = _score_from_benchmark(rates["ctr"], "ctr")
    components.append({
        "name": "Click-through rate",
        "score": round(ctr_score, 1),
        "tier": ctr_tier,
        "value": f"{rates['ctr']:.2f}%"
    })
    weighted_sum += ctr_score * 30
    total_weight += 30

    eng_score, eng_tier = _score_from_benchmark(rates["engagement_rate"], "engagement_rate")
    components.append({
        "name": "Engagement rate",
        "score": round(eng_score, 1),
        "tier": eng_tier,
        "value": f"{rates['engagement_rate']:.2f}%"
    })
    weighted_sum += eng_score * 25
    total_weight += 25

    has_video = m.get("has_video", False) and (m.get("video_views") or 0) > 0
    if has_video:
        vc = rates.get("video_completion_100") or rates.get("video_completion_75") or 0
        vc_score, vc_tier = _score_from_benchmark(vc, "video_completion")
        components.append({
            "name": "Video completion",
            "score": round(vc_score, 1),
            "tier": vc_tier,
            "value": f"{vc:.1f}%"
        })
        weighted_sum += vc_score * 25
        total_weight += 25
    else:
        copy_len = len((m.get("headline") or "") + (m.get("primary_text") or ""))
        if copy_len < 20:
            copy_score, copy_tier = 40, "poor"
        elif copy_len < 80:
            copy_score, copy_tier = 70, "average"
        else:
            copy_score, copy_tier = 85, "good"
        components.append({
            "name": "Copy length",
            "score": copy_score,
            "tier": copy_tier,
            "value": f"{copy_len} chars"
        })
        weighted_sum += copy_score * 25
        total_weight += 25

    conv_score, conv_tier = _score_from_benchmark(rates["conversion_rate"], "conversion_rate")
    components.append({
        "name": "Conversion rate",
        "score": round(conv_score, 1),
        "tier": conv_tier,
        "value": f"{rates['conversion_rate']:.2f}%"
    })
    weighted_sum += conv_score * 20
    total_weight += 20

    creative_total = round(weighted_sum / total_weight, 1)
    return {
        "score": min(100, creative_total),
        "grade": _score_to_grade(creative_total),
        "components": components,
    }


def compute_roas(m: dict) -> dict:
    """ROAS = Revenue / Ad Spend."""
    spend = m.get("ad_spend", 0) or 0
    revenue = m.get("revenue", 0) or 0
    if spend <= 0:
        return {
            "roas": 0.0,
            "formatted": "—",
            "tier": "unknown",
            "label": "No spend",
            "revenue": revenue,
            "spend": spend,
        }
    roas = revenue / spend
    _, tier = _score_from_benchmark(roas, "roas")
    labels = {
        "excellent": "Excellent",
        "good": "Good",
        "average": "Average",
        "below_average": "Below average",
        "poor": "Poor",
        "unknown": "—",
    }
    return {
        "roas": round(roas, 2),
        "formatted": f"{roas:.2f}x",
        "tier": tier,
        "label": labels.get(tier, tier),
        "revenue": revenue,
        "spend": spend,
    }


def compute_ad_score(creative_result: dict, roas_result: dict) -> dict:
    """Overall ad score: 50% creative, 50% ROAS."""
    creative_score = creative_result.get("score", 0)
    roas = roas_result.get("roas", 0)
    roas_score, _ = _score_from_benchmark(roas, "roas") if roas else (0, "unknown")
    combined = 0.5 * creative_score + 0.5 * roas_score
    return {
        "score": round(min(100, combined), 1),
        "grade": _score_to_grade(combined),
        "creative_contribution": round(creative_score, 1),
        "roas_contribution": round(roas_score, 1),
    }


def _score_to_grade(score: float) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def generate_improvements(m: dict, rates: dict, creative_result: dict, roas_result: dict) -> List[dict]:
    """Generate prioritized improvement suggestions."""
    suggestions = []
    spend = m.get("ad_spend", 0) or 0
    imp = m.get("impressions", 0) or 0

    if roas_result.get("tier") in ("poor", "below_average") and spend > 0:
        suggestions.append({
            "priority": "high",
            "category": "ROAS",
            "title": "Improve return on ad spend",
            "detail": f"Current ROAS is {roas_result.get('formatted', '—')}. Consider tightening audience targeting, testing lower-funnel creatives, or improving landing page conversion.",
            "metric": "ROAS",
        })

    if rates["ctr"] < BENCHMARKS["ctr"]["avg"] and imp > 100:
        suggestions.append({
            "priority": "high",
            "category": "Creative",
            "title": "Boost click-through rate",
            "detail": "CTR is below benchmark. Try a stronger hook in the first line, clearer value proposition, or a more direct call-to-action.",
            "metric": "CTR",
        })

    if rates["engagement_rate"] < BENCHMARKS["engagement_rate"]["avg"] and imp > 100:
        suggestions.append({
            "priority": "medium",
            "category": "Creative",
            "title": "Increase engagement",
            "detail": "Engagement rate is low. Test more relatable or emotional creatives, questions in the copy, or formats that invite interaction.",
            "metric": "Engagement",
        })

    if imp > 100 and rates["conversion_rate"] < BENCHMARKS["conversion_rate"]["avg"]:
        suggestions.append({
            "priority": "high",
            "category": "Conversion",
            "title": "Improve conversion rate",
            "detail": "Conversions are below benchmark. Align ad message with landing page, simplify the form or checkout, and ensure mobile experience is smooth.",
            "metric": "CVR",
        })

    has_video = m.get("has_video", False) and (m.get("video_views") or 0) > 0
    if has_video and rates.get("video_completion_100", 0) < BENCHMARKS["video_completion"]["avg"]:
        suggestions.append({
            "priority": "medium",
            "category": "Creative",
            "title": "Improve video completion",
            "detail": "Viewers are dropping off. Front-load the key message in the first 3 seconds and keep the video under 15 seconds for top-of-funnel.",
            "metric": "Video completion",
        })

    copy_len = len((m.get("headline") or "") + (m.get("primary_text") or ""))
    if 0 < copy_len < 30:
        suggestions.append({
            "priority": "medium",
            "category": "Creative",
            "title": "Add more context in copy",
            "detail": "Short copy can underperform. Add one clear benefit or social proof to improve relevance and trust.",
            "metric": "Copy",
        })

    if not (m.get("cta") or "").strip():
        suggestions.append({
            "priority": "medium",
            "category": "Creative",
            "title": "Use a clear call-to-action",
            "detail": "A visible CTA (e.g. Shop Now, Sign Up, Learn More) can improve CTR and conversion.",
            "metric": "CTA",
        })

    order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda x: (order.get(x["priority"], 2), x["category"]))
    return suggestions


def run_analysis(metrics: dict) -> dict:
    """Run full analysis: creative score, ad score, ROAS, improvements."""
    rates = _compute_rates(metrics)
    creative_result = compute_creative_score(metrics, rates)
    roas_result = compute_roas(metrics)
    ad_score_result = compute_ad_score(creative_result, roas_result)
    improvements = generate_improvements(metrics, rates, creative_result, roas_result)

    return {
        "creative_score": creative_result,
        "ad_score": ad_score_result,
        "roas": roas_result,
        "improvements": improvements,
        "metrics": {
            "impressions": metrics.get("impressions", 0),
            "clicks": metrics.get("clicks", 0),
            "engagements": metrics.get("engagements", 0),
            "conversions": metrics.get("conversions", 0),
            "spend": metrics.get("ad_spend", 0),
            "revenue": metrics.get("revenue", 0),
            **rates,
        },
    }
