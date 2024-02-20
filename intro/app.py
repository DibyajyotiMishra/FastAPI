from decimal import Decimal

from fastapi import FastAPI, Path, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI()


class Book:
    ID: int
    title: str
    author: str
    genre: str
    rating: Decimal
    published_date: int

    def __init__(self, ID, title, author, genre, rating, published_date):
        self.ID = ID
        self.title = title
        self.author = author
        self.genre = genre
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    ID: int | None = 0
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    genre: str = Field(min_length=3, max_length=10)
    rating: Decimal = Field(max_digits=2, decimal_places=1)
    published_date: int = Field(gt=0, lt=2025)

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'An awesome book',
                'author': 'John Doe',
                'genre': 'Comedy',
                'rating': 4.5,
                'published_date': 2015
            }
        }


BOOKS = [
    Book(1, "To the Lighthouse", "Virginia Woolf", "genre 1", 4, 2018),
    Book(2, "Ramayana", "Valmiki", "genre 1", 4.5, 90),
    Book(3, "Journey to the End of the Night", "Louis-Ferdinand Céline", "genre 2", 2.5, 2019),
]


@app.get("/")
async def get_all_books():
    return JSONResponse(status_code=200, content=jsonable_encoder(BOOKS))


@app.get("/books/{book_id}")
async def get_book_by_bookid(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.ID == int(book_id):
            return JSONResponse(status_code=200, content=jsonable_encoder(book))
    return JSONResponse(status_code=404, content="No match found!")


@app.get("/books/ratings/{rating}")
async def get_books_by_rating(rating: int = Path(gt=-1, lt=6)):
    res = []
    for book in BOOKS:
        if book.rating == rating:
            res.append(book)
    return JSONResponse(status_code=200, content=jsonable_encoder(res))


@app.get("/books/published-on/{published_date}")
async def get_books_by_published_date(published_date: int = Path(gt=0, lt=2025)):
    for book in BOOKS:
        if book.published_date == published_date:
            return JSONResponse(status_code=200, content=jsonable_encoder(book))
    return JSONResponse(status_code=404, content="No match found!")


@app.post("/books/add")
async def add_book(book_request: BookRequest):
    book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(book))
    return JSONResponse(status_code=201, content="A New Book got added.")


@app.put("/books/update")
async def update_book(book: BookRequest):
    for idx in range(len(BOOKS)):
        if BOOKS[idx].ID == book.ID:
            BOOKS[idx] = book
            return JSONResponse(status_code=204, content="Book got updated.")
    return JSONResponse(status_code=404, content="No match found!")


@app.delete("/books/delete")
async def delete_book(book_id: int = Query(gt=0)):
    for book in BOOKS:
        if book.ID == book_id:
            BOOKS.pop(book_id)
            return JSONResponse(status_code=204, content="Book got deleted.")
    return JSONResponse(status_code=404, content="No match found!")


def find_book_id(book: Book):
    print(book)
    book.ID = 1 if len(BOOKS) == 0 else BOOKS[-1].ID + 1
    return book
