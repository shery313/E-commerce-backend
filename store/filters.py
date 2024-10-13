import django_filters
from .models import Product, Color, Size

class ProductFilter(django_filters.FilterSet):
    # Add a filter for colors
    color = django_filters.CharFilter(
        field_name='color__name',
        lookup_expr='icontains',
        label="Color"
    )

    # Add a filter for sizes
    size = django_filters.CharFilter(
        field_name='size__name',
        lookup_expr='icontains',
        label="Size"
    )

    # Other existing filters
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = django_filters.CharFilter(field_name="category__title", lookup_expr='icontains')
    brand = django_filters.CharFilter(field_name="brand", lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['category', 'brand', 'min_price', 'max_price', 'color', 'size']
