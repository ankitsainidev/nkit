import typing as t
from pydantic import BaseModel
import enum
import arrow

class NoteType(enum.Enum):
	task = "task"
	update = "update"
	habit = "habit"
	think_block = "think"

class NoteCreate(BaseModel):
	ty: NoteType
	msg: str
	created_at: arrow.Arrow
	draft: bool
	deadline: t.Optional[arrow.Arrow]
	resources: t.List[str]
	refer_id: t.Optional[int]
	completed: t.Optional[bool]

	class Config:
		arbitrary_types_allowed = True

class Note(NoteCreate):
	id: int
