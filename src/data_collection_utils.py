import os
import json
# import yaml
import requests
from bs4 import BeautifulSoup
import time
import re
import random
import urllib3

# CONTENT SCRAPING
class VnExpress():

    def get_content_(self, url: str) -> str:
        """
        This function is responsible for:
        Fetching the RAW HTML content from a given URL,
        with an anti-bot detection mechanism.
        """

        # Import additional libraries locally to avoid global conflicts

        # Clean URL: remove the fragment part after '#' if it exists
        if '#' in url:
            url = url.split('#')[0]

        # Validate URL: it must start with "http"
        if not url.startswith('http'):
            return None  # Return None if the URL is invalid

        # A list of different User-Agents to randomly rotate (helps avoid blocking)
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

        # Create fake browser headers to make the request look human
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',  # “Do Not Track” header (Yêu cầu không theo dõi)
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'User-Agent': random.choice(user_agents),
            'Referer': 'https://vnexpress.net/',
            'Origin': 'https://vnexpress.net'
        }

        # Create a session to maintain cookies and headers across multiple requests
        session = requests.Session()

        # Disable SSL verification (some sites may have invalid certificates)
        session.verify = False

        # Suppress SSL warning messages from showing in the console
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Update session headers with our custom headers
        session.headers.update(headers)

        # Try sending the request up to 3 times in case of failure
        for attempt in range(3):
            try:
                # Add random delay between requests to avoid being rate-limited
                time.sleep(random.uniform(1, 3))

                # Send the GET request
                response = session.get(
                    url,
                    timeout=30,           # Max wait time = 30s (Giới hạn tối đa 30 giây)
                    allow_redirects=True, # Follow redirects automatically (Cho phép tự động theo redirect)
                    stream=False          # Download all content at once (Không tải kiểu stream)
                )

                # If successful response (status code 200)
                if response.status_code == 200:
                    response.encoding = 'utf-8'  # Set UTF-8 encoding for Vietnamese text (Đặt mã hóa UTF-8)
                    content = response.text      # Extract HTML content (Lấy nội dung HTML)
                    response.close()
                    session.close()
                    return content               # Return HTML content (Trả kết quả về)

                # If access is forbidden (HTTP 403)
                elif response.status_code == 403:
                    # Change User-Agent and retry
                    headers['User-Agent'] = random.choice(user_agents)
                    session.headers.update(headers)
                    time.sleep(random.uniform(2, 5))  # Wait 2–5 seconds before retrying (Nghỉ 2–5 giây rồi thử lại)
                    continue

                # If other HTTP errors occur
                else:
                    if attempt == 2:
                        print(f"HTTP {response.status_code} for {url}")
                    response.close()

            # Handle SSL errors
            except requests.exceptions.SSLError:
                continue  # Retry (Thử lại)

            # Handle general request errors (timeouts, connection issues, etc.)
            except requests.exceptions.RequestException as e:
                if attempt == 2:
                    print(f"Request error for {url}: {e}")

            # Handle any unexpected errors
            except Exception as e:
                if attempt == 2:
                    print(f"Unknown error for {url}: {e}")

            # Increase delay between retries to avoid server rate limits
            if attempt < 2:
                time.sleep(random.uniform(3 + attempt, 6 + attempt))

        # After 3 failed attempts, close the session and return None
        session.close()
        return None

    def get_content_with_curl(self, url: str) -> str:
        """
        Backup method using cURL to bypass anti-bot systems.
        -> If 'requests' fails or gets blocked, we use the external curl command instead.
        """
        import subprocess   # Used to run system commands (like 'curl')
        import tempfile     # Used to create temporary files
        import os           # Used for file operations (Dùng để xóa file tạm sau khi sử dụng)

        # Clean URL: remove any fragment part after '#'
        # (Làm sạch URL: loại bỏ phần sau dấu '#')
        if '#' in url:
            url = url.split('#')[0]

        # Validate URL: must start with 'http' or 'https'
        # (Kiểm tra tính hợp lệ: URL phải bắt đầu bằng http hoặc https)
        if not url.startswith('http'):
            return None

        try:
            # Create a temporary file to store the downloaded HTML
            # (Tạo file tạm thời để lưu kết quả tải về)
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.html') as temp_file:
                temp_filename = temp_file.name  # Save file path for later use (Lưu tên file để sử dụng sau)

            # Build the curl command to simulate a real browser (like Chrome)
            # (Tạo lệnh curl giả lập trình duyệt thật — ví dụ như Chrome)
            curl_command = [
                'curl',
                '-s',  # Silent mode: no progress bar or logs (Chế độ im lặng — không in log ra terminal)
                '-L',  # Follow redirects automatically (Tự động theo dõi các redirect)
                '--compressed',  # Enable compressed transfer (Cho phép tải nội dung nén)
                '--max-time', '30',  # Timeout after 30 seconds (Giới hạn thời gian 30 giây)
                '--retry', '2',      # Retry twice if request fails (Thử lại tối đa 2 lần nếu lỗi)
                '--user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                # Use a realistic User-Agent to avoid detection (Giả lập trình duyệt thật để tránh bị chặn)

                # Common browser headers (Các header phổ biến mà trình duyệt gửi kèm)
                '--header', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                '--header', 'Accept-Language: vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                '--header', 'Accept-Encoding: gzip, deflate, br',
                '--header', 'DNT: 1',  # Do Not Track header (Yêu cầu không theo dõi)
                '--header', 'Connection: keep-alive',
                '--header', 'Upgrade-Insecure-Requests: 1',
                '--header', 'Sec-Fetch-Dest: document',
                '--header', 'Sec-Fetch-Mode: navigate',
                '--header', 'Sec-Fetch-Site: none',
                '--header', 'Sec-Fetch-User: ?1',
                '--header', 'Cache-Control: max-age=0',
                '--referer', 'https://vnexpress.net/',  # Pretend to come from vnexpress homepage (Giả vờ người dùng click từ trang chủ)
                '--output', temp_filename,              # Save output HTML to temp file (Ghi nội dung tải về vào file tạm)
                url
            ]

            # Execute the curl command as a subprocess
            # (Chạy lệnh curl bên ngoài Python)
            result = subprocess.run(
                curl_command,            # Command to run (Lệnh cần chạy)
                capture_output=True,     # Capture stdout/stderr (Lưu stdout và stderr thay vì in ra)
                text=True,               # Return output as text (Trả kết quả về dạng chuỗi)
                timeout=35               # Total timeout for curl (Giới hạn thời gian tổng 35 giây)
            )

            # If curl executed successfully (exit code = 0)
            # (Nếu curl chạy thành công — mã thoát = 0)
            if result.returncode == 0:
                # Read the downloaded HTML content from temp file
                # (Đọc nội dung HTML từ file tạm)
                with open(temp_filename, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Remove the temp file after reading
                # (Xóa file tạm sau khi sử dụng)
                os.unlink(temp_filename)

                # Check if the content is long enough to be valid
                # (Kiểm tra xem nội dung có đủ dài để coi là hợp lệ không)
                if len(content) > 1000:
                    return content

            # Cleanup: if temp file still exists, delete it
            # (Dọn dẹp: nếu file tạm vẫn còn, xóa nó đi)
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

        except Exception as e:
            # Handle all possible errors (e.g. curl not installed, timeout)
            # (Xử lý các lỗi có thể xảy ra như curl chưa cài hoặc hết thời gian)
            print(f"Curl method failed for {url}: {e}")

        # Return None if download failed
        # (Trả về None nếu không tải được nội dung)
        return None

    def get_content_enhanced(self, url: str) -> str:
        """
        Combined method — try requests first, then fall back to cURL.
        """
        # Try to fetch content using the main requests-based method
        # Thử tải nội dung bằng hàm chính sử dụng requests
        content = self.get_content_(url)
        if content:
            return content  # Return immediately if successful

        # If requests failed, try using cURL as a backup
        # (Nếu requests thất bại, dùng cURL làm phương án dự phòng)
        # Nếu requests thất bại, dùng cURL làm backup (bypass anti-bot tốt hơn)
        print(f" Trying curl method for {url[:50]}... (Thử phương pháp curl cho {url[:50]}...)")
        content = self.get_content_with_curl(url)
        if content:
            print(f" Curl success! (Curl thành công!)")
            return content

        # If both methods fail, return None
        return None

    def parse_article(self, html_content: str, url: str) -> dict:
        """
        Parse article details from HTML content.
        Returns a dict with title, description, content, and URL.
        """
        try:
            # Check if HTML is empty or too short (<500 chars)
            # (Kiểm tra nếu HTML trống hoặc quá ngắn, có thể là trang lỗi hoặc redirect)
            if not html_content or len(html_content) < 500:
                return None

            # Create BeautifulSoup object for easier HTML navigation
            soup = BeautifulSoup(html_content, 'html.parser')

            # EXTRACT TITLE
            title_detail = None

            # List of CSS selectors that may contain the title (depends on website structure)
            title_selectors = [
                "h1.title-detail",
                "h1.title_news_detail",
                "h1[class*='title']",
                "h1",
                ".title-detail",
                ".title_news_detail",
                "title"
            ]

            # Iterate through selectors until a valid title is found
            for selector in title_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    # Skip if title is too short or contains site name
                    if text and len(text) > 10 and 'vnexpress' not in text.lower():
                        title_detail = text
                        break
                if title_detail:
                    break

            # If still no title found, skip article
            if not title_detail:
                title_detail = "NA"


            # EXTRACT DESCRIPTION
            description = ""

            # List of possible selectors for article description
            desc_selectors = [
                "p.description",
                "p.lead",
                "p[class*='description']",
                "p[class*='lead']",
                ".description",
                ".lead",
                "meta[name='description']",
                "meta[property='og:description']"
            ]

            # Try each selector until found
            for selector in desc_selectors:
                elements = soup.select(selector)
                for element in elements:
                    if element.name == 'meta':
                        text = element.get('content', '').strip()
                    else:
                        text = element.get_text().strip()
                    # Accept only if text length is meaningful
                    # (Chỉ chấp nhận nếu độ dài mô tả đủ lớn)
                    if text and len(text) > 20:
                        description = text
                        break
                if description:
                    break


            # ===================== EXTRACT MAIN CONTENT =====================
            content_text = ""

            # List of possible content containers
            content_selectors = [
                "article.fck_detail p.Normal",
                "article.fck_detail p",
                ".fck_detail p.Normal",
                ".fck_detail p",
                "article.content_detail p",
                ".content_detail p",
                "div.content_detail p",
                "article p",
                ".Normal",
                "div[class*='content'] p",
                "div[class*='article'] p",
                "main p"
            ]

            # Loop through each pattern to extract paragraphs
            for selector in content_selectors:
                paragraphs = soup.select(selector)
                if paragraphs:
                    temp_content = ""
                    for p in paragraphs:
                        text = p.get_text().strip()
                        # print(text)

                        # Skip irrelevant lines such as “Theo VnExpress”, “Ảnh:”, etc.
                        if ( text and len(text) > 50 and not re.match(r'^[\s\W]*$', text)):
                            temp_content += text + " "

                    # Accept if content length > 200 chars
                    if len(temp_content) > 200:
                        content_text = temp_content.strip()
                        break


            # ===================== IF STILL NO CONTENT FOUND =====================
            if len(content_text) < 200:
                main_content_selectors = [
                    "div[class*='content']",
                    "div[class*='article']",
                    "div[class*='detail']",
                    "main",
                    "article"
                ]

                # Try to extract text from larger containers
                
                for selector in main_content_selectors:
                    containers = soup.select(selector)
                    for container in containers:
                        paragraphs = container.find_all('p')
                        temp_content = ""
                        for p in paragraphs:
                            text = p.get_text().strip()
                            if text and len(text) > 30:
                                temp_content += text + " "
                        if len(temp_content) > len(content_text):
                            content_text = temp_content.strip()
                    if len(content_text) > 200:
                        break


            # ===================== FINAL CHECK AND RETURN =====================
            if len(content_text) < 100:
                # If article body is too short → likely not a valid article
                # (Nếu nội dung quá ngắn → có thể là trang rỗng, hoặc chỉ có video)
                return None
            author = name = soup.select_one('p.Normal strong').get_text(strip=True)

            # ====================== Extract Date & Time =========================

            day: str = ""
            time_set: str =""

            datetime_selectors = [
                "span[class*='date']",
                "div.header-content span",
                "time",
                "p.date",
                "div.date",
            ]

            for selector in datetime_selectors:
                elements = soup.select(selector)
                for element in elements:
                    day_text = element.get_text().split(",")[1].strip()
                    time_text = element.get_text().split(",")[2].strip()
                    if day_text and time_text:
                        day = day_text
                        time_set = time_text
                        break
                if day and time_set:
                    break

            # ====================== Extract Tag =========================

            keywords_list = []

            # Các selector phổ biến để tìm phần chứa keyword
            keyword_selectors = [
                "meta[name='keywords']",
                "div[class*='keyword']",
                "ul[class*='keyword'] li",
                "span[class*='keyword']",
                "a[class*='keyword']",
            ]

            for selector in keyword_selectors:
                elements = soup.select(selector)
                for element in elements:
                    # Nếu là thẻ <meta>, lấy thuộc tính "content"
                    if element.name == "meta" and "content" in element.attrs:
                        content = element['content'].strip()
                        if content:
                            # tách nếu có nhiều keyword trong content
                            for kw in [k.strip() for k in content.split(",") if k.strip()]:
                                keywords_list.append(kw)
                    else:
                        # Còn lại thì lấy text hiển thị
                        kw = element.get_text().strip()
                        if kw:
                            keywords_list.append(kw)
            # Xóa trùng lặp
            keywords_list = list(set(keywords_list))
                    
            # Return final result as dictionary
            # (Trả kết quả cuối cùng dưới dạng dictionary để dễ xử lý tiếp)
            return {
                "Source": "VnExpress",
                "url": url,
                "Date": day,
                "Time": time_set,
                "Author": author,
                "Title": title_detail,
                "Description": description if description else title_detail[:200],
                "Contents": content_text,
                "Key_words": keywords_list
            }

        except Exception as e:
            # If parsing fails, return None
            # (Nếu xảy ra lỗi trong quá trình phân tích, trả về None để bỏ qua bài lỗi)
            # print("ERROR: ",  e)
            return None

    def get_structure_content(self, url: str) -> dict:
        """
        Get detailed content of a news article from its URL.
        """
        try:
            # Try to get HTML from the URL (automatically chooses between requests and curl)
            raw_content = self.get_content_enhanced(url)

            # If unable to retrieve content (None returned), stop here
            if raw_content is None:
                return None

            # If HTML is fetched, parse and extract article info
            return self.parse_article(raw_content, url)

        except Exception as e:
            # If any unexpected error occurs (network, parsing, syntax, etc.)
            # print("ERROR: ", e)
            return f"Scraping ERROR with {url}"
    # CRAWLING
    def get_news_urls(self, page_link: str) -> list:
        """
        Get all article links from a VnExpress page.
        """
        # List to store all collected article links
        links = []  

        # Fetch full HTML content from the topic page (like "Thời sự", "Thế giới", etc.)
        raw_content = self.get_content_enhanced(page_link)

        # If no HTML content is retrieved, return an empty list
        if raw_content is None:
            return links

        # Parse the HTML content using BeautifulSoup for easier tag navigation
        soup = BeautifulSoup(raw_content, 'html.parser')

        # LIST OF POSSIBLE SELECTORS
        # Websites can use different HTML structures for articles.
        # Example: Articles may be inside <article>, <h2>, or <h3> tags.
        link_selectors = [
            "article h2.title-news a",  # Most common form (Dạng phổ biến nhất)
            "article h3.title-news a",  # Some pages use <h3> instead of <h2> (Một số trang dùng h3)
            "h2.title-news a",          # Without <article> wrapper (Không có thẻ <article> bọc ngoài)
            "h3.title-news a",
            "h2 a[href*='.html']",      # Any <h2> with an href containing ".html" (Bất kỳ thẻ h2 có .html)
            "h3 a[href*='.html']",
            "article a[href*='.html']", # All <a> inside <article> that link to .html (Mọi link trong <article> có .html)
            "a[href*='.html']"          # Fallback: any <a> with .html (Dự phòng: mọi <a> có .html)
        ]

        # Base URL to complete relative links
        base_url = "https://vnexpress.net"

        # LOOP THROUGH SELECTORS
        for selector in link_selectors:
            link_elements = soup.select(selector)
            for element in link_elements:
                # Extract the "href" attribute value
                href = element.get('href')

                if href:
                    # Remove fragment part after "#" if present
                    if '#' in href:
                        href = href.split('#')[0]

                    # If relative path (starts with "/"), join with base_url
                    if href.startswith('/'):
                        href = base_url + href
                    # Skip if link doesn’t start with "http" (invalid or external format)
                    elif not href.startswith('http'):
                        continue

                    # VALIDATION CHECKS
                    # Conditions:
                    # - Must contain ".html" (Phải có .html)
                    # - Must include at least one digit (Có ít nhất 1 chữ số)
                    # - Must contain "vnexpress.net" (Là link nội bộ)
                    # - Must be longer than 50 chars (Dài hơn 50 ký tự)
                    if ('.html' in href and
                        re.search(r'\d+', href) and
                        'vnexpress.net' in href and
                        len(href) > 50):
                        links.append(href)

            # Stop if valid links are found (don’t test other selectors)
            if links:
                break

        # POST-PROCESSING
        # Remove duplicate links using set, then convert back to list
        unique_links = list(set(links))

        return unique_links
    # Pagination
    def get_sub_topic_page(self, sub_topic_url, pages=1) -> list:
        """
        Generate a list of paginated URLs for a given VnExpress sub-topics
        Example:
            sub_topic_url = "https://vnexpress.net/the-gioi"
            pages = 3
            Output:
            [
                "https://vnexpress.net/the-gioi",
                "https://vnexpress.net/the-gioi-p2",
                "https://vnexpress.net/the-gioi-p3"
            ]
        Only the SUB topic has the more page, the main page only have 1 page
        """

        # Initialize the list with the base URL (first page)
        urls_list = [sub_topic_url]

        # Loop through page numbers from 2 to the specified number of pages
        for page in range(2, pages + 1):
            new_url = f"{sub_topic_url}-p{page}"
            # Add this generated URL to the list
            urls_list.append(new_url)

        # Return the complete list of URLs
        return urls_list



class DanTri():

    def get_content_(self, url: str) -> str:
        """
        This function is responsible for:
        Fetching the RAW HTML content from a given URL,
        with an anti-bot detection mechanism.

        RETURN: String of htm content
        """

        # Import additional libraries locally to avoid global conflicts

        # Clean URL: remove the fragment part after '#' if it exists
        if '#' in url:
            url = url.split('#')[0]

        # Validate URL: it must start with "http"
        if not url.startswith('http'):
            return None  # Return None if the URL is invalid

        # A list of different User-Agents to randomly rotate (helps avoid blocking)
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

        # Create fake browser headers to make the request look human
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',  
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'User-Agent': random.choice(user_agents),
            'Referer': 'https://dantri.com.vn/',
            'Origin': 'https://dantri.com.vn/'
        }

        # Create a session to maintain cookies and headers across multiple requests
        session = requests.Session()

        # Disable SSL verification (some sites may have invalid certificates)
        session.verify = False

        # Suppress SSL warning messages from showing in the console
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Update session headers with our custom headers
        session.headers.update(headers)

        # Try sending the request up to 3 times in case of failure
        for attempt in range(3):
            try:
                # Add random delay between requests to avoid being rate-limited
                time.sleep(random.uniform(1, 3))

                # Send the GET request
                response = session.get(
                    url,
                    timeout=30,           # Max wait time = 30s (Giới hạn tối đa 30 giây)
                    allow_redirects=True, # Follow redirects automatically (Cho phép tự động theo redirect)
                    stream=False          # Download all content at once (Không tải kiểu stream)
                )

                # If successful response (status code 200)
                if response.status_code == 200:
                    response.encoding = 'utf-8'  # Set UTF-8 encoding for Vietnamese text (Đặt mã hóa UTF-8)
                    content = response.text      # Extract HTML content (Lấy nội dung HTML)
                    response.close()
                    session.close()
                    return content               # Return HTML content (Trả kết quả về)

                # If access is forbidden (HTTP 403)
                elif response.status_code == 403:
                    # Change User-Agent and retry
                    headers['User-Agent'] = random.choice(user_agents)
                    session.headers.update(headers)
                    time.sleep(random.uniform(2, 5))  # Wait 2–5 seconds before retrying (Nghỉ 2–5 giây rồi thử lại)
                    continue

                # If other HTTP errors occur
                else:
                    if attempt == 2:
                        print(f"HTTP {response.status_code} for {url}")
                    response.close()

            # Handle SSL errors
            except requests.exceptions.SSLError:
                continue  # Retry (Thử lại)

            # Handle general request errors (timeouts, connection issues, etc.)
            except requests.exceptions.RequestException as e:
                if attempt == 2:
                    print(f"Request error for {url}: {e}")

            # Handle any unexpected errors
            except Exception as e:
                if attempt == 2:
                    print(f"Unknown error for {url}: {e}")

            # Increase delay between retries to avoid server rate limits
            if attempt < 2:
                time.sleep(random.uniform(3 + attempt, 6 + attempt))

        # After 3 failed attempts, close the session and return None
        session.close()
        return None
    
    def get_content_with_curl(self, url: str) -> str:
        """
        Backup method using cURL to bypass anti-bot systems.
        -> If 'requests' fails or gets blocked, we use the external curl command instead.
        
        RETURN: String of raw html text
        """
        import subprocess   # Used to run system commands (like 'curl')
        import tempfile     # Used to create temporary files
        import os           # Used for file operations (Dùng để xóa file tạm sau khi sử dụng)

        # Clean URL: remove any fragment part after '#'
        # (Làm sạch URL: loại bỏ phần sau dấu '#')
        if '#' in url:
            url = url.split('#')[0]

        # Validate URL: must start with 'http' or 'https'
        # (Kiểm tra tính hợp lệ: URL phải bắt đầu bằng http hoặc https)
        if not url.startswith('http'):
            return None

        try:
            # Create a temporary file to store the downloaded HTML
            # (Tạo file tạm thời để lưu kết quả tải về)
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.html') as temp_file:
                temp_filename = temp_file.name  # Save file path for later use (Lưu tên file để sử dụng sau)

            # Build the curl command to simulate a real browser (like Chrome)
            # (Tạo lệnh curl giả lập trình duyệt thật — ví dụ như Chrome)
            curl_command = [
                'curl',
                '-s',  # Silent mode: no progress bar or logs (Chế độ im lặng — không in log ra terminal)
                '-L',  # Follow redirects automatically (Tự động theo dõi các redirect)
                '--compressed',  # Enable compressed transfer (Cho phép tải nội dung nén)
                '--max-time', '30',  # Timeout after 30 seconds (Giới hạn thời gian 30 giây)
                '--retry', '2',      # Retry twice if request fails (Thử lại tối đa 2 lần nếu lỗi)
                '--user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                # Use a realistic User-Agent to avoid detection (Giả lập trình duyệt thật để tránh bị chặn)

                # Common browser headers (Các header phổ biến mà trình duyệt gửi kèm)
                '--header', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                '--header', 'Accept-Language: vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                '--header', 'Accept-Encoding: gzip, deflate, br',
                '--header', 'DNT: 1',  # Do Not Track header (Yêu cầu không theo dõi)
                '--header', 'Connection: keep-alive',
                '--header', 'Upgrade-Insecure-Requests: 1',
                '--header', 'Sec-Fetch-Dest: document',
                '--header', 'Sec-Fetch-Mode: navigate',
                '--header', 'Sec-Fetch-Site: none',
                '--header', 'Sec-Fetch-User: ?1',
                '--header', 'Cache-Control: max-age=0',
                '--referer', 'https://dantri.com.vn/',  # Pretend to come from vnexpress homepage (Giả vờ người dùng click từ trang chủ)
                '--output', temp_filename,              # Save output HTML to temp file (Ghi nội dung tải về vào file tạm)
                url
            ]

            # Execute the curl command as a subprocess
            # (Chạy lệnh curl bên ngoài Python)
            result = subprocess.run(
                curl_command,            # Command to run (Lệnh cần chạy)
                capture_output=True,     # Capture stdout/stderr (Lưu stdout và stderr thay vì in ra)
                text=True,               # Return output as text (Trả kết quả về dạng chuỗi)
                timeout=35               # Total timeout for curl (Giới hạn thời gian tổng 35 giây)
            )

            # If curl executed successfully (exit code = 0)
            # (Nếu curl chạy thành công — mã thoát = 0)
            if result.returncode == 0:
                # Read the downloaded HTML content from temp file
                # (Đọc nội dung HTML từ file tạm)
                with open(temp_filename, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Remove the temp file after reading
                # (Xóa file tạm sau khi sử dụng)
                os.unlink(temp_filename)

                # Check if the content is long enough to be valid
                # (Kiểm tra xem nội dung có đủ dài để coi là hợp lệ không)
                if len(content) > 1000:
                    return content

            # Cleanup: if temp file still exists, delete it
            # (Dọn dẹp: nếu file tạm vẫn còn, xóa nó đi)
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

        except Exception as e:
            # Handle all possible errors (e.g. curl not installed, timeout)
            # (Xử lý các lỗi có thể xảy ra như curl chưa cài hoặc hết thời gian)
            print(f"Curl method failed for {url}: {e}")

        # Return None if download failed
        # (Trả về None nếu không tải được nội dung)
        return None
    
    def get_content_enhanced(self, url: str) -> str:
        """
        Combined method — try requests first, then fall back to cURL.
        """
        # Try to fetch content using the main requests-based method
        # Thử tải nội dung bằng hàm chính sử dụng requests
        content = self.get_content_(url)
        if content:
            return content  # Return immediately if successful

        # If requests failed, try using cURL as a backup
        # (Nếu requests thất bại, dùng cURL làm phương án dự phòng)
        # Nếu requests thất bại, dùng cURL làm backup (bypass anti-bot tốt hơn)
        # print(f" Trying curl method for {url[:50]}...")
        content = self.get_content_with_curl(url)
        if content:
            print(f" Curl success!")
            return content
        # If both methods fail, return None
        return None
    
    def parse_article(self, html_content: str, url: str) -> dict:
        """
        Parse article details from HTML content.
        Returns a dict with title, description, content, and URL.
        """
        try:
            # Check if HTML is empty or too short (<500 chars)
            if not html_content or len(html_content) < 500:
                return None

            # Create BeautifulSoup object for easier HTML navigation
            soup = BeautifulSoup(html_content, 'html.parser')

            # EXTRACT TITLE
            title_detail = None

            # List of CSS selectors that may contain the title (depends on website structure)
            title_selectors = [
                "h1.title-detail",
                "h1.title_news_detail",
                "h1[class*='title']",
                "h1",
                ".title-detail",
                ".title_news_detail",
                "title"
            ]

            # Iterate through selectors until a valid title is found
            for selector in title_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    # Skip if title is too short or contains site name
                    if text and len(text) > 10 and 'vnexpress' not in text.lower():
                        title_detail = text
                        break
                if title_detail:
                    break

            # If still no title found, skip article
            if not title_detail:
                title_detail = "NA"


            # EXTRACT DESCRIPTION
            description = ""

            # List of possible selectors for article description
            desc_selectors = [
                "meta[name='twitter:description']",
                "p.description",
                "p.lead",
                "p[class*='description']",
                "p[class*='lead']",
                ".description",
                ".lead",
                "meta[name='description']",
                "meta[property='og:description']"
            ]

            # Try each selector until found
            for selector in desc_selectors:
                elements = soup.select(selector)
                for element in elements:
                    if element.name == 'meta':
                        text = element.get('content', '').strip()
                    else:
                        text = element.get_text().strip()
                    # Accept only if text length is meaningful
                    # (Chỉ chấp nhận nếu độ dài mô tả đủ lớn)
                    if text and len(text) > 20:
                        description = text
                        break
                if description:
                    break


            # EXTRACT MAIN CONTENT
            content_text = ""

            # List of possible content containers
            content_selectors = [
                "article.fck_detail p.Normal",
                "article.fck_detail p",
                ".fck_detail p.Normal",
                ".fck_detail p",
                "article.content_detail p",
                ".content_detail p",
                "div.content_detail p",
                "article p",
                ".Normal",
                "div[class*='content'] p",
                "div[class*='article'] p",
                "main p"
            ]

            # Loop through each pattern to extract paragraphs
            for selector in content_selectors:
                paragraphs = soup.select(selector)
                if paragraphs:
                    temp_content = ""
                    for p in paragraphs:
                        text = p.get_text().strip()
                        # print(text)

                        # Skip irrelevant lines such as “Theo VnExpress”, “Ảnh:”, etc.
                        if ( text and len(text) > 50 and not re.match(r'^[\s\W]*$', text)):
                            temp_content += text + " "

                    # Accept if content length > 200 chars
                    if len(temp_content) > 200:
                        content_text = temp_content.strip()
                        break


            # ===================== IF STILL NO CONTENT FOUND =====================
            if len(content_text) < 200:
                main_content_selectors = [
                    "div[class*='content']",
                    "div[class*='article']",
                    "div[class*='detail']",
                    "main",
                    "article"
                ]

                # Try to extract text from larger containers
                
                for selector in main_content_selectors:
                    containers = soup.select(selector)
                    for container in containers:
                        paragraphs = container.find_all('p')
                        temp_content = ""
                        for p in paragraphs:
                            text = p.get_text().strip()
                            if text and len(text) > 30:
                                temp_content += text + " "
                        if len(temp_content) > len(content_text):
                            content_text = temp_content.strip()
                    if len(content_text) > 200:
                        break


            # ===================== FINAL CHECK AND RETURN =====================
            if len(content_text) < 100:
                # If article body is too short → likely not a valid article
                return None
            
            # Extract author
            author: str = None

            author_selectors = [
                "a[class*='e-magazine__meta']",
                "div[class*='author-name']"
            ]

            for selector in author_selectors:
                elements = soup.select(selector)
                for element in elements:
                    author = element.get_text().strip()
                    if author:
                        break
                if author:
                    break

            # Extract Date & Time

            day: str = ""
            time_set: str =""

            datetime_selectors = [
                "span[class*='date']",
                "div.header-content span",
                "time",
                "p.date",
                "div.date",
            ]

            for selector in datetime_selectors:
                elements = soup.select(selector)
                for element in elements:
                    day_text = element.get_text().split("-")[0].strip()
                    time_text = element.get_text().split("-")[1].strip()
                    if time_text and day_text:
                        day = day_text
                        time_set = time_text
                        break
                if time_set and day:
                    break

            # ====================== Extract Keywords =========================

            keywords_list = []

            # Các selector phổ biến để tìm phần chứa keyword
            keyword_selectors = [
                "meta[name='keywords']",
                "div[class*='keyword']",
                "ul[class*='keyword'] li",
                "span[class*='keyword']",
                "a[class*='keyword']",
            ]

            for selector in keyword_selectors:
                elements = soup.select(selector)
                for element in elements:
                    # Nếu là thẻ <meta>, lấy thuộc tính "content"
                    if element.name == "meta" and "content" in element.attrs:
                        content = element['content'].strip()
                        if content:
                            # tách nếu có nhiều keyword trong content
                            for kw in [k.strip() for k in content.split(",") if k.strip()]:
                                keywords_list.append(kw)
                    else:
                        # Còn lại thì lấy text hiển thị
                        kw = element.get_text().strip()
                        if kw:
                            keywords_list.append(kw)
            # Xóa trùng lặp
            keywords_list = list(set(keywords_list))
                    
            # Return final result as dictionary
            # (Trả kết quả cuối cùng dưới dạng dictionary để dễ xử lý tiếp)
            return {
                "Source": "Dan Tri",
                "url": url,
                "Date": day,
                "Time": time_set,
                "Author": author,
                "Title": title_detail,
                "Description": description if description else title_detail[:200],
                "Contents": content_text,
                "Key_words": keywords_list
            }

        except Exception as e:
            # If parsing fails, return None
            # (Nếu xảy ra lỗi trong quá trình phân tích, trả về None để bỏ qua bài lỗi)
            print("ERROR: ",  e)
            return None

    def get_structure_content(self, url: str) -> dict:
        """
        Get detailed content of a news article from its URL.
        """
        try:
            # Try to get HTML from the URL (automatically chooses between requests and curl)
            raw_content = self.get_content_enhanced(url)

            # If unable to retrieve content (None returned), stop here
            if raw_content is None:
                return None

            # If HTML is fetched, parse and extract article info
            return self.parse_article(raw_content, url)

        except Exception as e:
            # If any unexpected error occurs (network, parsing, syntax, etc.)
            # print("ERROR: ", e)
            return f"Scraping ERROR with {url}"    
        
    def get_news_urls(self, page_link: str) -> list:
        # List to store all collected article links
        links = []  

        # Fetch full HTML content from the topic page (like "Thời sự", "Thế giới", etc.)
        raw_content = self.get_content_enhanced(page_link)

        # If no HTML content is retrieved, return an empty list
        if raw_content is None:
            return links

        # Parse the HTML content using BeautifulSoup for easier tag navigation
        soup = BeautifulSoup(raw_content, 'html.parser')

        # LIST OF POSSIBLE SELECTORS
        # Websites can use different HTML structures for articles.
        # Example: Articles may be inside <article>, <h2>, or <h3> tags.
        link_selectors = [
            "article h2.title-news a",  # Most common form (Dạng phổ biến nhất)
            "article h3.title-news a",  # Some pages use <h3> instead of <h2> (Một số trang dùng h3)
            "h2.title-news a",          # Without <article> wrapper (Không có thẻ <article> bọc ngoài)
            "h3.title-news a",
            "h2 a[href*='.htm']",
            "h3 a[href*='.htm']",
            "h2 a[href*='.html']",      # Any <h2> with an href containing ".html" (Bất kỳ thẻ h2 có .html)
            "h3 a[href*='.html']",
            "article a[href*='.htm']",
            "article a[href*='.html']",
            "a[href*='.htm']", # All <a> inside <article> that link to .html (Mọi link trong <article> có .html)
            "a[href*='.html']"          # Fallback: any <a> with .html (Dự phòng: mọi <a> có .html)
        ]

        # Base URL to complete relative links
        base_url = "https://dantri.com.vn/"

        # LOOP THROUGH SELECTORS
        for selector in link_selectors:
            link_elements = soup.select(selector)
            for element in link_elements:
                # Extract the "href" attribute value
                href = element.get('href')

                if href:
                    # Remove fragment part after "#" if present
                    if '#' in href:
                        href = href.split('#')[0]

                    # If relative path (starts with "/"), join with base_url
                    if href.startswith('/'):
                        href = base_url + href
                    # Skip if link doesn’t start with "http" (invalid or external format)
                    elif not href.startswith('http'):
                        continue

                    # VALIDATION CHECKS
                    # Conditions:
                    # - Must contain ".html" (Phải có .html)
                    # - Must include at least one digit (Có ít nhất 1 chữ số)
                    # - Must contain "vnexpress.net" (Là link nội bộ)
                    # - Must be longer than 50 chars (Dài hơn 50 ký tự)
                    if ('.htm' in href and
                        re.search(r'\d+', href) and
                        'dantri.com.vn' in href and
                        len(href) > 50):
                        links.append(href)

            # Stop if valid links are found (don’t test other selectors)
            if links:
                break

        # POST-PROCESSING
        # Remove duplicate links using set, then convert back to list
        unique_links = list(set(links))

        return unique_links
    
    def get_sub_topic_page(self, sub_topic_url, pages=1) -> list:
        """
        Generate a list of paginated URLs for a given VnExpress sub-topics
        Example:
            sub_topic_url = "https://dantri.com.vn/kinh-doanh/tai-chinh.htm"
            pages = 3
            Output:
            [
                "https://dantri.com.vn/kinh-doanh/tai-chinh.htm",
                "https://dantri.com.vn/kinh-doanh/tai-chinh/trang-2.htm",
                "https://dantri.com.vn/kinh-doanh/tai-chinh/trang-3.htm"
            ]
        Only the SUB topic has the more page, the main page only have 1 page
        """

        # Initialize the list with the base URL (first page)
        urls_list = [sub_topic_url]

        # Loop through page numbers from 2 to the specified number of pages
        base_structure = sub_topic_url[:-4]
        for page in range(2, pages + 1):
            new_url = f"{base_structure}/trang-{page}.htm"
            # Add this generated URL to the list
            urls_list.append(new_url)

        # Return the complete list of URLs
        return urls_list