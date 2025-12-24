from fastapi import Depends, FastAPI, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import os

from database import engine, SessionLocal
from models import Base
import models
# 연결한 DB엔진 table 생성 및 
# 정의한 model class와 매핑 작업 수행
Base.metadata.create_all(bind=engine)

# FastAPI() 객체 생성
app = FastAPI()

abs_path = os.path.dirname(os.path.realpath(__file__))
# print(abs_path)
# html 템플릿 폴더를 지정하여 jinja템플릿 객체 생성
# templates = Jinja2Templates(directory="templates")
templates = Jinja2Templates(directory=f"{abs_path}/templates")

# static 폴더(정적파일 폴더)를 app에 연결
# app.mount("/static", StaticFiles(directory=f"static"), name="static")
app.mount("/static", StaticFiles(directory=f"{abs_path}/static"), name="static")

# DB 세션 객체 생성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db  # 세션 작업이 완료될 때 까지 대기
    finally:
        db.close()


@app.get("/")
def home(request: Request,
         db : Session = Depends(get_db)):
    # todo 데이터 조회
    todos = db.query(models.Todo).order_by(models.Todo.id.asc())
    # print(todos)
    # for t in todos:   
    #     print(t.id, t.task, t.completed)
    return templates.TemplateResponse("index.html",
                                      {"request": request,
                                       "todos": todos
})


@app.post("/add")
def add(request: Request, 
        task : str = Form(...),
        db : Session = Depends(get_db)):
    # 새로운 todo 객체 생성
    todo = models.Todo(task = task, completed=False)
    print(todo)
    # todo를 db에 저장하기
    db.add(todo)
    # db 반영
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"),
                            status_code=status.HTTP_303_SEE_OTHER)