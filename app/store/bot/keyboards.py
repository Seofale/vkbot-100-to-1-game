class ColorButton:
    red = "negative"
    green = "positive"


class CommandLabel:
    join = "Присоединиться"


class CommandName:
    join = "join"


class ButtonCallback:
    def __init__(self, command: str, label: str, color: str):
        self.command = command
        self.label = label
        self.color = color

    def to_dict(self) -> dict:
        return dict(
            action=dict(
                type="callback",
                payload=dict(
                    command=self.command
                ),
                label=self.label
            ),
            color=self.color
        )


class Keyboard:
    def __init__(self, inline: bool, buttons: list[ButtonCallback]):
        self.inline = inline
        self.buttons = buttons

    def to_dict(self) -> dict:
        return dict(
            inline=self.inline,
            buttons=[[button.to_dict()] for button in self.buttons]
        )


def join_keyboard():
    return Keyboard(
        inline=True,
        buttons=[
            ButtonCallback(
                command=CommandName.join,
                label=CommandLabel.join,
                color=ColorButton.green,
            )
        ]
    )
