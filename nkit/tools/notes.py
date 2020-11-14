from dataclasses import dataclass
import typing as t
import enum

from ..storage.local import SessionLocal, Note as DbNote, NoteType

import arrow



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
	completed: t.Optional[bool] = None

	def save_note(self) -> int:
		assert self.id is None, "already has an id"
		db = SessionLocal()
		note = DbNote(
			ty=self.ty.name,
			msg=self.msg,
			created_at=self.created_at.datetime,
			draft=self.draft,
			resources="\n".join(self.resources),
			deadline=None if self.deadline is None else self.deadline.datetime,
			completed=self.completed,
			refer_id=self.refer_id
		)
		db.add(note)
		db.commit()
		db.refresh(note)

		self.id = note.id
		assert self.id is not None
		db.close()
		return note.id

def get_recent(limit: int=5) -> t.List[Note]:
	db = SessionLocal()
	results = db.query(DbNote).order_by(DbNote.created_at.asc()).limit(limit).all()
	notes = []
	for result in results:
		notes.append(Note(
			id=result.id,
			ty=result.ty,
			msg=result.msg,
			created_at=arrow.get(result.created_at),
			draft=result.draft,
			resources=result.resources.split('\n'),
			deadline=arrow.get(result.deadline),
			completed=result.completed,
			refer_id=result.refer_id
		))
	db.close()
	return notes

def delete(id: int) -> bool:
	db = SessionLocal()
	print("deleted: ",  db.query(DbNote).filter(DbNote.id==id).delete())
	db.commit()
	db.close()
	return True
