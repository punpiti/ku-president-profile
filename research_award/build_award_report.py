from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV = BASE_DIR / "extracted_award_data.csv"
OUTPUT_HTML = BASE_DIR / "award_insights_report.html"
OUTPUT_METRICS_CSV = BASE_DIR / "annual_award_metrics.csv"

PALETTE = {
    "teal": "#0f766e",
    "blue": "#2563eb",
    "orange": "#ea580c",
    "red": "#dc2626",
    "gold": "#a16207",
    "slate": "#334155",
    "mint": "#14b8a6",
    "violet": "#7c3aed",
    "rose": "#e11d48",
    "ink": "#0f172a",
    "bg": "#f8fafc",
    "panel": "#ffffff",
    "line": "#cbd5e1",
}


def pct_change(start: float, end: float) -> float:
    return (end / start - 1) * 100


def cagr(start: float, end: float, periods: int) -> float:
    return ((end / start) ** (1 / periods) - 1) * 100


def multiple(start: float, end: float) -> float:
    return end / start


def fig_to_html(fig: go.Figure, include_js: bool = False) -> str:
    return fig.to_html(full_html=False, include_plotlyjs="cdn" if include_js else False)


def metric_card(title: str, value: str, note: str) -> str:
    return f"""
    <div class="metric-card">
      <div class="metric-title">{title}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-note">{note}</div>
    </div>
    """


def section_block(title: str, body: str, chart_html: str, section_id: str) -> str:
    return f"""
    <section class="insight-block" id="{section_id}">
      <div class="insight-copy">
        <h3>{title}</h3>
        {body}
      </div>
      <div class="chart-wrap">
        {chart_html}
      </div>
    </section>
    """


def summary_reference(label: str, target_ids: list[str]) -> str:
    del target_ids
    return f'<span class="graph-cite">{label}</span>'


def build_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["award_share_pct"] = out["award_articles"] / out["scopus_articles_total"] * 100
    out["award_amount_researcher_baht_m"] = out["award_amount_researcher_baht"] / 1_000_000
    out["award_amount_full_baht_m"] = out["award_amount_full_baht"] / 1_000_000
    out["ku_total_research_funding_baht_b"] = out["ku_total_research_funding_baht"] / 1_000_000_000
    out["articles_per_researcher"] = out["award_articles"] / out["award_researchers_count"]
    out["avg_award_per_article_k"] = out["award_amount_researcher_baht"] / out["award_articles"] / 1000
    out["avg_award_per_researcher_k"] = (
        out["award_amount_researcher_baht"] / out["award_researchers_count"] / 1000
    )
    out["award_articles_index"] = out["award_articles"] / out["award_articles"].iloc[0] * 100
    out["ku_total_research_funding_index"] = (
        out["ku_total_research_funding_baht"] / out["ku_total_research_funding_baht"].iloc[0] * 100
    )
    out["award_articles_yoy_pct"] = out["award_articles"].pct_change() * 100
    out["award_amount_researcher_yoy_pct"] = out["award_amount_researcher_baht"].pct_change() * 100

    out["total_to_award_ratio"] = out["scopus_articles_total"] / out["award_articles"]
    out["reward_million_baht"] = out["award_amount_researcher_baht"] / 1_000_000
    out["awarded_articles_per_million_reward"] = out["award_articles"] / out["reward_million_baht"]
    out["total_articles_per_million_reward"] = out["scopus_articles_total"] / out["reward_million_baht"]
    out["reward_per_awarded_article_baht"] = out["award_amount_researcher_baht"] / out["award_articles"]
    out["reward_per_total_article_baht"] = out["award_amount_researcher_baht"] / out["scopus_articles_total"]
    out["full_reward_per_total_article_baht"] = out["award_amount_full_baht"] / out["scopus_articles_total"]
    out["researchers_yoy_change"] = out["award_researchers_count"].diff()
    out["researchers_yoy_pct"] = out["award_researchers_count"].pct_change() * 100
    out["awarded_articles_per_awarded_researcher"] = (
        out["award_articles"] / out["award_researchers_count"]
    )
    out["total_articles_per_awarded_researcher"] = (
        out["scopus_articles_total"] / out["award_researchers_count"]
    )
    return out


def style_fig(fig: go.Figure) -> go.Figure:
    fig.update_layout(font=dict(family="Arial, sans-serif", color=PALETTE["ink"]))
    return fig


def build_overview_figures(df: pd.DataFrame) -> dict[str, go.Figure]:
    years = df["year_be"]

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=years, y=df["award_articles"], mode="lines+markers", name="บทความที่ได้รางวัล", line=dict(color=PALETTE["teal"], width=3)))
    fig1.add_trace(go.Scatter(x=years, y=df["scopus_articles_total"], mode="lines+markers", name="บทความ Scopus ทั้งหมด", line=dict(color=PALETTE["blue"], width=3)))
    fig1.update_layout(title="บทความที่ได้รางวัลเติบโตเร็วกว่าบทความ Scopus ทั้งหมด", template="plotly_white", hovermode="x unified", margin=dict(l=40, r=20, t=60, b=40), legend=dict(orientation="h"))
    fig1.update_xaxes(dtick=1)
    fig1.update_yaxes(title="จำนวนบทความ")

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=years, y=df["award_share_pct"], mode="lines+markers", fill="tozeroy", name="สัดส่วนบทความที่ได้รางวัล", line=dict(color=PALETTE["red"], width=3)))
    fig2.update_layout(title="สัดส่วนบทความ Scopus ที่ได้รับรางวัล", template="plotly_white", hovermode="x unified", margin=dict(l=40, r=20, t=60, b=40))
    fig2.update_xaxes(dtick=1)
    fig2.update_yaxes(title="ร้อยละ", ticksuffix="%")

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=years, y=df["award_amount_researcher_baht_m"], name="งบรางวัลนักวิจัย", marker_color=PALETTE["orange"]))
    fig3.add_trace(go.Scatter(x=years, y=df["award_amount_full_baht_m"], mode="lines+markers", name="งบรวมเต็มรูปแบบ", line=dict(color=PALETTE["violet"], width=3)))
    fig3.update_layout(title="งบเงินรางวัลเติบโตเร็วกว่าจำนวนบทความที่ได้รางวัล", template="plotly_white", hovermode="x unified", margin=dict(l=40, r=20, t=60, b=40), legend=dict(orientation="h"))
    fig3.update_xaxes(dtick=1)
    fig3.update_yaxes(title="ล้านบาท")

    fig4 = make_subplots(specs=[[{"secondary_y": True}]])
    fig4.add_trace(go.Bar(x=years[1:], y=df["award_articles_yoy_pct"].iloc[1:], name="การเติบโตของบทความรางวัลจากปีก่อน", marker_color=PALETTE["mint"]), secondary_y=False)
    fig4.add_trace(go.Scatter(x=years[1:], y=df["award_amount_researcher_yoy_pct"].iloc[1:], mode="lines+markers", name="การเติบโตของงบรางวัลจากปีก่อน", line=dict(color=PALETTE["rose"], width=3)), secondary_y=True)
    fig4.add_vline(x=2553, line_dash="dot", line_color=PALETTE["gold"])
    fig4.add_vline(x=2559, line_dash="dot", line_color=PALETTE["slate"])
    fig4.update_layout(title="จุดเปลี่ยนสำคัญ: พุ่งแรงในปี 2553 และชะลอในปี 2559", template="plotly_white", hovermode="x unified", margin=dict(l=40, r=20, t=60, b=40), legend=dict(orientation="h"))
    fig4.update_xaxes(dtick=1)
    fig4.update_yaxes(title_text="บทความรางวัลจากปีก่อน (%)", secondary_y=False)
    fig4.update_yaxes(title_text="งบรางวัลจากปีก่อน (%)", secondary_y=True)

    fig5 = make_subplots(specs=[[{"secondary_y": True}]])
    fig5.add_trace(go.Bar(x=years, y=df["award_researchers_count"], name="จำนวนผู้ได้รับรางวัล", marker_color=PALETTE["mint"]), secondary_y=False)
    fig5.add_trace(go.Scatter(x=years, y=df["articles_per_researcher"], mode="lines+markers", name="บทความรางวัลต่อคน", line=dict(color=PALETTE["teal"], width=3)), secondary_y=True)
    fig5.update_layout(title="จำนวนผู้ได้รับรางวัลเพิ่มขึ้น ขณะที่ผลผลิตต่อคนเพิ่มแบบค่อยเป็นค่อยไป", template="plotly_white", hovermode="x unified", margin=dict(l=40, r=20, t=60, b=40), legend=dict(orientation="h"))
    fig5.update_xaxes(dtick=1)
    fig5.update_yaxes(title_text="จำนวนคน", secondary_y=False)
    fig5.update_yaxes(title_text="บทความรางวัลต่อคน", secondary_y=True)

    fig6 = make_subplots(specs=[[{"secondary_y": True}]])
    fig6.add_trace(go.Scatter(x=years, y=df["award_articles_index"], mode="lines+markers", name="ดัชนีบทความรางวัล", line=dict(color=PALETTE["teal"], width=3)), secondary_y=False)
    fig6.add_trace(go.Scatter(x=years, y=df["ku_total_research_funding_index"], mode="lines+markers", name="ดัชนีทุนวิจัยรวม", line=dict(color=PALETTE["gold"], width=3, dash="dash")), secondary_y=False)
    fig6.add_trace(go.Scatter(x=years, y=df["ku_total_research_funding_baht_b"], mode="lines+markers", name="ทุนวิจัยรวม (พันล้านบาท)", line=dict(color=PALETTE["slate"], width=2, dash="dot")), secondary_y=True)
    fig6.update_layout(title="ผลผลิตเติบโตเร็วกว่าทุนวิจัยรวมอย่างชัดเจน", template="plotly_white", hovermode="x unified", margin=dict(l=40, r=20, t=60, b=40), legend=dict(orientation="h"))
    fig6.update_xaxes(dtick=1)
    fig6.update_yaxes(title_text="ดัชนี (2551 = 100)", secondary_y=False)
    fig6.update_yaxes(title_text="พันล้านบาท", secondary_y=True)

    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(x=df["ku_total_research_funding_baht_b"], y=df["award_articles"], mode="markers+text", text=df["year_be"].astype(str), textposition="top center", marker=dict(size=12, color=df["year_be"], colorscale="Tealgrn", line=dict(width=1, color="white")), name="ปี"))
    fig7.update_layout(title="ความสัมพันธ์ระหว่างทุนวิจัยรวมกับบทความรางวัลค่อนข้างอ่อน", template="plotly_white", margin=dict(l=40, r=20, t=60, b=40))
    fig7.update_xaxes(title="ทุนวิจัยรวม (พันล้านบาท)")
    fig7.update_yaxes(title="บทความที่ได้รางวัล")

    fig8 = make_subplots(specs=[[{"secondary_y": True}]])
    fig8.add_trace(go.Scatter(x=years, y=df["avg_award_per_article_k"], mode="lines+markers", name="เงินรางวัลเฉลี่ยต่อบทความ", line=dict(color=PALETTE["orange"], width=3)), secondary_y=False)
    fig8.add_trace(go.Scatter(x=years, y=df["avg_award_per_researcher_k"], mode="lines+markers", name="เงินรางวัลเฉลี่ยต่อคน", line=dict(color=PALETTE["violet"], width=3)), secondary_y=True)
    fig8.update_layout(title="มูลค่าเงินรางวัลต่อบทความและต่อคนสูงขึ้นตามเวลา", template="plotly_white", hovermode="x unified", margin=dict(l=40, r=20, t=60, b=40), legend=dict(orientation="h"))
    fig8.update_xaxes(dtick=1)
    fig8.update_yaxes(title_text="พันบาทต่อบทความ", secondary_y=False)
    fig8.update_yaxes(title_text="พันบาทต่อคน", secondary_y=True)

    return {k: style_fig(v) for k, v in {
        "volume": fig1, "share": fig2, "budget": fig3, "turning": fig4,
        "people": fig5, "funding_gap": fig6, "scatter": fig7, "unit_value": fig8,
    }.items()}


def build_annual_figures(df: pd.DataFrame) -> dict[str, go.Figure]:
    years = df["year_be"]

    ratio_fig = make_subplots(specs=[[{"secondary_y": True}]])
    ratio_fig.add_trace(go.Bar(x=years, y=df["total_to_award_ratio"], name="บทความทั้งหมด / บทความได้รางวัล", marker_color=PALETTE["blue"]), secondary_y=False)
    ratio_fig.add_trace(go.Scatter(x=years, y=df["award_share_pct"], mode="lines+markers", name="สัดส่วนบทความที่ได้รางวัล", line=dict(color=PALETTE["red"], width=3)), secondary_y=True)
    ratio_fig.update_layout(title="อัตราบทความทั้งหมดต่อบทความที่ได้รางวัล", template="plotly_white", hovermode="x unified", margin=dict(l=40, r=20, t=60, b=40), legend=dict(orientation="h"))
    ratio_fig.update_xaxes(dtick=1)
    ratio_fig.update_yaxes(title_text="Ratio (เท่า)", secondary_y=False)
    ratio_fig.update_yaxes(title_text="สัดส่วนบทความที่ได้รางวัล (%)", secondary_y=True)

    efficiency_fig = make_subplots(specs=[[{"secondary_y": True}]])
    efficiency_fig.add_trace(go.Scatter(x=years, y=df["awarded_articles_per_million_reward"], mode="lines+markers", name="บทความได้รางวัลต่อ 1 ล้านบาท", line=dict(color=PALETTE["teal"], width=3)), secondary_y=False)
    efficiency_fig.add_trace(go.Scatter(x=years, y=df["total_articles_per_million_reward"], mode="lines+markers", name="บทความรวมต่อ 1 ล้านบาท", line=dict(color=PALETTE["orange"], width=3)), secondary_y=False)
    efficiency_fig.add_trace(go.Bar(x=years, y=df["reward_million_baht"], name="งบรางวัลนักวิจัย", marker_color=PALETTE["mint"], opacity=0.35), secondary_y=True)
    efficiency_fig.update_layout(title="ประสิทธิภาพของเงินรางวัลในการสร้างบทความ", template="plotly_white", hovermode="x unified", margin=dict(l=40, r=20, t=60, b=40), legend=dict(orientation="h"))
    efficiency_fig.update_xaxes(dtick=1)
    efficiency_fig.update_yaxes(title_text="บทความต่อ 1 ล้านบาท", secondary_y=False)
    efficiency_fig.update_yaxes(title_text="งบรางวัล (ล้านบาท)", secondary_y=True)

    cost_fig = go.Figure()
    cost_fig.add_trace(go.Scatter(x=years, y=df["reward_per_total_article_baht"], mode="lines+markers", name="รางวัลนักวิจัย / บทความรวม", line=dict(color=PALETTE["gold"], width=3)))
    cost_fig.add_trace(go.Scatter(x=years, y=df["full_reward_per_total_article_baht"], mode="lines+markers", name="ค่าใช้จ่ายรวม / บทความรวม", line=dict(color=PALETTE["violet"], width=3)))
    cost_fig.update_layout(title="ค่าใช้จ่ายต่อจำนวนเปเปอร์รวม", template="plotly_white", hovermode="x unified", margin=dict(l=40, r=20, t=60, b=40), legend=dict(orientation="h"))
    cost_fig.update_xaxes(dtick=1)
    cost_fig.update_yaxes(title="บาทต่อบทความรวม")

    people_fig = make_subplots(specs=[[{"secondary_y": True}]])
    people_fig.add_trace(go.Bar(x=years[1:], y=df["researchers_yoy_change"].iloc[1:], name="เพิ่มขึ้นจากปีก่อน (คน)", marker_color=PALETTE["mint"]), secondary_y=False)
    people_fig.add_trace(go.Scatter(x=years[1:], y=df["researchers_yoy_pct"].iloc[1:], mode="lines+markers", name="อัตราเพิ่มขึ้น (%)", line=dict(color=PALETTE["rose"], width=3)), secondary_y=True)
    people_fig.update_layout(title="จำนวนคนตีพิมพ์เพิ่มในแต่ละปี", template="plotly_white", hovermode="x unified", margin=dict(l=40, r=20, t=60, b=40), legend=dict(orientation="h"))
    people_fig.update_xaxes(dtick=1)
    people_fig.update_yaxes(title_text="จำนวนคนเพิ่มขึ้น", secondary_y=False)
    people_fig.update_yaxes(title_text="อัตราเพิ่มขึ้น (%)", secondary_y=True)

    per_person_fig = make_subplots(specs=[[{"secondary_y": True}]])
    per_person_fig.add_trace(go.Scatter(x=years, y=df["awarded_articles_per_awarded_researcher"], mode="lines+markers", name="บทความได้รางวัลต่อคน", line=dict(color=PALETTE["teal"], width=3)), secondary_y=False)
    per_person_fig.add_trace(go.Scatter(x=years, y=df["total_articles_per_awarded_researcher"], mode="lines+markers", name="บทความรวมต่อคน", line=dict(color=PALETTE["blue"], width=3)), secondary_y=True)
    per_person_fig.update_layout(title="การตีพิมพ์รวมและได้รางวัลต่อคน", template="plotly_white", hovermode="x unified", margin=dict(l=40, r=20, t=60, b=40), legend=dict(orientation="h"))
    per_person_fig.update_xaxes(dtick=1)
    per_person_fig.update_yaxes(title_text="บทความได้รางวัลต่อคน", secondary_y=False)
    per_person_fig.update_yaxes(title_text="บทความรวมต่อคน", secondary_y=True)

    return {k: style_fig(v) for k, v in {
        "ratio": ratio_fig, "efficiency": efficiency_fig, "cost": cost_fig,
        "people": people_fig, "per_person": per_person_fig,
    }.items()}


def build_metrics_table(df: pd.DataFrame) -> str:
    display = df[[
        "year_be", "total_to_award_ratio", "award_share_pct",
        "awarded_articles_per_million_reward", "total_articles_per_million_reward",
        "full_reward_per_total_article_baht", "researchers_yoy_change",
        "awarded_articles_per_awarded_researcher", "total_articles_per_awarded_researcher",
    ]].copy()
    display.columns = [
        "ปี", "บทความรวม/บทความรางวัล", "สัดส่วนบทความที่ได้รางวัล (%)", "บทความรางวัลต่อ 1 ล้านบาท",
        "บทความรวมต่อ 1 ล้านบาท", "ค่าใช้จ่ายรวมต่อบทความรวม (บาท)", "คนเพิ่มจากปีก่อน",
        "บทความรางวัลต่อคน", "บทความรวมต่อคน",
    ]
    display["คนเพิ่มจากปีก่อน"] = display["คนเพิ่มจากปีก่อน"].fillna(0)
    return display.to_html(index=False, classes="metrics-table", border=0, justify="center", float_format=lambda x: f"{x:,.2f}")


def build_raw_data_table(df: pd.DataFrame) -> str:
    raw = df[[
        "year_be",
        "award_articles",
        "scopus_articles_total",
        "award_amount_researcher_baht",
        "award_amount_full_baht",
        "award_researchers_count",
        "ku_total_research_funding_baht",
    ]].copy()
    raw.columns = [
        "ปี",
        "บทความที่ได้รางวัล",
        "บทความ Scopus ทั้งหมด",
        "งบรางวัลนักวิจัย (บาท)",
        "ค่าใช้จ่ายรวมเต็มรูปแบบ (บาท)",
        "จำนวนผู้ได้รับรางวัล",
        "ทุนวิจัยรวม (บาท)",
    ]
    return raw.to_html(
        index=False,
        classes="metrics-table",
        border=0,
        justify="center",
        float_format=lambda x: f"{x:,.2f}",
    )


def export_metrics_csv(df: pd.DataFrame) -> None:
    df[[
        "year_be", "total_to_award_ratio", "award_share_pct", "awarded_articles_per_million_reward",
        "total_articles_per_million_reward", "reward_per_awarded_article_baht", "reward_per_total_article_baht",
        "full_reward_per_total_article_baht", "researchers_yoy_change", "researchers_yoy_pct",
        "awarded_articles_per_awarded_researcher", "total_articles_per_awarded_researcher",
    ]].to_csv(OUTPUT_METRICS_CSV, index=False)


def main() -> None:
    df = build_derived_metrics(pd.read_csv(INPUT_CSV))
    export_metrics_csv(df)
    overview = build_overview_figures(df)
    annual = build_annual_figures(df)
    table_html = build_metrics_table(df)
    raw_table_html = build_raw_data_table(df)

    first = df.iloc[0]
    last = df.iloc[-1]
    periods = len(df) - 1
    corr = df["award_articles"].corr(df["ku_total_research_funding_baht"])
    best_people_year = int(df.loc[df["researchers_yoy_change"].idxmax(), "year_be"])
    best_people_change = int(df["researchers_yoy_change"].max())
    best_efficiency_year = int(df.loc[df["awarded_articles_per_million_reward"].idxmax(), "year_be"])
    lowest_cost_year = int(df.loc[df["full_reward_per_total_article_baht"].idxmin(), "year_be"])

    overview_cards = "".join([
        metric_card("บทความที่ได้รางวัล", f"{multiple(first['award_articles'], last['award_articles']):.1f} เท่า", f"เพิ่มสุทธิ {int(last['award_articles'] - first['award_articles']):,} บทความ และโตเฉลี่ย {cagr(first['award_articles'], last['award_articles'], periods):.1f}% ต่อปี"),
        metric_card("สัดส่วนบทความที่ได้รางวัล", f"{last['award_share_pct']:.1f}%", f"จาก {first['award_share_pct']:.1f}% ในปี {int(first['year_be'])}"),
        metric_card("งบรางวัลนักวิจัย", f"{multiple(first['award_amount_researcher_baht'], last['award_amount_researcher_baht']):.1f} เท่า", f"จาก {first['award_amount_researcher_baht_m']:.2f} เป็น {last['award_amount_researcher_baht_m']:.2f} ล้านบาท"),
        metric_card("จำนวนผู้ได้รับรางวัล", f"{multiple(first['award_researchers_count'], last['award_researchers_count']):.1f} เท่า", f"จาก {int(first['award_researchers_count'])} เป็น {int(last['award_researchers_count'])} คน"),
        metric_card("ทุนวิจัยรวม", f"{multiple(first['ku_total_research_funding_baht'], last['ku_total_research_funding_baht']):.2f} เท่า", "เติบโตช้ากว่าผลผลิตอย่างชัดเจน"),
        metric_card("ความสัมพันธ์ทุนกับผลงาน", f"{corr:.2f}", "ค่าใกล้ศูนย์ สะท้อนความสัมพันธ์เชิงเส้นที่อ่อน"),
    ])

    annual_cards = "".join([
        metric_card("สัดส่วนบทความรางวัลล่าสุด", f"{last['award_share_pct']:.1f}%", f"จาก {first['award_share_pct']:.1f}% ในปี {int(first['year_be'])}"),
        metric_card("บทความรวม/บทความรางวัล", f"{last['total_to_award_ratio']:.2f} เท่า", "ยิ่งต่ำ แปลว่าสัดส่วนบทความที่ได้รางวัลยิ่งสูง"),
        metric_card("ประสิทธิภาพสูงสุด", f"ปี {best_efficiency_year}", "วัดจากบทความได้รางวัลต่อ 1 ล้านบาทของงบรางวัลนักวิจัย"),
        metric_card("ต้นทุนต่อเปเปอร์ต่ำสุด", f"ปี {lowest_cost_year}", "วัดจากค่าใช้จ่ายรวมต่อบทความรวม"),
        metric_card("คนเพิ่มสูงสุด", f"+{best_people_change} คน", f"เกิดในปี {best_people_year}"),
        metric_card("ข้อจำกัดข้อมูล", "ใช้ผู้ได้รางวัลเป็นตัวแทน", "ไม่มีจำนวนผู้ตีพิมพ์รวมทั้งระบบในไฟล์นี้"),
    ])

    overview_sections = [
        section_block("1. ผลงานที่ได้รางวัลโตเร็วกว่าปริมาณบทความ Scopus", f"<p>บทความที่ได้รางวัลเพิ่มจาก {int(first['award_articles']):,} เป็น {int(last['award_articles']):,} บทความ หรือ {pct_change(first['award_articles'], last['award_articles']):.1f}% ขณะที่บทความ Scopus ทั้งหมดเพิ่ม {pct_change(first['scopus_articles_total'], last['scopus_articles_total']):.1f}%.</p><p>นัยสำคัญคือการเติบโตไม่ได้มาจากฐานบทความรวมอย่างเดียว แต่เกิดจากสัดส่วนผลงานที่เข้าเกณฑ์รางวัลมากขึ้นด้วย จึงตีความได้ว่าระบบรางวัลสัมพันธ์กับการยกระดับคุณสมบัติของผลงานในระบบ ไม่ใช่แค่การผลิตปริมาณ.</p><p>ข้อพึงปฏิบัติคือควรติดตามเส้นสองชุดนี้ควบคู่กันเสมอ เพราะถ้าบทความรวมยังโตแต่บทความรางวัลชะลอ จะสะท้อนว่าคุณภาพหรือการเข้าเกณฑ์เริ่มอ่อนลง ส่วนข้อควรระวังคือกราฟนี้บอกทิศทางของผลลัพธ์ แต่ยังไม่ได้พิสูจน์ว่าสาเหตุทั้งหมดมาจากรางวัลเพียงปัจจัยเดียว.</p>", fig_to_html(overview["volume"], include_js=True), "overview-volume"),
        section_block("2. สัดส่วนบทความที่ได้รางวัลต่อ Scopus สูงขึ้นต่อเนื่อง", f"<p>สัดส่วนบทความที่ได้รางวัลเพิ่มจาก {first['award_share_pct']:.1f}% เป็น {last['award_share_pct']:.1f}% และแตะจุดสูงสุดในปี {int(last['year_be'])}.</p><p>ผลกระทบเชิงนโยบายคือระบบรางวัลดูเหมือนจะไม่ได้เพียงเพิ่มจำนวนผลงาน แต่เพิ่มสัดส่วนของผลงานที่มีคุณลักษณะถึงเกณฑ์รางวัลด้วย ทำให้การใช้งบยังสะท้อนออกมาในรูปคุณภาพเชิงสัดส่วน ไม่ใช่แค่จำนวนดิบ.</p><p>ข้อพึงปฏิบัติคือควรใช้ตัวชี้วัดนี้เป็น KPI หลักร่วมกับจำนวนบทความ เพราะช่วยกันหลอกตัวเองจากการดูแต่ volume ส่วนข้อควรระวังคือหากเกณฑ์รางวัลเปลี่ยนในอนาคต ค่าชุดนี้อาจเปรียบเทียบข้ามปีได้ยากขึ้น.</p>", fig_to_html(overview["share"]), "overview-share"),
        section_block("3. งบเงินรางวัลขยายตัวเร็วกว่าจำนวนบทความ", f"<p>เงินรางวัลอาจารย์นักวิจัยเพิ่ม {pct_change(first['award_amount_researcher_baht'], last['award_amount_researcher_baht']):.1f}% เทียบกับบทความที่ได้รางวัลเพิ่ม {pct_change(first['award_articles'], last['award_articles']):.1f}%.</p><p>ความหมายตรงไปตรงมาคือเม็ดเงินเติบโตเร็วกว่าผลผลิต จึงบอกได้ว่าประสิทธิภาพของทุนต่อบทความอ่อนลงจากปีฐาน แม้ผลผลิตรวมยังขยายตัวแรงอยู่. อย่างไรก็ดี เมื่อดูประกอบกับกราฟต้นทุนต่อบทความ ระบบนี้ยังไม่ได้หลุดไปสู่ระดับที่ต้นทุนต่อเปเปอร์สูงผิดสัดส่วนในข้อมูลชุดนี้.</p><p>ข้อพึงปฏิบัติคือควรบริหารนโยบายให้โฟกัสทั้ง “ขยายผลผลิต” และ “คุมต้นทุนต่อผลผลิต” ไปพร้อมกัน ส่วนข้อควรระวังคือการเห็นงบโตแรงอาจทำให้สรุปว่าไม่มีประสิทธิภาพ ทั้งที่ในทางปฏิบัติระบบยังให้ผลลัพธ์จริงและต้นทุนต่อเปเปอร์ยังอยู่ในระดับรับได้.</p>", fig_to_html(overview["budget"]), "overview-budget"),
        section_block("4. จุดเปลี่ยนสำคัญอยู่ที่ปี 2553 และ 2559", "<p>ปี 2553 เป็นปีที่เร่งขึ้นแรงที่สุดทั้งจำนวนบทความและเม็ดเงินรางวัล ส่วนปี 2559 จำนวนบทความย่อลง แต่เงินรางวัลยังเพิ่มต่อ.</p><p>นี่สะท้อนว่าระบบไม่ได้ตอบสนองแบบเส้นตรงตลอดเวลา บางปีงบเพิ่มพร้อมผลลัพธ์เพิ่ม แต่บางปีงบยังขึ้นในขณะที่ผลลัพธ์ชะลอ จึงควรมองการเปลี่ยนแปลงแบบเป็นช่วงมากกว่ามองแบบปีเดียวแล้วสรุปนโยบายทันที.</p><p>ข้อพึงปฏิบัติคือเมื่อมีจุดเปลี่ยน ควรตรวจว่ามาจากฐานนักวิจัย เกณฑ์รางวัล หรือสภาพแวดล้อมการตีพิมพ์ในช่วงนั้น ส่วนข้อควรระวังคือไม่ควรใช้ปีที่ผิดปกติเพียงปีเดียวเป็นฐานตัดสินว่าจะเพิ่มหรือลดงบทันที.</p>", fig_to_html(overview["turning"]), "overview-turning"),
        section_block("5. ฐานผู้ได้รับรางวัลกว้างขึ้นมาก ขณะที่ productivity ต่อหัวเพิ่มแบบค่อยเป็นค่อยไป", f"<p>จำนวนนักวิจัยที่ได้รับรางวัลเพิ่มจาก {int(first['award_researchers_count'])} เป็น {int(last['award_researchers_count'])} คน หรือ {pct_change(first['award_researchers_count'], last['award_researchers_count']):.1f}%.</p><p>ผลกระทบเชิงบวกคือระบบรางวัลไม่ได้กระจุกอยู่กับคนกลุ่มเดิม แต่ดึงคนเข้าสู่ระบบได้มากขึ้น ขณะที่ผลผลิตต่อคนค่อยๆ สูงขึ้น จึงบอกได้ว่าการเติบโตช่วงหลังมาจากทั้งการขยายฐานคนและการเพิ่มผลผลิตรายคน แต่แรงขับหลักคือฐานคนที่กว้างขึ้น.</p><p>ข้อพึงปฏิบัติคือหากจะปรับงบ ควรถามก่อนว่าต้องการขยายฐานคนหรือเร่งผลงานต่อคน เพราะสองเป้าหมายนี้อาจต้องใช้กลไกต่างกัน ส่วนข้อควรระวังคือข้อมูลนี้ใช้ฐานผู้ได้รับรางวัล ไม่ใช่ผู้ตีพิมพ์ทั้งหมด จึงตีความเป็น productivity ของทั้งระบบไม่ได้.</p>", fig_to_html(overview["people"]), "overview-people"),
        section_block("6. ผลผลิตเติบโตไกลกว่าทุนวิจัยรวมของมหาวิทยาลัย", f"<p>ถ้าตั้งปี {int(first['year_be'])} = 100 จะเห็นว่าดัชนีบทความรางวัลขึ้นไปเหนือ 600 แต่ทุนวิจัยรวมขยับเพียงราว {100 + pct_change(first['ku_total_research_funding_baht'], last['ku_total_research_funding_baht']):.1f}.</p><p>นัยสำคัญคือ output ด้านตีพิมพ์และระบบรางวัลขยายตัวเร็วมากเมื่อเทียบกับทรัพยากรวิจัยรวมที่รายงานไว้ จึงพออ่านได้ว่าการเพิ่มผลงานไม่ได้เดินตามทุนวิจัยรวมแบบหนึ่งต่อหนึ่ง.</p><p>ข้อพึงปฏิบัติคือควรติดตามนโยบายรางวัลแยกจากนโยบายทุนวิจัยรวม เพราะสองเรื่องนี้ดูจะทำหน้าที่ต่างกันในข้อมูลชุดนี้ ส่วนข้อควรระวังคือไม่ควรแปลผลเกินไปว่า “ทุนวิจัยไม่สำคัญ” เพราะกราฟนี้เพียงชี้ว่าความเร็วของการเติบโตต่างกัน.</p>", fig_to_html(overview["funding_gap"]), "overview-funding-gap"),
        section_block("7. ความสัมพันธ์ระหว่างทุนวิจัยรวมกับบทความที่ได้รางวัลค่อนข้างอ่อน", f"<p>ค่าสหสัมพันธ์เชิงเส้นระหว่างทุนวิจัยรวมกับบทความที่ได้รางวัลอยู่ที่ {corr:.2f}.</p><p>เมื่อดูคู่กับกราฟดัชนีและกราฟการเปลี่ยนแปลงรายปี จะเห็นว่าบทความรางวัลไม่ได้ขึ้นลงตามทุนวิจัยรวมอย่างเรียบง่าย จึงทำให้การใช้นโยบาย “เพิ่มทุนรวมแล้วหวังให้บทความรางวัลขึ้นอัตโนมัติ” ไม่ได้รับการสนับสนุนชัดจากข้อมูลนี้.</p><p>ข้อพึงปฏิบัติคือหากจะออกแบบนโยบายเพิ่มผลงานตีพิมพ์ ควรดูเครื่องมือเชิงแรงจูงใจและฐานคนควบคู่กับทุน ส่วนข้อควรระวังคือ correlation ต่ำไม่ได้แปลว่าไม่มีความเกี่ยวข้องเลย เพียงแปลว่าในชุดข้อมูลนี้ความสัมพันธ์เชิงเส้นตรงไม่ชัด.</p>", fig_to_html(overview["scatter"]), "overview-scatter"),
        section_block("8. มูลค่ารางวัลต่อบทความและต่อผู้ได้รับรางวัลสูงขึ้น", f"<p>ค่าเฉลี่ยเงินรางวัลต่อบทความเพิ่มจาก {df['avg_award_per_article_k'].iloc[0]:.1f} พันบาท เป็น {df['avg_award_per_article_k'].iloc[-1]:.1f} พันบาท และต่อผู้ได้รับรางวัลเพิ่มจาก {df['avg_award_per_researcher_k'].iloc[0]:.1f} พันบาท เป็น {df['avg_award_per_researcher_k'].iloc[-1]:.1f} พันบาท.</p><p>ผลกระทบคือระบบมีแรงจูงใจเชิงมูลค่ามากขึ้น ซึ่งช่วยให้เม็ดเงินรวมยังขึ้นต่อได้แม้บางปีจำนวนบทความไม่ได้เร่งตาม แต่ในอีกด้านหนึ่งก็เป็นเหตุผลว่าทำไมเงินโตเร็วกว่าผลผลิต.</p><p>ข้อพึงปฏิบัติคือควรกำกับการขึ้นของมูลค่ารางวัลให้สัมพันธ์กับผลลัพธ์ที่ต้องการจริง ส่วนข้อควรระวังคือหากมูลค่าต่อบทความขึ้นเร็วเกินไปโดยไม่คุมผลผลิต ระบบจะเสี่ยงต่อการเสียประสิทธิภาพเชิงทุนในระยะยาว.</p>", fig_to_html(overview["unit_value"]), "overview-unit-value"),
    ]

    annual_sections = [
        section_block("1. อัตราบทความทั้งหมดต่อบทความที่ได้รางวัล", f"<p>ตัวชี้วัดนี้ลดจาก {first['total_to_award_ratio']:.2f} เท่าในปี {int(first['year_be'])} เหลือ {last['total_to_award_ratio']:.2f} เท่าในปี {int(last['year_be'])}.</p><p>อัตราที่ลดลงแปลว่าสัดส่วนบทความที่ได้รางวัลดีขึ้นเรื่อยๆ จึงเป็นสัญญาณที่ดีกว่าการดูจำนวนบทความอย่างเดียว เพราะแสดงว่าผลงานรางวัลกินสัดส่วนมากขึ้นใน output ทั้งหมด.</p><p>ข้อควรระวังคือหากอัตรานี้หยุดลดหรือกลับเพิ่มขึ้น แม้บทความรวมยังโตอยู่ ก็อาจสะท้อนว่าระบบเริ่มผลิตปริมาณมากขึ้นแต่ไม่สามารถดันคุณภาพตามเกณฑ์รางวัลได้.</p>", fig_to_html(annual["ratio"]), "annual-ratio"),
        section_block("2. ประสิทธิภาพของเงินรางวัลในการตีพิมพ์", f"<p>มองงบรางวัลนักวิจัยเป็น input และดูว่าแต่ละ 1 ล้านบาทสร้างบทความได้รางวัลกี่ชิ้นและบทความรวมกี่ชิ้น โดยปีที่มีประสิทธิภาพสูงสุดคือปี {best_efficiency_year}.</p><p>กราฟนี้เป็นหัวใจของการคุยเรื่องความคุ้มค่า เพราะตอบได้ตรงว่าเมื่อเงินเพิ่มขึ้น ผลลัพธ์ต่อ 1 ล้านบาทดีขึ้นหรือแผ่วลง. ในข้อมูลนี้ประสิทธิภาพไม่ได้ทรงตัว แต่มีแนวโน้มอ่อนลงจากช่วงต้น แม้ผลลัพธ์รวมยังเพิ่ม.</p><p>ข้อพึงปฏิบัติคือถ้าจะเพิ่มงบ ควรตั้งเป้าควบคู่กับตัวชี้วัดบทความต่อ 1 ล้านบาท ไม่เช่นนั้นระบบอาจโตแบบใช้เงินมากขึ้นโดยได้ผลตอบแทนต่อเม็ดเงินน้อยลง.</p>", fig_to_html(annual["efficiency"]), "annual-efficiency"),
        section_block("3. ค่าใช้จ่ายรวมต่อจำนวนเปเปอร์รวม", "<p>เส้นสีม่วงคือค่าใช้จ่ายรวมแบบเต็มรูปแบบต่อบทความรวม ส่วนเส้นสีน้ำตาลคือเฉพาะรางวัลนักวิจัยต่อบทความรวม.</p><p>กราฟนี้ช่วยถ่วงดุลการมองเชิงลบจากการที่งบโตเร็วกว่าเปเปอร์ เพราะแม้ประสิทธิภาพเชิงทุนอ่อนลงจากปีฐาน แต่ต้นทุนต่อบทความรวมในข้อมูลชุดนี้ยังไม่สูงจนบอกว่าระบบไร้ความคุ้มค่า.</p><p>ข้อควรระวังคือควรเฝ้าดูเส้นนี้มากกว่าดูแต่งบรวม เพราะหากงบเพิ่มแต่ต้นทุนต่อบทความยังคุมได้ ระบบอาจยังสมเหตุสมผลในทางบริหาร.</p>", fig_to_html(annual["cost"]), "annual-cost"),
        section_block("4. จำนวนคนตีพิมพ์เพิ่มในแต่ละปี", f"<p>จากข้อมูลที่มี วัดได้เฉพาะจำนวนผู้ได้รับรางวัลที่เพิ่มขึ้นจากปีก่อน โดยจุดเพิ่มสูงสุดอยู่ในปี {best_people_year} ที่เพิ่ม {best_people_change} คน.</p><p>ความสำคัญของกราฟนี้คือช่วยแยกว่าแรงของระบบมาจากการดึงคนใหม่เข้ามา หรือจากการเร่งคนเดิมให้ผลิตมากขึ้น ซึ่งในข้อมูลนี้น้ำหนักดูจะเอนมาทางการขยายฐานคนค่อนข้างมาก.</p><p>ข้อพึงปฏิบัติคือถ้าต้องการเพิ่ม participation นี่คือกราฟที่ควรใช้ติดตามก่อน ส่วนข้อควรระวังคืออย่าอ่านแทนจำนวนผู้ตีพิมพ์ทั้งหมด เพราะตัวเลขนี้ครอบคลุมเฉพาะผู้ได้รับรางวัล.</p>", fig_to_html(annual["people"]), "annual-people"),
        section_block("5. การตีพิมพ์รวมและได้รางวัลต่อคน", "<p>ตัวหารของกราฟนี้คือจำนวนผู้ได้รับรางวัลในแต่ละปี จึงควรอ่านเป็น productivity ต่อผู้ได้รับรางวัล ไม่ใช่ productivity ต่อผู้ตีพิมพ์ทั้งหมด.</p><p>กราฟนี้มีประโยชน์มากเวลาออกแบบนโยบาย เพราะถ้าบทความต่อคนไม่ขึ้น แต่จำนวนคนขึ้น แปลว่าระบบทำงานผ่านการขยายฐานมากกว่าการเร่ง productivity รายคน. ถ้าต้องการผลักผลงานต่อหัวให้สูงขึ้น อาจต้องใช้มาตรการคนละแบบกับมาตรการขยายการมีส่วนร่วม.</p><p>ข้อควรระวังคือหากใช้กราฟนี้ผิดความหมาย จะทำให้สรุปสถานการณ์ของทั้งมหาวิทยาลัยแรงเกินข้อมูลที่มีอยู่จริง.</p>", fig_to_html(annual["per_person"]), "annual-per-person"),
    ]

    html = f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>รายงานวิเคราะห์แนวโน้มรางวัลตีพิมพ์ มก. 2551-2566</title>
  <style>
    :root {{
      --bg: {PALETTE["bg"]}; --panel: {PALETTE["panel"]}; --ink: {PALETTE["ink"]}; --muted: {PALETTE["slate"]}; --line: {PALETTE["line"]};
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: Arial, sans-serif; color: var(--ink);
      background: radial-gradient(circle at top left, rgba(20,184,166,.10), transparent 28%), radial-gradient(circle at top right, rgba(37,99,235,.08), transparent 24%), linear-gradient(180deg, #f8fafc 0%, #eef6f7 100%);
    }}
    .page {{ max-width: 1240px; margin: 0 auto; padding: 32px 20px 64px; }}
    .hero {{ background: linear-gradient(135deg, rgba(15,118,110,.96), rgba(12,74,110,.92)); color: white; border-radius: 24px; padding: 32px; box-shadow: 0 24px 50px rgba(15, 23, 42, .12); }}
    .hero h1 {{ margin: 0 0 8px; font-size: 34px; line-height: 1.15; }}
    .hero p {{ margin: 0; max-width: 920px; font-size: 17px; line-height: 1.6; color: rgba(255,255,255,.9); }}
    .section-title {{ margin: 30px 0 14px; font-size: 22px; }}
    .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-top: 20px; }}
    .metric-card {{ background: var(--panel); border: 1px solid rgba(255,255,255,.7); border-radius: 18px; padding: 18px; box-shadow: 0 10px 30px rgba(15, 23, 42, .06); }}
    .metric-title {{ color: var(--muted); font-size: 13px; text-transform: uppercase; letter-spacing: .06em; }}
    .metric-value {{ margin-top: 10px; font-size: 28px; font-weight: 700; }}
    .metric-note {{ margin-top: 6px; font-size: 14px; line-height: 1.45; color: var(--muted); }}
    .summary {{ margin-top: 18px; background: rgba(255,255,255,.75); border: 1px solid rgba(203,213,225,.85); border-radius: 18px; padding: 18px 20px; line-height: 1.7; }}
    .summary h3 {{ margin: 0 0 8px; font-size: 18px; }}
    .summary p {{ margin: 0 0 12px; }}
    .summary p:last-child {{ margin-bottom: 0; }}
    .summary blockquote {{
      margin: 14px 0;
      padding: 14px 18px;
      border-left: 4px solid #0f766e;
      background: rgba(240,253,250,.9);
      color: #0f172a;
      font-size: 18px;
      line-height: 1.55;
      font-weight: 700;
      border-radius: 12px;
    }}
    .qa-list {{ margin: 14px 0 0; padding: 0; list-style: none; display: grid; gap: 12px; }}
    .qa-item {{ padding-top: 12px; border-top: 1px solid rgba(203,213,225,.9); }}
    .qa-q {{ margin: 0 0 6px; font-weight: 700; color: var(--ink); }}
    .qa-a {{ margin: 0; color: var(--muted); }}
    .graph-cite {{
      display: inline-block;
      color: #334155;
      font-weight: 700;
      border-bottom: 1px dotted rgba(51,65,85,.45);
    }}
    .insight-block {{ display: grid; grid-template-columns: minmax(280px, 360px) 1fr; gap: 18px; align-items: start; margin-top: 18px; padding: 18px; background: rgba(255,255,255,.82); border: 1px solid rgba(203,213,225,.8); border-radius: 22px; box-shadow: 0 10px 26px rgba(15, 23, 42, .05); }}
    .insight-copy h3 {{ margin: 0 0 10px; font-size: 21px; line-height: 1.3; }}
    .insight-copy p {{ margin: 0; color: var(--muted); line-height: 1.7; font-size: 15px; }}
    .chart-wrap {{ min-width: 0; background: white; border-radius: 16px; border: 1px solid rgba(226,232,240,.9); padding: 6px; }}
    .table-wrap {{ margin-top: 18px; overflow-x: auto; background: rgba(255,255,255,.82); border: 1px solid rgba(203,213,225,.8); border-radius: 22px; box-shadow: 0 10px 26px rgba(15, 23, 42, .05); padding: 18px; }}
    table.metrics-table {{ width: 100%; border-collapse: collapse; font-size: 14px; background: white; border-radius: 14px; overflow: hidden; }}
    .metrics-table th, .metrics-table td {{ padding: 10px 12px; border-bottom: 1px solid #e2e8f0; text-align: right; white-space: nowrap; }}
    .metrics-table th:first-child, .metrics-table td:first-child {{ text-align: center; }}
    .metrics-table th {{ position: sticky; top: 0; background: #eff6ff; }}
    .footnote {{ margin-top: 20px; color: var(--muted); font-size: 14px; line-height: 1.6; }}
    @media (max-width: 960px) {{ .insight-block {{ grid-template-columns: 1fr; }} .hero h1 {{ font-size: 28px; }} }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <h1>รายงานวิเคราะห์แนวโน้มรางวัลตีพิมพ์ มหาวิทยาลัยเกษตรศาสตร์</h1>
      <p>รายงานนี้คงส่วนวิเคราะห์ภาพรวมเดิมไว้ และเพิ่มหมวดวิเคราะห์รายปีตามตัวชี้วัดที่ต้องการ เพื่อให้ใช้ได้ทั้งสำหรับเล่า narrative เชิงนโยบายและดู annual diagnostics ในเอกสารเดียว.</p>
    </section>

    <h2 class="section-title">Executive Summary</h2>
    <div class="metrics-grid">{overview_cards}</div>
    <div class="summary">
      <h3>ข้อสรุปเชิงบริหาร</h3>
      <p>หากตีความในเชิงต้นทุนจริง มหาวิทยาลัยจ่ายงบรางวัลนักวิจัยเฉลี่ยประมาณ <strong>{df['reward_per_awarded_article_baht'].mean():,.0f} บาทต่อบทความที่ได้รางวัล</strong> โดยในแต่ละปีแกว่งอยู่ราว <strong>{df['reward_per_awarded_article_baht'].min():,.0f}-{df['reward_per_awarded_article_baht'].max():,.0f} บาทต่อบทความ</strong>. หากต้องการใช้เทียบกับมหาวิทยาลัยอื่น ควรใช้ตัวชี้วัดนี้เป็นแกนหลัก เพราะสะท้อน “จำนวนเงินที่จ่ายจริงต่อบทความที่ได้รับรางวัล” โดยตรง. ถ้าต้องการมองในเชิงต้นทุนต่อ output ทั้งระบบ ข้อมูลชุดนี้ชี้ว่าเฉลี่ยจ่ายราว <strong>{df['reward_per_total_article_baht'].mean():,.0f} บาทต่อบทความรวม</strong> หรือ <strong>{df['full_reward_per_total_article_baht'].mean():,.0f} บาทต่อบทความรวม</strong> เมื่อคิดรวมส่วนงานและค่าใช้จ่ายเต็มรูปแบบ {summary_reference("(อ้างอิงกราฟ 3, กราฟ 8 และกราฟภาคผนวก 3)", ["overview-budget", "overview-unit-value", "annual-cost"])}.</p>
      <blockquote>หากเป้าหมายคือเพิ่มจำนวนผลงานตีพิมพ์ ข้อมูลนี้สนับสนุนให้ใช้มาตรการจูงใจที่ผูกกับ output การตีพิมพ์โดยตรง มากกว่าพึ่งการเพิ่มทุนวิจัยรวมเพียงอย่างเดียว</blockquote>
      <p>ในมิติของประสิทธิผล หลักฐานจากกราฟทั้งหมดค่อนข้างสนับสนุนว่าระบบรางวัลนี้ <strong>มีประสิทธิผลในเชิงผลลัพธ์</strong> เพราะผลผลิตและการมีส่วนร่วมเพิ่มตามจริง: บทความที่ได้รางวัลเพิ่มเป็น <strong>{multiple(first['award_articles'], last['award_articles']):.1f} เท่า</strong>, สัดส่วนบทความที่ได้รางวัลเพิ่มจาก <strong>{first['award_share_pct']:.1f}%</strong> เป็น <strong>{last['award_share_pct']:.1f}%</strong>, และจำนวนผู้ได้รับรางวัลเพิ่มเป็น <strong>{multiple(first['award_researchers_count'], last['award_researchers_count']):.1f} เท่า</strong>. แต่ในมิติของประสิทธิภาพเชิงทุน ต้องยอมรับว่าเงินเพิ่มเป็น <strong>{multiple(first['award_amount_researcher_baht'], last['award_amount_researcher_baht']):.1f} เท่า</strong> ขณะที่บทความที่ได้รางวัลเพิ่ม <strong>{multiple(first['award_articles'], last['award_articles']):.1f} เท่า</strong> จึงแปลได้ว่าประสิทธิภาพของทุนต่อบทความอ่อนลงจากปีฐาน แม้กระนั้น ต้นทุนต่อเปเปอร์ในเอกสารนี้ยังอยู่ในระดับค่อนข้างต่ำ จึงยังพอสรุปได้ว่าการได้เปเปอร์เพิ่มยังคุ้มค่าในทางปฏิบัติ เพียงแต่ไม่ควรสรุปว่าเพิ่มงบแล้วประสิทธิภาพจะดีขึ้นเอง {summary_reference("(อ้างอิงกราฟ 1, 2, 3, 5 และกราฟภาคผนวก 2-3)", ["overview-volume", "overview-share", "overview-budget", "overview-people", "annual-efficiency", "annual-cost"])}.</p>
      <ol class="qa-list">
        <li class="qa-item">
          <p class="qa-q">คำถามเชิงนโยบาย 1: การให้รางวัลในระดับปัจจุบันถือว่าแพงหรือไม่</p>
          <p class="qa-a">หากใช้เกณฑ์ “เงินที่จ่ายจริงต่อบทความที่ได้รางวัล” ระดับปัจจุบันอยู่ในช่วงประมาณสองหมื่นบาทต่อบทความ และแกว่งอยู่ในกรอบไม่กว้างมากเมื่อมองตลอดทั้งช่วงเวลา จึงเป็นตัวชี้วัดที่เหมาะที่สุดสำหรับใช้เทียบกับมหาวิทยาลัยอื่น ส่วนถ้าจะเทียบในเชิงต้นทุนต่อผลผลิตรวม ค่าเฉลี่ยจะต่ำกว่านั้นพอสมควร {summary_reference("(ดูกราฟต้นทุน)", ["overview-budget", "overview-unit-value", "annual-cost"])}.</p>
        </li>
        <li class="qa-item">
          <p class="qa-q">คำถามเชิงนโยบาย 2: ระบบนี้มีประสิทธิผลหรือไม่</p>
          <p class="qa-a">ข้อมูลสนับสนุนว่ามีประสิทธิผลในเชิงผลลัพธ์ เพราะทั้งจำนวนบทความที่ได้รางวัล สัดส่วนบทความที่เข้าเกณฑ์รางวัล และจำนวนผู้ได้รับรางวัลเพิ่มขึ้นพร้อมกัน แต่ควรแยกคำว่า “ได้ผล” ออกจากคำว่า “คุ้มค่าที่สุด” เพราะประสิทธิภาพต่อ 1 ล้านบาทไม่ได้ดีขึ้นต่อเนื่องทุกปี {summary_reference("(ดูกราฟผลลัพธ์และประสิทธิภาพ)", ["overview-volume", "overview-share", "overview-people", "annual-efficiency"])}.</p>
        </li>
        <li class="qa-item">
          <p class="qa-q">คำถามเชิงนโยบาย 3: ถ้าปรับเพิ่มหรือลดรางวัล จะกระทบจำนวนคนหรือจำนวนเปเปอร์อย่างไร</p>
          <p class="qa-a">ข้อมูลนี้ยังไม่พอจะยืนยันเหตุและผลแบบตรงไปตรงมา แต่รูปแบบในข้อมูลชี้ว่าช่วงที่งบรางวัลขยายตัวแรง จำนวนผู้ได้รับรางวัลมักขยับตามเร็วกว่าจำนวนบทความ ดังนั้นหากเพิ่มงบ ผลกระทบน่าจะเริ่มเห็นที่ “จำนวนคนที่เข้าระบบ” ก่อน ส่วนถ้าลดงบ ความเสี่ยงแรกคือแรงจูงใจและการมีส่วนร่วมจะชะลอ ก่อนที่ผลกระทบต่อผลผลิตรวมจะตามมา {summary_reference("(ดูกราฟความสัมพันธ์และการเปลี่ยนแปลงรายปี)", ["overview-turning", "overview-people", "overview-scatter", "annual-people", "annual-per-person"])}.</p>
        </li>
      </ol>
    </div>

    <h2 class="section-title">การวิเคราะห์ภาพรวมตามประเด็น</h2>
    {''.join(overview_sections)}

    <h2 class="section-title">ภาคผนวกการวิเคราะห์รายปี</h2>
    <div class="metrics-grid">{annual_cards}</div>
    <div class="summary">ชุดข้อมูลนี้ตอบได้ดีในมิติของบทความรางวัล งบรางวัล และจำนวนผู้ได้รับรางวัลรายปี แต่ไม่มีตัวแปรจำนวนผู้ตีพิมพ์รวมทั้งระบบ ดังนั้นประเด็นที่เกี่ยวกับ “ต่อคน” ในส่วนเสริมนี้ใช้จำนวนผู้ได้รับรางวัลเป็นตัวหารแทน. ค่าที่ใช้ตอบคำถามเชิงนโยบายเรื่องการเพิ่มหรือลดรางวัลจึงควรอ่านเป็นหลักฐานเชิงแนวโน้ม ไม่ใช่ผลกระทบเชิงสาเหตุที่ยืนยันแล้ว.</div>
    {''.join(annual_sections)}

    <h2 class="section-title">ตารางตัวชี้วัดรายปี</h2>
    <div class="table-wrap">{table_html}</div>

    <h2 class="section-title">ข้อมูลดิบจากไฟล์ต้นฉบับ</h2>
    <div class="table-wrap">{raw_table_html}</div>

    <p class="footnote">ไฟล์ตัวชี้วัดรายปีถูก export แยกไว้เป็น <code>annual_award_metrics.csv</code>. ค่าที่เกี่ยวกับ “ต่อคน” ใช้ฐานผู้ได้รับรางวัลต่อปี ไม่ใช่จำนวนผู้ตีพิมพ์รวมทั้งมหาวิทยาลัย.</p>
  </main>
</body>
</html>
"""

    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT_HTML}")
    print(f"Wrote {OUTPUT_METRICS_CSV}")


if __name__ == "__main__":
    main()
