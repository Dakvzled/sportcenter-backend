from rest_framework import generics
from .models import Field
from .serializers import FieldSerializer

# API untuk menampilkan daftar seluruh lapangan (Katalog)
class FieldListView(generics.ListAPIView):
    queryset = Field.objects.filter(is_active=True) # Hanya tampilkan lapangan yang aktif
    serializer_class = FieldSerializer

# API untuk menampilkan detail satu lapangan spesifik
class FieldDetailView(generics.RetrieveAPIView):
    queryset = Field.objects.filter(is_active=True)
    serializer_class = FieldSerializer