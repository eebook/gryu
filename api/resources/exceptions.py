from ..common.exceptions import APIException


class ResourcesException(APIException):
    errors_map = {
        'resource_name_conflict': {
            'message': 'Name is already in use.',
            'type': 'bad_request'
        },
        'resource_name_invalid': {
            'message': 'Name should start with letter and can contain number, letter, dot, '
            'underscore and dash.',
            'type': 'bad_request'
        }
    }

