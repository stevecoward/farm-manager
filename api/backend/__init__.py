import os
from peewee import SqliteDatabase, Model, _ConnectionState
from contextvars import ContextVar


class PeeweeConnectionState(_ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__("_state", db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]


db_state_default = {"closed": None, "conn": None, "ctx": None, "transactions": None}
db_state = ContextVar("db_state", default=db_state_default.copy())

if os.path.exists('TESTING'):
    db = SqliteDatabase('tracker-test.db', check_same_thread=False)
else:
    db = SqliteDatabase('tracker.db', check_same_thread=False)
db._state = PeeweeConnectionState()


class BaseModel(Model):
    class Meta:
        database = db
