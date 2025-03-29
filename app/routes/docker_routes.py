from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
def test_docker():
    return {"message": "Docker route is working"}
