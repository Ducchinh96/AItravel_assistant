from django.core.management.base import BaseCommand
from app.models import Destination


class Command(BaseCommand):
    help = 'Seed database với dữ liệu mẫu cho bảng Destination (điểm đến)'

    def handle(self, *args, **options):
        # Xóa dữ liệu cũ (nếu có)
        Destination.objects.all().delete()
        self.stdout.write(self.style.WARNING('Đã xóa dữ liệu cũ trong bảng Destination.'))

        destinations = [
            {
                "name": "Vịnh Hạ Long",
                "short_description": "Di sản thiên nhiên thế giới với hàng nghìn hòn đảo đá vôi tuyệt đẹp. Du thuyền, chèo kayak, tham quan hang động.",
                "location": "Quảng Ninh",
                "latitude": 20.9101,
                "longitude": 107.1839,
                "image_url": "https://ik.imagekit.io/tvlk/blog/2023/02/ha-long-1.jpg"
            },
            {
                "name": "Phố Cổ Hội An",
                "short_description": "Phố cổ với đèn lồng, kiến trúc Nhật – Trung, ẩm thực như cao lầu, cơm gà, bánh bao vạc.",
                "location": "Quảng Nam",
                "latitude": 15.8801,
                "longitude": 108.3380,
                "image_url": "https://statics.vinpearl.com/hoi-an-pho-co-1_1632894604.jpg"
            },
            {
                "name": "Đà Lạt - Thành phố Ngàn Hoa",
                "short_description": "Thành phố cao nguyên mát mẻ, nhiều hoa, hồ Xuân Hương, thác Datanla, nông trại dâu.",
                "location": "Lâm Đồng",
                "latitude": 11.9404,
                "longitude": 108.4583,
                "image_url": "https://cdn.tcdullich.vn/upload/2022/11/14/da-lat-nghin-hoa-3_1668417551.jpg"
            },
            {
                "name": "Phú Quốc - Đảo Ngọc",
                "short_description": "Đảo biển lớn với bãi biển đẹp, lặn ngắm san hô, VinWonders, đặc sản nước mắm, rượu sim.",
                "location": "Kiên Giang",
                "latitude": 10.2899,
                "longitude": 103.9870,
                "image_url": "https://statics.vinpearl.com/phu-quoc-01_1628139741.jpg"
            },
            {
                "name": "Bà Nà Hills",
                "short_description": "Khu du lịch trên núi với Cầu Vàng, làng Pháp, cáp treo kỷ lục, khí hậu mát mẻ.",
                "location": "Đà Nẵng",
                "latitude": 15.9956,
                "longitude": 107.9968,
                "image_url": "https://banahills.sunworld.vn/wp-content/uploads/2019/03/cau-vang-1.jpg"
            },
            {
                "name": "Vườn Quốc Gia Phong Nha - Kẻ Bàng",
                "short_description": "Di sản thiên nhiên với hệ thống hang động đồ sộ như Sơn Đoòng, Phong Nha, Thiên Đường.",
                "location": "Quảng Bình",
                "latitude": 17.4810,
                "longitude": 106.2840,
                "image_url": "https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/08/phong-nha-ke-bang-1.jpg"
            },
            {
                "name": "Sa Pa - Thị trấn Sương Mù",
                "short_description": "Thị trấn vùng cao với ruộng bậc thang, Fansipan, bản làng dân tộc, khí hậu se lạnh.",
                "location": "Lào Cai",
                "latitude": 22.3364,
                "longitude": 103.8438,
                "image_url": "https://statics.vinpearl.com/sapa-mua-nao-dep-nhat-1_1632896298.jpg"
            },
            {
                "name": "Nha Trang - Thành phố Biển",
                "short_description": "Thành phố biển sôi động, nước trong xanh, nhiều hoạt động biển và hải sản phong phú.",
                "location": "Khánh Hòa",
                "latitude": 12.2388,
                "longitude": 109.1967,
                "image_url": "https://banahills.sunworld.vn/wp-content/uploads/2022/06/nha-trang-1.jpg"
            },
            {
                "name": "Huế - Cố đô",
                "short_description": "Cố đô với Đại Nội, lăng tẩm, sông Hương, nhiều món ăn cung đình đặc trưng.",
                "location": "Thừa Thiên Huế",
                "latitude": 16.4637,
                "longitude": 107.5909,
                "image_url": "https://statics.vinpearl.com/hue-la-gi-1_1629961835.jpg"
            },
            {
                "name": "Mũi Né",
                "short_description": "Biển, đồi cát trắng – đỏ, hoạt động thể thao biển, hải sản tươi.",
                "location": "Bình Thuận",
                "latitude": 10.9333,
                "longitude": 108.2833,
                "image_url": "https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/08/mui-ne-1.jpg"
            },
            {
                "name": "Mai Châu",
                "short_description": "Thung lũng yên bình, nhà sàn, ruộng lúa, văn hóa người Thái.",
                "location": "Hòa Bình",
                "latitude": 20.6667,
                "longitude": 105.0000,
                "image_url": "https://dulichkhampha24.com/wp-content/uploads/2020/01/mai-chau.jpg"
            },
            {
                "name": "Đảo Cát Bà",
                "short_description": "Đảo lớn vùng vịnh Lan Hạ, có vườn quốc gia, bãi tắm Cát Cò, hoạt động trekking, kayak.",
                "location": "Hải Phòng",
                "latitude": 20.7273,
                "longitude": 107.0454,
                "image_url": "https://statics.vinpearl.com/cat-ba-1_1629708350.jpg"
            },
            {
                "name": "Cù Lao Chàm",
                "short_description": "Cụm đảo gần Hội An, khu dự trữ sinh quyển, nổi tiếng với san hô và làng chài.",
                "location": "Quảng Nam",
                "latitude": 15.9500,
                "longitude": 108.5000,
                "image_url": "https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/08/cu-lao-cham-1.jpg"
            },
            {
                "name": "Côn Đảo",
                "short_description": "Quần đảo hoang sơ, nhiều bãi biển đẹp, lịch sử nhà tù Côn Đảo, nơi rùa biển đẻ trứng.",
                "location": "Bà Rịa - Vũng Tàu",
                "latitude": 8.6833,
                "longitude": 106.6000,
                "image_url": "https://statics.vinpearl.com/con-dao-1_1629450918.jpg"
            },
            {
                "name": "Cầu Rồng Đà Nẵng",
                "short_description": "Biểu tượng Đà Nẵng, cầu rồng phun lửa – nước cuối tuần, gần sông Hàn, biển Mỹ Khê.",
                "location": "Đà Nẵng",
                "latitude": 16.0544,
                "longitude": 108.2272,
                "image_url": "https://ik.imagekit.io/tvlk/blog/2023/01/cau-rong-da-nang-1.jpg"
            },
        ]

        created_count = 0
        for dest_data in destinations:
            Destination.objects.create(**dest_data)
            created_count += 1
            self.stdout.write(f"✓ Đã tạo: {dest_data['name']}")

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Hoàn thành! Đã thêm {created_count} địa điểm du lịch vào bảng Destination.')
        )
