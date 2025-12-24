# Postman Guide – Test API (Django REST Framework)

Tài liệu này hướng dẫn **test đầy đủ bằng Postman** cho các API trong project của bạn (theo `urls.py`, `views.py`, `serializers.py`, `models.py`).

> Gợi ý base URL mặc định khi chạy local: `http://127.0.0.1:8000`  
> Nếu bạn chạy port khác thì đổi lại trong Postman Environment.

---

## 0) Chuẩn bị Postman

### 0.1 Tạo Environment (Postman)
Tạo 1 Environment tên: `local` (hoặc tuỳ bạn) và thêm variables:

| Key | Initial value | Notes |
|---|---|---|
| base_url | http://127.0.0.1:8000 | URL backend |
| access_token | (trống) | lấy từ login |
| refresh_token | (trống) | lấy từ login |
| destination_id | (trống) | lưu id sau khi tạo/GET |
| service_id | (trống) | lưu id sau khi tạo/GET |
| itinerary_id | (trống) | lưu id sau khi tạo/GET |
| review_id | (trống) | lưu id sau khi tạo/GET |
| airport_id | (trống) | lưu id sau khi tạo/GET |
| flight_segment_id | (trống) | lưu id sau khi tạo/GET |
| preference_id | (trống) | lưu id sau khi tạo/GET |
| user_preference_id | (trống) | lưu id sau khi tạo/GET |
| chat_turn_id | (trống) | lưu id sau khi suggest-trip (saved_chat_turn.id) |

### 0.2 Header chung
- `Content-Type: application/json`
- Với API cần đăng nhập:  
  `Authorization: Bearer {{access_token}}`

> **Lưu ý:** Project trả JWT theo SimpleJWT (`access`, `refresh`). Không thấy route refresh token trong `urls.py`, nên khi access token hết hạn bạn **login lại** (hoặc tự bổ sung endpoint refresh nếu muốn).

---

## 1) AUTH APIs

### 1.1 Register – Đăng ký
**POST** `{{base_url}}/api/register/`  
Auth: **No**

Body (raw JSON):
```json
{
  "email": "user1@gmail.com",
  "password": "12345678",
  "confirm_password": "12345678",
  "first_name": "Tam",
  "last_name": "Tran"
}
```

Expected:
- `201 Created`
- `{ "message": "User registered successfully!" }`

---

### 1.2 Login – Đăng nhập (lấy JWT)
**POST** `{{base_url}}/api/login/`  
Auth: **No**

Body:
```json
{
  "email": "user1@gmail.com",
  "password": "12345678"
}
```

Expected:
- `200 OK`
- Response có `access`, `refresh`, `user`

✅ **Postman Tests Script** (tab **Tests**) để tự lưu token:
```js
const json = pm.response.json();
if (json.access) pm.environment.set("access_token", json.access);
if (json.refresh) pm.environment.set("refresh_token", json.refresh);
```

---

### 1.3 Logout – Đăng xuất (blacklist refresh token)
**POST** `{{base_url}}/api/logout/`  
Auth: **No** (trong code đang AllowAny)

Body:
```json
{
  "refresh_token": "{{refresh_token}}"
}
```

Expected:
- `205 RESET CONTENT` hoặc `400` nếu token không hợp lệ / blacklist chưa bật.

---

### 1.4 Forgot Password – Gửi mã xác nhận (email)
**POST** `{{base_url}}/api/forgot-password/`  
Auth: **No**

Body:
```json
{
  "email": "user1@gmail.com"
}
```

Expected:
- `200 OK`
- `{ "message": "Confirmation code sent to your email!" }`

> Code sẽ được lưu cache key `password_reset_code_<email>` trong 10 phút.

---

### 1.5 Reset Password – Đặt lại mật khẩu
**POST** `{{base_url}}/api/reset-password/`  
Auth: **No**

Body:
```json
{
  "email": "user1@gmail.com",
  "confirmation_code": "A1b2C3",
  "new_password": "newpass123"
}
```

Expected:
- `200 OK`
- `{ "message": "Password has been reset successfully!" }`

---

## 2) USER PROFILE

### 2.1 Get Profile – Lấy thông tin user hiện tại
**GET** `{{base_url}}/api/profile/`  
Auth: **Yes** (Bearer access)

Expected:
- `200 OK`
```json
{
  "id": 1,
  "username": "user1@gmail.com",
  "email": "user1@gmail.com",
  "first_name": "Tam",
  "last_name": "Tran"
}
```

### 2.2 Update Profile – Cập nhật user
**PUT** `{{base_url}}/api/profile/`  
Auth: **Yes**

Body:
```json
{
  "email": "user1@gmail.com",
  "first_name": "Tam Updated",
  "last_name": "Tran Updated"
}
```

Expected:
- `200 OK` trả về user sau update.

---

## 3) AI & CHAT

### 3.1 Suggest Trip (AI) – Gợi ý lịch trình + lưu ChatTurn + (có thể) tạo Itinerary
**POST** `{{base_url}}/api/suggest-trip/`  
Auth: **Yes**

Body:
```json
{
  "text_user": "Mình muốn đi Đà Lạt 3 ngày 2 đêm, thích cafe, chill, budget 3 triệu."
}
```

Expected:
- `200 OK`
- Response dạng:
```json
{
  "ok": true,
  "data": {
    "text_user": "...",
    "text_ai": "...",
    "saved_chat_turn": {
      "id": 12,
      "created_at": "2025-12-24T10:00:00.000000"
    },
    "ai_parsed": { "...": "..." },
    "chat_response": "...",
    "itinerary": { "...": "..." }
  }
}
```

✅ **Postman Tests Script** để lưu `chat_turn_id` + `itinerary_id` (nếu có):
```js
const res = pm.response.json();
if (res?.data?.saved_chat_turn?.id) {
  pm.environment.set("chat_turn_id", res.data.saved_chat_turn.id);
}
if (res?.data?.itinerary?.id) {
  pm.environment.set("itinerary_id", res.data.itinerary.id);
}
```

---

### 3.2 ChatTurn History – Lấy lịch sử chat đến id (pk)
**GET** `{{base_url}}/api/chat-turns/history/{{chat_turn_id}}/?limit=20`  
Auth: **Yes**

Expected:
- `200 OK`
```json
{
  "ok": true,
  "params": { "pk": 12, "limit": 20 },
  "count": 3,
  "items": [
    { "id": 10, "text_user": "...", "text_ai": "...", "created_at": "..." }
  ]
}
```

---

## 4) ITINERARIES (Lịch trình)

### 4.1 List Itineraries (của user hiện tại)
**GET** `{{base_url}}/api/itineraries/`  
Auth: **Yes**

Query params (optional):
- `is_fixed=true|false`

Ví dụ:
- `{{base_url}}/api/itineraries/?is_fixed=false`

---

### 4.2 Create Itinerary
**POST** `{{base_url}}/api/itineraries/`  
Auth: **Yes**

Body mẫu (tối thiểu):
```json
{
  "title": "Đà Nẵng 3N2Đ – Ăn chơi hết nấc",
  "summary": "Lịch trình tự tạo",
  "total_days": 3,
  "travel_style": "ẩm thực",
  "source_type": "custom",
  "status": "published",
  "is_fixed": false,
  "is_public": false,
  "main_destination_id": null,
  "base_itinerary": null,
  "budget_min": 1000000,
  "budget_max": 3000000
}
```

✅ Tests Script lưu `itinerary_id`:
```js
const json = pm.response.json();
if (json?.id) pm.environment.set("itinerary_id", json.id);
```

---

### 4.3 Get Itinerary Detail
**GET** `{{base_url}}/api/itineraries/{{itinerary_id}}/`  
Auth: **Yes** (owner hoặc admin)

---

### 4.4 Update Itinerary
**PATCH** `{{base_url}}/api/itineraries/{{itinerary_id}}/`  
Auth: **Yes**

Body:
```json
{
  "summary": "Update mô tả lịch trình",
  "is_public": true
}
```

---

### 4.5 Delete Itinerary
**DELETE** `{{base_url}}/api/itineraries/{{itinerary_id}}/`  
Auth: **Yes**

---

### 4.6 Public Itineraries Feed
**GET** `{{base_url}}/api/itineraries/public/`  
Auth: **No**

---

## 5) DESTINATIONS (Điểm đến)

### 5.1 List Destinations
**GET** `{{base_url}}/api/destinations/`  
Auth: **No**

---

### 5.2 Create Destination (Admin only)
**POST** `{{base_url}}/api/destinations/`  
Auth: **Yes** (Admin)

Body:
```json
{
  "name": "Đà Lạt",
  "short_description": "Thành phố ngàn hoa",
  "location": "Lâm Đồng",
  "latitude": 11.9404,
  "longitude": 108.4583,
  "image_url": "https://example.com/dalat.jpg"
}
```

✅ Tests Script lưu `destination_id`:
```js
const json = pm.response.json();
if (json?.id) pm.environment.set("destination_id", json.id);
```

---

### 5.3 Destination Detail
**GET** `{{base_url}}/api/destinations/{{destination_id}}/`  
Auth: **No**

### 5.4 Update Destination (Admin only)
**PATCH** `{{base_url}}/api/destinations/{{destination_id}}/`  
Auth: **Yes (Admin)**

Body:
```json
{
  "short_description": "Update mô tả ngắn"
}
```

### 5.5 Delete Destination (Admin only)
**DELETE** `{{base_url}}/api/destinations/{{destination_id}}/`  
Auth: **Yes (Admin)**

---

## 6) SERVICES (Dịch vụ: ăn uống/khách sạn/spa/...)

### 6.1 List Services
**GET** `{{base_url}}/api/services/`  
Auth: **No**

Query params (optional):
- `destination_id={{destination_id}}`
- `service_type=hotel|food|spa|activity|shopping|other`

Ví dụ:
- `{{base_url}}/api/services/?destination_id={{destination_id}}&service_type=food`

---

### 6.2 Create Service (Admin only)
**POST** `{{base_url}}/api/services/`  
Auth: **Yes (Admin)**

Body:
```json
{
  "destination_id": {{destination_id}},
  "name": "Bánh tráng nướng Cô Hoa",
  "service_type": "food",
  "description": "Quán ăn vặt nổi tiếng",
  "address": "61 Nguyễn Văn Trỗi, Đà Lạt",
  "price_from": 15000,
  "price_range": "15k-50k",
  "rating_avg": 4.6,
  "rating_count": 1200,
  "image_url": "https://example.com/banhtrangnuong.jpg"
}
```

✅ Tests Script lưu `service_id`:
```js
const json = pm.response.json();
if (json?.id) pm.environment.set("service_id", json.id);
```

---

### 6.3 Service Detail
**GET** `{{base_url}}/api/services/{{service_id}}/`  
Auth: **No**

### 6.4 Update Service (Admin only)
**PATCH** `{{base_url}}/api/services/{{service_id}}/`  
Auth: **Yes (Admin)**

Body:
```json
{
  "price_from": 20000,
  "rating_avg": 4.7
}
```

### 6.5 Delete Service (Admin only)
**DELETE** `{{base_url}}/api/services/{{service_id}}/`  
Auth: **Yes (Admin)**

---

## 7) WEATHER INFO (Thời tiết theo điểm đến)

### 7.1 List Weather Info
**GET** `{{base_url}}/api/weather/`  
Auth: **No**

Query params (optional):
- `destination_id={{destination_id}}`
- `month=12`

Ví dụ:
- `{{base_url}}/api/weather/?destination_id={{destination_id}}&month=12`

---

### 7.2 Create Weather Info (Admin only)
**POST** `{{base_url}}/api/weather/`  
Auth: **Yes (Admin)**

Body:
```json
{
  "destination_id": {{destination_id}},
  "month": 12,
  "note": "Tháng 12 trời se lạnh, có sương mù, nên mang áo ấm."
}
```

---

### 7.3 Weather Info Detail
**GET** `{{base_url}}/api/weather/1/`  
Auth: **No**

### 7.4 Update Weather Info (Admin only)
**PATCH** `{{base_url}}/api/weather/1/`  
Auth: **Yes (Admin)**

Body:
```json
{
  "note": "Update ghi chú"
}
```

### 7.5 Delete Weather Info (Admin only)
**DELETE** `{{base_url}}/api/weather/1/`  
Auth: **Yes (Admin)**

---

## 8) ITINERARY REVIEWS (Đánh giá lịch trình)

### 8.1 List Reviews
**GET** `{{base_url}}/api/itinerary-reviews/`  
Auth: **No**

Query params (optional):
- `itinerary_id={{itinerary_id}}`
- `user_id=1`

Ví dụ:
- `{{base_url}}/api/itinerary-reviews/?itinerary_id={{itinerary_id}}`

---

### 8.2 Create Review
**POST** `{{base_url}}/api/itinerary-reviews/`  
Auth: **Yes** (đăng nhập)

Body:
```json
{
  "itinerary": {{itinerary_id}},
  "rating": 5,
  "comment": "Lịch trình hợp lý, đi vui!"
}
```

✅ Tests Script lưu `review_id`:
```js
const json = pm.response.json();
if (json?.id) pm.environment.set("review_id", json.id);
```

---

### 8.3 Review Detail
**GET** `{{base_url}}/api/itinerary-reviews/{{review_id}}/`  
Auth: **Owner/Admin để sửa/xoá**, còn GET thì tuỳ IsOwnerOrReadOnly bạn set (hiện đang áp IsOwnerOrReadOnly).

### 8.4 Update Review
**PATCH** `{{base_url}}/api/itinerary-reviews/{{review_id}}/`  
Auth: **Yes (Owner/Admin)**

Body:
```json
{
  "rating": 4,
  "comment": "Update comment"
}
```

### 8.5 Delete Review
**DELETE** `{{base_url}}/api/itinerary-reviews/{{review_id}}/`  
Auth: **Yes (Owner/Admin)**

---

## 9) AIRPORTS (Sân bay)

### 9.1 List Airports
**GET** `{{base_url}}/api/airports/`  
Auth: **No**

### 9.2 Create Airport (Admin only)
**POST** `{{base_url}}/api/airports/`  
Auth: **Yes (Admin)**

Body:
```json
{
  "code": "DAD",
  "name": "Da Nang International Airport",
  "city": "Da Nang",
  "country": "Vietnam"
}
```

✅ Tests Script lưu `airport_id`:
```js
const json = pm.response.json();
if (json?.id) pm.environment.set("airport_id", json.id);
```

### 9.3 Airport Detail
**GET** `{{base_url}}/api/airports/{{airport_id}}/`  
Auth: **No**

### 9.4 Update Airport (Admin only)
**PATCH** `{{base_url}}/api/airports/{{airport_id}}/`  
Auth: **Yes (Admin)**

Body:
```json
{
  "name": "Da Nang Intl Airport (Updated)"
}
```

### 9.5 Delete Airport (Admin only)
**DELETE** `{{base_url}}/api/airports/{{airport_id}}/`  
Auth: **Yes (Admin)**

---

## 10) FLIGHT SEGMENTS (Chặng bay)

### 10.1 List Flight Segments
**GET** `{{base_url}}/api/flight-segments/`  
Auth: **No**

Query params (optional):
- `origin_airport_id={{airport_id}}`
- `destination_airport_id=...`
- `airline=Vietnam`

Ví dụ:
- `{{base_url}}/api/flight-segments/?origin_airport_id={{airport_id}}&airline=Vietnam`

---

### 10.2 Create Flight Segment (Admin only)
**POST** `{{base_url}}/api/flight-segments/`  
Auth: **Yes (Admin)**

Body:
```json
{
  "origin_airport_id": {{airport_id}},
  "destination_airport_id": {{airport_id}},
  "airline": "Vietnam Airlines",
  "flight_number": "VN123",
  "departure_time": "2025-12-25T08:00:00+07:00",
  "arrival_time": "2025-12-25T09:30:00+07:00",
  "price": 1250000
}
```

> Lưu ý: ví dụ trên dùng cùng airport_id cho origin/destination để demo nhanh. Thực tế bạn nên tạo **2 sân bay khác nhau**.

✅ Tests Script lưu `flight_segment_id`:
```js
const json = pm.response.json();
if (json?.id) pm.environment.set("flight_segment_id", json.id);
```

---

### 10.3 Flight Segment Detail
**GET** `{{base_url}}/api/flight-segments/{{flight_segment_id}}/`  
Auth: **No**

### 10.4 Update Flight Segment (Admin only)
**PATCH** `{{base_url}}/api/flight-segments/{{flight_segment_id}}/`  
Auth: **Yes (Admin)**

Body:
```json
{
  "price": 1350000
}
```

### 10.5 Delete Flight Segment (Admin only)
**DELETE** `{{base_url}}/api/flight-segments/{{flight_segment_id}}/`  
Auth: **Yes (Admin)**

---

## 11) PREFERENCES (Sở thích)

### 11.1 List Preferences
**GET** `{{base_url}}/api/preferences/`  
Auth: **No**

### 11.2 Create Preference (Admin only)
**POST** `{{base_url}}/api/preferences/`  
Auth: **Yes (Admin)**

Body:
```json
{
  "name": "beach"
}
```

✅ Tests Script lưu `preference_id`:
```js
const json = pm.response.json();
if (json?.id) pm.environment.set("preference_id", json.id);
```

### 11.3 Preference Detail
**GET** `{{base_url}}/api/preferences/{{preference_id}}/`  
Auth: **No**

### 11.4 Update Preference (Admin only)
**PATCH** `{{base_url}}/api/preferences/{{preference_id}}/`  
Auth: **Yes (Admin)**

Body:
```json
{
  "name": "mountain"
}
```

### 11.5 Delete Preference (Admin only)
**DELETE** `{{base_url}}/api/preferences/{{preference_id}}/`  
Auth: **Yes (Admin)**

---

## 12) USER PREFERENCES (Sở thích của user hiện tại)

### 12.1 List User Preferences (của chính user)
**GET** `{{base_url}}/api/user-preferences/`  
Auth: **Yes**

### 12.2 Add User Preference
**POST** `{{base_url}}/api/user-preferences/`  
Auth: **Yes**

Body:
```json
{
  "preference_id": {{preference_id}}
}
```

✅ Tests Script lưu `user_preference_id`:
```js
const json = pm.response.json();
if (json?.id) pm.environment.set("user_preference_id", json.id);
```

### 12.3 Delete User Preference
**DELETE** `{{base_url}}/api/user-preferences/{{user_preference_id}}/`  
Auth: **Yes (Owner/Admin)**

---

## 13) ADMIN APIs (Chỉ Admin)

### 13.1 List Users
**GET** `{{base_url}}/api/admin/users/`  
Auth: **Yes (Admin)**

### 13.2 User Detail
**GET** `{{base_url}}/api/admin/users/1/`  
Auth: **Yes (Admin)**

### 13.3 Update User
**PATCH** `{{base_url}}/api/admin/users/1/`  
Auth: **Yes (Admin)**

Body:
```json
{
  "first_name": "Admin Updated"
}
```

### 13.4 Delete User
**DELETE** `{{base_url}}/api/admin/users/1/`  
Auth: **Yes (Admin)**

### 13.5 Admin Statistics
**GET** `{{base_url}}/api/admin/statistics/`  
Auth: **Yes (Admin)**

Expected:
```json
{
  "ok": true,
  "statistics": {
    "total_counts": { "users": 10, "itineraries": 20, "destinations": 5 },
    "user_breakdown": { "active_users": 9, "inactive_users": 1, "admin_users": 1 },
    "last_30_days": { "new_users": 2, "new_itineraries": 3, "new_destinations": 1 },
    "last_7_days": { "new_users": 1, "new_itineraries": 1 }
  }
}
```

---

## 14) Flow test nhanh (đề xuất)

1) **Register** (tạo user thường)  
2) **Login** (lưu `access_token`, `refresh_token`)  
3) **GET /api/profile/** (check auth)  
4) Nếu bạn có admin: **Login admin**  
5) Admin tạo dữ liệu mẫu:
   - Create Destination → lưu `destination_id`
   - Create Service → lưu `service_id`
   - Create Preference → lưu `preference_id`
   - Create Airport (2 cái) → lưu `airport_id` origin + destination
   - Create Flight Segment
6) User thường:
   - POST /api/user-preferences/ (gắn sở thích)
   - POST /api/itineraries/ (tạo lịch trình custom) → `itinerary_id`
   - POST /api/itinerary-reviews/ (review)
7) Test AI:
   - POST /api/suggest-trip/ → lưu `chat_turn_id` và có thể có `itinerary_id`
   - GET /api/chat-turns/history/{{chat_turn_id}}/?limit=20

---

## 15) Troubleshooting nhanh

- **401 Unauthorized**: chưa set `Authorization: Bearer {{access_token}}` hoặc token hết hạn → login lại.
- **403 Forbidden**: endpoint yêu cầu Admin (POST/PUT/PATCH/DELETE ở destination/service/weather/airport/flight/preference/admin/*).
- **400 Bad Request**: sai field/kiểu dữ liệu; kiểm tra body JSON (đặc biệt `month`, `rating`, `total_days`, datetime).
- **Logout 400**: thường do blacklist chưa bật trong SimpleJWT (chưa cài app `rest_framework_simplejwt.token_blacklist` + migrate).

---

*Generated for your current code structure.*
