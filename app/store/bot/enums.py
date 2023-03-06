import enum


class ActionTypesEnum(enum.Enum):
    user_joined_chat = "chat_invite_user"


class BotCommandsEnum(enum.Enum):
    create_game = "create"
    end_game = "end"
    user_joined_game = "join"
    start_game = "start"
