from turtle import pos
from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
import time
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = [
    "http://localhost:4200"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


while True:
    try:
        conn = psycopg2.connect(host='localhost', database="fastapi-socialmedia",
                                user='postgres', password='s9m6K2a5', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("DataBase connection was succesful!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error:",  error)
        time.sleep(1)


@app.get("/")
def read_root():
    return {"message": "Welcome to my API"}


@app.get("/posts")
def get_posts():
    cursor.execute("""
        SELECT * FROM social_media_posts
    """)
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""
    INSERT INTO social_media_posts (title, content, published) VALUES (%s, %s,%s) RETURNING *
    """, (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""
    SELECT * FROM social_media_posts WHERE id={0}
    """.format(str(id)))
    post = cursor.fetchone()
    print(post)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id:{id} was not found')
    else:
        return{"post-detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""
    DELETE FROM social_media_posts WHERE id ={0} RETURNING *
    """.format(str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""
    UPDATE social_media_posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *
    """, (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    print(updated_post)
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    return {"data": updated_post}
