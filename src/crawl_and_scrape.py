import os
import json
import datetime
from data_collection_utils import get_sub_topic_page, get_news_urls, get_structure_content
from tqdm import tqdm

DATA_DIR = "D:/University/Kì 2025.1/Introduction to Data Science/OnlineNewsAnalysis/data"

topics_links = {
    "Thời sự": [
        "https://vnexpress.net/thoi-su"
        "https://vnexpress.net/thoi-su/chinh-tri",
        "https://vnexpress.net/thoi-su/huong-toi-ky-nguyen-moi",
        "https://vnexpress.net/thoi-su/80-nam-quoc-khanh",
        "https://vnexpress.net/thoi-su/dan-sinh",
        "https://vnexpress.net/thoi-su/lao-dong-viec-lam",
        "https://vnexpress.net/thoi-su/giao-thong",
        "https://vnexpress.net/thoi-su/quy-hy-vong"
    ],
    "Thế giới": [
        "https://vnexpress.net/the-gioi",
        "https://vnexpress.net/the-gioi/tu-lieu",
        "https://vnexpress.net/the-gioi/phan-tich",
        "https://vnexpress.net/the-gioi/quan-su"
    ],
    "Kinh doanh":[
        "https://vnexpress.net/kinh-doanh/net-zero",
        "https://vnexpress.net/kinh-doanh/quoc-te",
        "https://vnexpress.net/kinh-doanh/doanh-nghiep",
        "https://vnexpress.net/kinh-doanh/chung-khoan",

    ],
    "Khoa học công nghệ":[
        "https://vnexpress.net/khoa-hoc-cong-nghe/bo-khoa-hoc-va-cong-nghe",
        "https://vnexpress.net/khoa-hoc-cong-nghe/chuyen-doi-so",
        "https://vnexpress.net/khoa-hoc-cong-nghe/doi-moi-sang-tao",
        "https://vnexpress.net/khoa-hoc-cong-nghe/ai"
    ],
    "Bất động sản": [
        "https://vnexpress.net/bat-dong-san/chinh-sach",
        "https://vnexpress.net/bat-dong-san/thi-truong",
        "https://vnexpress.net/bat-dong-san/du-an",
        "https://vnexpress.net/bat-dong-san/khong-gian-song"
    ],
    "Sức khoẻ": [
        "https://vnexpress.net/suc-khoe/tin-tuc",
        "https://vnexpress.net/suc-khoe/cac-benh",
        "https://vnexpress.net/suc-khoe/song-khoe",
        "https://vnexpress.net/suc-khoe/vaccine"
    ],
    "Thể thao": [
        "https://vnexpress.net/bong-da",
        "https://vnexpress.net/the-thao/marathon",
        "https://vnexpress.net/the-thao/tennis",
        "https://vnexpress.net/the-thao/cac-mon-khac"
    ],
    "Giải trí": [
        "https://vnexpress.net/giai-tri/gioi-sao",
        "https://vnexpress.net/giai-tri/sach",
        "https://vnexpress.net/giai-tri/nhac",
        "https://vnexpress.net/giai-tri/thoi-trang"
    ],
    "Pháp luật": [
        "https://vnexpress.net/phap-luat/ho-so-pha-an",
        "https://vnexpress.net/phap-luat/tu-van"
    ],
    "Giáo dục": [
        "https://vnexpress.net/giao-duc/tin-tuc",
        "https://vnexpress.net/giao-duc/tuyen-sinh",
        "https://vnexpress.net/giao-duc/chan-dung",
        "https://vnexpress.net/giao-duc/giao-duc-40"
    ],
    "Đời sống": [
        "https://vnexpress.net/doi-song/nhip-song",
        "https://vnexpress.net/doi-song/to-am",
        "https://vnexpress.net/doi-song/bai-hoc-song",
        "https://vnexpress.net/doi-song/tieu-dung"
    ],
    "Du lịch": [
        "https://vnexpress.net/du-lich/diem-den",
        "http://vnexpress.net/du-lich/am-thuc",
        "https://vnexpress.net/du-lich/dau-chan",
        "https://vnexpress.net/du-lich/tu-van"
    ]
}

# Wanna to get the whole urls with related page
for key, value in topics_links.items():
    tmp_extend_urls_list = []
    for main_sub_links in value:
        pagination_urls = get_sub_topic_page(sub_topic_url=main_sub_links, pages=5)
        pagination_urls.append(main_sub_links)
        tmp_extend_urls_list.extend(pagination_urls)
    topics_links[key] = tmp_extend_urls_list

# Get the article urls
article_links = {}
for key, value in topics_links.items():
    article_url = []
    for sub_links in tqdm(value, desc=key):
        article_url.extend(get_news_urls(sub_links))
    article_links[key] = list(set(article_url))

# Get the day named the file
today = datetime.date.today().strftime("%Y-%m-%d")
filepath = f"data_{today}.json"

# Start open and put data into the json file
with open(os.path.join(DATA_DIR, filepath), "a", encoding="utf-8") as f:
    f.write("[\n")

    for key, value in article_links.items():
        for article_url in tqdm(value, desc=key):
            data = get_structure_content(article_url)
            if data != None:
                data["Tags"] = key
            # f.write("\t")
            json_string = json.dumps(data, ensure_ascii=False, indent=4)
            indented = "    " + json_string.replace("\n", "\n    ")
            f.write(indented)
            if key == list(article_links.keys())[-1] and article_url == value[-1]:
                f.write("\n")
            else:
                f.write(",\n")
    f.write("]")