import streamlit as st
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from openpyxl import Workbook
import base64

# ==================== CẤU HÌNH GIAO DIỆN ====================
st.set_page_config(page_title="Trình thu thập dữ liệu Google Maps", page_icon="", layout="wide")

st.markdown("""
    <style>
        /* Toàn bộ nền: Màu trắng hơi xanh nhẹ nhàng */
        .main {
            background-color: #F8F9FB; /* Nền rất sáng */
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* ---------------------------------------------------- */
        /* SỬA LỖI INHERIT: ÉP BUỘC TẤT CẢ VĂN BẢN LÀ XANH ĐẬM */
        /* ---------------------------------------------------- */
        body, 
        .main, 
        .stText, 
        .stMarkdown, 
        .stLabel, 
        .st-emotion-cache-1cpxq0x, /* Selector cho các label trong Streamlit */
        .st-emotion-cache-vk3ypb, /* Các container text chung của Streamlit */
        div, 
        span, 
        p, 
        li,
        .st-emotion-cache-1oe2x1e { /* Một số selector Streamlit khác */
            color: #15287a !important; 
        }

        /* Ghi đè lại màu chữ trắng cho các thành phần cần thiết */
        button[kind="primary"] * {
            color: #FFFFFF !important;
        }
        .stDownloadButton button * {
            color: #FFFFFF !important;
        }

        /* Tiêu đề chính H1 (Tên ứng dụng) - Dùng XANH ĐẬM */
        h1 {
            font-size: 2.5em;
            text-align: left;
            color: #15287a !important; /* Xanh đậm cho tiêu đề */
            text-shadow: none;
            border-bottom: 3px solid #e44e06; /* Dùng Cam làm đường phân cách */
            padding-bottom: 5px;
            margin-bottom: 0.5em;
        }

        /* stSubheader H2 - Dùng XANH ĐẬM */
        h2 {
            color: #15287a !important; /* Xanh đậm */
            font-weight: 600;
        }

        /* Hộp chứa nội dung chính - Trắng tinh, bo góc, bóng nhẹ */
        .stContainer {
            background: #FFFFFF; /* Màu trắng tinh */
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            border: 1px solid #15287a; /* Viền Xanh đậm */
        }

        .stContainer:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(21, 40, 122, 0.15); /* Bóng hơi xanh nhẹ */
        }
        
        /* Nút bấm hiện đại (Primary) - Dùng CAM làm màu hành động */
        button[kind="primary"] {
            background: #e44e06; /* Cam */
            font-weight: 600;
            border-radius: 8px;
            border: none;
            box-shadow: 0 4px 10px rgba(228, 78, 6, 0.4); /* Bóng cam */
            transition: all 0.3s ease-in-out;
            padding: 10px 20px;
        }
        button[kind="primary"]:hover {
            background: #15287a; /* Hover chuyển sang Xanh đậm */
            transform: translateY(-1px);
            box-shadow: 0 6px 15px rgba(21, 40, 122, 0.5); /* Bóng xanh */
        }
        
        /* Input Text - Màu XANH ĐẬM */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 1px solid #15287a; /* Xanh đậm */
            padding: 10px;
            color: #15287a !important; /* Đảm bảo màu chữ trong input là Xanh đậm */
        }
        
        /* Thanh tiến trình - Dùng CAM */
        .stProgress > div > div > div {
            background: #e44e06; /* Cam */
            border-radius: 5px;
        }

        /* Tải xuống - Nổi bật (Dùng XANH ĐẬM) */
        .stDownloadButton button {
            background: #15287a !important; /* Xanh đậm */
            font-weight: bold;
            border-radius: 8px !important;
            box-shadow: 0px 5px 15px rgba(21, 40, 122, 0.4) !important; /* Bóng xanh */
            padding: 10px 20px !important;
        }
        
        /* Container cho hình ảnh bản đồ */
        .map-container {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 25px rgba(228, 78, 6, 0.3); /* Bóng cam */
        }
        .map-container img {
            width: 100%;
            height: auto;
            display: block;
        }
    </style>
""", unsafe_allow_html=True)

# ==================== TIÊU ĐỀ & MÔ TẢ ====================
st.markdown("""
<h1>Google Maps Data Scraper</h1>
<p>Hệ thống chuyên nghiệp giúp trích xuất thông tin địa điểm (Tên, Địa chỉ, SĐT, Website) từ Google Maps chỉ với một từ khóa.</p>
""", unsafe_allow_html=True)

# ==================== HÀM CRAWL GOOGLE MAPS ====================
# (Giữ nguyên, không thay đổi chức năng)
def crawl_google_maps(query):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # LƯU Ý: Nếu chạy trên môi trường không có kết nối internet hoặc không cài đặt Chrome/Chromedriver, dòng này có thể gây lỗi.
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    st.info("Đang mở Google Maps...")
    driver.get(f"https://www.google.com/maps/search/{query}")
    time.sleep(5)

    st.info("Đang thu thập dữ liệu, vui lòng chờ...")
    data = []

    # Cuộn để tải nhiều kết quả hơn
    try:
        # TÌM XPATH TỐI ƯU HƠN HOẶC DÙNG DATA-ROLE NẾU CÓ
        scrollable_div = driver.find_element(By.XPATH, "//div[contains(@aria-label, 'Kết quả') or contains(@aria-label, 'Results')]")
        for _ in range(8):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(2)
    except:
        st.warning("Không thể cuộn danh sách — có thể giao diện Google hiện tại khác.")

    listings = driver.find_elements(By.XPATH, "//a[contains(@href, '/maps/place')]")
    st.write(f"Tìm thấy **{len(listings)}** địa điểm.")

    progress_bar = st.progress(0)

    for i, item in enumerate(listings):
        try:
            name = item.get_attribute("aria-label") or "Không rõ"
            link = item.get_attribute("href")

            # Mở tab chi tiết
            driver.execute_script("window.open(arguments[0], '_blank');", link)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(4)

            # ----------- LẤY ĐỊA CHỈ -----------
            address = "Không có địa chỉ"
            for xpath in [
                "//button[contains(@data-item-id, 'address')]//div[@class='Io6YTe']",
                "//div[@data-item-id='address']//div[@class='Io6YTe']",
                "//button[contains(@aria-label, 'Address')]/div",
                "//div[contains(text(), 'Địa chỉ')]/following-sibling::div"
            ]:
                try:
                    element = driver.find_element(By.XPATH, xpath)
                    address = element.text.strip()
                    if address:
                        break
                except:
                    continue

            # ----------- LẤY SỐ ĐIỆN THOẠI -----------
            phone = "Không có số điện thoại"
            for xpath in [
                "//button[contains(@data-item-id, 'phone')]//div[@class='Io6YTe']",
                "//button[contains(@aria-label, 'Phone')]/div",
                "//div[contains(text(), 'Điện thoại')]/following-sibling::div",
                "//div[contains(@aria-label, 'Phone')]/div"
            ]:
                try:
                    element = driver.find_element(By.XPATH, xpath)
                    phone = element.text.strip()
                    if phone:
                        break
                except:
                    continue

            # ----------- LẤY WEBSITE -----------
            website = "Không có website"
            try:
                # Ưu tiên data-item-id='authority' cho website
                website_element = driver.find_element(By.XPATH, "//a[contains(@data-item-id, 'authority')]")
                website = website_element.get_attribute("href")
            except:
                try:
                    # Tìm link http bất kỳ trong khu vực thông tin
                    website_element = driver.find_element(By.XPATH, "//a[contains(@href, 'http')]")
                    website = website_element.get_attribute("href")
                except:
                    pass

            data.append({
                "Tên địa điểm": name,
                "Địa chỉ": address,
                "Số điện thoại": phone,
                "Website": website,
                "Link Google Maps": link
            })

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            st.warning(f"Lỗi khi xử lý địa điểm: {e}")
            continue

        progress_bar.progress((i + 1) / len(listings))

    driver.quit()
    return data


# ==================== GIAO DIỆN CHÍNH (SỬ DỤNG COLUMNS) ====================

col1, col2 = st.columns([3, 2]) # Tỷ lệ 3:2 (Cột nội dung lớn hơn)

# --- Cột 1: Nhập liệu và Kết quả ---
with col1:
    st.subheader("Công cụ tìm kiếm")
    keyword = st.text_input(
        "Nhập tên cửa hàng, thương hiệu hoặc khu vực cần tìm:",
        placeholder="Ví dụ: PNJ, tiệm vàng PNJ tại TP.HCM",
        label_visibility="collapsed" # Ẩn label để giao diện gọn gàng hơn
    )

    if st.button("Bắt đầu thu thập dữ liệu", use_container_width=True, type="primary"):
        if keyword.strip() == "":
            st.warning("⚠️ Vui lòng nhập từ khóa trước khi bắt đầu.")
        else:
            # st.session_state để lưu dữ liệu tạm thời
            st.session_state['data'] = []
            
            with st.spinner("Đang xử lý, mở trình duyệt ẩn..."):
                data = crawl_google_maps(keyword)
                st.session_state['data'] = data
                
            if len(data) > 0:
                df = pd.DataFrame(data)
                st.session_state['df'] = df
                st.success(f"Thu thập thành công **{len(df)}** địa điểm!")

                st.markdown("---")
                st.subheader("Dữ liệu đã thu thập")
                st.dataframe(df, use_container_width=True)

                # Tải về Excel
                excel_file = "google_maps_data.xlsx"
                df.to_excel(excel_file, index=False)
                with open(excel_file, "rb") as f:
                    st.download_button("📥 Tải dữ liệu Excel", f, file_name=excel_file, use_container_width=True)

            else:
                st.error("❌ Không tìm thấy dữ liệu nào. Hãy thử lại với từ khóa khác.")
                
    st.markdown("</div>", unsafe_allow_html=True)

# --- Cột 2: Hình ảnh Bản đồ ---
with col2:
    st.markdown("<h3><br>Bản đồ trực quan</h3>", unsafe_allow_html=True) # Tạo khoảng trống
    st.markdown("""
        <div class="map-container">
            <img src="https://bizweb.dktcdn.net/100/235/532/articles/ho-chi-minh-ho-tro-cap-nhat-google-maps-ve-dich-covid-19-1.jpg?v=1623947998367" alt="Hình ảnh minh họa Google Maps" title="Minh họa giao diện Google Maps" />
        </div>
        <p style='text-align: center; color: #888; font-size: 0.9em; margin-top: 10px;'>Minh họa bản đồ số</p>
    """, unsafe_allow_html=True)


st.markdown("<hr>", unsafe_allow_html=True)