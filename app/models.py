from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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

# =========================
#  AI ITINERARY DRAFT (PENDING USER APPROVAL)
# =========================
class AIItineraryDraft(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="ai_itinerary_drafts",
        db_column="nguoidung",
    )
    text_user = models.TextField(db_column="noi_dung_nguoi_dung")
    ai_raw = models.TextField(db_column="noi_dung_ai")
    ai_payload = models.JSONField(null=True, blank=True, db_column="ai_payload")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_column="trang_thai",
    )
    is_public = models.BooleanField(
        default=False,
        db_column="cong_khai",
    )
    share_requested = models.BooleanField(
        default=False,
        db_column="yeu_cau_chia_se",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column="ngay_tao")
    updated_at = models.DateTimeField(auto_now=True, db_column="ngay_cap_nhat")

    class Meta:
        db_table = "ai_lichtrinh_nhap"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Draft #{self.id} - {self.user_id} ({self.status})"

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


# ======================================================
#  DỊCH VỤ (GỒM CẢ KHÁCH SẠN) - DÙNG CHUNG
#  ăn uống, khách sạn, spa, vui chơi, ...
# ======================================================
class Service(models.Model):
    class ServiceType(models.TextChoices):
        HOTEL = "hotel", "Khách sạn"
        FOOD = "food", "Ăn uống"
        SPA = "spa", "Spa"
        ACTIVITY = "activity", "Vui chơi/Hoạt động"
        SHOPPING = "shopping", "Mua sắm"
        OTHER = "other", "Khác"

    id = models.AutoField(primary_key=True, db_column="id_dich_vu")

    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="services",
        db_column="diem_den_id",
    )

    name = models.CharField(max_length=255, db_column="ten_dich_vu")

    service_type = models.CharField(
        max_length=50,
        choices=ServiceType.choices,
        default=ServiceType.FOOD,
        db_column="loai_dich_vu",
    )

    description = models.TextField(blank=True, db_column="mo_ta")
    address = models.CharField(max_length=255, blank=True, db_column="dia_chi")

    # === MỚI: giá tham khảo từ ===
    price_from = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        db_column="gia_tu",
    )

    # (Tuỳ bạn) Nếu muốn giữ tương thích dữ liệu cũ, có thể GIỮ field này.
    # Nếu bạn không cần nữa thì xoá hẳn field dưới và tạo migration drop cột.
    price_range = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_column="gia_tham_khao"
    )

    # === MỚI: rating ===
    rating_avg = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        db_column="diem_danh_gia_tb",
    )
    rating_count = models.PositiveIntegerField(
        default=0,
        db_column="so_luot_danh_gia",
    )

    image_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        db_column="hinh_anh"
    )

    created_at = models.DateTimeField(auto_now_add=True, db_column="ngay_tao")

    class Meta:
        db_table = "dich_vu"
        ordering = ["destination", "name"]
        indexes = [
            models.Index(fields=["destination"]),
            models.Index(fields=["service_type"]),
            models.Index(fields=["created_at"]),
        ]

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

    # Diem di/den
    origin_destination = models.ForeignKey(
        Destination,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='origin_itineraries',
        db_column='diem_di'
    )
    destination_destination = models.ForeignKey(
        Destination,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='destination_itineraries',
        db_column='diem_den'
    )

    # San bay di/den
    origin_airport = models.ForeignKey(
        "Airport",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='origin_itineraries',
        db_column='sanbay_di'
    )
    destination_airport = models.ForeignKey(
        "Airport",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='destination_itineraries',
        db_column='sanbay_den'
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

    services = models.ManyToManyField(
        Service,
        related_name='itineraries',
        blank=True,
        db_table='lichtrinh_dichvu'
    )

    flight_segments = models.ManyToManyField(
        "FlightSegment",
        related_name='itineraries',
        blank=True,
        db_table='lichtrinh_changbay'
    )

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
        ('s?ng', 'Bu?i s?ng'),
        ('chi?u', 'Bu?i chi?u'),
        ('t?i', 'Bu?i t?i'),
        ('c? ng?y', 'C? ng?y'),
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


# ======================================================
#  BẢNG REVIEW / COMMENT CHO LỊCH TRÌNH
# ======================================================
class ItineraryReview(models.Model):
    id = models.AutoField(primary_key=True, db_column="id")

    itinerary = models.ForeignKey(
        Itinerary,
        on_delete=models.CASCADE,
        related_name="reviews",
        db_column="lichtrinh",
    )

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="itinerary_reviews",
        db_column="nguoidung",
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        db_column="so_sao",
        help_text="Số sao 1-5 cho cả lịch trình",
    )

    comment = models.TextField(blank=True, db_column="noi_dung")
    created_at = models.DateTimeField(auto_now_add=True, db_column="ngay_tao")

    class Meta:
        db_table = "danhgia"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["itinerary"]),
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["rating"]),
        ]

    def __str__(self):
        return f"Đánh giá {self.itinerary_id} - {self.user_id} ({self.rating}★)"


# ======================================================
#  BẢNG SÂN BAY
# ======================================================
class Airport(models.Model):
    id = models.AutoField(primary_key=True, db_column="id")

    code = models.CharField(
        max_length=3,
        unique=True,
        db_column="ma_iata",
        help_text="Mã IATA, ví dụ DAD, SGN",
    )
    name = models.CharField(max_length=255, db_column="ten")
    city = models.CharField(max_length=255, blank=True, db_column="thanh_pho")
    country = models.CharField(max_length=255, blank=True, db_column="quoc_gia")

    class Meta:
        db_table = "sanbay"
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["city"]),
            models.Index(fields=["country"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


# ======================================================
#  BẢNG CHẶNG BAY (CHUYẾN BAY CƠ BẢN)
# ======================================================
class FlightSegment(models.Model):
    id = models.AutoField(primary_key=True, db_column="id")

    origin_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="chang_di",
        db_column="sanbay_di",
    )

    destination_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="chang_den",
        db_column="sanbay_den",
    )

    airline = models.CharField(max_length=255, blank=True, db_column="hang_bay")
    flight_number = models.CharField(max_length=50, blank=True, db_column="so_hieu")

    departure_time = models.DateTimeField(db_column="gio_di")
    arrival_time = models.DateTimeField(db_column="gio_den")

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        db_column="gia",
    )

    class Meta:
        db_table = "chang_bay"
        ordering = ["-departure_time", "id"]
        indexes = [
            models.Index(fields=["origin_airport"]),
            models.Index(fields=["destination_airport"]),
            models.Index(fields=["departure_time"]),
            models.Index(fields=["airline"]),
        ]

    def __str__(self):
        return f"{self.origin_airport.code} → {self.destination_airport.code} ({self.flight_number or 'N/A'})"


# ======================================================
#  BẢNG SỞ THÍCH
# ======================================================
class Preference(models.Model):
    id = models.AutoField(primary_key=True, db_column="id")

    name = models.CharField(
        max_length=100,
        unique=True,
        db_column="ten",
        help_text="Tên sở thích: beach, mountain, foodie, nightlife, museum…",
    )

    class Meta:
        db_table = "so_thich"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


# ======================================================
#  BẢNG NGƯỜI DÙNG - SỞ THÍCH
# ======================================================
class UserPreference(models.Model):
    id = models.AutoField(primary_key=True, db_column="id")

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="so_thich_nguoidung",
        db_column="nguoidung",
    )

    preference = models.ForeignKey(
        Preference,
        on_delete=models.CASCADE,
        related_name="nguoidung_so_thich",
        db_column="so_thich",
    )

    class Meta:
        db_table = "nguoidung_so_thich"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "preference"],
                name="uniq_nguoidung_so_thich"
            ),
        ]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["preference"]),
        ]

    def __str__(self):
        return f"{self.user_id} - {self.preference.name}"


# ======================================================
#  BANG REVIEW / COMMENT CHO AI DRAFT
# ======================================================
class AIDraftReview(models.Model):
    id = models.AutoField(primary_key=True, db_column="id")

    draft = models.ForeignKey(
        AIItineraryDraft,
        on_delete=models.CASCADE,
        related_name="reviews",
        db_column="ai_lichtrinh",
    )

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="ai_itinerary_reviews",
        db_column="nguoidung",
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        db_column="so_sao",
        help_text="So sao 1-5 cho AI itinerary",
    )

    comment = models.TextField(blank=True, db_column="noi_dung")
    created_at = models.DateTimeField(auto_now_add=True, db_column="ngay_tao")

    class Meta:
        db_table = "ai_danhgia"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["draft"]),
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["rating"]),
        ]

    def __str__(self):
        return f"AI Review {self.draft_id} - {self.user_id} ({self.rating})"
