from rest_framework import serializers
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    # Write_only memastikan password tidak pernah dikirim balik ke frontend saat response
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    first_name = serializers.CharField(required=True, label="Nama Lengkap")
    phone_number = serializers.CharField(required=True, label="Nomor Telepon")

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'phone_number', 'password', 'password_confirm']

    def validate(self, attrs):
        # Validasi FR-01: Memastikan konfirmasi password cocok
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password dan Konfirmasi Password tidak cocok."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        
        # FR-01: Gunakan create_user agar password di-hash secara otomatis
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            phone_number=validated_data['phone_number'],
            role='USER' 
        )
        return user