from hashlib import sha256

from sqlalchemy import select, and_

from app.admin.models import AdminModel
from app.admin.dataclasses import Admin
from app.base.base_accessor import BaseAccessor
from app.store.utils import decorate_all_methods, add_db_session_to_accessor


@decorate_all_methods(add_db_session_to_accessor)
class AdminAccessor(BaseAccessor):
    async def get_admin(
        self,
        email: str,
        password: str,
        **kwargs,
    ) -> Admin | None:
        query = select(
            AdminModel
        ).where(
            and_(
                AdminModel.email == email,
                AdminModel.password == sha256(password.encode()).hexdigest()
            )
        )
        session = kwargs.get("session")
        result = await session.execute(query)
        admin_model = result.scalar()
        if admin_model:
            return Admin(
                id=admin_model.id,
                email=admin_model.email,
                password=admin_model.password,
            )
        return None

    async def create_admin(
        self,
        email: str,
        password: str,
        **kwargs,
    ) -> Admin:
        session = kwargs.get("session")
        admin_model = AdminModel(
            email=email,
            password=sha256(password.encode()).hexdigest()
        )
        session.add(admin_model)
        await session.commit()
        return Admin(
            id=admin_model.id,
            email=admin_model.email,
            password=admin_model.password,
        )
