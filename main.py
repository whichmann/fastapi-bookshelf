from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uuid import uuid4
from random import choice
import json

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

items = []

def get_random_quote():
    with open("static/quotes.json", "r") as f:
        quotes = json.load(f)
        return choice(list(quotes.values()))[0]

class Item(BaseModel):
    id: str = str(uuid4())
    title: str
    author: str
    description: str = None
    is_done: bool = False 

@app.get("/", include_in_schema=False, name="home")
@app.get("/books", include_in_schema=False, name="books")
def books(request: Request):
    return templates.TemplateResponse(request, "home.html", { "books": items, "quote": get_random_quote(), "request": request })

@app.get("/books/{book_id}", include_in_schema=False)
def get_book(request: Request, book_id: str):
    item = next((item for item in items if item.id == book_id), None)
    if item is not None:
        return templates.TemplateResponse(request, "book.html", { "book": item, "request": request })
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@app.post("/api/items", tags=["items"], response_model=list[Item])
def create_item(item: Item):
    items.append(item)
    return items

@app.get("/api/items", tags=["items"], response_model=list[Item] )
def list_items(limit: int = 10):
    return items[0:limit]

@app.get("/api/items/{id}", tags=["items"], response_model=Item )
def get_item(id: str) -> Item:
    item = next((item for item in items if item.id == id), None)
    if item is not None:
        return item
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occured"
    )
    
    if request.url.path.startswith('/api'):
        return JSONResponse(status_code=exception.status_code, content={"detail": message})
    
    return templates.TemplateResponse(request, "error.html", {
        "status_code": exception.status_code,
        "title": exception.status_code,
        "message": message
    }, status_code=exception.status_code)

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
   
    if request.url.path.startswith('/api'):
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": exception.errors()})
    
    return templates.TemplateResponse(request, "error.html", {
        "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
        "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
        "message": "Invalid request"
    }, status.HTTP_422_UNPROCESSABLE_CONTENT)
