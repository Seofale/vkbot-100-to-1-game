class ColorButton:
    red = "negative"
    green = "positive"


class CommandLabel:
    create = "Создать игру"
    start = "Начать игру (для создателя)"
    end = "Закончить игру"
    join = "Присоединиться к игре"


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


create_keyboard = Keyboard(
    inline=False,
    buttons=[
        ButtonCallback(
            command="create",
            label=CommandLabel.create,
            color=ColorButton.green
        )
    ]
)

start_keyboard = Keyboard(
    inline=False,
    buttons=[
        ButtonCallback(
            command="start",
            label=CommandLabel.start,
            color=ColorButton.green
        ),
        ButtonCallback(
            command="join",
            label=CommandLabel.join,
            color=ColorButton.green
        ),
        ButtonCallback(
            command="end",
            label=CommandLabel.end,
            color=ColorButton.red
        )
    ]
)

end_keyboard = Keyboard(
    inline=False,
    buttons=[
        ButtonCallback(
            command="end",
            label=CommandLabel.end,
            color=ColorButton.red
        )
    ]
)
