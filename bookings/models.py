from django.db import models
from django.conf import settings
from fields.models import Field
from django.utils import timezone

# --- TAMBAHKAN CUSTOM QUERYSET UNTUK AUTO-CANCEL ---
class BookingQuerySet(models.QuerySet):
    def update_expired_bookings(self):
        """
        Mencari semua booking PENDING yang meledor/melewati deadline,
        lalu mengubah statusnya menjadi CANCELLED secara massal.
        """
        now = timezone.now()
        expired_bookings = self.filter(status='PENDING', payment_deadline__lt=now)
        if expired_bookings.exists():
            expired_bookings.update(status='CANCELLED')
        return self

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending (Menunggu Pembayaran)'),
        ('WAITING_CONFIRMATION', 'Menunggu Konfirmasi Admin'),
        ('CONFIRMED', 'Dikonfirmasi'),
        ('PAYMENT_REJECTED', 'Pembayaran Ditolak'),
        ('CANCELLED', 'Dibatalkan'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='bookings')
    
    booking_date = models.DateField(verbose_name="Tanggal Main")
    start_time = models.TimeField(verbose_name="Jam Mulai")
    end_time = models.TimeField(verbose_name="Jam Selesai")
    participants_count = models.IntegerField(verbose_name="Jumlah Orang")
    notes = models.TextField(blank=True, null=True, verbose_name="Catatan Tambahan")
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Biaya")
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING', verbose_name="Status Reservasi")
    payment_proof = models.ImageField(upload_to='payments/', blank=True, null=True, verbose_name="Bukti Pembayaran")
    payment_deadline = models.DateTimeField(blank=True, null=True, verbose_name="Batas Waktu Pembayaran")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Daftarkan objek manager baru ke dalam model
    objects = BookingQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self.pk and not self.payment_deadline:
            self.payment_deadline = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} | {self.field.name} | {self.booking_date}"