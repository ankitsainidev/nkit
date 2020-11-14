# TODO: file needs split
from .. import constants as c
import typing as t
import arrow
from .. import models
from ..exceptions import CrudException
from sqlalchemy import Column, Integer, Enum, Text, DateTime, Boolean, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# TODO: add command to support all fields
class Note(Base):
	__tablename__ = "notes"

	id = Column('id', Integer, primary_key=True)
	ty = Column('ty', Enum(models.NoteType), nullable=False)
	msg = Column('msg', Text, nullable=False)
	created_at = Column('created_at', DateTime, nullable=False)
	draft = Column('draft', Boolean, nullable=False)
	deadline = Column('deadline', DateTime, nullable=True)
	resources = Column('resources', Text, nullable=False)
	refer_id = Column('refer_id', ForeignKey('notes.id'), nullable=True)
	completed = Column('completed', Boolean, nullable=True)

	@classmethod
	def from_pydantic(cls, note: t.Union[models.NoteCreate, models.Note]):
		return cls(
			id=note.id if isinstance(note, models.Note) else None,
			ty=note.ty,
			msg=note.msg,
			created_at=note.created_at.datetime,
			draft=note.draft,
			deadline=note.deadline.datetime if note.deadline else None,
			resources="\n".join(note.resources),
			refer_id=note.refer_id,
			completed=note.completed
			)

	def to_pydantic(self) -> models.Note:
		return models.Note(
			id=self.id,
			ty=self.ty,
			msg=self.msg,
			created_at=arrow.get(self.created_at),
			draft=self.draft,
			deadline=arrow.get(self.deadline),
			resources=[a for a in self.resources.split("\n") if len(a)>0],
			refer_id=self.refer_id,
			completed=self.completed
			)



DB_PATH = f"sqlite:///{c.APP_DIR/'notes.db'}"

engine = create_engine(DB_PATH, echo=c.DEBUG, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine) # type: ignore


class BaseDb():
	def __enter__(self):
		self.db = SessionLocal()
		return self
	def __exit__(self, _exc_type, _exc_value, _tb):
		self.db.close()


class NoteDb(BaseDb):
	def insert(self, note: models.NoteCreate) -> models.Note:
		db_note = Note.from_pydantic(note)
		self.db.add(db_note)
		self.db.commit()
		self.db.refresh(db_note)
		return db_note.to_pydantic()
	
	def get_recent(self, limit: int) -> t.List[models.Note]:
		db_notes = self.db.query(Note).order_by(Note.created_at.desc()).limit(limit).all()
		return [db_note.to_pydantic() for db_note in db_notes]

	def delete_note(self, note: models.Note):
		return self.delete_by_id(id=note.id)

	def delete_by_id(self, id: int):
		rt = self.db.query(Note).filter(Note.id==id).delete()
		self.db.commit()
		if rt == 0:
			raise CrudException("Note is not in db", id)
		return rt == 1

