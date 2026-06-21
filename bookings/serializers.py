from rest_framework import serializers
from .models import Booking
from fields.models import Field
from django.db.models import Q
from datetime import datetime, date
from decimal import Decimal

# ==========================================
# 1. SERIALIZER UTAMA (CREATE BOOKING)
# ==========================================
class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id', 'field', 'booking_date', 'start_time', 'end_time', 
            'participants_count', 'notes', 'total_price', 'status', 'payment_deadline'
        ]
        # Kolom ini dikunci agar tidak bisa dimanipulasi manual oleh user dari frontend
        read_only_fields = ['id', 'total_price', 'status'] 

    def validate(self, data):
        # 1. Validasi Logika Waktu
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError({"end_time": "Jam selesai harus lebih besar dari jam mulai."})
        
        # 2. Algoritma Anti Double-Booking (Mencari irisan waktu)
        overlapping_bookings = Booking.objects.filter(
            field=data['field'],
            booking_date=data['booking_date'],
            status__in=['PENDING', 'WAITING_CONFIRMATION', 'CONFIRMED']
        ).filter(
            Q(start_time__lt=data['end_time']) & Q(end_time__gt=data['start_time'])
        )
        
        if overlapping_bookings.exists():
            raise serializers.ValidationError({
                "waktu": "Gagal. Slot waktu pada jam tersebut sudah dipesan atau sedang dalam proses pembayaran."
            })
            
        return data

    def create(self, validated_data):
        field = validated_data['field']
        booking_date = validated_data['booking_date']
        start_time = validated_data['start_time']
        end_time = validated_data['end_time']

        # 3. Kalkulasi Durasi (dalam Jam)
        delta = datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)
        duration_hours = delta.total_seconds() / 3600

        # 4. Kalkulasi Harga Dinamis (Weekday: 0-4, Weekend: 5-6)
        if booking_date.weekday() >= 5:
            price_per_hour = field.price_weekend
        else:
            price_per_hour = field.price_weekday
            
        total_price = price_per_hour * Decimal(str(duration_hours))

        # 5. Simpan ke Database
        booking = Booking.objects.create(
            user=self.context['request'].user, 
            total_price=total_price,
            **validated_data
        )
        return booking


# ==========================================
# 2. SERIALIZER KHUSUS (UPLOAD BUKTI TRANSFER)
# ==========================================
class PaymentProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        # Serializer ini SANGAT DIBATASI, hanya membuka akses ke kolom gambar.
        fields = ['payment_proof']

    def update(self, instance, validated_data):
        # 1. Simpan gambar yang diunggah
        instance.payment_proof = validated_data.get('payment_proof', instance.payment_proof)
        
        # 2. LOGIKA KRITIS: Pindahkan status agar selamat dari Auto-Cancel
        instance.status = 'WAITING_CONFIRMATION'
        
        instance.save()
        return instance