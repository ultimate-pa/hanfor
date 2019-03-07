""" 

@copyright: 2017 Samuel Roth <samuel@smel.de>
@licence: GPLv3
"""
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

from reqtransformer import Pattern
from static_utils import pickle_dump_obj_to_file, pickle_load_from_dump

PATTERN_EXAMPLES = [
    {'label': 'Invariant', 'desc': 'it is always the case that if "{R}" holds, then "{S}" holds as well'},
    {'label': 'Invariant', 'desc': 'it is always the case that if yolo holds, then swag holds as well'},
    {'label': 'Absence', 'desc': 'it is never the case that "{R}" holds'},
    {'label': 'Universality', 'desc': 'it is always the case that "{R}" holds'},
    {'label': 'Existence', 'desc': '"{R}" eventually holds'},
    {'label': 'BoundedExistence', 'desc': 'transitions to states in which "{R}" holds occur at most twice'},
    {'label': 'Precedence', 'desc': 'it is always the case that if "{R}" holds then "{S}" previously held'},
    {'label': 'PrecedenceChain1-2',
     'desc': 'it is always the case that if "{R}" holds and is succeeded by "{S}", then "{T}" previously held'},
    {'label': 'PrecedenceChain2-1',
     'desc': 'it is always the case that if "{R}" holds then "{S}" previously held and was preceded by "{T}"'},
    {'label': 'Response', 'desc': 'it is always the case that if "{R}" holds then "{S}" eventually holds'},
    {'label': 'ResponseChain1-2',
     'desc': 'it is always the case that if "{R}" holds then "{S}" eventually holds and is succeeded by "{T}"'},
    {'label': 'ResponseChain2-1',
     'desc': 'it is always the case that if "{R}" holds and is succeeded by "{S}", then "{T}" eventually holds after '
             '"{S}"'},
    {'label': 'ConstrainedChain',
     'desc': 'it is always the case that if "{R}" holds then "{S}" eventually holds and is succeeded by "{T}", '
             'where "{U}" does not hold between "{S}" and "{T}"'},
    {'label': 'MinDuration',
     'desc': 'it is always the case that once "{R}" becomes satisfied, it holds for at least "{S}" time units'},
    {'label': 'MaxDuration',
     'desc': 'it is always the case that once "{R}" becomes satisfied, it holds for less than "{S}" time units'},
    {'label': 'BoundedRecurrence',
     'desc': 'it is always the case that "{R}" holds at least every "{S}" time units'},
    {'label': 'BoundedResponse',
     'desc': 'it is always the case that if "{R}" holds, then "{S}" holds after at most "{T}" time units'},
    {'label': 'BoundedInvariance',
     'desc': 'it is always the case that if "{R}" holds, then "{S}" holds for at least "{T}" time units'},
    {'label': 'TimeConstrainedMinDuration',
     'desc': 'if {R} holds for at least {S} time units, then {T} holds afterwards for at least {U} time units'},
    {'label': 'TimeConstrainedInvariant',
     'desc': 'if {R} holds for at least {S} time units, then {T} holds afterwards'},
    {'label': 'ConstrainedTimedExistence',
     'desc': 'it is always the case that if {R} holds, then {S} holds after at most {T} time units for '
             'at least {U} time units'},
    {'label': 'NotFormalizable', 'desc': 'Some non formalizable Text'}
]

SCOPE_EXAMPLES = [
    {'label': 'GLOBALLY', 'desc': 'Globally foo'},
    {'label': 'GLOBALLY', 'desc': 'it is always'},
    {'label': 'GLOBALLY', 'desc': 'it is never'},
    {'label': 'GLOBALLY', 'desc': 'it will never'},
    {'label': 'GLOBALLY', 'desc': 'in all cases'},
    {'label': 'GLOBALLY', 'desc': 'in no case'},
    {'label': 'BEFORE', 'desc': 'Before foo'},
    {'label': 'AFTER', 'desc': 'After foo'},
    {'label': 'BETWEEN', 'desc': 'Between foo and foo'},
    {'label': 'AFTER_UNTIL', 'desc': 'After foo until foo'}
]


class SvmPatternClassifier:
    def __init__(self):
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

    def load(self, location):
        self.pattern_pipeline = pickle_load_from_dump(location)
        self.scope_pipeline = pickle_load_from_dump(location)

    def store(self, location):
        pickle_dump_obj_to_file(self.pattern_pipeline, location)
        pickle_dump_obj_to_file(self.scope_pipeline, location)

    def load_training_set(self, doc_list, mapping):
        """ Returns a training_data dictionary from a documents list.

        :param mapping: Mapping label_name -> int
        :type mapping: dict
        :param doc_list: A list documents (one document is {'desc': 'the doc text string', 'label': 'label_name'})
        :type doc_list: list
        :return:
        :rtype:
        """
        training_data = dict()
        training_data['labels'] = []
        training_data['data'] = []

        for document in doc_list:
            training_data['data'].append(document['desc'])
            training_data['labels'].append(mapping[document['label']])

        return training_data

    def train(self):
        # todo: train using a labeled session. This is only pseudo training data.
        print('start training svm.')
        training_set = self.load_training_set(PATTERN_EXAMPLES, self.pattern_name_mapping)
        self.pattern_pipeline.fit(training_set['data'], training_set['labels'])
        training_set = self.load_training_set(SCOPE_EXAMPLES, self.scope_name_mapping)
        self.scope_pipeline.fit(training_set['data'], training_set['labels'])

    def predict_catregory(self, description):
        raise NotImplementedError('Predicting a category is not implemented yet.')

    def predict_scope(self, description, n=5):
        """ Returns a list of the top n predicted scope names.

        :param n:
        :type n:
        :param description:
        :type description:
        :return:
        :rtype:
        """
        if n > len(self.scope_names):
            n = len(self.scope_names)

        decision_function = self.scope_pipeline.decision_function((description,))
        scopes = self.get_top_n_predictions(decision_function, n, self.scope_names)
        result = []
        for scope in scopes:
            scope_id = self.scope_name_mapping[scope]
            result.append((scope, self.scope_instances[scope_id]))
        return result[:n]

    def predict_pattern(self, description, n=5, category=None):
        """ Returns a list of the top n predicted pattern names.

        :param description:
        :type description:
        :param n:
        :type n:
        :return:
        :rtype:
        """
        if n > len(self.pattern_names):
            n = len(self.pattern_names)
        decision_function = self.pattern_pipeline.decision_function((description,))

        # Get the predicted patterns
        patterns = self.get_top_n_predictions(decision_function, len(self.pattern_names), self.pattern_names)
        result = []
        for pattern in patterns:
            pattern_id = self.pattern_name_mapping[pattern]
            result.append(Pattern(self.pattern_names[pattern_id], self.pattern_patterns[pattern_id]))
        return result[:n]

    def get_top_n_predictions(self, decision_function, n, label_names):
        """ Get the top n label_names from a decision function (1:n ndarray) descending by confidence.

        :type decision_function: ndarray
        :param n: Number of labels in the result
        :type n: int
        :param label_names: List of the label names.
        :type label_names: list
        :return: List of top n label names.
        :rtype: list
        """
        result = []
        for index, score in enumerate(decision_function[0]):
            # add the label name with its score to the result.
            result.append((score, label_names[index]))

        # sort by importance
        result.sort(reverse=True)

        # throw away the scores.
        result = [p[1] for p in result]

        return result[:n]
