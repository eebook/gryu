from ..common.exceptions import APIException


class JobsException(APIException):
    errors_map = {
        'job_config_not_exist': {
            'message': 'Job config is not exist.',
            'type': 'not_found'
        }
    }

