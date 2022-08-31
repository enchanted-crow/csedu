class InvalidInputException(Exception):
    """Invalid input."""

    def __str__(self):
        return 'Invalid input.'


class InvalidQueryTypeException(InvalidInputException):
    """Invalid query type. Query type must be 'A', 'AAAA', 'NS', 'CNAME' or 'MX'"""

    def __str__(self):
        return 'Invalid query type. Query type must be \'A\', \'AAAA\', \'NS\', \'CNAME\' or \'MX\''


class InvalidHostnameException(InvalidInputException):
    """Invalid hostname."""

    def __str__(self):
        return 'Invalid hostname.'


class TimeoutException(Exception):

    def __str__(self):
        return 'TIMEOUT!'
