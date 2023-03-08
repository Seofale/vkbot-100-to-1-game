from aiohttp.web import HTTPForbidden
from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema
from app.web.app import View
from app.web.utils import json_response
from app.web.mixins import AuthRequiredMixin


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        admin = await self.store.admins.get_admin(
            email=self.data["email"],
            password=self.data["password"]
        )
        if admin:
            session = await new_session(request=self.request)
            session["admin"] = AdminSchema().dump(admin)
            return json_response(data=AdminSchema().dump(admin))

        raise HTTPForbidden


class AdminCurrentView(AuthRequiredMixin, View):
    @response_schema(AdminSchema, 200)
    async def get(self):
        return json_response(data=AdminSchema().dump(self.request.admin))
