from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model

from .models import Booking
# 🔥 PERBAIKAN: Tambahkan AvailabilitySerializer pada import di bawah ini
from .serializers import BookingSerializer, PaymentProofSerializer, RegisterSerializer, AvailabilitySerializer

# Mengambil model User aktif di Django
User = get_user_model()

# ==========================================
# FITUR REGISTRASI PENGGUNA BARU
# ==========================================
class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny] # Terbuka untuk publik
    serializer_class = RegisterSerializer


# ==========================================
# FITUR CEK KETERSEDIAAN JADWAL (PUBLIK)
# ==========================================
# 🔥 PERBAIKAN: Kelas ini wajib ada agar React bisa mengecat merah jam yang sudah dipesan
class FieldAvailabilityView(generics.ListAPIView):
    serializer_class = AvailabilitySerializer
    permission_classes = [AllowAny]  # Siapa saja bisa akses untuk cek jadwal

    def get_queryset(self):
        # Memicu pembersihan otomatis untuk booking yang kedaluwarsa
        Booking.objects.update_expired_bookings()
        
        # Mengambil semua booking dari seluruh user
        queryset = Booking.objects.all()
        
        # Mengambil parameter filter dari URL parameter (?field=...&date=...)
        field_id = self.request.query_params.get('field')
        date_str = self.request.query_params.get('date')
        
        if field_id:
            queryset = queryset.filter(field_id=field_id)
        if date_str:
            queryset = queryset.filter(booking_date=date_str)
            
        return queryset


# ==========================================
# GOLONGAN USER BIASA (CLIENT-SIDE - FR-07, FR-08, FR-09, FR-10)
# ==========================================

# 1. Menangani Pembuatan dan Daftar Riwayat
class BookingCreateListView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        # UTAMA: Bersihkan booking expired setiap kali user melihat atau membuat booking baru
        Booking.objects.update_expired_bookings()
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')


# 2. Menangani Detail, Update Biasa, dan Hapus (DELETE)
class BookingDetailUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Bersihkan juga saat user melihat, mengubah, atau menghapus detail spesifik
        Booking.objects.update_expired_bookings()
        # Memastikan pengguna hanya bisa memodifikasi/menghapus booking milik mereka sendiri
        return Booking.objects.filter(user=self.request.user)


# 3. Menangani Logika Pembatalan Pesanan (Manual oleh User)
class BookingCancelView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        if booking.status in ['PENDING', 'WAITING_CONFIRMATION']:
            booking.status = 'CANCELLED'
            booking.save()
            return Response({"message": "Pesanan berhasil dibatalkan."}, status=status.HTTP_200_OK)
        return Response(
            {"error": "Pesanan tidak dapat dibatalkan karena sudah diproses oleh admin."}, 
            status=status.HTTP_400_BAD_REQUEST
        )


# ==========================================
# FITUR BARU: UPLOAD BUKTI PEMBAYARAN
# ==========================================

# 3.5 Menangani Upload Gambar Struk Transfer
class UploadPaymentProofView(generics.UpdateAPIView):
    serializer_class = PaymentProofSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] # Wajib agar bisa menerima file

    def get_queryset(self):
        # User hanya bisa upload bukti untuk bokingannya yang masih PENDING
        return Booking.objects.filter(
            user=self.request.user, 
            status='PENDING'
        )


# ==========================================
# GOLONGAN SUPER ADMIN (BACK-OFFICE - FR-08 BERSILANG)
# ==========================================

# 4. Menangani daftar semua booking dari seluruh user (Khusus Admin)
class AdminBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAdminUser] 
    
    def get_queryset(self):
        # Admin memicu pembersihan otomatis agar data dashboard real-time dan akurat
        Booking.objects.update_expired_bookings()
        return Booking.objects.all().order_by('-created_at')


# 5. Menangani persetujuan/penolakan status booking (Khusus Admin)
class AdminBookingStatusUpdateView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAdminUser]
    queryset = Booking.objects.all()

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        new_status = request.data.get('status')

        if new_status in ['CONFIRMED', 'PAYMENT_REJECTED', 'CANCELLED']: 
            booking.status = new_status
            booking.save()
            return Response(
                {"message": f"Status pesanan berhasil diperbarui menjadi {new_status}."}, 
                status=status.HTTP_200_OK
            )
        return Response(
            {"error": "Status tidak valid. Admin hanya bisa mengubah ke CONFIRMED atau PAYMENT_REJECTED."}, 
            status=status.HTTP_400_BAD_REQUEST
        )