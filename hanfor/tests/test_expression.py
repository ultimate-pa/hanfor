from hanfor import db
from hanfor.boogie_parsing import boogie_parsing
from hanfor.models import Tag, Variable, Expression
from hanfor.tests.test_environment import TestEnvironment


class TestExpression(TestEnvironment):

    def test_parsing(self):
        strings = [
            ('this != that', boogie_parsing.BoogieType.bool),
            ('this != that', boogie_parsing.BoogieType.bool),
            ('this != that', boogie_parsing.BoogieType.bool),
            ('that == 12', boogie_parsing.BoogieType.bool),
            ('42', boogie_parsing.BoogieType.int),
            ('123.23', boogie_parsing.BoogieType.real)
        ]

        for string, expected_type in strings:
            exp = Expression()
            db.session.add(exp)
            exp.input_string = string
            exp.parse_expression()

            self.assertTrue(exp in db.session)

            ret_exp = Expression().query.filter_by(id=exp.id).first()  # type: Expression
            self.assertEqual(string, ret_exp.input_string)
            self.assertEqual(expected_type, ret_exp.derived_type)


    def test_parsing_type_inference(self):
        string = "(((((b + a) + d) * 23) < 4) && x ==> y )"
        var_a = Variable()
        var_a.name = 'a'
        var_a.type = 'unknown'
        db.session.add(var_a)
        db.session.commit()
        exp = Expression()
        db.session.add(exp)
        exp.input_string = string
        exp.parse_expression()

        expected_var_types = [
            ('a', boogie_parsing.BoogieType.int),
            ('b', boogie_parsing.BoogieType.int),
            ('d', boogie_parsing.BoogieType.int),
            ('x', boogie_parsing.BoogieType.bool),
            ('y', boogie_parsing.BoogieType.bool),
        ]

        for var_name, expected_var_type in expected_var_types:
            var = Variable.query.filter_by(name=var_name).first()
            self.assertEqual(expected_var_type.name, var.type)
