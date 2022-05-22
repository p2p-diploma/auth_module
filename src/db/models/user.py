import datetime
import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship

from db.base_class import Base


class UserRole(enum.Enum):
    USER = "U"
    ADMIN = "A"
    SUPERUSER = "SU"

    @classmethod
    @property
    def roles_order(cls) -> list["UserRole"]:
        return [cls.USER, cls.ADMIN, cls.SUPERUSER]

    def is_child_of(self, role: "UserRole") -> bool:
        order = self.roles_order
        return order.index(self) < order.index(role)


class User(Base):
    email: Mapped[str] = Column(String, unique=True, primary_key=True, index=True, nullable=False)
    full_name: Mapped[str] = Column(String, index=True)
    role: Mapped[UserRole] = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    hashed_password: Mapped[str] = Column(String, nullable=False)
    is_banned: Mapped[bool] = Column(Boolean(), default=False)
    is_superuser: Mapped[bool] = Column(Boolean(), default=False)
    created_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.now(), nullable=False)
    last_login: Mapped[datetime.datetime] = Column(DateTime, nullable=False)

    token: Mapped["Token"] = relationship("Token", back_populates="user", uselist=False)


class Token(Base):
    email: Mapped[str] = Column(String, ForeignKey("user.email"), primary_key=True)
    access_token: Mapped[str] = Column(String, index=True, nullable=False)
    refresh_token: Mapped[str] = Column(String, index=True, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="token")
