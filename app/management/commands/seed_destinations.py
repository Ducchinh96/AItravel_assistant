from django.core.management.base import BaseCommand
from app.models import Destination

class Command(BaseCommand):
    help = 'Seed database with sample destination data'

    def handle(self, *args, **options):
        # Xóa dữ liệu cũ (nếu có)
        Destination.objects.all().delete()
        self.stdout.write(self.style.WARNING('Đã xóa dữ liệu cũ.'))

        # Dữ liệu mẫu 15 địa điểm du lịch Việt Nam
        destinations = [
            {
                "name": "Vịnh Hạ Long",
                "description": "Di sản thiên nhiên thế giới với hàng nghìn hòn đảo đá vôi tuyệt đẹp. Hoạt động: Du thuyền qua đêm, chèo kayak, tham quan hang động Sửng Sốt, Thiên Cung.",
                "location": "Quảng Ninh",
                "latitude": 20.9101,
                "longitude": 107.1839,
                "image_url": "https://ik.imagekit.io/tvlk/blog/2023/02/ha-long-1.jpg"
            },
            {
                "name": "Phố Cổ Hội An",
                "description": "Thành phố cổ được UNESCO công nhận. Nổi tiếng với đèn lồng, kiến trúc Nhật-Trung hòa quyện. Ẩm thực: Cao lầu, Bánh bao vạc, Cơm gà.",
                "location": "Quảng Nam",
                "latitude": 15.8801,
                "longitude": 108.3380,
                "image_url": "https://statics.vinpearl.com/hoi-an-pho-co-1_1632894604.jpg"
            },
            {
                "name": "Đà Lạt - Thành phố Ngàn Hoa",
                "description": "Thành phố cao nguyên mát mẻ quanh năm. Điểm đến lãng mạn với hồ Xuân Hương, thác Datanla, vườn hoa. Đặc sản: Dâu tây, rau củ cao nguyên.",
                "location": "Lâm Đồng",
                "latitude": 11.9404,
                "longitude": 108.4583,
                "image_url": "https://cdn.tcdullich.vn/upload/2022/11/14/da-lat-nghin-hoa-3_1668417551.jpg"
            },
            {
                "name": "Phú Quốc - Đảo Ngọc",
                "description": "Đảo lớn nhất Việt Nam với bãi biển đẹp nhất thế giới. Hoạt động: Lặn ngắm san hô, câu cá, tham quan VinWonders. Đặc sản: Nước mắm, sim rượu.",
                "location": "Kiên Giang",
                "latitude": 10.2899,
                "longitude": 103.9870,
                "image_url": "https://statics.vinpearl.com/phu-quoc-01_1628139741.jpg"
            },
            {
                "name": "Bà Nà Hills",
                "description": "Khu du lịch nghỉ dưỡng trên núi với Cầu Vàng nổi tiếng thế giới. Cáp treo Guinness, làng Pháp, Fantasy Park. Nhiệt độ mát mẻ quanh năm.",
                "location": "Đà Nẵng",
                "latitude": 15.9956,
                "longitude": 107.9968,
                "image_url": "https://banahills.sunworld.vn/wp-content/uploads/2019/03/cau-vang-1.jpg"
            },
            {
                "name": "Vườn Quốc Gia Phong Nha - Kẻ Bàng",
                "description": "Di sản thiên nhiên với hang động lớn nhất thế giới - Sơn Đoòng. Tham quan hang Phong Nha, Thiên Đường bằng thuyền. Cảnh quan kỳ vĩ.",
                "location": "Quảng Bình",
                "latitude": 17.4810,
                "longitude": 106.2840,
                "image_url": "https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/08/phong-nha-ke-bang-1.jpg"
            },
            {
                "name": "Sa Pa - Thị trấn Sương Mù",
                "description": "Thị trấn miền núi với ruộng bậc thang tuyệt đẹp. Leo đỉnh Fanxipan, tham quan bản Cát Cát, chợ tình. Đặc sản: Thịt trâu gác bếp, cá tầm.",
                "location": "Lào Cai",
                "latitude": 22.3364,
                "longitude": 103.8438,
                "image_url": "https://statics.vinpearl.com/sapa-mua-nao-dep-nhat-1_1632896298.jpg"
            },
            {
                "name": "Nha Trang - Thành phố Biển",
                "description": "Bãi biển đẹp với nước trong xanh. Hoạt động: Lặn biển, tham quan Vinpearl Land, tắm bùn Tháp Bà. Ẩm thực hải sản phong phú.",
                "location": "Khánh Hòa",
                "latitude": 12.2388,
                "longitude": 109.1967,
                "image_url": "https://banahills.sunworld.vn/wp-content/uploads/2022/06/nha-trang-1.jpg"
            },
            {
                "name": "Huế - Cố đô",
                "description": "Kinh đô cũ với Đại Nội, lăng tẩm vua Nguyễn. Ẩm thực cung đình: Bún bò Huế, Bánh khoái, Cơm hến. Sông Hương thơ mộng.",
                "location": "Thừa Thiên Huế",
                "latitude": 16.4637,
                "longitude": 107.5909,
                "image_url": "https://statics.vinpearl.com/hue-la-gi-1_1629961835.jpg"
            },
            {
                "name": "Mũi Né",
                "description": "Bãi biển với đồi cát trắng, cát đỏng độc đáo. Hoạt động: Lướt ván diều, ATV, xem bình minh Suối Tiên. Hải sản tươi ngon.",
                "location": "Bình Thuận",
                "latitude": 10.9333,
                "longitude": 108.2833,
                "image_url": "https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/08/mui-ne-1.jpg"
            },
            {
                "name": "Mai Châu",
                "description": "Thung lũng xanh mướt với bản làng dân tộc Thái. Trải nghiệm nhà sàn, múa sạp, cơm lam. Đạp xe qua ruộng lúa, leo núi.",
                "location": "Hòa Bình",
                "latitude": 20.6667,
                "longitude": 105.0000,
                "image_url": "https://dulichkhampha24.com/wp-content/uploads/2020/01/mai-chau.jpg"
            },
            {
                "name": "Đảo Cát Bà",
                "description": "Đảo lớn nhất vịnh Lan Hạ. Vườn Quốc gia với voọc Cát Bà quý hiếm. Hoạt động: Trekking, leo núi, kayak, bơi lội ở bãi Cát Cò.",
                "location": "Hải Phòng",
                "latitude": 20.7273,
                "longitude": 107.0454,
                "image_url": "https://statics.vinpearl.com/cat-ba-1_1629708350.jpg"
            },
            {
                "name": "Cù Lao Chàm",
                "description": "Khu dự trữ sinh quyển thế giới. Lặn ngắm san hô, tham quan làng chài, đạp xe quanh đảo. Hải sản tươi sống giá rẻ.",
                "location": "Quảng Nam",
                "latitude": 15.9500,
                "longitude": 108.5000,
                "image_url": "https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/08/cu-lao-cham-1.jpg"
            },
            {
                "name": "Côn Đảo",
                "description": "Quần đảo hoang sơ với lịch sử anh hùng. Bãi Đầm Trầu - một trong bãi biển đẹp nhất Việt Nam. Lặn biển, ngắm rùa biển đẻ trứng.",
                "location": "Bà Rịa - Vũng Tàu",
                "latitude": 8.6833,
                "longitude": 106.6000,
                "image_url": "https://statics.vinpearl.com/con-dao-1_1629450918.jpg"
            },
            {
                "name": "Cầu Rồng Đà Nẵng",
                "description": "Biểu tượng thành phố với cầu rồng phun lửa, phun nước vào cuối tuần. Khu vực gần Sông Hàn, phố đi bộ, bãi biển Mỹ Khê.",
                "location": "Đà Nẵng",
                "latitude": 16.0544,
                "longitude": 108.2272,
                "image_url": "https://ik.imagekit.io/tvlk/blog/2023/01/cau-rong-da-nang-1.jpg"
            },
        ]

        # Thêm từng địa điểm vào DB
        created_count = 0
        for dest_data in destinations:
            Destination.objects.create(**dest_data)
            created_count += 1
            self.stdout.write(f"✓ Đã tạo: {dest_data['name']}")

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Hoàn thành! Đã thêm {created_count} địa điểm du lịch vào database.')
        )
