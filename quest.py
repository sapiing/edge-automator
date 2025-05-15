from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os

def quest(isPhone=False, progress_callback=None, stop_event=None, profile_path=None):
    """
    Opens Edge browser, navigates to rewards.bing.com, and completes quests.

    Args:
        isPhone (bool): If True, uses mobile user agent and viewport size for iPhone 10
        progress_callback (callable, optional): Function to call with progress updates (0-100).
        stop_event (threading.Event, optional): Event to check for stopping the quest.
        profile_path (str, optional): Path to Edge user profile. If None, uses default profile.
    """
    edge_options = Options()

    if isPhone:
        iphone_user_agent = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        )
        edge_options.add_argument(f"--user-agent={iphone_user_agent}")
        edge_options.add_argument("--window-size=375,812")
    else:
        edge_options.add_argument("--start-maximized")

    driver = None
    try:
        # Add user data directory if profile path is specified
        if profile_path:
            edge_options.add_argument(f"--user-data-dir={os.path.dirname(profile_path)}")
            edge_options.add_argument(f"--profile-directory={os.path.basename(profile_path)}")
            print(f"Using Edge profile: {profile_path}")

        driver = webdriver.Edge(options=edge_options)
        main_window = None

        def navigate_to_rewards():
            driver.get("https://rewards.bing.com/")
            print("Navigated to rewards.bing.com")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
            time.sleep(random.uniform(2, 3))

            # Update progress if callback provided
            if progress_callback:
                progress_callback(10)

        def handle_new_tab():
            try:
                WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
                new_window = [w for w in driver.window_handles if w != main_window][0]
                driver.switch_to.window(new_window)
                time.sleep(random.uniform(3, 5))  # Wait for activity to load
                driver.close()
                driver.switch_to.window(main_window)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                )
                return True
            except Exception:
                return False

        def click_cards_in_container(container, description, progress_start, progress_end):
            cards = container.find_elements(By.TAG_NAME, "mee-card")
            print(f"Found {len(cards)} mee-card elements in {description}")

            # Calculate progress increment per card
            progress_increment = (progress_end - progress_start) / max(1, len(cards))

            for i, card in enumerate(cards):
                # Check if we should stop
                if stop_event and stop_event.is_set():
                    print(f"Quest stopped by user during {description}")
                    return False

                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(card))
                    card.click()
                    print(f"Clicked mee-card #{i + 1} in {description}")
                    time.sleep(random.uniform(2, 4))

                    if not handle_new_tab():
                        # fallback: reload rewards page if no new tab opened
                        driver.get("https://rewards.bing.com/")
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                        )
                    time.sleep(random.uniform(2, 3))

                    # Update progress if callback provided
                    if progress_callback:
                        current_progress = progress_start + (i + 1) * progress_increment
                        progress_callback(min(progress_end, int(current_progress)))

                except Exception as e:
                    print(f"Error clicking mee-card #{i + 1} in {description}: {e}")
                    navigate_to_rewards()

            return True

        # Start main flow
        navigate_to_rewards()
        main_window = driver.current_window_handle

        # Check if we should stop before starting
        if stop_event and stop_event.is_set():
            print("Quest stopped by user before starting")
            return

        # FIRST TASK: Click mee-cards in the main div.m-card-group container
        try:
            main_card_group = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.m-card-group"))
            )
            if not click_cards_in_container(main_card_group, "main card group", 20, 60):
                return  # Stop if requested
        except Exception as e:
            print(f"Failed to find or click cards in main card group: {e}")
            if progress_callback:
                progress_callback(60)  # Skip to next section's progress

        # Check if we should stop before second task
        if stop_event and stop_event.is_set():
            print("Quest stopped by user after first task")
            return

        # SECOND TASK: Click mee-cards inside nested #more-activities section
        try:
            outer_div = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "more-activities"))
            )
            mee_card_group = outer_div.find_element(By.CSS_SELECTOR, "mee-card-group#more-activities")
            nested_card_group = mee_card_group.find_element(By.CSS_SELECTOR, "div.m-card-group")
            if not click_cards_in_container(nested_card_group, "#more-activities nested card group", 60, 95):
                return  # Stop if requested
        except Exception as e:
            print(f"Failed to find or click cards in #more-activities nested group: {e}")
            if progress_callback:
                progress_callback(95)  # Skip to end progress

        print("All tasks completed successfully.")

        # Final progress update
        if progress_callback:
            progress_callback(100)

    except Exception as e:
        print(f"Critical error: {e}")
    finally:
        if driver:
            driver.quit()
        print("Browser closed. Quest completed.")

if __name__ == "__main__":
    import sys
    isPhone = "--phone" in sys.argv
    quest(isPhone=isPhone)
