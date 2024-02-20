from fastapi import Body, FastAPI

app = FastAPI()

BOOKS = [
    {
        "title": "To the Lighthouse",
        "author": "Virginia Woolf",
        "genre": "genre 1"
    },
    {
        "title": "Ramayana",
        "author": "Valmiki",
        "genre": "genre 1"
    },
    {
        "title": "Journey to the End of the Night",
        "author": "Louis-Ferdinand Céline",
        "genre": "genre 2"
    },
    {
        "title": "The Castle",
        "author": "Franz Kafka",
        "genre": "genre 2"
    },
    {
        "title": "Lolita",
        "author": "Vladimir Nabokov",
        "genre": "genre 3"
    },
    {
        "title": "The Sound and the Fury",
        "author": "William Faulkner",
        "genre": "genre 3"
    },
    {
        "title": "Absalom, Absalom!",
        "author": "William Faulkner",
        "genre": "genre 4"
    },
    {
        "title": "Beloved",
        "author": "Toni Morrison",
        "genre": "genre 3"
    },
    {
        "title": "Love in the Time of Cholera",
        "author": "Gabriel García Márquez",
        "genre": "genre 4"
    },
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "genre": "genre 4"
    }
]


@app.get("/")
async def get_books():
    return BOOKS


@app.get("/books/{book_title}")
async def get_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            return book


@app.get("/books/authors/{author}")
async def get_books_by_author(author: str):
    requested_books = []
    for book in BOOKS:
        if book.get('author').casefold() == author.casefold():
            requested_books.append(book)
    return requested_books


@app.get("/books/")
async def get_books_by_genre(genre: str):
    requested_books = []
    for book in BOOKS:
        if book.get('genre').casefold() == genre.casefold():
            requested_books.append(book)
    return requested_books


@app.get("/books/{author}/")
async def get_books_by_author_and_genre(author: str, genre: str):
    requested_books = []
    for book in BOOKS:
        if book.get('author').casefold() == author.casefold() \
                and book.get('genre').casefold() == genre.casefold():
            requested_books.append(book)
    return requested_books


@app.post("/books/add")
async def add_book(book=Body()):
    BOOKS.append(book)
    return {"message": "Book added successfully!"}


@app.put("/books/update")
async def update_book(book=Body()):
    for idx in range(len(BOOKS)):
        if BOOKS[idx].get('genre').casefold() == book.get('genre').casefold():
            BOOKS[idx] = book
    return {"message": "Updated the book"}


@app.delete("/books/delete/{title}")
async def delete_book(title: str):
    for idx in range(len(BOOKS)):
        if BOOKS[idx].get('title').casefold() == title.casefold():
            BOOKS.pop(idx)
            break
    return {"message": "Deleted book with title " + title}
