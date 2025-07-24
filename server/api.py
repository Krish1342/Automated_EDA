from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import json
import os
import aiofiles
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import asyncio

from services.data_processor import DataProcessor
from services.ai_agent import AIAgent
from services.chart_generator import ChartGenerator

router = APIRouter(prefix="/api", tags=["EDA"])

# In-memory storage for uploaded files (use database in production)
uploaded_files = {}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload CSV file for EDA processing"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    file_id = str(uuid.uuid4())
    file_path = f"uploads/{file_id}_{file.filename}"
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Load and validate CSV
    try:
        df = pd.read_csv(file_path)
        
        # Store file metadata
        uploaded_files[file_id] = {
            "filename": file.filename,
            "file_path": file_path,
            "upload_time": datetime.now(),
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict()
        }
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "preview": df.head().to_dict('records')
        }
        
    except Exception as e:
        # Clean up file if CSV parsing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Error reading CSV file: {str(e)}")

@router.get("/file/{file_id}/info")
async def get_file_info(file_id: str):
    """Get basic information about uploaded file"""
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
    options: Optional[str] = Form(None)  # JSON string of options
):
    """Process data based on operation and mode"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])
    
    # Parse options if provided
    processed_options = json.loads(options) if options else {}
    
    processor = DataProcessor()
    chart_generator = ChartGenerator()
    
    try:
        if mode == "ai":
            ai_agent = AIAgent()
            result = await ai_agent.process_data(df, operation, processed_options)
        else:
            # Manual mode processing
            if operation == "clean":
                result = processor.clean_data(df, processed_options)
            elif operation == "transform":
                result = processor.transform_data(df, processed_options)
            elif operation == "classify":
                result = processor.classify_data(df, processed_options)
            elif operation == "visualize":
                result = chart_generator.generate_charts(df, processed_options)
            else:
                raise HTTPException(status_code=400, detail="Invalid operation")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@router.get("/charts/{file_id}")
async def get_charts(file_id: str, chart_types: Optional[str] = None):
    """Generate charts for visualization"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])
    
    chart_generator = ChartGenerator()
    charts = chart_generator.generate_all_charts(df, chart_types)
    
    return {"charts": charts}

@router.get("/insights/{file_id}")
async def get_ai_insights(file_id: str):
    """Get AI-generated insights about the dataset"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])
    
    ai_agent = AIAgent()
    insights = await ai_agent.generate_insights(df)
    
    return {"insights": insights}

@router.delete("/file/{file_id}")
async def delete_file(file_id: str):
    """Delete uploaded file"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = uploaded_files[file_id]
    
    # Remove file from disk
    if os.path.exists(file_info["file_path"]):
        os.remove(file_info["file_path"])
    
    # Remove from memory
    del uploaded_files[file_id]
    
    return {"message": "File deleted successfully"}

