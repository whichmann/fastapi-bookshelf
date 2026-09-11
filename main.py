from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

app = FastAPI()

items = []

class Item(BaseModel):
    title: str
    author: str
    description: str = None
    is_done: bool = False 

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/items", response_class=HTMLResponse, include_in_schema=False)
def root():
    return f"<h1>{items[0].title}</h1>"

@app.post("/api/items", tags=["items"], response_model=list[Item])
def create_item(item: Item):
    items.append(item)
    return items

@app.get("/api/items", tags=["items"], response_model=list[Item] )
def list_items(limit: int = 10):
    return items[0:limit]

@app.get("/api/items/{item_id}", tags=["items"], response_model=Item )
def get_item(item_id: int) -> Item:
    if item_id < len(items):
        return items[item_id]
    else:
        raise HTTPException(status_code=404, detail="Item not found")