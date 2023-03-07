import json
import random
from app.game.dataclasses import Answer


def get_answers_keyboard(answers: list[Answer]) -> str:
    answers_keyboard = {
        "inline": False,
        "buttons": []
    }
    for answer in answers:
        answers_keyboard["buttons"].append(
            [
                {
                    "action": {
                        "type": "callback",
                        "payload": json.dumps(
                            {
                                "command": "answer",
                                "answer": answer.title,
                            }
                        ),
                        "label": answer.title
                    },
                    "color": "primary"
                },
            ],
        )

    random.shuffle(answers_keyboard["buttons"])

    answers_keyboard["buttons"].append(
        [
            {
                "action": {
                    "type": "callback",
                    "payload": json.dumps(
                            {"command": "end"}
                    ),
                    "label": "Закончить игру"
                },
                "color": "negative"
            },
        ],
    )

    return json.dumps(answers_keyboard)
