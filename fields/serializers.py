from rest_framework import serializers
from .models import Field

class FieldSerializer(serializers.ModelSerializer):
    # Field tambahan untuk menampilkan label jenis olahraga yang lebih mudah dibaca
    sport_type_label = serializers.CharField(source='get_sport_type_display', read_only=True)

    class Meta:
        model = Field
        fields = [
            'id', 
            'name', 
            'sport_type', 
            'sport_type_label', 
            'capacity', 
            'price_weekday', 
            'price_weekend', 
            'image', 
            'is_active'
        ]