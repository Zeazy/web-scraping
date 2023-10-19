from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pathlib import Path
import time
import random


def setup_browser():
    """Initialize and return a browser instance."""
    browser = webdriver.Chrome()
    return browser


def get_blog_content(browser):
    """Extract the content of the blog post."""
    try:
        p_elements = browser.find_elements(
            By.CSS_SELECTOR, "#entry #mainentrydiv .col p"
        )
        content = " ".join([p.text for p in p_elements])
        return content
    except Exception as e:
        print(
            f"Error extracting content: {e}. Might be a change in website structure or the element isn't present."
        )
        return None


def get_next_entry_links(browser):
    """Extract links to other blog posts."""

    # Waiting for the links within 'entries-list' to appear, with a timeout of 10 seconds
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#entries-list a.entry[href*="read"]')
        )
    )

    links = browser.find_elements(
        By.CSS_SELECTOR, '#entries-list a.entry[href*="read"]'
    )
    return [link.get_attribute("href") for link in links]


def save_posts(title, posts):
    # Create a new directory named title.lower() if it doesn't exist already
    dir_path = Path(__file__).parent / "data" / title.lower().strip().replace(" ", "_")
    dir_path.mkdir(parents=True, exist_ok=True)

    for i, (date, post) in enumerate(posts, start=1):
        # Save the post in the directory as date.txt
        with open(dir_path / f"{date}.txt", "w") as f:
            f.write(post)


def toggle_list_entry(browser):
    """
    Toggles entry list for the start page so we can see all previous entries.
    """
    try:
        # Wait until the button is present
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.ID, "entrylist_btn"))
        )

        # Find the button and click it
        button = browser.find_element(By.ID, "entrylist_btn")
        button.click()
    except Exception as e:
        print(f"Error toggling entry list: {e}. The button might not be present.")


def click_consent(browser):
    """
    Clicks the consent button on the webpage.
    """
    try:
        # Wait until the button is present
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".fc-button.fc-cta-consent.fc-primary-button")
            )
        )

        # Find the button and click it
        button = browser.find_element(
            By.CSS_SELECTOR, ".fc-button.fc-cta-consent.fc-primary-button"
        )
        button.click()
    except Exception as e:
        print(f"Error clicking consent button: {e}. The button might not be present.")


def get_title(browser):
    """
    <h5 class="heading text-center">Dailylog2023</h5>
    Gets this h5 tag
    """
    try:
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h5.heading.text-center"))
        )
        title = browser.find_element(By.CSS_SELECTOR, "h5.heading.text-center").text
        print(title)
        return title
    except Exception as e:
        print(f"Error getting title: {e}. The title might not be present.")


def get_date(browser):
    """
    <div id="mainentrydiv" class="row">
    <div class="col">
    <div style="text-align:right;">2023-10-19 07:12:43 (UTC)</div>
    Gets this div tag
    """
    try:
        # Wait until the div is present
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainentrydiv .col div"))
        )

        # Find the div and extract its text
        date_div = browser.find_element(By.CSS_SELECTOR, "#mainentrydiv .col div")
        date_text = date_div.text
        return date_text
    except Exception as e:
        print(f"Error getting date: {e}. The date might not be present.")


def extract(browser):
    post_date = get_date(browser)
    post_content = get_blog_content(browser)
    return post_date, post_content


def random_sleep(end, start=0.05):
    time.sleep(random.uniform(start, end))


def main(
    start_url: str = "https://www.my-diary.org/read/e/546661233/unknown%3A-today%E2%80%99s-workout%E2%80%A6#blue",
    init_sleep_range=2.21,
    program_sleep_range=0.195,
):
    browser = setup_browser()
    browser.get(start_url)
    random_sleep(init_sleep_range)
    click_consent(browser)
    title = get_title(browser)
    toggle_list_entry(browser)

    visited_urls = set()
    visited_urls.add(start_url)
    posts = []
    posts.append(extract(browser))

    other_entries = get_next_entry_links(browser)

    for entry in other_entries:
        visited_urls.add(entry)
        browser.get(entry)
        posts.append(extract(browser))
        random_sleep(program_sleep_range)

    browser.quit()

    # Process the `posts` list for further usage
    save_posts(title, posts)


if __name__ == "__main__":
    main()
