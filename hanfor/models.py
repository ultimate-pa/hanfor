from flask import current_app, url_for
from hanfor import db
import hanfor.boogie_parsing.boogie_parsing as boogie_parsing

expressions_variables = db.Table('expressions_variables',
    db.Column('variable_id', db.Integer, db.ForeignKey('variable.id')),
    db.Column('expression_id', db.Integer, db.ForeignKey('expression.id'))
)

expressions_tags = db.Table('expressions_tags',
    db.Column('expression_id', db.Integer, db.ForeignKey('expression.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

formalizations_expressions = db.Table('formalizations_expressions',
    db.Column('formalization_id', db.Integer, db.ForeignKey('formalization.id')),
    db.Column('expression_id', db.Integer, db.ForeignKey('expression.id'))
)

formalizations_tags = db.Table('formalizations_tags',
    db.Column('formalization_id', db.Integer, db.ForeignKey('formalization.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class Variable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    type = db.Column(db.String(64), index=True)
    value = db.Column(db.String(128))
    expressions = db.relationship('Expression', secondary=expressions_variables, back_populates='variables')

    def __repr__(self):
        return 'Variable(name="{name}", type="{type}", value="{value}")'.format(
            name=self.name, type=self.type, value=self.value
        )

    @staticmethod
    def get_boogie_type_env():
        mapping = {
            'bool': boogie_parsing.BoogieType.bool,
            'int': boogie_parsing.BoogieType.int,
            'real': boogie_parsing.BoogieType.real,
            'unknown': boogie_parsing.BoogieType.unknown,
            'error': boogie_parsing.BoogieType.error
        }
        type_env = dict()
        for var in Variable.query.all():
            if var.type is None:
                type_env[var.name] = mapping['unknown']
            elif var.type.lower() in mapping.keys():
                type_env[var.name] = mapping[var.type.lower()]
            elif var.type == 'CONST':
                # Check for int, real or unknown based on value.
                try:
                    x = float(var.value)
                except ValueError:
                    type_env[var.name] = mapping['unknown']
                    continue

                if '.' in var.value:
                    type_env[var.name] = mapping['real']
                    continue

                type_env[var.name] = mapping['int']
            else:
                type_env[var.name] = mapping['unknown']

        return type_env

    def to_dict(self):
        result = {
            'id': self.id,
            'name': self.name,
            'type': self.type
            # 'tags': [tag.name for tag in self.tags]
            # 'type_inference_errors': @TODO
            # type_inference_errors
            # type_inference_errors
        }

        return result


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    color = db.Column(db.String(32), index=True)
    expressions = db.relationship('Expression', secondary=expressions_tags, back_populates='tags')


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)


class Expression(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_string = db.Column(db.String(2048))
    parsed_string = db.Column(db.String(2048))
    variables = db.relationship('Variable', secondary=expressions_variables, back_populates='expressions')
    var_prefix = 'var_id_'
    tags = db.relationship('Tag', secondary=expressions_tags, lazy='subquery', back_populates='expressions')
    formalizations = db.relationship('Formalization', secondary=formalizations_expressions, lazy='subquery', back_populates='expressions')
    derived_type = db.Column(db.PickleType)

    def parse_expression(self):
        """ 1. Boogie parse the expressions input_string.
            2. Check if used variables exist and Create missing Variables.
            4. Add used variables to self.variables.
            5. Store type inference results.
            5. Store parsed_string:
               A parsed version of input_string with variables replaced by var_id_<id> in expression.
        """
        parser = boogie_parsing.get_parser_instance()
        tree = parser.parse(self.input_string)

        # Clear former parsing
        self.variables.clear()
        replacement_mapping = dict()

        self.derived_type, type_env = boogie_parsing.infer_variable_types(
            tree, Variable.get_boogie_type_env()).derive_type()
        used_variable_names = set(boogie_parsing.get_variables_list(tree))
        
        for var_name in used_variable_names:
            var = Variable.query.filter_by(name=var_name).first()
            if var is None: # Create missing variable.
                var = Variable(name=var_name)
                db.session.add(var)
                db.session.flush()

            if var.type is None or var.type == 'unknown':
                var.type = type_env[var.name].name
            # TODO: Add allowed_types to expression and check if derived type is allowed.
            if var.type != type_env[var.name].name:
                # Set type of variable not equal the derived type.
                print('derived type inference error.')

            replacement_mapping[var.name] = '{}{}'.format(Expression.var_prefix, var.id)
            self.variables.append(var)
        self.parsed_string = boogie_parsing.replace_var_in_expression(self.input_string, replacement_mapping, parser)
        db.session.commit()

    def __repr__(self):
        return 'Expression(string="{}")'.format(self.input_string)

    def __str__(self):
        result = str(self.parsed_string)

        for var_id, replacement in self.get_var_mapping().items():
            result = result.replace(var_id, replacement)

        return result

    def get_var_mapping(self):
        mapping = dict()
        for var in self.variables:

            mapping['{}{}'.format(Expression.var_prefix, var.id)] = var.name
        return mapping

    def has_type_inference_error(self):
        return self.derived_type == boogie_parsing.BoogieType.error


class Scope(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    scope = db.Column(db.String(1024), index=True)
    allowed_types = db.Column(db.PickleType)


class Pattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    pattern = db.Column(db.String(1024), index=True)
    allowed_types = db.Column(db.PickleType)


class Formalization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scope_id = db.Column(db.Integer, db.ForeignKey('scope.id'))
    scope = db.relationship("Scope")
    pattern_id = db.Column(db.Integer, db.ForeignKey('pattern.id'))
    pattern = db.relationship("Pattern")
    expressions = db.relationship('Expression', secondary=formalizations_expressions, back_populates='formalizations')
    tags = db.relationship('Tag', secondary=formalizations_tags)


class CsvEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    header_id = db.Column(db.Integer, db.ForeignKey('csv_entry.id'))
    header = db.relationship("CsvEntry")
    text = db.Column(db.Text)
    order = db.Column(db.Integer)

    def is_header(self):
        return self.header_id is None


class Requirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rid = db.relationship('CsvEntry', lazy=True)
    formalizations = db.relationship('Formalization', lazy=True)
    csv_entries = db.relationship('CsvEntry', lazy=True)
    description = db.relationship('CsvEntry', lazy=True)
    type_in_csv = db.relationship('CsvEntry', lazy=True)
    pos_in_csv = db.Column(db.Integer)
    tags = db.relationship('Tag', lazy=True)
    status = db.relationship('Status', lazy=True)
