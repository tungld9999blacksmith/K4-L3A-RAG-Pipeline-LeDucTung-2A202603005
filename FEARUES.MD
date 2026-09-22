# Tính năng ứng dụng RAG

## 1. Giới thiệu

Ứng dụng là một chatbot RAG (Retrieval-Augmented Generation) hỗ trợ tra cứu
thông tin du lịch, di tích lịch sử, địa điểm tham quan, làng nghề, văn hóa,
ẩm thực và truyền thống tại **Huế, Đà Nẵng và Hội An**.

Thay vì trả lời hoàn toàn dựa trên kiến thức có sẵn của mô hình ngôn ngữ,
chatbot tìm kiếm thông tin liên quan trong bộ tài liệu đã thu thập, sau đó
dùng các tài liệu này để tạo câu trả lời có nguồn tham khảo (citation).

## 2. Phạm vi chủ đề

### Huế

- Quần thể di tích Cố đô Huế.
- Đại Nội, các lăng tẩm và chùa Thiên Mụ.
- Lịch sử, kiến trúc và công tác bảo tồn di sản Huế.
- Ẩm thực và truyền thống văn hóa Huế.

### Đà Nẵng

- Ngũ Hành Sơn và bán đảo Sơn Trà.
- Bảo tàng Điêu khắc Chăm.
- Văn hóa Chăm tại khu vực miền Trung.
- Ẩm thực địa phương, trong đó có mì Quảng.
- Các địa điểm du lịch và giá trị văn hóa tiêu biểu.

### Hội An

- Phố cổ Hội An và các công trình kiến trúc lịch sử.
- Chùa Cầu, nhà cổ và hội quán.
- Làng rau Trà Quế, nghề thủ công và sinh hoạt truyền thống.
- Cao lầu, bánh bao bánh vạc và các món ăn địa phương.
- Đèn lồng, lễ hội và sự giao thoa văn hóa của thương cảng cổ.

## 3. Các tính năng chính

### 3.1. Chat hỏi đáp bằng tiếng Việt

Người dùng có thể đặt câu hỏi tự nhiên về các địa điểm, di tích, văn hóa,
ẩm thực và truyền thống trong phạm vi ba khu vực.

Ví dụ:

- “Những di tích nổi bật ở Huế là gì?”
- “Hội An chịu ảnh hưởng của những nền văn hóa nào?”
- “Bảo tàng Điêu khắc Chăm ở Đà Nẵng giới thiệu nội dung gì?”
- “Gợi ý lịch trình tham quan văn hóa Huế – Đà Nẵng – Hội An.”

### 3.2. Tra cứu kết hợp Dense Search và BM25

Ứng dụng sử dụng hai phương pháp tìm kiếm:

- **Dense retrieval:** tìm các đoạn văn có ý nghĩa tương đồng với câu hỏi,
  kể cả khi cách diễn đạt không trùng hoàn toàn.
- **BM25 lexical retrieval:** tìm chính xác từ khóa, tên riêng và thuật ngữ
  như “Chùa Cầu”, “Festival Huế”, “Ngũ Hành Sơn” hoặc “mì Quảng”.

Hai kết quả được chuẩn hóa về cùng schema `SearchResult`.

### 3.3. Hybrid retrieval với RRF

Hệ thống dùng Reciprocal Rank Fusion (RRF) để kết hợp thứ hạng từ dense
retrieval và BM25. Việc này giúp cân bằng giữa:

- Khả năng hiểu ngữ nghĩa.
- Khả năng nhận diện từ khóa chính xác.
- Khả năng tìm thông tin về tên riêng và địa danh.

RRF được thực hiện một lần theo `chunk_id`, bảo đảm không làm mất liên kết
giữa đoạn văn và nguồn gốc của đoạn văn đó.

### 3.4. Lọc và ưu tiên theo metadata

Mỗi tài liệu có metadata về:

- Địa điểm: `hue`, `da_nang`, `hoi_an`.
- Nhóm nội dung: di sản, di tích, văn hóa, ẩm thực, truyền thống, lễ hội.
- Loại tài liệu và đơn vị phát hành.
- URL nguồn và ngôn ngữ.

Metadata giúp hệ thống ưu tiên tài liệu đúng địa phương và đúng loại nội dung,
đồng thời hỗ trợ các câu hỏi so sánh giữa nhiều địa phương.

### 3.5. Citation và hiển thị nguồn

Mỗi câu trả lời được liên kết với các `SearchResult` đã sử dụng. Giao diện
hiển thị:

- Nội dung câu trả lời.
- Tên tài liệu hoặc nguồn tham khảo.
- URL gốc.
- Phương pháp retrieval.
- Điểm tìm kiếm khi phù hợp.

Citation giúp người dùng kiểm tra lại thông tin và hạn chế câu trả lời không
có căn cứ.

### 3.6. Fallback khi không đủ bằng chứng

Nếu dense search và BM25 không tìm được bằng chứng đủ tin cậy, hệ thống có thể
chuyển sang PageIndex/vectorless fallback cho tài liệu có cấu trúc nhiều
tiêu đề hoặc mục nội dung.

Fallback sử dụng cosine score gốc của dense retrieval để đánh giá ngưỡng,
không dùng trực tiếp RRF score cho quyết định này.

### 3.7. Safe refusal

Chatbot không tự bịa thông tin khi bộ tài liệu không có bằng chứng phù hợp.
Với các câu hỏi ngoài phạm vi hoặc cần dữ liệu thời gian thực, chatbot sẽ
thông báo rõ giới hạn.

Các nội dung không cam kết cung cấp gồm:

- Thời tiết hiện tại hoặc dự báo theo ngày.
- Giá vé máy bay, khách sạn và dịch vụ theo thời gian thực.
- Tình trạng giao thông hiện tại.
- Lịch lễ hội chưa có trong corpus.
- Thông tin không được hỗ trợ bởi nguồn đã thu thập.

### 3.8. Giao diện Streamlit

Ứng dụng có giao diện chat trên Streamlit với:

- Ô nhập câu hỏi.
- Lịch sử hội thoại trong phiên.
- Thanh chọn số lượng chunks (`top_k`).
- Khu vực hiển thị câu trả lời và nguồn.
- Thông tin về phương pháp retrieval và bằng chứng sử dụng.

## 4. Pipeline xử lý dữ liệu

```text
Thu thập tài liệu
        |
        v
Chuẩn hóa sang Markdown
        |
        v
Chunking và tạo metadata
        |
        +--> Embedding --> ChromaDB --> Dense retrieval
        |
        +--> BM25 index -----------> Lexical retrieval
                                      |
                                      v
                               RRF fusion
                                      |
                                      v
                         Reranking/fallback tùy chọn
                                      |
                                      v
                           Context có nguồn gốc
                                      |
                                      v
                         Generation có citation
```

## 5. Nguồn dữ liệu hiện có

Metadata các nguồn đã thu thập được lưu tại
[acquisition/docs/metadata.json](acquisition/docs/metadata.json).

Corpus hiện bao gồm các nguồn:

- Cục Di sản Văn hóa về bảo tồn di tích Huế.
- Trung tâm Quản lý Bảo tồn Di sản Văn hóa Hội An.
- UNESCO về Quần thể di tích Cố đô Huế, Đô thị cổ Hội An và Thánh địa Mỹ Sơn.
- Vietnam National Authority of Tourism về Huế, Đà Nẵng và Hội An.

Nguồn dữ liệu được ưu tiên theo thứ tự:

1. Tài liệu chính thức từ cơ quan quản lý di sản và văn hóa.
2. Tài liệu UNESCO và các tổ chức chuyên môn.
3. Trang thông tin du lịch chính thức có nội dung factual.

## 6. Các loại câu hỏi hỗ trợ

| Nhóm câu hỏi | Ví dụ |
|---|---|
| Di tích lịch sử | “Quần thể di tích Huế có giá trị lịch sử gì?” |
| Địa điểm du lịch | “Nên tham quan gì ở Hội An?” |
| Văn hóa | “Văn hóa Chăm được thể hiện ở đâu tại Đà Nẵng?” |
| Ẩm thực | “Món ăn đặc trưng của Huế và Hội An là gì?” |
| Làng nghề | “Hội An có những làng nghề truyền thống nào?” |
| Lễ hội và truyền thống | “Những hoạt động văn hóa nào gắn với phố cổ Hội An?” |
| So sánh địa phương | “Huế và Hội An khác nhau thế nào về di sản?” |
| Lịch trình | “Gợi ý lịch trình văn hóa ba ngày tại miền Trung.” |
| Ngoài phạm vi | “Giá khách sạn Hội An tối nay là bao nhiêu?” |

## 7. Định hướng đánh giá

Ứng dụng được đánh giá bằng một golden dataset tối thiểu 15 câu hỏi, gồm
câu hỏi đúng phạm vi, câu hỏi so sánh, câu hỏi cần citation và câu hỏi ngoài
phạm vi.

Các chỉ số cần theo dõi:

- Faithfulness.
- Answer relevance.
- Context recall.
- Context precision.

Ngoài ra, nhóm sẽ so sánh:

```text
Dense-only
    với
Hybrid: Dense + BM25 + RRF
```

Hai cấu hình cần dùng cùng bộ câu hỏi, cùng mô hình generation và cùng điều
kiện đánh giá để kết quả A/B có ý nghĩa.

## 8. Trạng thái triển khai

Các contract và module nền tảng của pipeline đã được chuẩn bị cho:

- Thu thập và chuẩn hóa tài liệu.
- Chunking và indexing.
- Dense search.
- BM25 search.
- RRF/reranking.
- PageIndex fallback.
- Generation có citation.
- Streamlit chatbot.

Giao diện và các module có comment `TODO` vẫn cần được hoàn thiện để kết nối
đầy đủ pipeline, hiển thị nguồn và lưu kết quả hội thoại end-to-end.

## 9. Mục tiêu sản phẩm

Sản phẩm hoàn thiện cần cung cấp một chatbot có khả năng:

1. Hiểu câu hỏi tiếng Việt về Huế, Đà Nẵng và Hội An.
2. Tìm đúng thông tin trong corpus bằng hybrid retrieval.
3. Trả lời ngắn gọn, dễ hiểu và dựa trên bằng chứng.
4. Hiển thị citation và URL nguồn.
5. Từ chối an toàn khi thiếu thông tin.
6. Hỗ trợ đánh giá chất lượng retrieval và generation.
