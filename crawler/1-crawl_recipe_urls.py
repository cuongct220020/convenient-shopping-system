import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time

BASE_URL = "https://www.dienmayxanh.com"
file_out = './crawler/data/recipe_urls_2.csv'
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
}

# --- Session có retry tự động ---
session = requests.Session()
retry_strategy = Retry(
    total=5,  # thử lại tối đa 5 lần
    backoff_factor=1,  # chờ 1s, 2s, 4s,...
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

def get_categories():
    """Lấy danh sách categories (ổn định, có retry và timeout)"""
    print("Đang tải danh mục...")
    try:
        response = session.get(f"{BASE_URL}/vao-bep/", headers=HEADERS, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Lỗi khi tải danh mục: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")

    categories = []
    menu_div = soup.find("div", class_="menu-cooking topmenu")
    if menu_div:
        ul = menu_div.find("ul")
        if ul:
            for li in ul.find_all("li", recursive=False):
                link = li.find("a")
                if link and link.get("href"):
                    href = link["href"]
                    if href.startswith("/vao-bep/") and href != "/vao-bep/":
                        categories.append({
                            "name": link.text.strip(),
                            "url": BASE_URL + href
                        })
    print(f"✅ Tìm thấy {len(categories)} danh mục.")
    return categories

def get_all_articles(category_url, max_articles_per_category=None):
    """Lấy tất cả URLs từ 1 category (click nút Xem thêm)"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--log-level=3")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(category_url)

        # Click "Xem thêm" đến khi hết hoặc đạt giới hạn
        while True:
            try:
                btn = driver.find_element(By.CLASS_NAME, "seemore-cook")
                driver.execute_script("arguments[0].scrollIntoView();", btn)
                time.sleep(0.5)
                btn.click()
                time.sleep(1.2)
                
                # Nếu đã đủ số lượng, dừng sớm
                if max_articles_per_category is not None:
                    soup_tmp = BeautifulSoup(driver.page_source, "html.parser")
                    current_count = len(soup_tmp.find_all("li"))
                    if current_count >= max_articles_per_category:
                        break

            except Exception:
                break

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        articles = []
        article_list = soup.find("ul", class_="cate-cook")
        if article_list:
            for li in article_list.find_all("li"):
                link = li.find("a")
                if link and link.get("href"):
                    articles.append(BASE_URL + link["href"])

        # Giới hạn danh sách cuối cùng
        if max_articles_per_category is not None:
            articles = articles[:max_articles_per_category]

        return articles

    except Exception as e:
        print(f"  ⚠️ Lỗi khi lấy bài viết từ {category_url}: {e}")
        return []


def main():
    print("🚀 Bắt đầu crawl URLs...")
    categories = get_categories()
    if not categories:
        print("❌ Không tìm thấy category nào, dừng chương trình.")
        return

    categories = categories[6:]  # bỏ 6 cái đầu nếu cần
    all_data = []

    for i, category in enumerate(categories, 1):
        print(f"\n[{i}/{len(categories)}] {category['name']}")
        articles = get_all_articles(category["url"], max_articles_per_category=50)


        for url in articles:
            all_data.append({
                "category": category["name"],
                "url": url
            })

        print(f"  ✅ {len(articles)} bài viết được thu thập.")
        # Lưu tạm mỗi vòng để tránh mất dữ liệu
        pd.DataFrame(all_data).to_csv(file_out, index=False, encoding="utf-8-sig")

        # Nghỉ giữa các category để tránh bị chặn
        time.sleep(2)

    print(f"\n🎉 Hoàn thành! Đã lưu {len(all_data)} URLs vào recipe_urls.csv")

if __name__ == "__main__":
    main()
