from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """
    Паджинатор, позволяющий ограничивать количество
    объектов в результате.
    - параметр строки: 'limit'.
    """

    page_size_query_param = "limit"
    max_page_size = 100
