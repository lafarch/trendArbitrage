from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from main import TrendArbitrageEngine
import pandas as pd

# Asegúrate de que no haya espacios antes de 'app'
app = FastAPI(title="TrendArbitrage API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = TrendArbitrageEngine()


@app.get("/analyze")
async def analyze(keywords: str = Query(None)):
    kw_list = [k.strip() for k in keywords.split(",")] if keywords else None
    report_df = engine.run_pipeline(keywords=kw_list)
    return report_df.to_dict(orient="records")


@app.get("/trending")
async def trending():
    report_df = engine.run_pipeline(use_trending=True)
    return report_df.to_dict(orient="records")
