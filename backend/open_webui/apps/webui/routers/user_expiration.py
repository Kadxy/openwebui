from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from open_webui.apps.webui.models.user_expiration import UserExpirations, UserExpirationModel
from open_webui.apps.webui.models.users import UserModel

router = APIRouter()


@router.get("/")
def okkk():
    raise HTTPException(status_code=200, detail="123")

class UserExpirationRequest(BaseModel):
    expiration_at: int
    auth: str

@router.post("/{user_id}")
async def set_user_expiration(
    user_id: str,
    request: UserExpirationRequest = Body(...),
):
    if request.auth != "wedwedjwipejwpwewew2ioddh2ow0dhy2":
        raise HTTPException(status_code=403, detail="Not authorized")
    expiration = UserExpirations.set_user_expiration(user_id, request.expiration_at)
    if not expiration:
        raise HTTPException(status_code=404, detail="User not found")
    return expiration



@router.get("/{user_id}")
async def get_user_expiration(
        user_id: str,
):
    expiration = UserExpirations.get_user_expiration(user_id)
    if not expiration:
        raise HTTPException(status_code=404, detail="Expiration not set for this user")
    return expiration
