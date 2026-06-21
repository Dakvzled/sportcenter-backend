from django.urls import path
from . import views
from .views import (
    BookingCreateListView, 
    BookingDetailUpdateView, 
    BookingCancelView,
    UploadPaymentProofView,       # <-- 1. Tambahkan import kelas baru ini
    AdminBookingListView,         
    AdminBookingStatusUpdateView  
)

urlpatterns = [
    # ==========================================
    # RUTE CLIENT-SIDE (USER BIASA)
    # ==========================================
    path('', BookingCreateListView.as_view(), name='booking-list-create'),
    path('<int:pk>/', BookingDetailUpdateView.as_view(), name='booking-detail-update'),
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='booking-cancel'),
    
    # --- RUTE BARU KHUSUS UPLOAD BUKTI ---
    path('<int:pk>/upload-proof/', UploadPaymentProofView.as_view(), name='upload_payment_proof'),
    
    # ==========================================
    # RUTE BACK-OFFICE (KHUSUS ADMIN)
    # ==========================================
    path('admin/all/', AdminBookingListView.as_view(), name='admin-booking-list'),
    path('admin/<int:pk>/status/', AdminBookingStatusUpdateView.as_view(), name='admin-booking-status-update'),
]