from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

import random
import time
import os
from datetime import datetime

def search(isPhone=False, num_searches_input=None, progress_callback=None, stop_event=None):
    """
    Opens Edge browser, navigates to Bing.com, and performs searches with a list of search terms.
    Implements human-like behavior by scrolling 3 times with delays between scrolls before moving to the next search term.
    Allows user to specify the number of searches to perform and randomizes search terms.

    Args:
        isPhone (bool): If True, uses mobile user agent and viewport size for iPhone 10
        num_searches_input (int, optional): Number of searches to perform. If None, will prompt user.
        progress_callback (callable, optional): Function to call with progress updates (0-100).
        stop_event (threading.Event, optional): Event to check for stopping the search.
    """
    # Setup Edge options
    edge_options = Options()

    if isPhone:
        # iPhone 10 user agent
        iphone_user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        edge_options.add_argument(f"--user-agent={iphone_user_agent}")
        # Set viewport size to match iPhone 10
        edge_options.add_argument("--window-size=375,812")  # Scaled down for browser
    else:
        edge_options.add_argument("--start-maximized")

    # List of search terms
    search_terms = [
        # Technology (10)
        "latest technology news 2023",
        "best new gadgets 2023",
        "AI advancements this year",
        "cybersecurity tips for beginners",
        "how to build a PC",
        "smart home device reviews",
        "upcoming smartphone releases",
        "best laptops for programming",
        "cloud computing trends",
        "blockchain technology explained",

        # Food/Cooking (10)
        "best recipes for dinner tonight",
        "quick healthy meals under 30 minutes",
        "vegetarian meal prep ideas",
        "baking tips for beginners",
        "international cuisine recipes",
        "keto diet meal plans",
        "instant pot recipes 2023",
        "gluten-free dessert ideas",
        "meal prep for weight loss",
        "food presentation techniques",

        # Learning/Education (10)
        "how to learn programming fast",
        "best online courses 2023",
        "language learning techniques",
        "mathematics for beginners",
        "science experiments for kids",
        "history documentaries to watch",
        "photography tips for beginners",
        "music theory basics",
        "public speaking skills",
        "critical thinking exercises",

        # Travel (10)
        "top travel destinations 2023",
        "budget travel tips Europe",
        "best beaches in the world",
        "solo travel safety tips",
        "eco-friendly travel options",
        "hidden gem vacation spots",
        "road trip packing list",
        "cultural etiquette guide",
        "best travel credit cards",
        "how to travel with pets",

        # Fitness/Health (10)
        "fitness tips for beginners at home",
        "yoga routines for flexibility",
        "weight training fundamentals",
        "nutrition for muscle building",
        "mental health self-care tips",
        "home workout no equipment",
        "running tips for beginners",
        "sleep improvement techniques",
        "stress management exercises",
        "posture correction exercises",

        # Books/Literature (10)
        "best book recommendations 2023",
        "classic novels everyone should read",
        "self-improvement books 2023",
        "how to read more books",
        "sci-fi book series to start",
        "biographies of famous people",
        "book club discussion ideas",
        "speed reading techniques",
        "best audiobook platforms",
        "writing your first novel",

        # Lifestyle (10)
        "sustainable living ideas for homes",
        "minimalism for beginners",
        "zero waste lifestyle tips",
        "ethical fashion brands",
        "mindfulness meditation guide",
        "digital detox methods",
        "tiny house living pros and cons",
        "homemade natural cleaning products",
        "capsule wardrobe essentials",
        "financial independence tips",

        # Productivity (10)
        "best productivity tools 2023",
        "time management techniques",
        "how to stop procrastinating",
        "notetaking apps comparison",
        "morning routine for success",
        "email management strategies",
        "focus techniques for studying",
        "remote work best practices",
        "goal setting frameworks",
        "decision making strategies",

        # Hobbies (10)
        "gardening tips for spring 2023",
        "indoor plant care guide",
        "beginner painting techniques",
        "woodworking projects for starters",
        "knitting patterns for beginners",
        "home brewing beer guide",
        "astronomy for amateurs",
        "bird watching essentials",
        "chess strategies for beginners",
        "collecting rare coins guide"
    ]

    # Get number of searches to perform
    if num_searches_input is not None:
        num_searches = min(max(1, num_searches_input), len(search_terms))
        print(f"Performing {num_searches} searches")
    else:
        # Ask user for number of searches to perform
        while True:
            try:
                num_searches = int(input(f"How many searches would you like to perform? (1-{len(search_terms)}): "))
                if 1 <= num_searches <= len(search_terms):
                    break
                print(f"Please enter a number between 1 and {len(search_terms)}")
            except ValueError:
                print("Invalid input. Please enter a number.")

    # Randomize search terms without repeating (unless necessary)
    available_terms = search_terms.copy()
    random.shuffle(available_terms)

    # If requested searches exceed available terms, allow duplicates
    selected_terms = []
    for i in range(num_searches):
        if not available_terms:  # If we've used all terms, reset the list
            available_terms = [term for term in search_terms if term not in selected_terms[-5:]]  # Avoid recent duplicates
            if not available_terms:  # If still empty, use all terms
                available_terms = search_terms.copy()
            random.shuffle(available_terms)

        selected_terms.append(available_terms.pop(0))

    driver = None
    try:
        # Initialize the driver
        driver = webdriver.Edge(options=edge_options)

        # Navigate to Bing.com
        driver.get("https://www.bing.com")
        print("Navigated to Bing.com")

        # Wait for page to load
        time.sleep(random.uniform(2.0, 3.0))

        # Perform searches with human-like behavior
        for i, term in enumerate(selected_terms):
            # Check if we should stop
            if stop_event and stop_event.is_set():
                print("Search stopped by user")
                break

            # Update progress if callback provided
            if progress_callback:
                progress = int((i / num_searches) * 100)
                progress_callback(progress)

            print(f"\nSearch {i+1}/{num_searches}: {term}")

            # Find the search box
            try:
                search_box = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "sb_form_q"))
                )

                # Clear the search box
                search_box.clear()

                # Type the search term with random delays between keystrokes to mimic human typing
                for char in term:
                    search_box.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.2))  # Random delay between keystrokes

                # Submit the search
                search_box.send_keys(Keys.RETURN)
                print(f"Submitted search: {term}")

                # Wait for search results to load
                time.sleep(random.uniform(2.0, 3.0))

                # Scroll down 3 times with delays in between to mimic human behavior
                for scroll in range(3):
                    # Scroll down
                    if isPhone:
                        # For mobile, use smaller scroll steps
                        driver.execute_script("window.scrollBy(0, 300);")
                    else:
                        driver.execute_script("window.scrollBy(0, 500);")

                    print(f"Scroll {scroll+1}/3")

                    # Random delay between scrolls (1-3 seconds)
                    time.sleep(random.uniform(1.0, 3.0))

                # Additional delay before moving to the next search term
                time.sleep(random.uniform(2.0, 4.0))

                # Navigate back to Bing.com for the next search
                driver.get("https://www.bing.com")
                time.sleep(random.uniform(1.5, 2.5))

            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error finding search box: {e}")
                # Try to navigate back to Bing.com and continue
                driver.get("https://www.bing.com")
                time.sleep(random.uniform(2.0, 3.0))

        print("\nAll searches completed successfully")

        # Final progress update
        if progress_callback:
            progress_callback(100)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the browser when done
        if driver:
            driver.quit()
        print("Browser closed. Search completed.")

if __name__ == "__main__":
    # Allow command-line execution with optional phone mode
    import sys
    isPhone = "--phone" in sys.argv
    search(isPhone=isPhone)
