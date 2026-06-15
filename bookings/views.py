from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser # <-- TAMBAHAN BARU
from .models import Booking
from .serializers import BookingSerializer, PaymentProofSerializer # <-- TAMBAHAN BARU

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


# 2. Menangani Detail dan Update Biasa
class BookingDetailUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Bersihkan juga saat user melihat detail spesifik sebuah booking
        Booking.objects.update_expired_bookings()
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

        if new_status in ['CONFIRMED', 'PAYMENT_REJECTED', 'CANCELLED']: # <-- Disesuaikan dengan model Anda
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