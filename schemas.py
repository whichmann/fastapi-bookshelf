from pydantic import BaseModel, ConfigDict, Field

class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=0)
    is_done: bool = False
    
class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    date_posted: str 
    
