import os
from typing import Dict, List, Any
import pandas as pd
import numpy as np
from groq import Groq
import json
import asyncio

from .data_processor import DataProcessor
from .chart_generator import ChartGenerator

class AIAgent:
    """AI-powered agent using Groq for automated EDA"""
    
    def __init__(self):
        self.groq_client = Groq(
            api_key=os.getenv("GROQ_API_KEY", "")
        )
        self.data_processor = DataProcessor()
        self.chart_generator = ChartGenerator()
    
    async def analyze_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze the dataset structure and characteristics"""
        
        # Get basic information
        basic_info = self.data_processor.get_basic_info(df)
        
        # Generate AI analysis using Groq
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
                    {"role": "system", "content": "You are a data science expert specializing in exploratory data analysis."},
                    {"role": "user", "content": analysis_prompt}
                ],
                model="llama3-8b-8192",
                temperature=0.1,
                max_tokens=1024
            )
            
            ai_analysis = json.loads(response.choices[0].message.content)
            
        except Exception as e:
            # Fallback analysis if AI fails
            ai_analysis = {
                "quality_score": 75,
                "issues": ["Could not generate AI analysis"],
                "recommendations": ["Perform standard data cleaning"],
                "column_insights": {}
            }
        
        return {
            "basic_info": basic_info,
            "ai_analysis": ai_analysis
        }
    
    async def generate_recommendations(self, operation: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific recommendations based on the analysis"""
        
        recommendations = []
        
        if operation == "clean":
            # Data cleaning recommendations
            missing_values = analysis["basic_info"]["missing_values"]
            if any(count > 0 for count in missing_values.values()):
                recommendations.append({
                    "action": "handle_missing_values",
                    "method": "imputation" if sum(missing_values.values()) < len(analysis["basic_info"]["shape"]) * 0.3 else "removal",
                    "columns": [col for col, count in missing_values.items() if count > 0]
                })
            
            recommendations.append({
                "action": "remove_duplicates",
                "method": "drop_duplicates"
            })
            
            recommendations.append({
                "action": "convert_data_types",
                "method": "automatic_conversion"
            })
        
        elif operation == "transform":
            # Data transformation recommendations
            numerical_cols = [col for col, dtype in analysis["basic_info"]["dtypes"].items() 
                            if dtype in ['int64', 'float64']]
            categorical_cols = [col for col, dtype in analysis["basic_info"]["dtypes"].items() 
                              if dtype == 'object']
            
            if numerical_cols:
                recommendations.append({
                    "action": "scale_features",
                    "method": "standard_scaling",
                    "columns": numerical_cols
                })
            
            if categorical_cols:
                recommendations.append({
                    "action": "encode_categorical",
                    "method": "label_encoding",
                    "columns": categorical_cols
                })
        
        elif operation == "classify":
            recommendations.append({
                "action": "analyze_data_types",
                "method": "comprehensive_classification"
            })
        
        elif operation == "visualize":
            recommendations.append({
                "action": "create_comprehensive_charts",
                "method": "automatic_chart_selection"
            })
        
        return recommendations
    
    async def apply_operations(self, df: pd.DataFrame, operation: str, recommendations: List[Dict[str, Any]], options: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the recommended operations"""
        
        results = {}
        
        if operation == "clean":
            # Apply cleaning operations
            cleaning_options = {
                "remove_duplicates": True,
                "missing_strategy": "impute",
                "numerical_impute_strategy": "mean",
                "categorical_impute_strategy": "most_frequent",
                "convert_dtypes": True,
                "remove_outliers": options.get("remove_outliers", False)
            }
            results = self.data_processor.clean_data(df, cleaning_options)
        
        elif operation == "transform":
            # Apply transformation operations
            transform_options = {
                "scaling_method": options.get("scaling_method", "standard"),
                "encoding_method": options.get("encoding_method", "label"),
                "create_features": options.get("create_features", False)
            }
            results = self.data_processor.transform_data(df, transform_options)
        
        elif operation == "classify":
            # Apply classification analysis
            results = self.data_processor.classify_data(df, options)
        
        elif operation == "visualize":
            # Generate visualizations
            chart_options = {"chart_type": "auto"}
            results = self.chart_generator.generate_charts(df, chart_options)
        
        return results
    
    async def generate_insights(self, df: pd.DataFrame, operation_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate final insights and summary"""
        
        # Get basic analysis
        basic_info = self.data_processor.get_basic_info(df)
        
        # Generate AI insights
        insights_prompt = f"""
        Based on this data analysis:
        - Data shape: {basic_info['shape']}
        - Analysis results: {str(operation_results)[:500] if operation_results else 'No specific operation results'}...
        
        Generate key insights and actionable recommendations for this dataset.
        Focus on practical implications and next steps.
        
        Return insights as a JSON object with keys: key_findings, recommendations, next_steps.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a data science expert providing actionable insights."},
                    {"role": "user", "content": insights_prompt}
                ],
                model="llama3-8b-8192",
                temperature=0.2,
                max_tokens=512
            )
            
            insights = json.loads(response.choices[0].message.content)
            
        except Exception as e:
            insights = {
                "key_findings": ["Analysis completed successfully"],
                "recommendations": ["Review the processed data"],
                "next_steps": ["Continue with further analysis"]
            }
        
        return insights
    
    async def process_data(self, df: pd.DataFrame, operation: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to process data using AI workflow"""
        
        try:
            # Step 1: Analyze data
            analysis = await self.analyze_data(df)
            
            # Step 2: Generate recommendations
            recommendations = await self.generate_recommendations(operation, analysis)
            
            # Step 3: Apply operations
            operation_results = await self.apply_operations(df, operation, recommendations, options)
            
            # Step 4: Generate insights
            insights = await self.generate_insights(df, operation_results)
            
            # Step 5: Create visualizations if not already done
            charts = []
            if operation != "visualize":
                charts = self.chart_generator.generate_all_charts(df, "distribution,correlation,missing")
            else:
                charts = operation_results.get("charts", [])
            
            return {
                "success": True,
                "operation": operation,
                "analysis": analysis,
                "results": operation_results,
                "charts": charts,
                "insights": insights,
                "recommendations": recommendations
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            }
