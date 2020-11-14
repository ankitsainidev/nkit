# TODO: file needs split
import dataset
import enum
from ..constants import APP_DIR
from sqlalchemy import Column, Integer, Enum, Text, DateTime, Boolean, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class NoteType(enum.Enum):
	task = "task"
	update = "update"
	habit = "habit"
	think_block = "think"

class Note(Base):
	__tablename__ = "notes"


	id = Column('id', Integer, primary_key=True)
	ty = Column('ty', Enum(NoteType), nullable=False)
	msg = Column('msg', Text, nullable=False)
	created_at = Column('created_at', DateTime, nullable=False)
	draft = Column('draft', Boolean, nullable=False)
	deadline = Column('deadline', DateTime, nullable=True)
	resources = Column('resources', Text, nullable=False)
	refer_id = Column('refer_id', ForeignKey('notes.id'), nullable=True)
	completed = Column('completed', Boolean, nullable=True)


DB_PATH = f"sqlite:///{APP_DIR/'notes.db'}"

engine = create_engine(DB_PATH, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine) # type: ignore
