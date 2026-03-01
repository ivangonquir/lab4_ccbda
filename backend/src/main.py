from fastapi import FastAPI, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

from src.library import Item, ItemCreate, StorageDB

config = Config(".env")

storage = StorageDB(config("STORAGE_TABLE"))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=config("FRONTEND_URLS", cast=CommaSeparatedStrings),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get a list with all items
@app.get("/", response_model=list[Item])
async def list_items() -> list[Item]:
    return storage.all_items()


# Create
@app.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate) -> Item:
    return storage.new_item(item)


# Read
@app.get("/{item_id}", response_model=Item)
async def get_item(item_id: int) -> Item:
    item = storage.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


# Update
@app.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate) -> Item:
    item_updated = storage.set_item(item_id, item)
    if item_updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item_updated


# Delete
@app.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int) -> None:
    if storage.delete_item(item_id) is False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
