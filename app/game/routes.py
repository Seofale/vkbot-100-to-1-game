import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    from app.game.views import (
        QuestionAddView, QuestionListView, UsersListView,
        QuestionEditView, GamesListView, RoadmapsListView,
        UserStatisticsListView,

    )
    app.router.add_view("/questions.add", QuestionAddView)
    app.router.add_view("/questions.list", QuestionListView)
    app.router.add_view("/questions.edit", QuestionEditView)
    app.router.add_view("/games.list", GamesListView)
    app.router.add_view("/roadmaps.list", RoadmapsListView)
    app.router.add_view("/users.list", UsersListView)
    app.router.add_view("/statistics.list", UserStatisticsListView)
