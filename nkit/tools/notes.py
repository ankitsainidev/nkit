from dataclasses import dataclass
import typing as t
import enum

from ..storage.local import db as local_db

import arrow

note_db = local_db["note"]
class NoteType(enum.Enum):
	task = "task"
	update = "update"
	habit = "habit"
	think_block = "think"


@dataclass
class Note:
	id: t.Optional[int]
	ty: NoteType
	msg: str
	created_at: arrow.Arrow
	draft: bool
	resources: list
	deadline: t.Optional[arrow.Arrow]
	refer_id: t.Optional[int]
	_db = note_db

	def save_note(self) -> int:
		assert self.id is None, "already has an id"
		self.id = self._db.insert(dict(
			ty=self.ty.name,
			msg=self.msg,
			created_at=self.created_at.datetime,
			draft=self.draft,
			resources="\n".join(self.resources),
			deadline=None if self.deadline is None else self.deadline.datetime,
			refer_id=self.refer_id
		))

		assert self.id is not None
		return self.id

def get_recent(limit: int=5) -> t.List[Note]:
	results = note_db.find(order_by="-created_at", _limit=limit)
	notes = []
	for result in results:
		notes.append(Note(
			id=result['id'],
			ty=NoteType.__members__[result['ty']],
			msg=result['msg'],
			created_at=result['created_at'],
			draft=result['draft'],
			resources=result['resources'].split('\n'),
			deadline=result['deadline'],
			refer_id=result['refer_id']
		))


	return notes

def delete(id: int) -> bool:
	return note_db.delete(id=id)
