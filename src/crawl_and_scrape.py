import os
import json
import datetime
import pandas as pd
from data_collection_utils import VnExpress, DanTri
from tqdm import tqdm

REPO_DIR = os.path.dirname(os.getcwd())
DATA_DIR = os.path.join(REPO_DIR, "data")
vnexpress_processor = VnExpress()
dantri_processor = DanTri()

vnexpress_topics_links = {
    # "Thời sự": [
    #     "https://vnexpress.net/thoi-su",
    #     "https://vnexpress.net/thoi-su/chinh-tri",
    #     "https://vnexpress.net/thoi-su/huong-toi-ky-nguyen-moi",
    #     "https://vnexpress.net/thoi-su/80-nam-quoc-khanh"
    # ],
    # "Thế giới": [
    #     "https://vnexpress.net/the-gioi",
    #     "https://vnexpress.net/the-gioi/tu-lieu",
    #     "https://vnexpress.net/the-gioi/phan-tich",
    #     "https://vnexpress.net/the-gioi/quan-su"
    # ],
    # "Kinh doanh":[
    #     "https://vnexpress.net/kinh-doanh/net-zero",
    #     "https://vnexpress.net/kinh-doanh/quoc-te",
    #     "https://vnexpress.net/kinh-doanh/doanh-nghiep",
    #     "https://vnexpress.net/kinh-doanh/chung-khoan",

    # ],
    # "Khoa học công nghệ":[
    #     "https://vnexpress.net/khoa-hoc-cong-nghe/bo-khoa-hoc-va-cong-nghe",
    #     "https://vnexpress.net/khoa-hoc-cong-nghe/chuyen-doi-so",
    #     "https://vnexpress.net/khoa-hoc-cong-nghe/doi-moi-sang-tao",
    #     "https://vnexpress.net/khoa-hoc-cong-nghe/ai"
    # ],
    # "Bất động sản": [
    #     "https://vnexpress.net/bat-dong-san/chinh-sach",
    #     "https://vnexpress.net/bat-dong-san/thi-truong",
    #     "https://vnexpress.net/bat-dong-san/du-an",
    #     "https://vnexpress.net/bat-dong-san/khong-gian-song"
    # ],
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

dantri_topic_links = {
    "Thời sự": [
        "https://dantri.com.vn/thoi-su/chinh-tri.htm",
        "https://dantri.com.vn/thoi-su/hoc-tap-bac.htm",
        "https://dantri.com.vn/thoi-su/dai-hoi-dang-xiv.htm",
        "https://dantri.com.vn/thoi-su/moi-truong.htm"
    ],
    "Thế giới": [
        "https://dantri.com.vn/the-gioi/quan-su.htm",
        "https://dantri.com.vn/the-gioi/phan-tich-binh-luan.htm",
        "https://dantri.com.vn/the-gioi/phan-tich-binh-luan.htm",
        "https://dantri.com.vn/the-gioi/phan-tich-binh-luan.htm"
    ],
    "Kinh doanh": [
        "https://dantri.com.vn/kinh-doanh/tai-chinh.htm",
        "https://dantri.com.vn/kinh-doanh/chung-khoan.htm",
        "https://dantri.com.vn/kinh-doanh/doanh-nghiep.htm",
        "https://dantri.com.vn/kinh-doanh/khoi-nghiep.htm"
    ],
    "Khoa học công nghệ": [
        "https://dantri.com.vn/khoa-hoc/the-gioi-tu-nhien.htm",
        "https://dantri.com.vn/khoa-hoc/vu-tru.htm",
        "https://dantri.com.vn/khoa-hoc/khoa-hoc-doi-song.htm",
        "https://dantri.com.vn/khoa-hoc/khoa-hoc-doi-song.htm",
        "https://dantri.com.vn/cong-nghe/an-ninh-mang.htm",
        "https://dantri.com.vn/cong-nghe/san-pham-cong-dong.htm"
    ],
    "Bất động sản": [
        "https://dantri.com.vn/bat-dong-san/du-an.htm",
        "https://dantri.com.vn/bat-dong-san/thi-truong.htm",
        "https://dantri.com.vn/bat-dong-san/nha-dat.htm",
        "https://dantri.com.vn/bat-dong-san/nhip-song-do-thi.htm"
    ],
    "Sức khoẻ": [
        "https://dantri.com.vn/suc-khoe.htm",
        "https://dantri.com.vn/suc-khoe/song-khoe.htm",
        "https://dantri.com.vn/suc-khoe/ung-thu.htm",
        "https://dantri.com.vn/suc-khoe/kien-thuc-gioi-tinh.htm"
    ],
    "Thể thao": [
        "https://dantri.com.vn/the-thao/bong-da.htm",
        "https://dantri.com.vn/the-thao/pickleball.htm",
        "https://dantri.com.vn/the-thao/tennis.htm",
        "https://dantri.com.vn/the-thao/golf.htm"
    ],
    "Giải trí": [
        "https://dantri.com.vn/giai-tri/hau-truong.htm",
        "https://dantri.com.vn/giai-tri/dien-anh.htm",
        "https://dantri.com.vn/giai-tri/am-nhac.htm",
        "https://dantri.com.vn/giai-tri/thoi-trang.htm"
    ],
    "Pháp luật": [
        "https://dantri.com.vn/phap-luat/ho-so-vu-an.htm",
        "https://dantri.com.vn/phap-luat/phap-dinh.htm"
    ],
    "Giáo dục": [
        "https://dantri.com.vn/giao-duc.htm",
        "https://dantri.com.vn/giao-duc/goc-phu-huynh.htm",
        "https://dantri.com.vn/giao-duc/khuyen-hoc.htm",
        "https://dantri.com.vn/giao-duc/guong-sang.htm",
    ],
    "Đời sống": [
        "https://dantri.com.vn/doi-song.htm",
        "https://dantri.com.vn/doi-song/cong-dong.htm",
        "https://dantri.com.vn/doi-song/thuong-luu.htm",
        "https://dantri.com.vn/doi-song/nha-dep.htm",
        "https://dantri.com.vn/doi-song/gioi-tre.htm"
    ],
    "Du lịch": [
        "https://dantri.com.vn/du-lich.htm",
        "https://dantri.com.vn/du-lich/tin-tuc.htm",
        "https://dantri.com.vn/du-lich/kham-pha.htm",
        "https://dantri.com.vn/du-lich/mon-ngon-diem-dep.htm"
    ]
}

# Function to get the result

# Get list link to an artical
def get_full_link_list(topic_links: dict, processor):
    full_topics_links = dict()
    for key, value in topic_links.items():
        tmp_extend_urls_list = []
        for main_sub_links in value:
            pagination_urls = processor.get_sub_topic_page(sub_topic_url=main_sub_links, pages=6)
            tmp_extend_urls_list.extend(pagination_urls)
        full_topics_links[key] = list(set(tmp_extend_urls_list))
    
    return full_topics_links

# get the link list and process article corresponding to each link
def article_processing(topics_links, processor, f):
    topics_links = get_full_link_list(topics_links, processor)
    for key, value in topics_links.items():
        article_urls = []
        for sub_links in tqdm(value, desc=key):
            article_urls.extend(processor.get_news_urls(sub_links))
        article_urls = list(set(article_urls))

        for article_url in tqdm(article_urls, desc=key):
            data = processor.get_structure_content(article_url)
            if data != None and type(data) != str :
                data["Tags"] = key
            json_string = json.dumps(data, ensure_ascii=False, indent=4)
            indented = "    " + json_string.replace("\n", "\n    ")
            f.write(indented)
            if topics_links == vnexpress_topics_links and key == list(topics_links.keys())[-1] and article_url == article_urls[-1]:
                f.write("\n")
            else:
                f.write(",\n")

def scrape_missing_paper(json_path: str, f):

    with open(json_path, "r", encoding="utf-8") as file:
        article_urls = json.load(file)

    for url in tqdm(article_urls, desc="missing article"):
        if url[-3:] == "htm":
            processor = dantri_processor
        else:
            processor = vnexpress_processor

        data = processor.get_structure_content(url)
        if data != None and type(data) != str :
            data["Tags"] = "NA"
        json_string = json.dumps(data, ensure_ascii=False, indent=4)
        indented = "    " + json_string.replace("\n", "\n    ")
        f.write(indented)
        if url == article_urls[-1]:
            f.write("\n")
        else:
            f.write(",\n")

def merging_data(json_path_1, json_path_2, output_path):

    with open(json_path_1, "r", encoding="utf-8") as file:
        article_info = json.load(file)
    
    clean_article_info = [x for x in article_info if type(x) == dict]
    print(len(clean_article_info))

    with open(json_path_2, "r", encoding="utf-8") as file:
        missing_info = json.load(file)

    clean_missing_info = [x for x in missing_info if type(x) == dict]
    for info in clean_missing_info:
        info["Related_link"] = []
    print(len(clean_missing_info))
    
    clean_article_info += clean_missing_info
    print(len(clean_article_info))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(clean_article_info, f, ensure_ascii=False, indent=4)
    print("Merging finished !")

def sorting_related_links_not_crawled(data_json_path, missing_json_path, output_path):
    with open(data_json_path, "r", encoding="utf-8") as file:
        article_info = json.load(file)

    with open(missing_json_path, "r", encoding="utf-8") as file:
        missing_url_list = json.load(file)
    
    for info in article_info:
        new_related_link = []
        for related_link in info["Related_link"]:
            if related_link not in missing_url_list:
                new_related_link.append(related_link)
        info["Related_link"] = new_related_link

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(article_info, f, ensure_ascii=False, indent=4)
    print("Sorting finished !")

def index_article(data_json_path, output_path):
    with open(data_json_path, "r", encoding="utf-8") as file:
        article_info = json.load(file)
    
    index_count = 1
    for info in article_info:
        info["article_index"] = index_count
        index_count += 1
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(article_info, f, ensure_ascii=False, indent=4)
    
if __name__ == "__main__":
    # Get the day named the file
    today = datetime.date.today().strftime("%Y-%m-%d")
    # filepath = f"data_{today}.json"
    filepath = f"data_2025-12-16.json"

    ## Crawl & scrape first
    # # Start open and put data into the json file
    # with open(os.path.join(DATA_DIR, filepath), "a", encoding="utf-8") as f:
    #     f.write("[\n")
    #     # Get the article urls
    #     # article_processing(dantri_topic_links, dantri_processor, f)
    #     article_processing(vnexpress_topics_links, vnexpress_processor, f)
    #     f.write("]")

    ## Add missing info
    # missing_path = "D:/University/Kì 2025.1/Introduction to Data Science/OnlineNewsAnalysis/data/missing_article.json"
    # missing_processed_file = "missing_data_structure.json"
    # with open(os.path.join(DATA_DIR, missing_processed_file), "a", encoding="utf-8") as f:
    #     # f.write("[\n")
    #     scrape_missing_paper(json_path=missing_path, f = f)
    #     f.write("]")

    ## Merging 2 file
    # raw_data_path = os.path.join(DATA_DIR, "data_2025-12-16.json")
    # missing_data_path = os.path.join(DATA_DIR, "missing_data_structure.json")
    # output_path = os.path.join(DATA_DIR, "merging_data_info.json")
    # merging_data(raw_data_path, missing_data_path, output_path)

    # # Remove not crawled articles in related links
    # data_json_path = os.path.join(DATA_DIR, "merging_data_info.json")
    # missing_articles_path = os.path.join(DATA_DIR, "missing_article.json")
    # output_path = os.path.join(DATA_DIR, "Cleanest_data.json")
    # sorting_related_links_not_crawled(data_json_path, missing_articles_path, output_path)

    # Indexing data
    data_json_path = os.path.join(DATA_DIR, "Cleanest_data.json")
    output_path = os.path.join(DATA_DIR, "Indexed_cleanest_data.json")
    index_article(data_json_path, output_path)