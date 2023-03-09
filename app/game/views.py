from aiohttp_apispec import querystring_schema, request_schema, response_schema
from aiohttp.web_exceptions import (
    HTTPConflict, HTTPBadRequest, HTTPNotFound
)

from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response
from app.game.schemes import (
    QuestionSchema, QuestionListSchema, StatisticsListQuerySchema,
    QuestionListQuerySchema, GameListQuerySchema, GameListSchema,
    UserListSchema, RoadmapListSchema, QuestionEditSchema,
    StatisticsListSchema, UserListQuerySchema, RoadmapListQuerySchema
)
from app.game.dataclasses import Answer


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        title = self.data["title"]
        question = await self.store.game.get_question_by_title(title=title)
        if question:
            raise HTTPConflict
        answers = [Answer(score=a["score"], title=a["title"])
                   for a in self.data["answers"]]
        if len(answers) != 3:
            raise HTTPBadRequest
        question = await self.store.game.create_question(
            title=title,
            answers=answers
        )
        return json_response(data=QuestionSchema().dump(question))


class QuestionEditView(AuthRequiredMixin, View):
    @request_schema(QuestionEditSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        question_dict = QuestionEditSchema().load(self.data)
        question = await self.store.game.get_question_by_id(
            id=question_dict["id"]
        )
        if not question:
            raise HTTPNotFound
        answers = [Answer(id=a["id"], score=a["score"], title=a["title"])
                   for a in question_dict["answers"]]
        question = await self.store.game.edit_question(
            id=question_dict["id"],
            title=question_dict["title"],
            answers=answers
        )
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @querystring_schema(QuestionListQuerySchema)
    @response_schema(QuestionListSchema)
    async def get(self):
        query_dict = QuestionListQuerySchema().load(self.request.query)
        questions = await self.store.game.list_questions(
            game_id=query_dict.get("game_id"),
            page=query_dict.get("page")
        )
        return json_response(QuestionListSchema().dump(
            {"questions": questions}
        ))


class GamesListView(AuthRequiredMixin, View):
    @querystring_schema(GameListQuerySchema)
    @response_schema(GameListSchema)
    async def get(self):
        query_dict = GameListQuerySchema().load(self.request.query)
        games = await self.store.game.list_games(
            peer_id=query_dict.get("peer_id"),
            page=query_dict.get("page")
        )
        return json_response(GameListSchema().dump(
            {"games": games}
        ))


class UsersListView(AuthRequiredMixin, View):
    @querystring_schema(UserListQuerySchema)
    @response_schema(UserListSchema)
    async def get(self):
        query_dict = UserListQuerySchema().load(self.request.query)
        users = await self.store.game.list_users(
            game_id=query_dict.get("game_id"),
            page=query_dict.get("page")
        )
        return json_response(UserListSchema().dump(
            {"users": users}
        ))


class RoadmapsListView(AuthRequiredMixin, View):
    @querystring_schema(RoadmapListQuerySchema)
    @response_schema(RoadmapListSchema)
    async def get(self):
        query_dict = RoadmapListQuerySchema().load(self.request.query)
        roadmaps = await self.store.game.list_roadmaps(
            game_id=query_dict.get("game_id"),
            page=query_dict.get("page")
        )
        return json_response(RoadmapListSchema().dump(
            {"roadmaps": roadmaps}
        ))


class UserStatisticsListView(AuthRequiredMixin, View):
    @querystring_schema(StatisticsListQuerySchema)
    @response_schema(StatisticsListSchema)
    async def get(self):
        query_dict = StatisticsListQuerySchema().load(self.request.query)
        user_statistics = await self.store.game.list_user_statistics(
            user_id=query_dict.get("user_id"),
            game_id=query_dict.get("game_id"),
            page=query_dict.get("page")
        )
        return json_response(StatisticsListSchema().dump(
            {"user_statistics": user_statistics}
        ))
