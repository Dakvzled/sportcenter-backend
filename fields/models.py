from django.db import models

class Field(models.Model):
    # Membatasi input hanya untuk 5 jenis lapangan sesuai SRS
    SPORT_CHOICES = (
        ('BADMINTON', 'Badminton'),
        ('VOLI', 'Voli'),
        ('FUTSAL', 'Futsal'),
        ('MINI_SOCCER', 'Mini Soccer'),
        ('BASKET', 'Basket'),
    )

    name = models.CharField(max_length=100, verbose_name="Nama Lapangan")
    sport_type = models.CharField(max_length=20, choices=SPORT_CHOICES, verbose_name="Jenis Olahraga")
    capacity = models.IntegerField(verbose_name="Kapasitas Orang")
    
    # Pemisahan tarif sesuai FR-12
    price_weekday = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tarif Weekday (/jam)")
    price_weekend = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tarif Weekend (/jam)")
    
    image = models.ImageField(upload_to='fields/', verbose_name="Foto Lapangan")
    is_active = models.BooleanField(default=True, verbose_name="Status Aktif")

    def __str__(self):
        return f"{self.name} ({self.get_sport_type_display()})"