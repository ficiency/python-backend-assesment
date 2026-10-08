from sqlmodel import Field, SQLModel


class TransformedWord(SQLModel, table=True):
    __tablename__ = "transforms"

    # The original word. One row is enough to skip the outside service next time.
    word: str = Field(primary_key=True)
    result: str


class StoredPayload(SQLModel, table=True):
    __tablename__ = "payloads"

    id: str = Field(primary_key=True)
    # Built from the original lists, so the same request finds this row again.
    label: str = Field(unique=True, index=True)
    output: str
