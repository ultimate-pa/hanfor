import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

import utils
from guesser.AbstractGuesser import AbstractGuesser
from guesser.Guess import Guess
from guesser.guesser_registerer import register_guesser
from reqtransformer import ScopedPattern, Scope, Pattern, Requirement


class SimpleSVMGuesser(AbstractGuesser):
    def __init__(self, requirement, variable_collection, app):
        super().__init__(requirement, variable_collection, app)
        self.pattern_pipeline = Pipeline([
            ('vect', CountVectorizer(
                min_df=0.000,
                max_df=0.2,
                strip_accents='unicode',
                max_features=20000,
                ngram_range=(1, 3))),
            ('tfidf', TfidfTransformer()),
            ('clf', SGDClassifier(
                loss='epsilon_insensitive',
                penalty='l2',
                alpha=0.005,
                max_iter=7,
                random_state=42,
                verbose=100,
                n_jobs=-1
            )),
        ])
        self.scope_pipeline = Pipeline([
            ('vect', CountVectorizer(
                min_df=0.000,
                max_df=0.2,
                strip_accents='unicode',
                max_features=20000,
                ngram_range=(1, 3))),
            ('tfidf', TfidfTransformer()),
            ('clf', SGDClassifier(
                loss='epsilon_insensitive',
                penalty='l2',
                alpha=0.005,
                max_iter=7,
                random_state=42,
                verbose=100,
                n_jobs=-1
            )),
        ])
        self.pattern_names = []
        self.pattern_patterns = []
        for name, pattern in Pattern.name_mapping.items():
            self.pattern_names.append(name)
            self.pattern_patterns.append(pattern)
        self.pattern_patterns_mapping = dict((key, value) for value, key in enumerate(self.pattern_patterns))
        self.pattern_name_mapping = dict((key, value) for value, key in enumerate(self.pattern_names))
        self.scope_names = [
            'GLOBALLY', 'BEFORE', 'AFTER', 'BETWEEN', 'AFTER_UNTIL'
        ]
        self.scope_instances = [
            'Globally', 'Before "{P}"', 'After "{P}"', 'Between "{P}" and "{Q}"', 'After "{P}" until "{Q}"'
        ]
        self.scope_name_mapping = dict((key, value) for value, key in enumerate(self.scope_names))
        self.training_data = self.generate_training_set()

    def guess(self):
        pass

    def train(self):
        pass

    def generate_training_set(self):
        training_data = {
            'data': list(),
            'label': list()
        }
        # Load the requirements
        filenames = utils.get_filenames_from_dir(self.app.config['REVISION_FOLDER'])
        # Check for Requirements with formalizations and add them to the training data.
        for filename in filenames:
            req = utils.pickle_load_from_dump(filename)  # type: Requirement
            if type(req) is Requirement:
                # Todo: Preprocess the description, like replace vars "s_sdf_56_dodo" by "var_a"
                # Todo: Preprocess desc: replace := by "assign", etc.
                for formalization in req.formalizations:
                    training_data['data'].append(
                        req.description
                    )
                    training_data['label'].append(
                        self.scope_name_mapping[formalization.scoped_pattern.scope.name]
                    )
        return training_data
