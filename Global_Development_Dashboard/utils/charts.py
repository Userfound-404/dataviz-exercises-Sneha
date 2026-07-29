"""Reusable Plotly chart builders, styled per storytelling-with-data
principles: minimal gridlines, clear titles/subtitles, labeled axes,
consistent palette, generous whitespace.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

PALETTE = px.colors.qualitative.Set2
TEMPLATE = "plotly_white"
FONT = dict(family="Helvetica, Arial, sans-serif", size=13, color="#2b2b2b")


def _apply_common_layout(fig, title, subtitle=None, height=440):
    full_title = f"<b>{title}</b>"
    if subtitle:
        full_title += f"<br><span style='font-size:12px;color:#7a7a7a'>{subtitle}</span>"
    fig.update_layout(
        title=dict(text=full_title, x=0.02, xanchor="left"),
        template=TEMPLATE,
        font=FONT,
        height=height,
        margin=dict(l=40, r=30, t=70, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="white"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#eee", zeroline=False)
    return fig


def choropleth_world(df, value_col, label, title, subtitle=None, color_scale="Viridis"):
    fig = px.choropleth(
        df, locations="iso_code", color=value_col, hover_name="country",
        color_continuous_scale=color_scale,
        labels={value_col: label},
        projection="natural earth",
    )
    fig.update_geos(showframe=False, showcoastlines=False, bgcolor="rgba(0,0,0,0)")
    return _apply_common_layout(fig, title, subtitle, height=480)


def bubble_map(df, size_col, color_col, hover_name, title, subtitle=None):
    fig = px.scatter_geo(
        df, locations="iso_code", size=size_col, color=color_col,
        hover_name=hover_name, projection="natural earth",
        color_discrete_sequence=PALETTE,
    )
    fig.update_geos(showframe=False, showcoastlines=False, bgcolor="rgba(0,0,0,0)")
    return _apply_common_layout(fig, title, subtitle, height=480)


def top_n_bar(df, category_col, value_col, n, title, subtitle=None, color_col=None, ascending=False):
    d = df.sort_values(value_col, ascending=ascending).head(n)
    fig = px.bar(
        d, x=value_col, y=category_col, orientation="h",
        color=color_col if color_col else None,
        color_discrete_sequence=PALETTE,
    )
    fig.update_yaxes(categoryorder="total ascending")
    return _apply_common_layout(fig, title, subtitle, height=420)


def sparkline_trend(df, x_col, y_col, title, subtitle=None):
    fig = px.line(df, x=x_col, y=y_col, markers=False)
    fig.update_traces(line=dict(width=3, color=PALETTE[0]))
    return _apply_common_layout(fig, title, subtitle, height=260)


def time_series_line(df, x_col, y_col, color_col=None, title="", subtitle=None):
    fig = px.line(df, x=x_col, y=y_col, color=color_col, color_discrete_sequence=PALETTE)
    fig.update_traces(line=dict(width=2.5))
    return _apply_common_layout(fig, title, subtitle)


def area_chart(df, x_col, y_col, color_col=None, title="", subtitle=None):
    fig = px.area(df, x=x_col, y=y_col, color=color_col, color_discrete_sequence=PALETTE)
    return _apply_common_layout(fig, title, subtitle)


def slopegraph(df, start_col, end_col, label_col, title, subtitle=None,
               start_label="Start", end_label="End"):
    fig = go.Figure()
    for _, row in df.iterrows():
        color = "#2ca02c" if row[end_col] >= row[start_col] else "#d62728"
        fig.add_trace(go.Scatter(
            x=[start_label, end_label], y=[row[start_col], row[end_col]],
            mode="lines+markers+text",
            text=[row[label_col], f"{row[label_col]}: {row[end_col]:,.1f}"],
            textposition=["middle left", "middle right"],
            line=dict(color=color, width=2),
            marker=dict(size=7, color=color),
            showlegend=False,
        ))
    fig.update_xaxes(showgrid=False)
    return _apply_common_layout(fig, title, subtitle, height=max(400, 30 * len(df)))


def animated_scatter(df, x_col, y_col, size_col, color_col, hover_name, animation_col, title, subtitle=None):
    fig = px.scatter(
        df, x=x_col, y=y_col, size=size_col, color=color_col,
        hover_name=hover_name, animation_frame=animation_col,
        size_max=55, color_discrete_sequence=PALETTE,
        log_x=True,
    )
    return _apply_common_layout(fig, title, subtitle, height=520)


def scatter_with_trend(df, x_col, y_col, size_col=None, color_col=None, hover_name=None,
                        title="", subtitle=None):
    fig = px.scatter(
        df, x=x_col, y=y_col, size=size_col, color=color_col, hover_name=hover_name,
        trendline="ols", trendline_scope="overall",
        color_discrete_sequence=PALETTE, opacity=0.75,
    )
    return _apply_common_layout(fig, title, subtitle, height=500)


def box_by_region(df, category_col, value_col, title, subtitle=None):
    fig = px.box(df, x=category_col, y=value_col, color=category_col, color_discrete_sequence=PALETTE)
    fig.update_layout(showlegend=False)
    return _apply_common_layout(fig, title, subtitle)


def grouped_bar(df, category_col, value_cols, title, subtitle=None):
    fig = go.Figure()
    for i, col in enumerate(value_cols):
        fig.add_trace(go.Bar(name=col, x=df[category_col], y=df[col], marker_color=PALETTE[i % len(PALETTE)]))
    fig.update_layout(barmode="group")
    return _apply_common_layout(fig, title, subtitle)


def stacked_bar(df, category_col, value_cols, title, subtitle=None):
    fig = go.Figure()
    for i, col in enumerate(value_cols):
        fig.add_trace(go.Bar(name=col, x=df[category_col], y=df[col], marker_color=PALETTE[i % len(PALETTE)]))
    fig.update_layout(barmode="stack")
    return _apply_common_layout(fig, title, subtitle)


def heatmap(df, title, subtitle=None):
    fig = px.imshow(df, color_continuous_scale="Viridis", text_auto=".1f", aspect="auto")
    return _apply_common_layout(fig, title, subtitle, height=440)


def treemap(df, path_cols, value_col, title, subtitle=None):
    fig = px.treemap(df, path=path_cols, values=value_col, color=value_col,
                      color_continuous_scale="Viridis")
    return _apply_common_layout(fig, title, subtitle, height=500)


def radar_chart(categories, country_values, world_values, country_name, title, subtitle=None):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=country_values, theta=categories, fill="toself", name=country_name,
                                   line_color=PALETTE[0]))
    fig.add_trace(go.Scatterpolar(r=world_values, theta=categories, fill="toself", name="World Average",
                                   line_color=PALETTE[1]))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)))
    return _apply_common_layout(fig, title, subtitle, height=480)
