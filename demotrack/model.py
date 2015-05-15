import logging

from .data import DefinedTable


logger = logging.getLogger(__name__)


def ensure_tables():
    """When called, ensure that all the tables that we need are created in the
    database. The real work is supplied by the DefinedTable base class
    """
    for tab in [Subject, ExpCondition]:
        logger.debug("Creating table %s", tab.get_table_name())
        tab.ensure_table()


class Subject(DefinedTable):
    """An experimental subject that we are tracking in an experimental condition
    """

    @classmethod
    def get_table_name(self):
        return "Subjects"

    @classmethod
    def get_key_name(self):
        return "subject_id"

    def __init__(
        self,
        subject_id=None,
        first_name=None,
        last_name=None,
        email=None,
        exp_condition=None
    ):
        self.subject_id = subject_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.exp_condition = exp_condition

    def errors(self):
        if not self.subject_id:
            yield "Missing subject ID"
        if not self.exp_condition:
            yield "Missing Experimental Condition"


class ExpCondition(DefinedTable):
    """A single experimental condition that any number of subjects may be a part of
    """

    @classmethod
    def get_table_name(self):
        return "Conditions"

    @classmethod
    def get_key_name(self):
        return "condition_id"

    def __init__(
        self,
        condition_id=None,
        condition_name=None,
        description=None
    ):
        self.condition_id = condition_id
        self.condition_name = condition_name
        self.description = description
