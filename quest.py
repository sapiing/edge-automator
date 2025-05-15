from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def quest(isPhone=False):
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
        driver = webdriver.Edge(options=edge_options)
        main_window = None

        def navigate_to_rewards():
            driver.get("https://rewards.bing.com/")
            print("Navigated to rewards.bing.com")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
            time.sleep(random.uniform(2, 3))

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

        def click_cards_in_container(container, description):
            cards = container.find_elements(By.TAG_NAME, "mee-card")
            print(f"Found {len(cards)} mee-card elements in {description}")
            for i, card in enumerate(cards):
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
                except Exception as e:
                    print(f"Error clicking mee-card #{i + 1} in {description}: {e}")
                    navigate_to_rewards()

        # Start main flow
        navigate_to_rewards()
        main_window = driver.current_window_handle

        # FIRST TASK: Click mee-cards in the main div.m-card-group container
        try:
            main_card_group = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.m-card-group"))
            )
            click_cards_in_container(main_card_group, "main card group")
        except Exception as e:
            print(f"Failed to find or click cards in main card group: {e}")

        # SECOND TASK: Click mee-cards inside nested #more-activities section
        try:
            outer_div = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "more-activities"))
            )
            mee_card_group = outer_div.find_element(By.CSS_SELECTOR, "mee-card-group#more-activities")
            nested_card_group = mee_card_group.find_element(By.CSS_SELECTOR, "div.m-card-group")
            click_cards_in_container(nested_card_group, "#more-activities nested card group")
        except Exception as e:
            print(f"Failed to find or click cards in #more-activities nested group: {e}")

        print("All tasks completed successfully.")

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
