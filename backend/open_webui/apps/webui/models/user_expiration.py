import time
import uuid
from typing import Optional

from open_webui.apps.webui.internal.db import Base, get_db
from pydantic import BaseModel, ConfigDict  # type: ignore
from sqlalchemy import BigInteger, Column, String  # type: ignore


class UserExpiration(Base):
    __tablename__ = "user_expiration"

    id = Column(String, primary_key=True)
    user_id = Column(String, unique=True)
    expiration_at = Column(BigInteger)  # timestamp in epoch

class UserExpirationModel(BaseModel):
    id: str
    user_id: str
    expiration_at: int # timestamp in epoch

    model_config = ConfigDict(from_attributes=True)

class UserExpirationTable:
    def set_user_expiration(self, user_id: str, expiration_at: int) -> Optional[UserExpirationModel]:
        with get_db() as db:
            try:
                # 首先尝试获取现有记录
                existing = db.query(UserExpiration).filter_by(user_id=user_id).first()
                
                if existing:
                    # 如果记录存在，更新它
                    existing.expiration_at = expiration_at
                    result = existing
                else:
                    # 如果记录不存在，创建新记录
                    new_expiration = UserExpiration(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        expiration_at=expiration_at
                    )
                    db.add(new_expiration)
                    result = new_expiration
                
                # 提交事务
                db.commit()
                
                # 重新查询以确保获取最新数据
                refreshed_result = db.query(UserExpiration).filter_by(id=result.id).first()
                
                return UserExpirationModel.model_validate(refreshed_result) if refreshed_result else None
            
            except Exception as e:
                db.rollback()
                print(f"Error in set_user_expiration: {str(e)}")
                return None

    def get_user_expiration(self, user_id: str) -> Optional[UserExpirationModel]:
        # 获取用户过期时间
        with get_db() as db:
            expiration = db.query(UserExpiration).filter_by(user_id=user_id).first()
            return UserExpirationModel.model_validate(expiration) if expiration else None

    def is_user_expired(self, user_id: str) -> bool:
        try:
            with get_db() as db:
                expiration = db.query(UserExpiration).filter_by(user_id=user_id).first()
                if not expiration:
                    return False
                return int(time.time()) > expiration.expiration_at
        except Exception as e:
            print(f"Database error in is_user_expired: {str(e)}")  # 添加日志
            return False

UserExpirations = UserExpirationTable()
