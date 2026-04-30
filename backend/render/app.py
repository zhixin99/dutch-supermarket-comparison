from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from search_logic import search_one_product
from pydantic import BaseModel  
from typing import List

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dutch-supermarket-comparison.vercel.app",
        "http://localhost:5173",
        "https://compare-dutch-supermarkets.netlify.app/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    lang: str = "du"
    supermarkets: List[str] = ["ah", "dirk", "hoogvliet"]

@app.post("/search")
def search(req: SearchRequest):
    """
    Expects JSON: {"query": "your product"}
    The 'embed=True' means it looks for the 'query' key inside the JSON body.
    """
    try:
        results = search_one_product(
            query_text=req.query,
            search_lang=req.lang,
            supermarkets=req.supermarkets,
            sort_by="unit_price"
        )
        return {"results": results}
    except Exception as e:
        print(f"Error during search: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/")
def health():
    return {"status": "ok", "message": "Render backend running"}