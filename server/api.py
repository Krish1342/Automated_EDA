from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import pandas as pd
import os
import aiofiles
import json
from typing import Optional, Dict, Any
import uuid
from datetime import datetime


from services.utils import clean_json  # Make sure this is defined!
from services.data_processor import DataProcessor
from services.ai_agent import AIAgent
from services.chart_generator import ChartGenerator

router = APIRouter()
uploaded_files = {}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    file_id = str(uuid.uuid4())
    file_path = f"uploads/{file_id}_{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    try:
        df = pd.read_csv(file_path)
        uploaded_files[file_id] = {
            "filename": file.filename,
            "file_path": file_path,
            "upload_time": datetime.now(),
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
        }
        result = {
            "file_id": file_id,
            "filename": file.filename,
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "preview": df.head().to_dict("records"),
        }
        return clean_json(result)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Error reading CSV file: {str(e)}")


@router.get("/file/{file_id}/info")
async def get_file_info(file_id: str):
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])
    processor = DataProcessor()
    basic_info = processor.get_basic_info(df)
    return basic_info


@router.post("/process")
async def process_data(
    file_id: str = Form(...),
    operation: str = Form(...),  # 'clean', 'transform', 'classify', 'visualize'
    mode: str = Form(...),  # 'manual', 'ai'
    options: Optional[str] = Form(None),  # JSON string of options
):
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])
    processed_options = json.loads(options) if options else {}
    processor = DataProcessor()
    chart_generator = ChartGenerator()
    try:
        if mode == "ai":
            ai_agent = AIAgent()
            result = await ai_agent.process_data(df, operation, processed_options)
        else:
            if operation == "clean":
                # Clean operation
                result = processor.clean_data(df, processed_options)
                cleaned_df = pd.DataFrame(result["cleaned_data"])

                cleaned_dir = "uploads/cleaned"
                os.makedirs(cleaned_dir, exist_ok=True)
                cleaned_file_path = f"{cleaned_dir}/{file_id}_cleaned.csv"
                cleaned_df.to_csv(cleaned_file_path, index=False)
                if not os.path.exists(cleaned_file_path):
                    raise HTTPException(
                        status_code=500, detail="Cleaned file not found"
                    )

                result["download_url"] = f"/static/cleaned/{file_id}_cleaned.csv"
            elif operation == "transform":
                # Transform operation
                result = processor.transform_data(df, processed_options)
                if "transformed_data" in result:
                    transformed_df = pd.DataFrame(result["transformed_data"])

                    transformed_dir = "uploads/transformed"
                    os.makedirs(transformed_dir, exist_ok=True)
                    transformed_file_path = (
                        f"{transformed_dir}/{file_id}_transformed.csv"
                    )
                    transformed_df.to_csv(transformed_file_path, index=False)

                    result["download_url"] = (
                        f"/static/transformed/{file_id}_transformed.csv"
                    )
            elif operation == "classify":
                # Classification operation
                result = processor.classify_data(df, processed_options)
                # Save classification results as a JSON file
                classification_dir = "uploads/classification"
                os.makedirs(classification_dir, exist_ok=True)
                classification_file_path = (
                    f"{classification_dir}/{file_id}_classification.json"
                )
                with open(classification_file_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2)

                result["download_url"] = (
                    f"/static/classification/{file_id}_classification.json"
                )
            elif operation == "visualize":
                result = chart_generator.generate_charts(df, processed_options)
            else:
                raise HTTPException(status_code=400, detail="Invalid operation")
        return clean_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.get("/charts/{file_id}")
async def get_charts(
    file_id: str, chart_types: Optional[str] = None, mode: str = "manual"
):
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])
    chart_generator = ChartGenerator()
    if mode == "ai":
        ai_agent = AIAgent()
        chart_specs = await ai_agent.get_ai_chart_suggestions(df)
        charts = chart_generator.generate_custom_charts(df, chart_specs)
    else:
        print("Requested chart types:", chart_types)
        print("✅ chart_types param received from frontend:", chart_types)

        charts = chart_generator.generate_all_charts(df, chart_types)
    # Filter charts to keep only valid plotly JSON charts
    filtered_charts = []
    for c in charts:
        try:
            raw_data = c.get("data")
            if not isinstance(raw_data, str):
                continue
            parsed = json.loads(raw_data)
            if isinstance(parsed, dict) and "data" in parsed and "layout" in parsed:
                filtered_charts.append(c)
        except Exception:
            continue
    return clean_json({"charts": filtered_charts})


@router.get("/insights/{file_id}")
async def get_ai_insights(file_id: str):
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])
    ai_agent = AIAgent()
    insights = await ai_agent.generate_insights(df)
    return clean_json({"insights": insights})


@router.delete("/file/{file_id}")
async def delete_file(file_id: str):
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    file_info = uploaded_files[file_id]
    if os.path.exists(file_info["file_path"]):
        os.remove(file_info["file_path"])
    del uploaded_files[file_id]
    return {"message": "File deleted successfully"}
