import os
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from groq import Groq
import re
import json
import asyncio
import warnings

from services.utils import clean_json
from .data_processor import DataProcessor
from .chart_generator import ChartGenerator

# Suppress datetime parsing warnings
warnings.filterwarnings("ignore", message="Could not infer format")


class AIAgent:
    """AI-powered agent using Groq for automated EDA"""

    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        self.data_processor = DataProcessor()
        self.chart_generator = ChartGenerator()

    @staticmethod
    def extract_json_array(text: str) -> Optional[str]:
        """Extracts the first JSON array from a block of text"""
        try:
            patterns = [
                r"\[\s*\{.*?\}\s*\]",  # Standard array
                r"\[[\s\S]*?\]",  # Any array content
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    return match.group(0)
            return None
        except Exception:
            return None

    def _looks_like_datetime(self, value: str) -> bool:
        """Check if a string value looks like it could be a datetime"""
        if not isinstance(value, str) or len(value.strip()) < 4:
            return False
        datetime_patterns = [
            r"\d{4}-\d{1,2}-\d{1,2}",  # YYYY-MM-DD
            r"\d{1,2}/\d{1,2}/\d{4}",  # MM/DD/YYYY or DD/MM/YYYY
            r"\d{1,2}-\d{1,2}-\d{4}",  # MM-DD-YYYY or DD-MM-YYYY
            r"\d{4}/\d{1,2}/\d{1,2}",  # YYYY/MM/DD
            r"\w+\s+\d{1,2},?\s+\d{4}",  # Month DD, YYYY
        ]
        for pattern in datetime_patterns:
            if re.search(pattern, value.strip()):
                return True
        return False

    async def analyze_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze the dataset structure and characteristics"""
        basic_info = self.data_processor.get_basic_info(df)
        analysis_prompt = f"""
Analyze this dataset with the following characteristics:
- Shape: {basic_info['shape']}
- Columns: {basic_info['columns']}
- Data types: {basic_info['dtypes']}
- Missing values: {basic_info['missing_values']}
Provide a comprehensive analysis including:
1. Data quality assessment
2. Potential data issues
3. Column type recommendations
4. Suggested preprocessing steps
Return your analysis in JSON format with keys: quality_score, issues, recommendations, column_insights.
"""
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data science expert specializing in exploratory data analysis.",
                    },
                    {"role": "user", "content": analysis_prompt},
                ],
                model="llama3-8b-8192",
                temperature=0.1,
                max_tokens=1024,
            )
            ai_analysis = json.loads(response.choices[0].message.content)
        except Exception:
            ai_analysis = {
                "quality_score": 75,
                "issues": ["Could not generate AI analysis"],
                "recommendations": ["Perform standard data cleaning"],
                "column_insights": {},
            }
        return {"basic_info": basic_info, "ai_analysis": ai_analysis}

    async def generate_recommendations(
        self, operation: str, analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate specific recommendations based on the analysis"""
        recommendations = []

        if operation == "clean":
            missing_values = analysis["basic_info"]["missing_values"]
            if any(count > 0 for count in missing_values.values()):
                recommendations.append(
                    {
                        "action": "handle_missing_values",
                        "method": (
                            "imputation"
                            if sum(missing_values.values())
                            < len(analysis["basic_info"]["shape"]) * 0.3
                            else "removal"
                        ),
                        "columns": [
                            col for col, count in missing_values.items() if count > 0
                        ],
                    }
                )
            recommendations.append(
                {"action": "remove_duplicates", "method": "drop_duplicates"}
            )
            recommendations.append(
                {"action": "convert_data_types", "method": "automatic_conversion"}
            )

        elif operation == "transform":
            numerical_cols = [
                col
                for col, dtype in analysis["basic_info"]["dtypes"].items()
                if dtype in ["int64", "float64"]
            ]
            categorical_cols = [
                col
                for col, dtype in analysis["basic_info"]["dtypes"].items()
                if dtype == "object"
            ]
            if numerical_cols:
                recommendations.append(
                    {
                        "action": "scale_features",
                        "method": "standard_scaling",
                        "columns": numerical_cols,
                    }
                )
            if categorical_cols:
                recommendations.append(
                    {
                        "action": "encode_categorical",
                        "method": "label_encoding",
                        "columns": categorical_cols,
                    }
                )
        elif operation == "classify":
            recommendations.append(
                {
                    "action": "analyze_data_types",
                    "method": "comprehensive_classification",
                }
            )
        elif operation == "visualize":
            recommendations.append(
                {
                    "action": "create_comprehensive_charts",
                    "method": "automatic_chart_selection",
                }
            )
        return recommendations

    async def apply_operations(
        self,
        df: pd.DataFrame,
        operation: str,
        recommendations: List[Dict[str, Any]],
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply the recommended operations"""
        results = {}
        if operation == "clean":
            cleaning_options = {
                "remove_duplicates": True,
                "missing_strategy": "impute",
                "numerical_impute_strategy": "mean",
                "categorical_impute_strategy": "most_frequent",
                "convert_dtypes": True,
                "remove_outliers": options.get("remove_outliers", False),
            }
            results = self.data_processor.clean_data(df, cleaning_options)
        elif operation == "transform":
            transform_options = {
                "scaling_method": options.get("scaling_method", "standard"),
                "encoding_method": options.get("encoding_method", "label"),
                "create_features": options.get("create_features", False),
            }
            results = self.data_processor.transform_data(df, transform_options)
        elif operation == "classify":
            results = self.data_processor.classify_data(df, options)
        elif operation == "visualize":
            chart_options = {"chart_type": "auto"}
            results = self.chart_generator.generate_charts(df, chart_options)
        return results

    async def generate_insights(
        self, df: pd.DataFrame, operation_results: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate final insights and summary"""
        basic_info = self.data_processor.get_basic_info(df)
        insights_prompt = f"""
Based on this data analysis:
- Data shape: {basic_info['shape']}
- Analysis results: {str(operation_results)[:500] if operation_results else 'No specific operation results'}...
Generate key insights and actionable recommendations for this dataset.
Focus on practical implications and next steps.
Return insights as a valid JSON object with the following keys:
  - "key_findings": an array of string insights,
  - "recommendations": an array of actionable recommendation strings,
  - "next_steps": an array of string next steps.
Output ONLY a JSON object and nothing else.
"""
        ai_output = None
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data science expert providing actionable insights.",
                    },
                    {"role": "user", "content": insights_prompt},
                ],
                model="llama3-8b-8192",
                temperature=0.2,
                max_tokens=512,
            )
            ai_output = response.choices[0].message.content.strip()
            print("[AI INSIGHTS Raw Response]:", ai_output)
            insights = json.loads(ai_output)
        except Exception as e:
            print("[AI INSIGHTS ERROR]:", str(e))
            insights = {
                "key_findings": ["Analysis completed successfully"],
                "recommendations": ["Review the processed data"],
                "next_steps": ["Continue with further analysis"],
            }
            ai_output = None
        return {"insights": insights, "ai_output": ai_output}

    def get_top_correlated_pairs(self, df, num=2, threshold=0.3):
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return []
        corr = df[numeric_cols].corr().abs()
        pairs = (
            corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
            .stack()
            .reset_index()
            .sort_values(0, ascending=False)
        )
        pairs.columns = ["x", "y", "corr"]
        filtered = pairs[pairs["corr"] >= threshold].head(num)
        return [
            {
                "chart_type": "scatter",
                "x": row["x"],
                "y": row["y"],
                "title": f"Scatter: {row['y']} vs {row['x']}",
            }
            for _, row in filtered.iterrows()
        ]
    def validate_chart_specs(
        self, df: pd.DataFrame, chart_specs: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Validate and fix chart specifications"""
        valid_specs = []
        available_columns = df.columns.tolist()
        for spec in chart_specs:
            try:
                chart_type = (
                    spec.get("chart_type", spec.get("type", "")).lower().strip()
                )
                x_col = spec.get("x", spec.get("x_column", "")).strip()
                y_col = spec.get("y", spec.get("y_column", "")).strip()
                if not x_col or x_col not in available_columns:
                    continue
                if y_col and y_col not in available_columns:
                    continue
                valid_chart_types = [
                    "bar",
                    "histogram",
                    "scatter",
                    "box",
                    "line",
                    "pie",
                ]
                if chart_type not in valid_chart_types:
                    chart_type = "bar"
                if chart_type == "histogram" and not pd.api.types.is_numeric_dtype(
                    df[x_col]
                ):
                    continue
                if chart_type == "scatter" and y_col:
                    if not (
                        pd.api.types.is_numeric_dtype(df[x_col])
                        and pd.api.types.is_numeric_dtype(df[y_col])
                    ):
                        continue
                valid_spec = {
                    "chart_type": chart_type,
                    "x": x_col,
                    "title": f"{chart_type.title()} of {x_col}",
                }
                if y_col:
                    valid_spec["y"] = y_col
                    valid_spec["title"] = f"{chart_type.title()}: {y_col} vs {x_col}"
                valid_specs.append(valid_spec)
            except Exception:
                continue
        return valid_specs

    def create_fallback_chart_specs(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        """Create fallback chart specifications when AI fails"""
        specs = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()
        for col in numeric_cols[:3]:
            specs.append(
                {"chart_type": "histogram", "x": col, "title": f"Distribution of {col}"}
            )
        for col in categorical_cols[:3]:
            if df[col].nunique() <= 20:
                specs.append(
                    {"chart_type": "bar", "x": col, "title": f"Distribution of {col}"}
                )
        if len(numeric_cols) >= 2:
            specs.append(
                {
                    "chart_type": "scatter",
                    "x": numeric_cols[0],
                    "y": numeric_cols[1],
                    "title": f"{numeric_cols[1]} vs {numeric_cols[0]}",
                }
            )
        return specs[:5]

    async def get_ai_chart_suggestions(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        """Suggest charts using AI and correlation analysis."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = [
            col
            for col in df.columns
            if df[col].dtype == "object" and df[col].nunique() <= 30
        ]
        prompt = f"""
You are a data visualization expert. Given this dataset information, suggest 5-7 useful charts in JSON array format.
Dataset columns: {list(df.columns)}
Numerical columns: {numeric_cols}
Categorical columns: {categorical_cols}
Rules:
1. Only use column names that exist in the dataset
2. Use appropriate chart types: bar, histogram, scatter, box, line
3. For bar charts, use categorical columns
4. For histograms, use numerical columns
5. For scatter plots, use two numerical columns
6. For box plots, use categorical x and numerical y
Output ONLY a JSON array like this:
{{"chart_type": "histogram", "x": "{numeric_cols[0] if numeric_cols else 'column_name'}"}},
{{"chart_type": "bar", "x": "{categorical_cols[0] if categorical_cols else 'column_name'}"}},
{{"chart_type": "scatter", "x": "{numeric_cols[0] if len(numeric_cols) > 1 else 'col1'}", "y": "{numeric_cols[1] if len(numeric_cols) > 1 else 'col2'}"}}
No explanations. Only the JSON array.
"""
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data visualization expert. Respond only with valid JSON arrays.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model="llama3-8b-8192",
                temperature=0.1,
                max_tokens=512,
            )
            ai_output = response.choices[0].message.content.strip()
            clean_json_text = self.extract_json_array(ai_output)
            if not clean_json_text:
                raise ValueError("No valid JSON array found")
            chart_specs = json.loads(clean_json_text)
            validated_specs = self.validate_chart_specs(df, chart_specs)
            if not validated_specs:
                validated_specs = self.create_fallback_chart_specs(df)
        except Exception:
            validated_specs = self.create_fallback_chart_specs(df)
        cor_scatter_specs = self.get_top_correlated_pairs(df, num=2, threshold=0.3)
        key_fn = lambda s: (s.get("chart_type"), s.get("x"), s.get("y"))
        dedup = {key_fn(s): s for s in (validated_specs + cor_scatter_specs)}
        all_specs = list(dedup.values())
        return all_specs

    async def process_data(
        self, df: pd.DataFrame, operation: str, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Main method to process data using AI workflow."""
        try:
            # Step 1: Analyze data
            analysis = await self.analyze_data(df)
            # Step 2: Generate recommendations
            recommendations = await self.generate_recommendations(operation, analysis)
            # Step 3: Apply operations
            operation_results = await self.apply_operations(
                df, operation, recommendations, options
            )
            # Step 4: Generate insights
            insights = await self.generate_insights(df, operation_results)
            # Step 5: Chart generation logic
            charts_manual = []
            charts_ai = []
            if operation == "visualize":
                charts_manual = self.chart_generator.generate_all_charts(
                    df, "distribution,correlation,missing"
                )
                chart_specs = await self.get_ai_chart_suggestions(df)
                if chart_specs:
                    charts_ai = self.chart_generator.generate_custom_charts(
                        df, chart_specs
                    )
                manual_keys = set(
                    (c.get("type"), c.get("x"), c.get("y")) for c in charts_manual
                )
                filtered_ai_charts = [
                    c
                    for c in charts_ai
                    if (c.get("type"), c.get("x"), c.get("y")) not in manual_keys
                ]
                charts = charts_manual + filtered_ai_charts
            else:
                charts = operation_results.get("charts", [])
            result = {
                "success": True,
                "operation": operation,
                "analysis": analysis,
                "results": operation_results,
                "charts": charts,
                "insights": insights,
                "recommendations": recommendations,
            }
            return clean_json(result)
        except Exception as e:
            print(f"[AI PROCESS ERROR]: {str(e)}")
            return {"success": False, "error": str(e), "operation": operation}
