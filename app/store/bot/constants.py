import json


CREATE_GAME_KEYBOARD = {
    "inline": False,
    "buttons": [
        [
            {
                "action": {
                    "type": "callback",
                    "payload": json.dumps(
                        {"command": "create"}
                    ),
                    "label": "Создать игру"
                },
                "color": "positive"
            },
        ],
    ],
}

START_GAME_KEYBOARD = {
    "inline": False,
    "buttons": [
        [
            {
                "action": {
                    "type": "callback",
                    "payload": json.dumps(
                        {"command": "start"}
                    ),
                    "label": "Начать игру (для создателя)"
                },
                "color": "positive"
            },
        ],
        [
            {
                "action": {
                    "type": "callback",
                    "payload": json.dumps(
                        {"command": "join"}
                    ),
                    "label": "Присоединиться"
                },
                "color": "positive"
            },
        ],
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
        ]
    ]
}

END_GAME_KEYBOARD = {
    "inline": False,
    "buttons": [
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
    ],
}
