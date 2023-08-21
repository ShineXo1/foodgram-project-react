from rest_framework.pagination import PageNumberPagination


class FoodgramPafination(PageNumberPagination):
    page_size_query_param = 'limit'
    max_page_size = 50
    page_size = 10
