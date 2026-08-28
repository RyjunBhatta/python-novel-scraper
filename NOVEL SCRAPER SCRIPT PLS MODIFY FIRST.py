import time
import random
import os
from pathlib import Path
from ebooklib import epub
from playwright.sync_api import sync_playwright

def main():
    # Set the save location directly to your system's Downloads folder
    downloads_path = os.path.join(Path.home(), "Downloads")
    output_filename = os.path.join(downloads_path, 'Return_of_the_Disaster_Class_Young_Lord_TEST.epub')

    # 1. Setup the EPUB book structure
    book = epub.EpubBook()
    book.set_title("Return of the Disaster-Class Young Lord")
    book.set_language("en")
    book.add_author("NovelDex Creator")

    total_chapters = 135
    urls = [
        f"https://noveldex.io/series/novel/return-of-the-disaster-class-young-lord/chapter/{i}"
        for i in range(1, total_chapters + 1)
    ]

    chapters = []

    print("Launching visible browser. Testing Chapter 1...")
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
        )
        page = context.new_page()
        
        for i, url in enumerate(urls, start=1):
            print(f"[{i}/{total_chapters}] Accessing chapter url: {url}")
            
            if i > 1:
                sleep_time = random.uniform(4.0, 7.0)
                print(f"⏳ Waiting {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)

            try:
                page.goto(url, timeout=90000, wait_until="domcontentloaded")
                time.sleep(3.0) 

                unwanted_selectors = [
                    "#comments", 
                    ".comments", 
                    ".comment-section", 
                    ".disqus-thread", 
                    ".nav-links",
                    "button", 
                    "script", 
                    "style"
                ]

                for unwanted in unwanted_selectors:
                    page.evaluate(f"""
                        document.querySelectorAll('{unwanted}').forEach(el => el.remove());
                    """)

                target_locator = page.locator("div.overflow-visible").first
                
                if target_locator.count() > 0:
                    body_content = target_locator.inner_html()
                else:
                    print(f"⚠️ Target div.overflow-visible not found for Chapter {i}, falling back to body.")
                    body_content = page.locator("body").inner_html()

                title = f"Chapter {i}"
                chapter = epub.EpubHtml(title=title, file_name=f"chap_{i}.xhtml", lang="en")
                chapter.content = f"<h1>{title}</h1><div class='chapter-text'>{body_content}</div>"
                
                book.add_item(chapter)
                chapters.append(chapter)
                print(f"✅ Successfully grabbed and packed Chapter {i}!")
                
            except Exception as e:
                print(f"❌ Failed processing Chapter {i}: {e}. Skipping to next.")
                continue

        browser.close()

    print("\nCompiling test EPUB file...")
    book.toc = tuple(chapters)
    book.spine = ['nav'] + chapters
    book.add_item(epub.EpubNav())
    book.add_item(epub.EpubNcx())

    epub.write_epub(output_filename, book)
    print(f"🎉 Success! Ebook saved directly to Downloads:\n{output_filename}")

if __name__ == "__main__":
    main()
    # Keeps the CMD window open after execution finishes
    input("\nPress Enter to exit...")