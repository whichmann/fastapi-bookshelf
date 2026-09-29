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

from schemas import BookCreate, BookResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

booksList = []

def get_random_quote():
    with open("static/quotes.json", "r") as f:
        quotes = json.load(f)
        return choice(list(quotes.values()))[0]

@app.get("/", include_in_schema=False, name="home")
@app.get("/books", include_in_schema=False, name="books")
def books(request: Request):
    return templates.TemplateResponse(request, "home.html", { "books": booksList, "quote": get_random_quote(), "request": request })

@app.get("/books/{book_id}", include_in_schema=False)
def get_book(request: Request, book_id: str):
    book = next((book for book in booksList if book["id"] == book_id), None)
    if book is not None:
        return templates.TemplateResponse(request, "book.html", { "book": booksList, "request": request })
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")







@app.post("/api/books", tags=["books"], response_model=list[BookResponse], status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    new_id = max(book["id"] for book in booksList) + 1 if booksList else 1
    new_book = {
        "id": new_id,
        "author": book.author,
        "description": book.description,
        "title": book.title,
        "date_posted": "asd"
        
    }
    booksList.append(new_book)
    return booksList

@app.get("/api/books", tags=["books"], response_model=list[BookResponse] )
def list_books(limit: int = 10):
    return booksList[0:limit]

@app.get("/api/books/{id}", tags=["books"], response_model=BookResponse )
def get_book(id: int) -> BookResponse:
    book = next((book for book in booksList if book["id"] == id), None)
    if book is not None:
        return book
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
