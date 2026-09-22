import os
import time
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Tải cấu hình biến môi trường
load_dotenv()

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Di sản Miền Trung AI — Huế • Đà Nẵng • Hội An",
    page_icon="🏮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Khởi tạo trạng thái phiên làm việc (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []

if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None

# Sidebar - Thông tin đề tài và bộ điều khiển kỹ thuật
with st.sidebar:
    st.title("🏮 Di sản Miền Trung AI")
    st.markdown(
        """
        **Hệ thống RAG Tra cứu Du lịch & Văn hóa**  
        *Phạm vi dữ liệu: Cố đô Huế, Thành phố Đà Nẵng và Đô thị cổ Hội An.*
        """
    )
    st.divider()

    st.subheader("⚙️ Cấu hình Retrieval Pipeline")
    top_k = st.slider("Số lượng chunks trích xuất (top_k)", min_value=3, max_value=10, value=5)
    score_threshold = st.slider(
        "Ngưỡng Dense fallback (Score Threshold)",
        min_value=0.1,
        max_value=0.8,
        value=float(os.getenv("SCORE_THRESHOLD", "0.3")),
        step=0.05,
        help="Nếu điểm cosine gốc của Dense retrieval < ngưỡng này, hệ thống sẽ kích hoạt PageIndex fallback.",
    )
    use_reranking = st.toggle("Sử dụng RRF Reranking (Hybrid)", value=True)

    st.subheader("📍 Định hướng địa phương")
    destination_filter = st.selectbox(
        "Ưu tiên câu hỏi theo vùng:",
        options=["Tất cả Miền Trung", "Huế 🏯", "Đà Nẵng 🌊", "Hội An 🏮"],
        index=0,
    )

    st.subheader("🔬 Chế độ thử nghiệm A/B")
    ab_mode = st.checkbox(
        "So sánh A/B (Dense-only vs Hybrid RRF)",
        value=False,
        help="Chạy song song 2 cấu hình để so sánh sự khác biệt về nguồn trích xuất và câu trả lời.",
    )

    st.divider()
    if st.button("🗑️ Xóa lịch sử trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.session_state.quick_prompt = None
        st.rerun()

    st.markdown(
        """
        ---
        **Pipeline Stack:**
        - **Vector DB:** ChromaDB (Cosine)
        - **Lexical Search:** BM25 (Rank-BM25)
        - **Fusion:** Reciprocal Rank Fusion (RRF)
        - **Fallback:** PageIndex Vectorless
        - **Generator:** Gemini / OpenAI / Claude
        """
    )

# Header chính của giao diện
st.title("🏛️ Trợ Lý Di Sản & Du Lịch Huế — Đà Nẵng — Hội An")
st.caption(
    "Hỏi đáp thông minh về di tích lịch sử, danh lam thắng cảnh, văn hóa, làng nghề và ẩm thực "
    "dựa trên tài liệu chính thức từ Cục Di sản Văn hóa, UNESCO và Ban quản lý di sản."
)

# Gợi ý câu hỏi nhanh theo các nhóm trong FEATURES.MD
st.markdown("##### 💡 Gợi ý câu hỏi nhanh theo chủ đề:")
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

with col1:
    if st.button("🏯 Cố đô Huế có giá trị gì nổi bật?", use_container_width=True):
        st.session_state.quick_prompt = "Quần thể di tích Cố đô Huế có những giá trị văn hóa và lịch sử gì nổi bật?"

with col2:
    if st.button("🏮 Di sản & làng nghề Hội An?", use_container_width=True):
        st.session_state.quick_prompt = "Phố cổ Hội An chịu ảnh hưởng của những nền văn hóa nào và có những làng nghề truyền thống gì?"

with col3:
    if st.button("🗿 Văn hóa Chăm tại Đà Nẵng?", use_container_width=True):
        st.session_state.quick_prompt = "Bảo tàng Điêu khắc Chăm ở Đà Nẵng trưng bày những nội dung và hiện vật gì tiêu biểu?"

with col4:
    if st.button("🍜 Ẩm thực đặc trưng Huế - Hội An?", use_container_width=True):
        st.session_state.quick_prompt = "Những món ăn đặc sản truyền thống tiêu biểu nhất của Huế và Hội An là gì?"

with col5:
    if st.button("🧭 Gợi ý lịch trình 3 ngày?", use_container_width=True):
        st.session_state.quick_prompt = "Gợi ý lịch trình tham quan văn hóa di sản ba ngày tại Huế, Đà Nẵng và Hội An."

with col6:
    if st.button("🚫 Thử nghiệm Safe Refusal (Giá vé/Phòng)?", use_container_width=True):
        st.session_state.quick_prompt = "Giá phòng khách sạn Hội An và vé máy bay đến Đà Nẵng tối nay là bao nhiêu?"

# Hàm trợ giúp hiển thị badge phương thức retrieval
def get_method_badge(method: str) -> str:
    badges = {
        "hybrid": "🟣 Hybrid (Dense + BM25 + RRF)",
        "dense": "🟢 Dense Semantic",
        "bm25": "🔵 BM25 Lexical",
        "pageindex": "🟠 PageIndex Fallback",
        "none": "⚪ Safe Refusal",
    }
    return badges.get(method.lower(), f"🏷️ {method}")

# Hàm hiển thị chi tiết các nguồn trích dẫn
def render_sources(sources: list[dict], retrieval_source: str):
    if not sources:
        st.info("ℹ️ Không có nguồn trích dẫn trực tiếp cho phản hồi này (Safe Refusal).")
        return

    st.markdown(f"**Phương thức truy xuất chính:** `{get_method_badge(retrieval_source)}`")
    with st.expander(f"📚 Xem {len(sources)} nguồn tài liệu trích dẫn & bằng chứng", expanded=False):
        for idx, src in enumerate(sources, 1):
            metadata = src.get("metadata", {})
            title = metadata.get("title", "Không rõ tiêu đề")
            source_file = metadata.get("source", "Tài liệu nội bộ")
            doc_type = metadata.get("doc_type", "Chính sách/Báo chí")
            score = src.get("score", 0.0)
            method = src.get("retrieval_method", "hybrid")
            url = metadata.get("url")

            st.markdown(f"**[{idx}] {title}** (`{source_file}`) — {get_method_badge(method)}")
            col_m1, col_m2 = st.columns([2, 1])
            with col_m1:
                st.caption(f"Loại tài liệu: **{doc_type}** | Điểm tương đồng/RRF: **{score:.4f}**")
            with col_m2:
                if url:
                    st.markdown(f"[🔗 Xem liên kết gốc]({url})")

            st.text_area(
                label=f"Nội dung trích dẫn [{idx}]",
                value=src.get("content", "").strip(),
                height=110,
                key=f"chunk_box_{idx}_{src.get('id', '')}_{time.time()}",
                disabled=True,
            )
            st.divider()

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("is_ab", False):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("#### 🟢 Cấu hình A (Dense Only)")
                st.markdown(message["content_a"])
                render_sources(message.get("sources_a", []), "dense")
            with col_b:
                st.markdown("#### 🟣 Cấu hình B (Hybrid + RRF)")
                st.markdown(message["content_b"])
                render_sources(message.get("sources_b", []), message.get("retrieval_source_b", "hybrid"))
        else:
            st.markdown(message["content"])
            if message["role"] == "assistant" and "sources" in message:
                render_sources(message["sources"], message.get("retrieval_source", "hybrid"))

# Tiếp nhận câu hỏi từ khung chat hoặc nút gợi ý
user_input = st.chat_input("Nhập câu hỏi về di sản, du lịch Huế - Đà Nẵng - Hội An...")
query = None

if st.session_state.quick_prompt:
    query = st.session_state.quick_prompt
    st.session_state.quick_prompt = None
elif user_input:
    query = user_input

# Xử lý khi có câu hỏi
if query:
    # Nếu chọn bộ lọc địa phương cụ thể, bổ sung gợi ý ngữ cảnh
    augmented_query = query
    if destination_filter != "Tất cả Miền Trung":
        clean_dest = destination_filter.split()[0]
        augmented_query = f"[{clean_dest}] {query}"

    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        if ab_mode:
            # Chế độ A/B: Chạy song song Dense-only và Hybrid RRF
            with st.spinner("Đang chạy thử nghiệm A/B (Dense vs Hybrid)..."):
                try:
                    from src.task5_semantic_search import semantic_search
                    from src.task9_retrieval_pipeline import retrieve
                    from src.task10_generation import (
                        SYSTEM_PROMPT,
                        call_llm,
                        format_context,
                        reorder_for_llm,
                    )

                    # Config A: Dense Only
                    start_a = time.time()
                    dense_chunks = semantic_search(augmented_query, top_k=top_k)
                    if dense_chunks:
                        context_a = format_context(reorder_for_llm(dense_chunks))
                        answer_a = call_llm(SYSTEM_PROMPT, f"Context:\n{context_a}\n\nQuestion: {query}")
                    else:
                        answer_a = "Tôi không thể xác minh thông tin này từ nguồn hiện có (Dense tìm không thấy)."
                    lat_a = time.time() - start_a

                    # Config B: Hybrid + RRF (+ Fallback)
                    start_b = time.time()
                    hybrid_chunks = retrieve(
                        augmented_query,
                        top_k=top_k,
                        score_threshold=score_threshold,
                        use_reranking=use_reranking,
                    )
                    if hybrid_chunks:
                        context_b = format_context(reorder_for_llm(hybrid_chunks))
                        answer_b = call_llm(SYSTEM_PROMPT, f"Context:\n{context_b}\n\nQuestion: {query}")
                        source_b_method = hybrid_chunks[0].get("retrieval_method", "hybrid")
                    else:
                        answer_b = "Tôi không thể xác minh thông tin này từ nguồn hiện có."
                        source_b_method = "none"
                    lat_b = time.time() - start_b

                    col_res_a, col_res_b = st.columns(2)
                    with col_res_a:
                        st.markdown(f"#### 🟢 Config A: Dense-Only (`{lat_a:.2f}s`)")
                        st.markdown(answer_a)
                        render_sources(dense_chunks, "dense")

                    with col_res_b:
                        st.markdown(f"#### 🟣 Config B: Hybrid RRF (`{lat_b:.2f}s`)")
                        st.markdown(answer_b)
                        render_sources(hybrid_chunks, source_b_method)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "is_ab": True,
                        "content_a": answer_a,
                        "sources_a": dense_chunks,
                        "content_b": answer_b,
                        "sources_b": hybrid_chunks,
                        "retrieval_source_b": source_b_method,
                    })

                except Exception as e:
                    err_msg = f"⚠️ Lỗi khi thực hiện so sánh A/B: `{str(e)}`"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})

        else:
            # Chế độ thông thường: Sử dụng Pipeline hoàn chỉnh (Task 10)
            with st.spinner("Đang tra cứu di sản và tổng hợp câu trả lời có trích dẫn..."):
                try:
                    from src.task10_generation import generate_with_citation

                    start_time = time.time()
                    result = generate_with_citation(augmented_query, top_k=top_k)
                    latency = time.time() - start_time

                    answer = result.get("answer", "")
                    sources = result.get("sources", [])
                    retrieval_source = result.get("retrieval_source", "hybrid")

                    st.markdown(answer)
                    st.caption(f"⏱️ Thời gian phản hồi: {latency:.2f} giây")
                    render_sources(sources, retrieval_source)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                        "retrieval_source": retrieval_source,
                    })

                except Exception as e:
                    err_msg = (
                        f"⚠️ Đã xảy ra lỗi khi xử lý câu hỏi: `{str(e)}`.\n\n"
                        "Vui lòng kiểm tra lại cấu hình API key trong `.env` hoặc thử lại với câu hỏi khác."
                    )
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
