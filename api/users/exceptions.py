from ..common.exceptions import APIException


class UserException(APIException):

    errors_map = {
        'user_not_exist': {
            'message': 'User {} does not exist.'
        },
        'user_not_active': {
            'message': 'User {} is not active.'
        },
        'invalid_old_password': {
            'message': 'Invalid old password'
        },
        'social_access_key_out_of_date': {
            'message': 'Social access key is out of date'
        },
        'socialuser_data_invalid': {
            'message': 'Social user data is invalid'
        },
        'mobile_already_exist': {
            'message': 'User with this Mobile already exists.',
            'type': 'bad_request'
        },
        'username_already_exist': {
            'message': 'User with this username already exists.',
            'type': 'bad_request'
        },
        'email_already_exist': {
            'message': 'User with this email already registered.',
            'type': 'bad_request'
        },
        'provided_credentials_not_correct': {
            'message': 'username/email or password is incorrect.'
        },
        'authentication_credentials_not_provided': {
            'message': 'Authentication credentials were not provided.',
            'type': 'unauthorized'
        },
    }

