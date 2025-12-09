from django.db import models


# =========================
#  LƯỢT CHAT VỚI AI
# =========================
class ChatTurn(models.Model):
    id = models.AutoField(primary_key=True)
    text_user = models.TextField(db_column='noi_dung_nguoi_dung')
    text_ai = models.TextField(db_column='noi_dung_ai')
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='nguoidung'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column='ngay_tao')

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["created_at"]),
        ]
        db_table = 'luot_chat'

    def __str__(self):
        return f"#{self.id} - {self.text_user[:40]}..."


# =========================
#  ĐIỂM ĐẾN / ĐỊA ĐIỂM
# =========================
class Destination(models.Model):
    name = models.CharField(max_length=255, db_column='ten')
    short_description = models.TextField(
        db_column='mo_ta_ngan',
        blank=True
    )
    # Ví dụ: tên tỉnh/thành/khu vực
    location = models.CharField(
        max_length=255,
        db_column='khu_vuc',
        blank=True
    )
    latitude = models.FloatField(
        null=True,
        blank=True,
        db_column='vi_do'
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        db_column='kinh_do'
    )
    image_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        db_column='url_anh'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column='ngay_tao')

    class Meta:
        db_table = 'diemden'
        ordering = ['name']

    def __str__(self):
        return self.name


# =========================
#  KHÁCH SẠN THEO ĐIỂM ĐẾN
# =========================
class Hotel(models.Model):
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='hotels',
        db_column='diemden'
    )
    name = models.CharField(max_length=255, db_column='ten')
    address = models.CharField(
        max_length=255,
        db_column='dia_chi',
        blank=True
    )
    price_range = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='gia_tham_khao'
    )
    image_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        db_column='url_anh'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column='ngay_tao')

    class Meta:
        db_table = 'khachsan'
        ordering = ['destination', 'name']

    def __str__(self):
        return f"{self.name} - {self.destination.name}"


# =========================
#  ĂN UỐNG THEO ĐIỂM ĐẾN
# =========================
class FoodPlace(models.Model):
    TYPE_CHOICES = [
        ('restaurant', 'Nhà hàng'),
        ('street_food', 'Quán ăn đường phố'),
        ('cafe', 'Cafe'),
        ('other', 'Khác'),
    ]

    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='food_places',
        db_column='diemden'
    )
    name = models.CharField(max_length=255, db_column='ten')
    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        default='restaurant',
        db_column='loai_hinh'
    )
    address = models.CharField(
        max_length=255,
        db_column='dia_chi',
        blank=True
    )
    price_range = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column='gia_tham_khao'
    )
    image_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        db_column='url_anh'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column='ngay_tao')

    class Meta:
        db_table = 'anuong'
        ordering = ['destination', 'name']

    def __str__(self):
        return f"{self.name} - {self.destination.name}"


# =========================
#  THỜI TIẾT THEO ĐIỂM ĐẾN
# =========================
class WeatherInfo(models.Model):
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='weather_infos',
        db_column='diemden'
    )
    month = models.PositiveSmallIntegerField(
        db_column='thang',
        help_text='Tháng trong năm (1-12)'
    )
    note = models.TextField(
        db_column='ghi_chu',
        blank=True,
        help_text='Ghi chú tổng quan: nên đi/không nên đi, thời tiết thế nào'
    )

    class Meta:
        db_table = 'thoitiet_diemden'
        ordering = ['destination', 'month']
        unique_together = ('destination', 'month')

    def __str__(self):
        return f"Thời tiết {self.destination.name} - Tháng {self.month}"


# =========================
#  LỊCH TRÌNH DU LỊCH
# =========================
class Itinerary(models.Model):
    SOURCE_TYPE_CHOICES = [
        ('sample', 'Lịch trình mẫu'),
        ('ai', 'Lịch trình AI gợi ý'),
        ('custom', 'Lịch trình tùy chỉnh'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Nháp'),
        ('published', 'Công khai'),
        ('archived', 'Lưu trữ'),
    ]

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='nguoidung'
    )

    # Lịch trình này có thể clone từ một lịch trình mẫu gốc
    base_itinerary = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_itineraries',
        db_column='lichtrinh_goc'
    )

    # Điểm đến chính của lịch trình (để filter nhanh)
    main_destination = models.ForeignKey(
        Destination,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='main_itineraries',
        db_column='diemden_chinh'
    )

    title = models.CharField(max_length=255, db_column='tieu_de')
    summary = models.TextField(
        db_column='tong_quan',
        blank=True
    )

    total_days = models.PositiveSmallIntegerField(
        db_column='so_ngay',
        help_text='Tổng số ngày trong lịch trình'
    )

    budget_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='chi_phi_tu'
    )
    budget_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        db_column='chi_phi_den'
    )

    travel_style = models.CharField(
        max_length=50,
        blank=True,
        db_column='phong_cach',
        help_text='Ví dụ: nghỉ dưỡng, khám phá, ẩm thực...'
    )

    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        default='sample',
        db_column='nguon'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='published',
        db_column='trang_thai'
    )

    is_fixed = models.BooleanField(
        default=False,
        db_column='co_dinh',
        help_text='Lịch trình mẫu cố định, chỉ admin được sửa'
    )
    is_public = models.BooleanField(
        default=False,
        db_column='cong_khai'
    )

    created_at = models.DateTimeField(auto_now_add=True, db_column='ngay_tao')
    updated_at = models.DateTimeField(auto_now=True, db_column='ngay_cap_nhat')

    # Danh sách điểm đến trong lịch trình (thông qua bảng nối chi tiết)
    destinations = models.ManyToManyField(
        Destination,
        through='ItineraryDestination',
        related_name='itineraries',
        blank=True
    )

    # Nếu sau này bạn vẫn muốn lưu raw JSON của AI thì bật thêm trường này:
    # raw_ai_details = models.JSONField(
    #     null=True,
    #     blank=True,
    #     db_column='chi_tiet_ai'
    # )

    class Meta:
        db_table = 'lichtrinh'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# =========================
#  CHI TIẾT LỊCH TRÌNH THEO NGÀY / BUỔI
# =========================
class ItineraryDestination(models.Model):
    PART_OF_DAY_CHOICES = [
        ('morning', 'Buổi sáng'),
        ('afternoon', 'Buổi chiều'),
        ('evening', 'Buổi tối'),
        ('full_day', 'Cả ngày'),
    ]

    itinerary = models.ForeignKey(
        Itinerary,
        on_delete=models.CASCADE,
        db_column='lichtrinh',
        related_name='itinerary_destinations'
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        db_column='diemden',
        related_name='itinerary_destinations'
    )

    day_number = models.PositiveIntegerField(
        db_column='ngay',
        help_text='Ngày thứ mấy trong lịch trình (1,2,3,...)'
    )
    part_of_day = models.CharField(
        max_length=20,
        choices=PART_OF_DAY_CHOICES,
        db_column='buoi'
    )

    activity_title = models.CharField(
        max_length=255,
        db_column='tieu_de_hoat_dong',
        blank=True
    )
    activity_description = models.TextField(
        db_column='mo_ta_hoat_dong',
        blank=True
    )

    order = models.PositiveIntegerField(
        db_column='thu_tu',
        default=1,
        help_text='Thứ tự trong cùng 1 buổi của ngày đó'
    )

    class Meta:
        db_table = 'lichtrinh_diemden'
        ordering = ['itinerary', 'day_number', 'part_of_day', 'order', 'id']

    def __str__(self):
        return f"{self.itinerary} - Ngày {self.day_number} ({self.part_of_day}) - {self.destination}"
