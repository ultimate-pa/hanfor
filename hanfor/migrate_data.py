import glob
import os
import pickle
import shutil
from copy import deepcopy

from reqtransformer import VariableCollection, Formalization, Requirement, Pattern

CONFIG_CHANGES = {
    'ResponseChain2-1': {'name': 'ResponseChain21'},
    'ResponseChain1-2': {'name': 'ResponseChain12'},
    'PrecedenceChain2-1': {'name': 'PrecedenceChain21'},
    'PrecedenceChain1-2': {'name': 'PrecedenceChain12'},
    'BoundedExistence': {'name': 'ExistenceBoundU'},
    'Invariant': {'name': 'Invariance'},
    'BoundedResponse': {'name': 'ResponseDelay'},
    'BoundedRecurrence': {'name': 'ReccurrenceBound'},
    'MaxDuration': {'name': 'DurationBoundU'},
    'TimeConstrainedMinDuration': {'name': 'ResponseBoundL12'},
    'BoundedInvariance': {'name': 'InvarianceBoundL2'},
    'TimeConstrainedInvariant': {'name': 'ResponseBoundL1'},
    'MinDuration': {'name': 'DurationBoundL'},
    'ConstrainedTimedExistence': {'name': 'ResponseDelayBoundL2'},
    'EdgeResponsePatternDelayed': {'name': 'EdgeResponseDelay'},
    'BndEdgeResponsePattern': {'name': 'EdgeResponseBoundL2'},
    'BndEdgeResponsePatternDelayed': {'name': 'EdgeResponseDelayBoundL2'},
    'BndEdgeResponsePatternTU ': {'name': 'EdgeResponseBoundU1'},
    'BndTriggeredEntryConditionPattern': {'name': 'TriggerResponseBoundL1'},
    'BndTriggeredEntryConditionPatternDelayed': {'name': 'TriggerResponseDelayBoundL1'}
}


# Update pattern name.
def migrate_pattern(pattern: Pattern) -> Pattern:
    if pattern is None:
        return None

    result = deepcopy(pattern)
    if result.name in CONFIG_CHANGES:
        new_name = CONFIG_CHANGES[result.name]['name']

        print(f'\tUpdate pattern name: {result.name} --> {new_name}')
        result.name = new_name

    return result


# Add attribute id to Formalization.
def migrate_formalization(id: int, formalization: Formalization) -> Formalization:
    if formalization is None:
        return None

    print(f'\tAdd attribute id to formalization: {id}')
    result = Formalization()
    result._hanfor_version = formalization._hanfor_version
    result.id = id
    result.expressions_mapping = formalization.expressions_mapping
    result.belongs_to_requirement = formalization.belongs_to_requirement
    result.type_inference_errors = formalization.type_inference_errors

    if hasattr(formalization, 'scoped_pattern'):
        result.scoped_pattern = formalization.scoped_pattern

    return result


def main() -> int:
    base_dir = 'data/daimler_cs/revision_0/'
    paths = glob.glob(base_dir + '*.pickle')

    for path in paths:
        print(f'Check file: "{os.path.basename(path)}" ...')
        is_migrated = False

        with open(path, 'rb') as file:
            object = pickle.load(file)

        if isinstance(object, VariableCollection):
            for variable_name, variable in object.collection.items():

                if not hasattr(variable, 'constraints') or variable.constraints is None:
                    continue

                for id, formalization in variable.constraints.items():
                    result = migrate_formalization(id, formalization)

                    if result is not None and hasattr(result, 'scoped_pattern') and result.scoped_pattern is not None:
                        result.scoped_pattern.pattern = migrate_pattern(result.scoped_pattern.pattern)

                    variable.constraints[id] = result
                    is_migrated = True

        elif isinstance(object, Requirement):
            for id, formalization in object.formalizations.items():
                result = migrate_formalization(id, formalization)

                if result is not None and hasattr(result, 'scoped_pattern') and result.scoped_pattern is not None:
                    result.scoped_pattern.pattern = migrate_pattern(result.scoped_pattern.pattern)

                object.formalizations[id] = result
                is_migrated = True

        else:
            print()

        if is_migrated:
            shutil.copy(path, path + '.backup')

            with open(path, 'wb') as file:
                pickle.dump(object, file)

    return 0


if __name__ == '__main__':
    main()
