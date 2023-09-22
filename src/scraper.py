import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from typing import List, Optional

from base import BaseClass
from config import config
from utils.utils import get_file_path

class Scraper(BaseClass):
    def __init__(self, dry: bool = False, verbose: bool = False) -> None:
        super().__init__(dry, verbose)
        options = Options()
        options.headless = True  # Enable headless mode
        self.driver = webdriver.Firefox(options=options)  
        self.base_url = config.base_url

    def __str__(self):
        return "Scraper(base_url={}, dry={}, verbose={})".format(
            self.base_url, self.dry, self.verbose
        )

    def stop(self):
        self.log("Stopping...")
        self.driver.close()
        self.driver.quit()
        self.log("Stopped!")

    async def run(self):
        topics = {}

        try:
            self.log("Scraper running...")
            self.driver.get("https://neetcode.io/practice")
            assert "Practice" in self.driver.title

            # click tab /html/body/app-root/app-pattern-table-list/div/div[2]/div[2]/ul/li[4]/a
            self.click(
                By.XPATH,
                "/html/body/app-root/app-pattern-table-list/div/div[2]/div[2]/ul/li[4]/a",
            )

            # get and go through each item and append to topics
            # app-pattern-table.ng-star-inserted
            topicElements = self.get_all(
                By.CSS_SELECTOR,
                "app-pattern-table",
            )

            self.log("Found {} topics".format(len(topicElements)))

            for topicElement in topicElements:
                # first p element is the topic name
                topic = self.get_text(By.CSS_SELECTOR, "p:nth-child(1)", topicElement)
                # topic_data = {}
                # topic_data[topic] = {}
                # click the topic parent button
                self.log("Getting problems for topic: {}...".format(topic))
                button = self.get(By.CSS_SELECTOR, "button", topicElement)
                button.click()
                sleep(3)
                # find element of class accordion-panel with stle visibility: visible
                # body > app-root > app-pattern-table-list > div > div.flex-container-col.content.ng-star-inserted > app-pattern-table:nth-child(4) > app-accordion > div > div
                # Wait for the tableDiv to become visible
                tableDiv = WebDriverWait(topicElement, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "app-table"))
                )

                # get all problems in table. problem title is <a> as 3rd td in tr, difficulty is 4th td in tr
                # my-table-container table tbody tr
                problemElements = self.get_all(
                    By.CSS_SELECTOR, "div > table > tbody tr", tableDiv
                )
                problems = [
                    {
                        "problem": self.get_text(
                            By.CSS_SELECTOR, "td:nth-child(3) a", problemElement
                        ),
                        "link": self.get(
                            By.CSS_SELECTOR, "td:nth-child(3) a", problemElement
                        ).get_attribute("href"),
                        "difficulty": self.get_text(
                            By.CSS_SELECTOR, "td:nth-child(4)", problemElement
                        ),
                    }
                    for problemElement in problemElements
                    if all(
                        [
                            self.get_text(
                                By.CSS_SELECTOR, "td:nth-child(3) a", problemElement
                            ),
                            self.get_text(
                                By.CSS_SELECTOR, "td:nth-child(4)", problemElement
                            ),
                            self.get(
                                By.CSS_SELECTOR, "td:nth-child(3) a", problemElement
                            ).get_attribute("href"),
                        ]
                    )
                ]
                topics[topic] = problems
                self.log("Got {} problems for topic: {}".format(len(problems), topic))
                # close the topic
                button.click()

            self.log("Done! Found {} topics".format(len(topics)))

        except Exception as e:
            self.log("Error: {}".format(e))
        finally:
            saved = self.save_to_json_file(topics)
            if saved:
                self.log("Saved to json file!")
            self.stop()

    def click(self, by, path: str, element: Optional[WebElement] = None) -> None:
        if element:
            element.find_element(by, path).click()
            return
        self.driver.find_element(by, path).click()

    def get(
        self, by, path: str, element: Optional[WebElement] = None
    ) -> Optional[WebElement]:
        if element:
            return element.find_element(by, path)
        return self.driver.find_element(by, path)

    def get_all(
        self, by, path: str, element: Optional[WebElement] = None
    ) -> Optional[List[WebElement]]:
        if element:
            return element.find_elements(by, path)
        return self.driver.find_elements(by, path)

    def get_text(
        self, by, path: str, element: Optional[WebElement] = None
    ) -> Optional[str]:
        if element:
            return element.find_element(by, path).text
        return self.driver.find_element(by, path).text

    def save_to_json_file(self, data) -> bool:
        try:
            path_to_file = get_file_path(config.problems_file)
            with open(path_to_file, "w") as json_file:
                json.dump(data, json_file, indent=4)
            return True
        except Exception as e:
            self.log("Error saving to json file: {}".format(e))
            return False
