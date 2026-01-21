from django.urls import path

from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product-list'),
    path('search/', views.ProductSearchView.as_view(), name='product-search'),
    # Accept UUID or slug as identifier (frontend may use either)
    path('<str:identifier>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('<str:identifier>/related/', views.ProductRelatedView.as_view(), name='product-related'),
]

# Category URL patterns (to be included in main urls.py)
category_urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category-list'),
    path('<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('<slug:parent_slug>/subcategories/', views.SubcategoryListView.as_view(), name='subcategory-list'),
]

# Brands URL patterns (for product brand names)
brands_urlpatterns = [
    path('', views.BrandListView.as_view(), name='brand-list'),
]

# Brand showcase URL patterns (for homepage brand cards)
brand_showcase_urlpatterns = [
    path('', views.BrandShowcaseView.as_view(), name='brand-showcase'),
]
