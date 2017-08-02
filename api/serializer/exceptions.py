from ..libs.exceptions import EEBookAPIException


class UserException(EEBookAPIException):

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


class OSSAuthException(EEBookAPIException):

    errors_map = {
        'signature_expired': {
            'message': ('The signature you provided is expired. Signature will expires in 3 hours '
                        'since it is created.'),
            'type': 'forbidden'
        },
        'signature_not_match': {
            'message': ('The request signature we calculated does not match the signature you '
                        'provided. Check your key and signing method.'),
            'type': 'forbidden'
        },
        'token_not_exist': {
            'message': 'The token provided does not exist',
            'type': 'forbidden'
        },
        'username_not_exist': {
            'message': 'The username provided in the signed url does not exist',
            'type': 'forbidden'
        },
        'bucket_not_allowed': {
            'message': 'The current user is not allowed to operate the requested bucket',
            'type': 'forbidden'
        }
    }
