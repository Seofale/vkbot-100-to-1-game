from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(required=True)
    vk_id = fields.Int(required=True)
    score = fields.Int(required=False)


class RoadmapSchema(Schema):
    id = fields.Int(required=True)
    game_id = fields.Int(required=True)
    question_id = fields.Int(required=True)
    status = fields.Int(required=True)


class GameSchema(Schema):
    id = fields.Int(required=True)
    peer_id = fields.Int(required=True)
    in_process = fields.Bool(required=True)
    started_at = fields.DateTime(required=True)
    ended_at = fields.DateTime(required=False)
    roadmaps = fields.Nested(RoadmapSchema, many=True)


class StatisticsSchema(Schema):
    id = fields.Int(required=True)
    game_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    is_creator = fields.Bool(required=True)
    points = fields.Int(required=True)
    failures = fields.Int(required=True)
    is_lost = fields.Bool(required=True)


class AnswerSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)
    score = fields.Int(required=True)
    question_id = fields.Int(required=False)


class QuestionSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)
    answers = fields.Nested(AnswerSchema, many=True)


class QuestionEditSchema(Schema):
    id = fields.Int(required=True)
    title = fields.Str(required=True)
    answers = fields.Nested(AnswerSchema, many=True)


class QuestionListSchema(Schema):
    questions = fields.Nested(QuestionSchema, many=True)


class GameListSchema(Schema):
    games = fields.Nested(GameSchema, many=True)


class RoadmapListSchema(Schema):
    roadmaps = fields.Nested(RoadmapSchema, many=True)


class UserListSchema(Schema):
    users = fields.Nested(UserSchema, many=True)


class StatisticsListSchema(Schema):
    statistics = fields.Nested(StatisticsSchema, many=True)


class ListQuerySchema(Schema):
    page = fields.Int()


class QuestionListQuerySchema(ListQuerySchema):
    game_id = fields.Int()


class GameListQuerySchema(ListQuerySchema):
    peer_id = fields.Int()


class UserListQuerySchema(ListQuerySchema):
    game_id = fields.Int()


class RoadmapListQuerySchema(ListQuerySchema):
    game_id = fields.Int()


class StatisticsListQuerySchema(ListQuerySchema):
    user_id = fields.Int()
    game_id = fields.Int()
