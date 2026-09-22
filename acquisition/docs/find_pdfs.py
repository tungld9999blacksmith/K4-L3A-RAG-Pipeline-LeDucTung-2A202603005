import urllib.request
import re
import sys
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0'}

# Tìm kiếm trực tiếp trên dsvh.gov.vn
search_urls = [
    'https://dsvh.gov.vn/tim-kiem?keyword=da+nang',
    'https://dsvh.gov.vn/tim-kiem?keyword=ngu+hanh+son',
    'https://dsvh.gov.vn/tim-kiem?keyword=hoi+an'
]

found_pdfs = []

# Kiểm tra các số tạp chí DSVH đã biết:
# https://dsvh.gov.vn/Upload/files/Tap%20chi%20DSVH/So%203/...
# Thử quét các số tạp chí khác trên dsvh.gov.vn:
for so in range(1, 60):
    url = f'https://dsvh.gov.vn/tap-chi-di-san-van-hoa-so-{so}'
    # hoặc duyệt các bài viết
