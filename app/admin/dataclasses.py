from dataclasses import dataclass


@dataclass
class Admin:
    id: int
    email: str
    password: str | None = None

    @classmethod
    def from_session(cls, session: dict | None):
        if session:
            return cls(
                id=session["admin"]["id"],
                email=session["admin"]["email"],
            )
        return None
