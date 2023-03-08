from aiohttp_apispec import querystring_schema, request_schema, response_schema
from aiohttp.web_exceptions import (
    HTTPConflict, HTTPBadRequest
)

from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response
from app.game.schemes import (
    QuestionSchema, QuestionListSchema, UserIdSchema,
    GameIdSchema, GamePeerIdSchema, GameListSchema,
    UserListSchema, RoadmapListSchema, QuestionEditSchema
)
from app.game.dataclasses import Answer


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        title = self.data["title"]
        question = await self.store.game.get_question_by_title(title=title)
        if not question:
            raise HTTPBadRequest
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
        id = self.data["id"]
        question = await self.store.game.get_question_by_id(id=int(id))
        if not question:
            raise HTTPConflict
        answers = [Answer(id=a["id"], score=a["score"], title=a["title"])
                   for a in self.data["answers"]]
        question = await self.store.game.edit_question(
            id=id,
            title=self.data["title"],
            answers=answers
        )
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @querystring_schema(GameIdSchema)
    @response_schema(QuestionListSchema)
    async def get(self):
        game_id = self.request.query.get("game_id")
        if game_id:
            questions = await self.store.game.list_questions(
                game_id=int(game_id)
            )
        else:
            questions = await self.store.game.list_questions()
        return json_response(QuestionListSchema().dump(
            {"questions": questions}
        ))


class GamesListView(AuthRequiredMixin, View):
    @querystring_schema(GamePeerIdSchema)
    @response_schema(GameListSchema)
    async def get(self):
        peer_id = self.request.query.get("peer_id")
        if peer_id:
            questions = await self.store.game.list_games(
                game_id=int(peer_id)
            )
        else:
            questions = await self.store.game.list_games()
        return json_response(QuestionListSchema().dump(
            {"games": questions}
        ))


class UsersListView(AuthRequiredMixin, View):
    @querystring_schema(GameIdSchema)
    @response_schema(UserListSchema)
    async def get(self):
        game_id = self.request.query.get("game_id")
        if game_id:
            questions = await self.store.game.list_users(
                game_id=int(game_id)
            )
        else:
            questions = await self.store.game.list_users()
        return json_response(QuestionListSchema().dump(
            {"users": questions}
        ))


class RoadmapsListView(AuthRequiredMixin, View):
    @querystring_schema(GameIdSchema)
    @response_schema(RoadmapListSchema)
    async def get(self):
        game_id = self.request.query.get("game_id")
        if game_id:
            questions = await self.store.game.list_roadmaps(
                game_id=int(game_id)
            )
        else:
            questions = await self.store.game.list_roadmaps()
        return json_response(QuestionListSchema().dump(
            {"roadmaps": questions}
        ))


class UserStatisticsListView(AuthRequiredMixin, View):
    @querystring_schema(GameIdSchema)
    @querystring_schema(UserIdSchema)
    @response_schema(UserListSchema)
    async def get(self):
        game_id = self.request.query.get("game_id")
        user_id = self.request.query.get("user_id")
        if game_id and user_id:
            questions = await self.store.game.list_user_statistics(
                game_id=int(game_id),
                user_id=int(user_id)
            )
        elif game_id:
            questions = await self.store.game.list_user_statistics(
                game_id=int(game_id),
            )
        elif user_id:
            questions = await self.store.game.list_user_statistics(
                user_id=int(user_id)
            )
        else:
            questions = await self.store.game.list_user_statistics()
        return json_response(QuestionListSchema().dump(
            {"roadmaps": questions}
        ))
