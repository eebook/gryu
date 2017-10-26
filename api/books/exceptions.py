from ..common.exceptions import APIException


class BooksException(APIException):
    errors_map = {
        'book_name_conflict': {
            'message': 'Book name is already in use.',
            'type': 'bad_request'
        }
    }
