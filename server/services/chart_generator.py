import pandas as pd
import numpy as np
import plotly.express as px
from typing import Dict, List, Any, Optional
import logging

class ChartGenerator:
    """Generate various charts and visualizations for EDA"""

    def __init__(self):
        self.chart_configs = {
            "histogram": {"bins": 30, "opacity": 0.7},
            "scatter": {"size": 5, "opacity": 0.7},
            "box": {"notched": True},
            "bar": {"opacity": 0.8},
            "line": {"mode": "lines+markers"},
            "heatmap": {"colorscale": "Viridis"},
            "pie": {"hole": 0.3},
        }


    def _create_distribution_charts(
        self, df: pd.DataFrame, column: str
    ) -> List[Dict[str, Any]]:
        charts = []
        fig_hist = px.histogram(
            df,
            x=column,
            title=f"Distribution of {column}",
            nbins=self.chart_configs["histogram"]["bins"],
            opacity=self.chart_configs["histogram"]["opacity"],
        )
        fig_hist.update_layout(
            xaxis_title=column, yaxis_title="Frequency", showlegend=False
        )
        charts.append(
            {
                "id": f"histogram_{column}",
                "type": "histogram",
                "title": f"Distribution of {column}",
                "data": fig_hist.to_json(),
                "description": f"Histogram showing the distribution of values in {column}",
            }
        )
        fig_box = px.box(
            df,
            y=column,
            title=f"Box Plot of {column}",
            notched=self.chart_configs["box"]["notched"],
        )
        charts.append(
            {
                "id": f"boxplot_{column}",
                "type": "box",
                "title": f"Box Plot of {column}",
                "data": fig_box.to_json(),
                "description": f"Box plot showing quartiles, median, and outliers for {column}",
            }
        )
        return charts

    def _create_categorical_charts(
        self, df: pd.DataFrame, column: str
    ) -> List[Dict[str, Any]]:
        charts = []
        value_counts = df[column].value_counts()
        fig_bar = px.bar(
            x=value_counts.index,
            y=value_counts.values,
            title=f"Distribution of {column}",
            opacity=self.chart_configs["bar"]["opacity"],
        )
        fig_bar.update_layout(xaxis_title=column, yaxis_title="Count", showlegend=False)
        charts.append(
            {
                "id": f"bar_{column}",
                "type": "bar",
                "title": f"Distribution of {column}",
                "data": fig_bar.to_json(),
                "description": f"Bar chart showing the frequency of each category in {column}",
            }
        )
        if len(value_counts) <= 10:
            fig_pie = px.pie(
                values=value_counts.values,
                names=value_counts.index,
                title=f"Proportion of {column}",
                hole=self.chart_configs["pie"]["hole"],
            )
            charts.append(
                {
                    "id": f"pie_{column}",
                    "type": "pie",
                    "title": f"Proportion of {column}",
                    "data": fig_pie.to_json(),
                    "description": f"Pie chart showing the proportion of each category in {column}",
                }
            )
        return charts

    def _create_correlation_heatmap(
        self, df: pd.DataFrame, numerical_cols: List[str]
    ) -> Dict[str, Any]:
        correlation_matrix = df[numerical_cols].corr()
        fig = px.imshow(
            correlation_matrix,
            title="Correlation Heatmap",
            color_continuous_scale=self.chart_configs["heatmap"]["colorscale"],
            aspect="auto",
            text_auto=True,
        )
        fig.update_layout(width=600, height=600)
        return {
            "id": "correlation_heatmap",
            "type": "heatmap",
            "title": "Correlation Heatmap",
            "data": fig.to_json(),
            "description": "Heatmap showing correlations between numerical variables",
        }

    def _create_relationship_charts(
        self, df: pd.DataFrame, numerical_cols: List[str], categorical_cols: List[str]
    ) -> List[Dict[str, Any]]:
        charts = []
        # Scatter plots for numerical vs numerical
        if len(numerical_cols) >= 2:
            for i in range(min(3, len(numerical_cols))):
                for j in range(i + 1, min(3, len(numerical_cols))):
                    col_x, col_y = numerical_cols[i], numerical_cols[j]
                    fig_scatter = px.scatter(
                        df,
                        x=col_x,
                        y=col_y,
                        title=f"{col_y} vs {col_x}",
                        opacity=self.chart_configs["scatter"]["opacity"],
                    )
                    charts.append(
                        {
                            "id": f"scatter_{col_x}_{col_y}",
                            "type": "scatter",
                            "title": f"{col_y} vs {col_x}",
                            "data": fig_scatter.to_json(),
                            "description": f"Scatter plot showing relationship between {col_x} and {col_y}",
                        }
                    )
        # Box plots for categorical vs numerical
        if len(categorical_cols) > 0 and len(numerical_cols) > 0:
            for cat_col in categorical_cols[:2]:
                for num_col in numerical_cols[:2]:
                    if df[cat_col].nunique() <= 10:
                        fig_box = px.box(
                            df, x=cat_col, y=num_col, title=f"{num_col} by {cat_col}"
                        )
                        charts.append(
                            {
                                "id": f"box_{cat_col}_{num_col}",
                                "type": "box_group",
                                "title": f"{num_col} by {cat_col}",
                                "data": fig_box.to_json(),
                                "description": f"Box plot showing {num_col} distribution across {cat_col} categories",
                            }
                        )
        return charts

    def _create_missing_values_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        missing_data = df.isnull().sum()
        missing_percentage = (missing_data / len(df)) * 100
        missing_cols = missing_data[missing_data > 0]
        missing_perc = missing_percentage[missing_percentage > 0]
        fig = px.bar(
            x=missing_cols.index,
            y=missing_perc.values,
            title="Missing Values by Column",
            labels={"x": "Columns", "y": "Missing Percentage (%)"},
        )
        fig.update_layout(
            xaxis_title="Columns",
            yaxis_title="Missing Percentage (%)",
            showlegend=False,
        )
        return {
            "id": "missing_values",
            "type": "missing",
            "title": "Missing Values Analysis",
            "data": fig.to_json(),
            "description": "Bar chart showing percentage of missing values per column",
        }

    def _create_summary_table(self, df: pd.DataFrame) -> Dict[str, Any]:
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numerical_cols) > 0:
            summary_stats = df[numerical_cols].describe()
            fig = px.imshow(
                summary_stats,
                title="Summary Statistics Heatmap",
                color_continuous_scale="Blues",
                aspect="auto",
                text_auto=True,
            )
            fig.update_layout(
                width=800, height=400, xaxis_title="Columns", yaxis_title="Statistics"
            )
            return {
                "id": "summary_stats",
                "type": "summary",
                "title": "Summary Statistics",
                "data": fig.to_json(),
                "description": "Heatmap of summary statistics for numerical columns",
                "table_data": summary_stats.to_dict(),
            }
        return {
            "id": "summary_stats",
            "type": "summary",
            "title": "Summary Statistics",
            "data": None,
            "description": "No numerical columns found for summary statistics",
        }

    def generate_all_charts(self, df: pd.DataFrame, chart_types: Optional[str] = None) -> List[Dict[str, Any]]:
        charts = []
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        # Normalize chart_types input
        requested_types = (
            [t.strip().lower().replace(" ", "_") for t in chart_types.split(",")]
            if chart_types else ["all"]
        )
        print("✅ Final normalized requested_types:", requested_types)

        # Distribution / Histogram
        if "all" in requested_types or "distribution" in requested_types or "histogram" in requested_types:
            for col in numerical_cols:
                if df[col].nunique() > 1:
                    charts.extend(self._create_distribution_charts(df, col))

        # Categorical / Bar Charts
        if "all" in requested_types or "categorical" in requested_types or "categorical_analysis" in requested_types or "bar" in requested_types:
            for col in categorical_cols:
                if df[col].nunique() <= 20:
                    charts.extend(self._create_categorical_charts(df, col))

        # Correlation Charts
        if "all" in requested_types or "correlation" in requested_types or "correlation_analysis" in requested_types:
            if len(numerical_cols) > 1:
                charts.append(self._create_correlation_heatmap(df, numerical_cols))

        # Relationship / Scatter Charts
        if "all" in requested_types or "relationships" in requested_types or "relationship_analysis" in requested_types or "scatter" in requested_types:
            charts.extend(self._create_relationship_charts(df, numerical_cols, categorical_cols))

        # Missing Values Chart
        if "all" in requested_types or "missing" in requested_types or "missing_values" in requested_types:
            if df.isnull().sum().sum() > 0:
                charts.append(self._create_missing_values_chart(df))

        # Summary Table
        if "all" in requested_types or "summary" in requested_types or "summary_table" in requested_types:
            charts.append(self._create_summary_table(df))
        if not charts:
            print("⚠️ No charts generated. Requested types:", requested_types)
            print("📊 Numerical cols:", numerical_cols)
            print("🔤 Categorical cols:", categorical_cols)

        return charts

    def generate_charts(
        self, df: pd.DataFrame, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        chart_type = options.get("chart_type", "auto")
        columns = options.get("columns", [])
        if chart_type == "auto":
            return {"charts": self.generate_all_charts(df)}
        charts = []
        if chart_type == "histogram" and columns:
            for col in columns:
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    charts.extend(self._create_distribution_charts(df, col))
        elif chart_type == "scatter" and len(columns) >= 2:
            col_x, col_y = columns[0], columns[1]
            if col_x in df.columns and col_y in df.columns:
                charts.extend(
                    self._create_relationship_charts(df, [col_x, col_y], [])
                )
        elif chart_type == "bar" and columns:
            for col in columns:
                if col in df.columns and (
                    pd.api.types.is_categorical_dtype(df[col])
                    or df[col].dtype == "object"
                ):
                    charts.extend(self._create_categorical_charts(df, col))
        return {"charts": charts}

    def generate_custom_charts(
        self, df: pd.DataFrame, chart_specs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        charts = []
        for spec in chart_specs:
            try:
                chart_type = spec.get("chart_type", "").lower()
                x = spec.get("x", "")
                y = spec.get("y", None)
                if x not in df.columns or (y and y not in df.columns):
                    logging.warning(f"[CHART GENERATOR] Invalid columns in spec: {spec}")
                    continue
                if chart_type == "histogram" and pd.api.types.is_numeric_dtype(df[x]):
                    fig = px.histogram(df, x=x, title=spec.get("title", f"Histogram of {x}"))
                    charts.append({
                        "id": f"histogram_{x}",
                        "type": "histogram",
                        "title": f"Histogram of {x}",
                        "data": fig.to_json(),
                        "description": f"Histogram of {x}",
                        "x": x,
                        "y": None
                    })
                elif chart_type == "scatter" and y and pd.api.types.is_numeric_dtype(df[x]) and pd.api.types.is_numeric_dtype(df[y]):
                    fig = px.scatter(df, x=x, y=y, title=spec.get("title", f"Scatter plot: {y} vs {x}"))
                    charts.append({
                        "id": f"scatter_{x}_{y}",
                        "type": "scatter",
                        "title": f"Scatter plot: {y} vs {x}",
                        "data": fig.to_json(),
                        "description": f"Scatter plot of {y} vs {x}",
                        "x": x,
                        "y": y
                    })
                elif chart_type == "bar" and (pd.api.types.is_categorical_dtype(df[x]) or df[x].dtype == "object"):
                    vc = df[x].value_counts()
                    fig = px.bar(x=vc.index, y=vc.values, title=spec.get("title", f"Bar chart of {x}"))
                    charts.append({
                        "id": f"bar_{x}",
                        "type": "bar",
                        "title": f"Bar chart of {x}",
                        "data": fig.to_json(),
                        "description": f"Bar chart of {x}",
                        "x": x,
                        "y": None
                    })
                elif chart_type == "box" and y and pd.api.types.is_numeric_dtype(df[y]):
                    fig = px.box(df, x=x, y=y, title=spec.get("title", f"Box plot: {y} vs {x}"))
                    charts.append({
                        "id": f"box_{x}_{y}",
                        "type": "box",
                        "title": f"Box plot: {y} vs {x}",
                        "data": fig.to_json(),
                        "description": f"Box plot of {y} vs {x}",
                        "x": x,
                        "y": y
                    })
            except Exception as e:
                logging.error(f"[CHART GENERATOR ERROR] Failed for spec {spec}: {str(e)}")
                continue
        return charts
