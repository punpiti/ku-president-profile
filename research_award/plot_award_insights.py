from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV = BASE_DIR / "extracted_award_data.csv"
OUTPUT_HTML = BASE_DIR / "award_insights_dashboard.html"


def format_baht_millions(series: pd.Series) -> pd.Series:
    return series / 1_000_000


def main() -> None:
    df = pd.read_csv(INPUT_CSV)
    df["award_share_pct"] = df["award_articles"] / df["scopus_articles_total"] * 100
    df["award_amount_researcher_million"] = format_baht_millions(
        df["award_amount_researcher_baht"]
    )
    df["award_amount_full_million"] = format_baht_millions(df["award_amount_full_baht"])
    df["ku_total_research_funding_billion"] = df["ku_total_research_funding_baht"] / 1_000_000_000

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Awarded Articles vs Scopus Articles",
            "Publication Reward Budget",
            "Award Share and Researchers",
            "Award Articles vs Total Research Funding",
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": True}, {"secondary_y": True}],
        ],
        horizontal_spacing=0.1,
        vertical_spacing=0.16,
    )

    years = df["year_be"]

    fig.add_trace(
        go.Scatter(
            x=years,
            y=df["award_articles"],
            mode="lines+markers",
            name="Awarded articles",
            line=dict(color="#0f766e", width=3),
            marker=dict(size=7),
            hovertemplate="ปี %{x}<br>Awarded articles: %{y:,}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=years,
            y=df["scopus_articles_total"],
            mode="lines+markers",
            name="Scopus articles",
            line=dict(color="#2563eb", width=3),
            marker=dict(size=7),
            hovertemplate="ปี %{x}<br>Scopus articles: %{y:,}<extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=years,
            y=df["award_amount_researcher_million"],
            name="Researcher reward",
            marker_color="#f97316",
            hovertemplate="ปี %{x}<br>Researcher reward: %{y:,.2f}M baht<extra></extra>",
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=years,
            y=df["award_amount_full_million"],
            mode="lines+markers",
            name="Full reward package",
            line=dict(color="#7c3aed", width=3),
            marker=dict(size=7),
            hovertemplate="ปี %{x}<br>Full reward: %{y:,.2f}M baht<extra></extra>",
        ),
        row=1,
        col=2,
    )

    fig.add_trace(
        go.Scatter(
            x=years,
            y=df["award_share_pct"],
            mode="lines+markers",
            name="Award share of Scopus",
            line=dict(color="#dc2626", width=3),
            marker=dict(size=7),
            hovertemplate="ปี %{x}<br>Award share: %{y:.1f}%<extra></extra>",
        ),
        row=2,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            x=years,
            y=df["award_researchers_count"],
            name="Researchers awarded",
            marker_color="#14b8a6",
            opacity=0.7,
            hovertemplate="ปี %{x}<br>Researchers: %{y:,}<extra></extra>",
        ),
        row=2,
        col=1,
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(
            x=years,
            y=df["award_articles"],
            mode="lines+markers",
            name="Awarded articles (repeat)",
            line=dict(color="#0f766e", width=3),
            marker=dict(size=7),
            showlegend=False,
            hovertemplate="ปี %{x}<br>Awarded articles: %{y:,}<extra></extra>",
        ),
        row=2,
        col=2,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=years,
            y=df["ku_total_research_funding_billion"],
            mode="lines+markers",
            name="Total research funding",
            line=dict(color="#a16207", width=3, dash="dot"),
            marker=dict(size=7),
            hovertemplate="ปี %{x}<br>Total funding: %{y:,.2f}B baht<extra></extra>",
        ),
        row=2,
        col=2,
        secondary_y=True,
    )

    fig.update_xaxes(tickmode="linear", dtick=1)
    fig.update_yaxes(title_text="Articles", row=1, col=1)
    fig.update_yaxes(title_text="Million baht", row=1, col=2)
    fig.update_yaxes(title_text="Award share (%)", row=2, col=1, secondary_y=False)
    fig.update_yaxes(title_text="Researchers", row=2, col=1, secondary_y=True)
    fig.update_yaxes(title_text="Awarded articles", row=2, col=2, secondary_y=False)
    fig.update_yaxes(title_text="Funding (billion baht)", row=2, col=2, secondary_y=True)

    fig.update_layout(
        title=dict(
            text="Kasetsart University Publication Reward Trends (2551-2566)",
            x=0.5,
            xanchor="center",
        ),
        template="plotly_white",
        height=900,
        width=1400,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=60, r=40, t=120, b=60),
    )

    fig.add_annotation(
        x=0.5,
        y=-0.08,
        xref="paper",
        yref="paper",
        text=(
            "Key pattern: awarded articles and reward budgets rose strongly, while total research funding remained comparatively flat."
        ),
        showarrow=False,
        font=dict(size=13, color="#334155"),
    )

    fig.write_html(OUTPUT_HTML, include_plotlyjs="cdn")
    print(f"Wrote {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
