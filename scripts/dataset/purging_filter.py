import json
import re
from pathlib import Path

# Patterns for non-flood metaphors
non_flood_metaphor_patterns = [
    r'ngập tràn\s+(hoa|cây cảnh|đèn lồng|sắc hoa|cây xanh|hải sản|topping|đặc sản|yêu thương|deal|hộp|hành lá|niềm vui|ánh nắng|sắc xuân|cảm xúc|gốm|tình cảm|nước mắt|không khí|đồ đẹp|cờ đỏ)',
    r'tràn ngập\s+(hoa|cây cảnh|đèn lồng|sắc hoa|cây xanh|hải sản|topping|đặc sản|yêu thương|deal|hộp|hành lá|niềm vui|ánh nắng|sắc xuân|cảm xúc|gốm|tình cảm|nước mắt|không khí|đồ đẹp|cờ đỏ|tiếng cười|hạnh phúc|tinh tế|sắc màu|áo dài|tình thân|ánh sáng)',
    r'quà ngập tràn',
    r'nhận quà ngập',
    r'ưu đãi ngập tràn',
    r'voucher ngập tràn',
    r'deal ngập tràn',
    r'sale ngập tràn',
    r'tiện ích ngập tràn',
    r'ngập ngụa\s+(nhân|topping|phô mai|kem|thịt)',
    r'ngập tràn trong hành lá',
    r'ngập tràn hộp lun á',
    r'ngập ngừng',
    r'đầm nhà em tràn ngập sen',
    r'đại lộ bình dương tràn ngập những chiếc xe hoa',
    r'buổi tập đầu tiên.*ngập ngừng',
    r'tài xế ngập ngừng',
    r'mỗi đêm đều ngập tràn nước mắt',
]

# Patterns for real estate ads (BDS)
bds_patterns = [
    r'1tr8 máy lạnh',
    r'3tr490 có máy lạnh',
    r'3tr290k có máy lạnh',
    r'CÒN 2 PHÒNG ĐẸP – NGUYỄN VĂN QUÁ',
    r'115 phạm hữu lầu.*khoá vân tay',
    r'Mới xây sạch sẽ.*ko ngập.*Cho nuôi pet',
    r'CẦU BÌNH LỢI, ĐH VĂN LANG - 1PN',
    r'Phòng trệt, ko ngập 📍430 Đào Sư Tích',
    r'HƠN 5 TỶ – MẶT TIỀN ĐÀO SƯ TÍCH – NHÀ 3 TẦNG',
    r'NHÀ ĐẸP GÒ VẤP – GIÁP QUANG TRUNG – TIỆN ÍCH NGẬP TRÀN',
    r'MỄ CỐC Q8 – 42\.5M² – 3 TẦNG',
    r'MỄ CỐC Q8 – 44M²',
    r'DTĐCN : 49,5m2.*ko ngập nước',
    r'Chủ ngộp giảm thêm 1,5tỷ.*1 trệt 2 lầu',
    r'Nhà hẻm Bến Phú Định Q8.*chỉ hơn 4ty',
    r'Nhà hẻm Phạm Thế Hiển P4 Q8.*1 trệt , 1 lầu',
    r'Nhà 1/ Đường Tân Hòa Đông.*Chỉ 4 T\.ỷ',
    r'Nhà 1/ Đườg Tân Hòa Đông.*Kết cấu: 1 trệt',
    r'Cần bán Chung Cư Thái An.*khu không ngập nước',
    r'2 căn Huỳnh Tấn Phát, Nhà Bè, 150m², giảm 500tr',
    r'Phòng cực kỳ rộng rãi, tràn ngập ánh sáng tự nhiên với cửa kính và ban công',
    r'Giá thuê : 4\.700\.000đ / tháng.*ko bị ngập',
    r'- 6T\.ỷ\+ Nhà hẻm xe hơi ngang nhà Huỳnh Tấn Phát',
    r'HÒNG TRỌ KHU BÀU CÁT – TÂN BÌNH',
    r'Vài bước chân ra phố, tiện ích ngập tràn',
    r'Tiện ích ngập tràn \.',
    r'Vậy lúc đó Ascent Lakeside có ngập không\?',
]

# Patterns for commercial advertisements
ads_patterns = [
    r'LocknLock x Vincom',
    r'The Pizza Company Vincom Thảo Điền',
    r'Ngân hàng Shinhan.*sinh nhật',
    r'Sài Gòn Ninh Chữ.*Ưu đãi ngập tràn',
    r'GRAND OPENING VIKINGS 15',
    r'Duy nhất tại Sachi Garden.*ƯU ĐÃI NGẬP TRÀN',
    r'Minh Tuấn Mobile.*ưu đãi ngập tràn',
    r'sắm sửa thả ga - nhận quà ngập tràn',
    r'CO\.OPMART HUỲNH TẤN PHÁT LÊN KỆ RỒI ĐÂY',
    r'mua xe ghé 635 Phạm Thế Hiển',
    r'Hồng trà sữa Tam Hảo',
    r'DEAL SỐC NGẬP TRÀN – EMART PHAN HUY ÍCH',
    r'TUYỂN DỤNG NGẬP TRÀN.*BHX BÀ RỊA',
    r'BÁNH CANH CUA THẢO ĐIỀN nay dời về địa điểm mới',
    r'Karaoke ICOOL Ung Văn Khiêm',
    r'Quán Lẩu Bò mới toanh topping ngập tràn',
    r'CÔ NÀNG LILA KHÁM PHÁ WATSONS NGUYỄN XÍ',
    r'ƯU ĐÃI HÈ NGẬP TRÀN TẠI JOSEON PEARL CENTER',
    r'LifeWear hiện đại, ngập tràn',
    r'Ms Hoa Junior.*Không khí Halloween ngập tràn',
    r'Mầm coffee - Quán cà phê quận 2 tràn ngập',
    r'Choáng ngợp với góc hoa ly.*Nhâm Coffee Thảo Điền',
    r'BÚN BÒ HUẾ BÚN RIÊU TỪ 30K topping ngập tràn',
    r'Lẩu bò nóng hổi nghi ngút khói.*ngập tràn đèn lồng',
    r'bữa tiệc hải sản ngập tràn tại Poseidon',
]

# Patterns for holiday/event announcements
holiday_patterns = [
    r'Không khí noel đã tràn ngập ở Sài Gòn',
    r'Không khí Noel đã tràn ngập khắp đường phố Sài Gòn',
    r'Không khí Halloween đã tràn ngập khắp',
    r'TRĂNG RẰM CỦA BÉ – ĐÊM TRUNG THU ĐONG ĐẦY YÊU THƯƠNG',
    r'Không khí Tết trung thu đã tràn ngập tại phố đi bộ Bạch Đằng',
    r'Chợ Hải Sản 79 chúc bạn.*tràn ngập hạnh phúc',
    r'Không khí Noel tràn ngập khắp đường phố TP\.HCM',
    r'TRƯỜNG TIỂU HỌC LÊ LAI.*GIỜ RA CHƠI.*tràn ngập tiếng cười',
    r'Không khí giáng sinh đã tràn ngập tại Goncy 196 Lê Lai',
    r'GHTK’s Care.*Mặt trời yêu thương.*tràn ngập tiếng cười',
    r'CUỘC SỐNG ĐẶC BIỆT CỦA EM BÉ MẮC BỆNH HIẾM GẶP.*tràn ngập tiếng cười',
    r'Ga Sài Gòn.*tràn ngập sắc xanh áo lính',
    r'Chợ hoa xuân TP\.HCM trên bến dưới thuyền tràn ngập sắc màu',
    r'SẮC XUÂN TRÀN NGẬP, ÁO DÀI TẾT THƯỚT THA',
    r'Chúc các chị em có một ngày tràn ngập niềm vui',
    r'Không khí giáng sinh đã tràn ngập khắp nơi tại Sài Gòn',
    r'KHÔNG KHÍ MÙA XUÂN TRÀN NGẬP TPHCM',
    r'Cờ đỏ sao vàng tràn ngập TPHCM.*đi bão',
    r'kỷ niệm 114 năm.*tràn ngập tình thân ái',
    r'Kính chúc quý khách có một ngày 20/10 tràn ngập niềm vui',
    r'KHÔNG KHÍ TẾT NGẬP TRÀN TẠI TRƯỜNG THPT NGUYỄN DUY TRINH',
    r'KHÔNG KHÍ GIÁNG SINH.*NGẬP TRÀN VĂN PHÒNG PQR SÀI GÒN',
    r'Không khí Noel ngập tràn đường phố Sài Gòn rồi nè',
    r'KHÔNG KHÍ TRUNG THU NGẬP TRÀN TẠI CÁC CHI NHÁNH TRUNG TÂM KIỂM SOÁT CẬN THỊ',
    r'Câu chuyện về 2 bé Hổ song sinh',
    r'Ngập tràn sắc xuân tại Trụ sở các đơn vị thuộc Công an TPHCM',
    r'NGẬP TRÀN CẢM XÚC VỚI HỘI THAO 2024',
    r'Phố Tây Bùi Viện ngập tràn cờ đỏ sao vàng',
    r'HỘI THI VẼ TRANH.*NÉT CỌ XINH.*SẮC MÀU TUỔI THƠ NGẬP TRÀN',
    r'Ở Vạng Hàng Xanh có chiếc bàn sen đá ngập tràn ánh nắng',
    r'KHÔNG KHÍ TẾT NGẬP TRÀN: NGƯỜI DÂN TP\.HCM ĐỔ VỀ KHU CHỢ HOA',
    r'đi chợ hoa tết bà con ơi.*bày bán ngập tràn',
    r'Mừng 20/10 – ngập tràn yêu thương',
    r'Ở Thảo Điền lại có quán mới.*ngập tràn cây xanh',
]

all_filters = non_flood_metaphor_patterns + bds_patterns + ads_patterns + holiday_patterns
regex = re.compile('|'.join(all_filters), re.IGNORECASE)

def compute_purging_indices(dataset):
    to_remove = set()
    matched = []
    for idx, item in enumerate(dataset):
        content = item.get('content', {}) or {}
        text = (content.get('text', '') or '') + ' ' + (content.get('title', '') or '')
        m = regex.search(text)
        if m:
            to_remove.add(idx)
            matched.append({
                'idx': idx,
                'seq_id': item.get('seq_id'),
                'id': item.get('id'),
                'kw': m.group(0),
                'text': text.strip()[:120]
            })
    return to_remove, matched

# Lazy load or compute if file exists
to_remove_indices = set()
_data_file = Path('data/processed/hcmc_flood_annotated_v3_multimodal.json')
if _data_file.exists():
    try:
        with open(_data_file, 'r', encoding='utf-8') as _f:
            _dataset = json.load(_f)
        to_remove_indices, _ = compute_purging_indices(_dataset)
    except Exception:
        pass
