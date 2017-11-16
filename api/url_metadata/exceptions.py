from ..common.exceptions import APIException


class UrlMetadataException(APIException):
    errors_map = {
        'url_not_support': {
            'message': 'This url is not supported',
            'type': 'bad_request'
        }
    }

