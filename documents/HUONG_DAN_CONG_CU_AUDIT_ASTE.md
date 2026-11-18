# Công cụ audit ASTE sau đợt sửa 18/11/2026

Nguồn quy tắc: [cẩm nang gán nhãn](BI_QUYET_GAN_NHAN_VA_AUDIT_DATASET_ASTE.md).
Tài liệu này giải thích công cụ, không thay thế hoặc thay đổi quy ước gán nhãn.

## Phạm vi và kết quả

Ba lệnh audit giữ nguyên đường dẫn và cú pháp cũ, dùng chung `scripts/aste_audit_core.py`.
Chúng là các cách chạy của **một bộ kiểm tra**, không phải ba annotator độc lập.
Kiểm định kép trong cẩm nang là agent đọc hiểu + chương trình kiểm tra kỹ thuật.

- `ERROR`: lỗi cấu trúc/index hoặc vi phạm quy tắc span rõ ràng trong cẩm nang.
- `REVIEW`: dấu hiệu cần agent đọc toàn bộ câu để phân xử, không phải kết luận nhãn sai.
- Báo cáo tách số lượt phát hiện (`errors`, `reviews`) khỏi số dòng liên quan
  (`error_records`, `review_records`); hai nhóm dòng có thể giao nhau.
- Mọi dòng đều cần đọc hiểu, kể cả không có cảnh báo. `semantic_status` luôn là `NOT_CERTIFIED`.
- `[]` hợp lệ về định dạng nhưng luôn được nhắc kiểm tra quyết định REJECT.
- Công cụ không sửa, chuẩn hóa text, chèn địa danh, xóa dòng hoặc ghi lại dataset.
- Số dòng là số dòng vật lý, bắt đầu 1. Dòng trắng bị báo lỗi, không bị lọc mất.
- Triplet lưu bằng list kiểu JSON được báo `TRIPLET_CONTAINER` vì cẩm nang dùng tuple;
  vẫn giải mã và kiểm tra index bên trong, không bỏ qua hoặc tự chuyển định dạng.
- Tách token bằng `text.split()`, index bắt đầu 0. Unicode/BOM được đọc mà không tự sửa text.

Mã thoát: **0** = không phát hiện ERROR; **1** = có ERROR;
**2** = không đọc được đầu vào, manifest JSON không hợp lệ, file rỗng hoặc khoảng lô sai.
Thêm `--fail-on-review` để trả 1 khi còn REVIEW. Không sửa/REJECT dữ liệu chỉ để hết cảnh báo.

## Cách chạy

Chạy từ thư mục gốc dự án. Trong PyCharm, dùng interpreter được cấu hình cho project.

```powershell
# 50 dòng đầu: khoảng [0, 50); dòng 51–100 dùng 50 100.
.\.venv\Scripts\python.exe scripts/verify_batch_50.py data/validate_label/thuan/phase3.txt 0 50

# Xem tất cả token, index và triplet trong lô để đọc đối chiếu.
.\.venv\Scripts\python.exe scripts/verify_batch_50.py data/validate_label/thuan/phase3.txt 0 50 --show-tokens

# Toàn file, nhóm theo 10 nhóm kiểm tra kỹ thuật/cảnh báo.
.\.venv\Scripts\python.exe scripts/deep_10_pass_audit.py data/validate_label/thuan/phase3.txt

# Báo cáo đầy đủ ở stdout JSON; bản hiển thị thường giới hạn 30 chi tiết.
.\.venv\Scripts\python.exe scripts/audit_index_integrity.py data/validate_label/thuan/phase3.txt --json

# Chạy kiểm thử hồi quy của công cụ, không sửa dataset.
.\.venv\Scripts\python.exe -B -m unittest scripts.test_aste_audit -v
```

`--max-details N` đổi số chi tiết ở bản hiển thị thường; phần tổng hợp luôn đếm toàn bộ.
`--json` bao gồm tất cả dòng, token, triplet đã giải mã và issues, không bị giới hạn bởi `--max-details`.
Khoảng lô đếm dòng vật lý, start bao gồm/end không bao gồm; end vượt cuối file được cắt về cuối.
Start ngoài file, start âm hoặc end không lớn hơn start bị từ chối, không báo thành công trên lô rỗng.
Không truyền file: deep mặc định phase3 của Thuận, index và batch giữ mặc định phase1 như trước.

## Đối chiếu index với quyết định đã đọc hiểu

Index hợp lệ không chứng minh đã chọn đúng từ. Ví dụ chọn `ở` thay vì `TPHCM`
hoặc chọn lần `TPHCM` thứ nhất thay vì thứ hai đều có thể nằm trong phạm vi câu.

Agent cần chọn **cụm từ + vị trí xuất hiện** sau khi đọc hiểu. Tạo manifest JSON riêng
cho các dòng đã duyệt trên **text cuối cùng**, không sinh manifest bằng cách chép lại
index hiện có rồi coi đó là một đánh giá độc lập.

Ví dụ text `TPHCM ngập , TPHCM hết ngập`, triplet đang xét mô tả địa danh ở lần thứ hai:

```json
{
  "1": {
    "text": "TPHCM ngập , TPHCM hết ngập",
    "triplets": [
      {"asp": "TPHCM", "asp_start": 3, "opi": "hết ngập", "opi_start": 4, "pol": "POS"}
    ]
  }
}
```

Đây chỉ minh họa cách chọn lần xuất hiện cho một triplet; annotator vẫn phải đọc
toàn câu để quyết định có cần trích xuất thêm trạng thái `ngập` ở mệnh đề trước hay không.

```powershell
.\.venv\Scripts\python.exe scripts/verify_batch_50.py data/validate_label/thuan/phase3.txt 0 50 --expected scripts/scratch/phase3_reviewed.json --json
```

Manifest phải có **mọi dòng trong khoảng đang kiểm tra**, kể cả dòng loại với `triplets: []`.
JSON trùng key (trùng số dòng hoặc trùng trường trong một quyết định) bị từ chối,
không lấy âm thầm giá trị cuối cùng.
Key là số dòng vật lý (chuỗi JSON). Một manifest toàn file có thể dùng cho nhiều lô.
Chương trình so text chính xác và đối chiếu tập triplet, gồm cụm từ, start và polarity;
thứ tự liệt kê triplet không quan trọng. Sai text sau khi thêm fallback/chỉnh câu sẽ báo lỗi.
Manifest không phải bằng chứng tự động về tính đúng ngữ nghĩa: người tạo nó phải đọc hiểu.

## Span helper

`make_triplet(text, asp_phrase, opi_phrase, polarity)` giữ bốn đối số cơ bản.
Không còn tự chọn lần khớp đầu hoặc tự gọt phrase một cách âm thầm.

```python
from scripts.span_helper import make_triplet

make_triplet(
    'TPHCM ngập , TPHCM hết ngập', 'TPHCM', 'hết ngập', 'POS',
    asp_start=3,
)
# ([3], [4, 5], 'POS')
```

- Nếu cụm lặp: chỉ định `asp_start` / `opi_start` (index tuyệt đối), hoặc
  `asp_occurrence` / `opi_occurrence` (lần xuất hiện bắt đầu 0).
- Khớp token nguyên văn, phân biệt hoa/thường. Không tự thêm `đường`.
- Phrase rỗng, không tìm thấy, lựa chọn mơ hồ, overlap, polarity sai, giới từ đầu
  Aspect và dấu câu/emoji ở rìa sẽ gây `ValueError`, kể cả chạy Python với `-O`.
- `sanitize_span` vẫn có thể gọi **tường minh** để đề xuất cắt rìa; phải đọc lại
  kết quả và chọn phrase cuối. `make_triplet` không tự gọi hàm này.
- Không cắt `khu` khỏi `khu dân cư`. Không cắt dấu phẩy nằm giữa Opinion.
- Helper tính vị trí; phải chạy audit sau đó để kiểm tra các quy tắc còn lại.

## Bao phủ quy tắc và phần agent bắt buộc làm

| Quy định cẩm nang | Công cụ hỗ trợ | Agent bắt buộc đối chiếu |
|---|---|---|
| I, VIII: đọc đầy đủ, lô 50 | Chạy theo khoảng dòng; không tự sửa | Đọc từng câu và hashtag, không dùng cảnh báo thay thế việc đọc |
| II: định dạng/index/REJECT | Schema nghiêm, int không nhận bool/float, span liên tục, giới hạn, polarity | Quyết định giữ/loại, giữ đồng bộ số dòng |
| III.2.1–3: xe/người/giới từ | Danh sách cấm tường minh; đủ giới từ, kể cả span một token | Nhận diện vai trò/tên riêng ngoài danh sách; địa danh một token hợp lệ |
| III.2.4, X.2: fallback | REVIEW khi fallback kèm dấu hiệu đường | Đọc quan hệ thực thể, chuyển đúng địa danh; không REJECT để lách audit |
| III.2.5–6: generic/triều | ERROR cho aspect trơ trọi liệt kê, triều trơ trong NEU/NEG | Chỉ bổ sung text theo đúng ngoại lệ, tính lại tất cả index bị ảnh hưởng |
| III.2.7,9: trùng cấp/liệt kê | Triplet trùng chính xác là ERROR; chung Opinion là REVIEW | Không bỏ sót đường, không gom cả danh sách hoặc gán thừa thành phố/phường |
| III.2.8: nguyên văn/tiền tố | Helper khớp nguyên văn; cảnh báo tiền tố/trợ từ | Chọn đầy đủ tên hạ tầng, không tự thêm token không có trong text |
| IV: Opinion đầy đủ/ranh giới | ERROR dấu câu/emoji rìa, danh từ trơ, causal; REVIEW ranh giới/ngữ cảnh trái | Đủ phủ định, mức độ, thời; dừng trước trích dẫn/metadata/khuyến cáo |
| IV: anti-overlap | ERROR giao index Aspect/Opinion | Đảm bảo hai span có quan hệ ngữ nghĩa đúng |
| V, X.5: polarity | Kiểm tra bộ ba nhãn; REVIEW dấu hiệu dự báo/phục hồi | Phân biệt thực tế/dự báo/đo lường/giải pháp; không đổi POS chỉ vì có `sẽ` |
| VI, X.1,3,4: phạm vi/rác | Cảnh báo ngữ cảnh địa lý, nhắc xem lại mọi `[]` | Bình Dương/Vũng Tàu hợp lệ; hashtag quê quán; ẩn dụ/meme vs hiện trường; câu cụt vẫn đủ A–O |
| VII, X.6: kiểm định kép | Linter read-only, mã thoát, giải mã + `--expected` | Đọc và phân xử độc lập; không suy ra 100% đúng từ 0 lỗi |
| IX: tài liệu nền tảng | Không tự giải quyết mâu thuẫn tài liệu | Đọc tài liệu liên quan; ghi nhận quy tắc mơ hồ thay vì tự đoán |

Danh sách từ khóa trong REVIEW chỉ giúp khoanh vùng; không bao phủ hết địa danh,
phủ định hoặc nội dung rác. Không có quy tắc tự động loại câu vì thấy tên tỉnh ngoài.
Các câu không bị cảnh báo vẫn cần kiểm định ngữ nghĩa đầy đủ.

## Thay đổi tương thích cần biết

- Tên lệnh và đối số vị trí cũ giữ nguyên; thêm tùy chọn ở trên.
- Ba auditor dùng chung schema/rules để không mâu thuẫn; không còn coi chạy cả ba là ba bằng chứng độc lập.
- `inspect_sub_batch` giữ trường `rec`, `text`, `triplets`, `flaws`, `status`, thêm `issues` và `tokens`.
  Status sạch kỹ thuật là `STRUCTURE_OK`, dòng loại là `REJECTED_UNREVIEWED`, có lỗi là `FLAWED`.
- Caller của helper cần xử lý `ValueError`, cung cấp vị trí khi phrase lặp và duyệt phrase có rìa sai.
- Dòng trắng không còn bị bỏ qua. Parser lỗi không làm dừng kiểm tra các dòng sau.
- Các thông báo cũ “100% khớp từ”, “sẵn sàng train” đã được bỏ vì vượt khả năng kiểm định.

Kết quả chạy thực tế trên Phase 3 chưa phải một lượt tái gán nhãn. Không sửa dataset
hoặc thay nhãn theo cảnh báo tự động trong đợt nâng cấp công cụ này.

## Checkpoint tiếp tục sau khi hết usage

Đã chạy lại và xác nhận:

- 23 bài kiểm thử hồi quy đều đạt, gồm kiểm thử CLI của cả ba lệnh.
- Ba CLI đọc đủ 3.875 dòng, giải mã 4.976 triplet và trả cùng kết quả khi kiểm tra cùng phạm vi.
- Phát hiện 364 lượt ERROR trên 308 dòng: 241 lượt là triplet lưu bằng list thay vì tuple theo mẫu cẩm nang,
  123 lượt còn lại thuộc các quy tắc span. Đây là số phát hiện, không phải 364 dòng sai duy nhất.
- Có 1.046 lượt REVIEW trên 849 dòng cần đọc phân xử, không được coi toàn bộ là nhãn sai.
- Mã thoát 1 trên file này là hành vi đúng vì vẫn còn ERROR trong dữ liệu.
- SHA-256 Phase 3 giữ nguyên:
  `2312144842bf11c8baf02b88ee7c94428516a4cf76899433958e808e77af1aaa`.

Phần công cụ đã có thể dùng hỗ trợ cross-check. Việc tiếp theo là đọc hiểu và audit
nhãn theo từng block 50, báo tiến độ mỗi 100 theo yêu cầu của Thuận, ghi rõ phrase/vị trí
đã duyệt để dùng `--expected`. Không cần viết lại công cụ hoặc tự động sửa dataset từ cảnh báo.

Lượt rà soát bổ sung đã sửa ba điểm: nhận diện emoji keycap và ký tự Unicode rời ở rìa span;
từ chối key trùng trong manifest; báo `ValueError` rõ ràng nếu helper nhận text/phrase sai kiểu.
Có thêm kiểm thử index với đáp án đặt trước, lần xuất hiện của Opinion lặp,
token số/địa danh hợp lệ và thống kê số dòng. Các kiểm thử không chứng minh toàn bộ
ngữ nghĩa đã đúng; keyword trong REVIEW vẫn chỉ là gợi ý, không bao phủ mọi tình huống.
