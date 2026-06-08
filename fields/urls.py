from django.urls import path
from .views import FieldListView, FieldDetailView

urlpatterns = [
    path('', FieldListView.as_view(), name='field-list'),
    path('<int:pk>/', FieldDetailView.as_view(), name='field-detail'),
]