from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidElementStateException
from selenium.webdriver.chrome.service import Service
import os
import sys
import pandas as pd
import time
from urllib.parse import urlparse, parse_qs


sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from config import username, psw
from consts.consts import CLASSES, COMMENTS_TEXT, LOGIN, NOTIFICATIONS_CB, SAVE, GRADE


s = Service("C:\chromedriver.exe")
driver = webdriver.Chrome(service=s)
#
# Open the login page
driver.get("https://moodle.ruppin.ac.il/login/index.php")
#


def login():
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    username_field.clear()
    password_field.clear()
    username_field.send_keys(username)
    password_field.send_keys(psw)

    driver.find_element(By.ID, LOGIN).click()


login()
to_check = [1487]


def extract_details(data: pd.Series, ex_str: str):
    """
    extracts the necessary details of a task, such as students, comment on the task and its grade.
    @returns students, grade, comment, has_comment
    """
    students = [name.strip() for name in data["students"].split(",")]
    has_grade = not pd.isna(data[ex_str])
    if has_grade == True:
        grade = int(data[ex_str])
    else:
        grade = None
    comment = data[ex_str + "_comments"]
    has_comment = pd.notna(comment)
    if has_comment == False:
        comment = None
    return students, grade, comment


def check_all_students_selected():
    print("in check_all_students_selected")
    max_retry = 3  # Maximum retry attempts
    for _ in range(max_retry):
        try:
            # Wait for the elements to be present
            wait = WebDriverWait(driver, 20)  # Increased timeout
            elements = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li > a"))
            )

            # Filter elements with inner HTML as 'X'
            target_elements = [
                element
                for element in elements
                if element.get_attribute("innerText") == "הכל"
            ]

            # Click on each filtered element
            for element in target_elements:
                # Check if the element is interactable before clicking
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    print("Clicked!")
                else:
                    print("Element not interactable")
            break  # Break the loop if successful
        except (StaleElementReferenceException, InvalidElementStateException):
            continue  # Retry if exceptions occur


def uncheck_notifications():
    print("in uncheck_notifications")
    # Find the element by name with a wait
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "sendstudentnotifications"))
    )
    # Set its value
    element.send_keys(0)


def set_quick_grading():
    print("in set_quick_grading")
    checkbox = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "quickgrading"))
    )
    # Check if the checkbox is currently checked
    if not checkbox.is_selected():
        # If checked, uncheck it by clicking
        checkbox.click()


def fill_grade(student_name, grade, comment=None, user_id=None):
    xpath = f'//tr/td[3]/a[text()="{student_name}"]'
    # print(xpath)
    a_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    href = a_element.get_attribute("href")

    # Parse the URL and extract the 'id' parameter
    parsed_url = urlparse(href)
    id_value = parse_qs(parsed_url.query).get("id", [None])[0]

    # Fill in the grade
    grade_xpath = f'//td/input[@id="quickgrade_{id_value}"]'
    grade_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, grade_xpath))
    )
    # Check if the input field is empty
    if grade_input.get_attribute("value") == "":
        input_value = grade
        grade_input.send_keys(input_value)

    else:
        return

    # fill comment if needed
    if comment is not None:
        textarea_id = f"quickgrade_comments_{id_value}"
        textarea_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, textarea_id))
        )
        # Set the desired text
        textarea_value = comment
        textarea_element.clear()
        textarea_element.send_keys(textarea_value)


# iterate over class id
for task in to_check:
    class_data = CLASSES[task]
    task_num = class_data["task_number_in_excel"]
    path = class_data["path"]
    task_to_fill = class_data["task_code_in_moodle"]
    for task_num, task_moodle_id in zip(task_num, task_to_fill):
        ex_str = f"ex{task_num}"
        df = pd.read_excel(os.path.join(path, "grades.xlsx"))
        # Navigate to the grading page
        path = f"https://moodle.ruppin.ac.il/mod/assign/view.php?id={task_moodle_id}&action=grading"
        driver.get(path)
        # check_all_students_selected()
        # print("check_all_students_selected Done")
        uncheck_notifications()
        # print("set_element_value_by_name Done")
        # set_quick_grading()
        # print("set_quick_grading Done")
        for i, data in df.iterrows():
            students, grade, comment, has_comment, has_grade = extract_details(
                data, ex_str
            )
            if has_grade == False:
                continue
            print(f"Filling grades for {str(students)}, {str(comment)}")
            time.sleep(1)

            for student in students:
                fill_grade(student, grade, comment)


driver.close()
