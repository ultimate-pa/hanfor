from hanfor import db
from hanfor.models import Tag, Variable, Expression
from hanfor.tests.test_environment import TestEnvironment


class TestRequirement(TestEnvironment):

    def test_something(self):
        string = 'Swaggalishious'
        exp = Expression(string)
        db.session.add(exp)
        db.session.commit()

        # this works
        assert exp in db.session

        response = self.client.get("/")

        # this raises an AssertionError
        #assert ex in self.db.session