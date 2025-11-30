from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, DataError
from app.config import settings
from app.database import engine, Base

from app.api.v1 import auth, courses, assignments, materials, grading, analytics
from app.api.admin import users, analytics as admin_analytics, mock_data

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="LMS Backend API",
    version="1.0.0",
    debug=settings.DEBUG
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации"""
    simplified_errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(x) for x in error["loc"][1:])  # Пропускаем 'body'
        simplified_errors.append({
            "field": field_path,
            "message": error["msg"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid input data", "errors": simplified_errors}
    )


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """Обработчик ошибок целостности БД"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Database integrity error. Please check your input data."}
    )


@app.exception_handler(DataError)
async def data_exception_handler(request: Request, exc: DataError):
    """Обработчик ошибок данных БД"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Invalid data format. Please check your input."}
    )


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(courses.router, prefix="/api/v1")
app.include_router(assignments.router, prefix="/api/v1")
app.include_router(materials.router, prefix="/api/v1")
app.include_router(grading.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")

# admin routers
app.include_router(users.router, prefix="/api/v1")
app.include_router(admin_analytics.router, prefix="/api/v1")
app.include_router(mock_data.router, prefix="/api/v1")


@app.get("/")
def root():
    """Корневой endpoint"""
    return {
        "message": "LMS Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
