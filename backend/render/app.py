from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from search_logic import search_one_product

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dutch-supermarket-comparison.vercel.app",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search")
def search(query: str = Body(..., embed=True)):
    """
    Expects JSON: {"query": "your product"}
    The 'embed=True' means it looks for the 'query' key inside the JSON body.
    """
    try:
        results = search_one_product(
            query_text=query,
            search_lang="du",
            supermarkets=["ah", "dirk", "hoogvliet"],
            sort_by="unit_price"
        )
        return {"results": results}
    except Exception as e:
        print(f"Error during search: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/")
def health():
    return {"status": "ok", "message": "Render backend running"}