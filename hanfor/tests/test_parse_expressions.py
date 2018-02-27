import boogie_parsing
from unittest import TestCase
from lark.lexer import UnexpectedInput


class TestParseExpressions(TestCase):
    def test_parse_real_numbers(self):
        parser = boogie_parsing.get_parser_instance()
        expression = '1.1 < 0.0'
        parseable = True
        try:
            tree = parser.parse(expression)
        except:
            parseable = False
        self.assertEqual(parseable, True)
        # pydot__tree_to_png(tree, "parse_tree.png")

    def test_reconstruction_real_numbers(self):
        parser = boogie_parsing.get_parser_instance()
        expressions = [
            '1.1<0.0',
            '(1.1<0.0)&&(1.1<0.0)&&(1.1<0.0)',
            '((1.1<0.0)&&(1.1<0.0))||(1.1<0.0)',
            '((-1.1<-0.0)&&(-1.1<-0.0))||(-1.1<-0.0)',
            '((-1.2341<-0.2340)&&(-1.1<-0.000023498))||(-1234.1<-23.0)',
            '((-1.2341<-0.2340)&&(BAR<-0.000023498))==>(-1234.1<FOO)',
            '((-1.2341<-0.2340)&&(BAR<-0.000023498))<==>(-1234.1<FOO)',
            '((-1.2341>-0.2340)&&(BAR>-0.000023498))==>(1234.1>FOO)',
            '((-1.2341==-0.2340)==(BAR<-0.000023498))==>(-1234.1==FOO)',
            '((-1.2341<-0.2340)&&(BAR<-0.000023498))==>(-1234.1<FOO)',
            '((-1.2341<-0.2340)&&(BAR+-2.000023498))==>(-1234.1<FOO)',
        ]
        for index, expression in enumerate(expressions):
            try:
                tree = parser.parse(expression)
                reconstructed_expression = boogie_parsing.Reconstructor(parser).reconstruct(tree)
            except UnexpectedInput as e:
                print('Error in expression:\n{}\n{}^'.format(expression, ' '*(e.column-1)))
                raise e
            self.assertEqual(expression, reconstructed_expression, 'Reconstructed expression should match origin.')
