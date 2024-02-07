from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
import os
import sys
import pandas as pd
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from config import username, psw
from consts.consts import classes, COMMENTS_TEXT, LOGIN, NOTIFICATIONS_CB, SAVE, GRADE


s = Service("C:\chromedriver.exe")
driver = webdriver.Chrome(service=s)
#
# Open the login page
driver.get("https://moodle.ruppin.ac.il/login/index.php")
#


def login():
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")

    # Replace 'your_username' and 'your_password' with your actual username and password
    username_field.send_keys(username)
    password_field.send_keys(psw)
    #
    driver.find_element(By.ID, LOGIN).click()
    # time.sleep(1)


login()
to_check = [397]


def search_user(name: str):
    search_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[placeholder="חיפוש משתמש"]')
        )
    )
    name_splitted = name.split(" ")
    id = ""
    if name_splitted[-1].isdigit():
        id = name_splitted[-1]
        print("has id ", str(id))
        name_without_id = " ".join(name_splitted[:2])
        search_input.clear()
        search_input.send_keys(name_without_id)
    else:
        search_input.clear()
        search_input.send_keys(name)
    time.sleep(1)
    # Wait for the suggestions to appear
    suggestions = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "ul[aria-label='Suggestions']")
        )
    )

    try:
        # Find all <li> elements under the <ul> element
        li_elements = WebDriverWait(suggestions, 20).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "li"))
        )

        for suggestion in li_elements:
            try:
                span = WebDriverWait(suggestion, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "span"))
                )
                student_details = span.get_attribute("innerText").split(", ")
                print("student_details", student_details)

                if name in student_details[0]:
                    print("Student found!")
                    # return span
                    span.click()
                    time.sleep(1)

                    try:
                        # Check if the popup appears
                        popup = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, SAVE))
                        )

                        # Popup appeared, click "Save and Continue"
                        save_and_continue_button = WebDriverWait(popup, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, SAVE))
                        )
                        save_and_continue_button.click()
                        return

                    except TimeoutException:
                        print("Popup did not appear. No need to save and continue.")

                    # If no popup, continue with saving
                    try:
                        save_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, SAVE))
                        )

                        save_element = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, SAVE))
                        )

                        save_element.click()
                        return

                    except TimeoutException:
                        print(
                            "Element with data-action='save' not found or not clickable. No need saving."
                        )

            except StaleElementReferenceException:
                # Handle stale element exception by re-finding the suggestion elements
                continue

    except StaleElementReferenceException:
        print(
            "Stale element exception while finding suggestions. Exiting the function."
        )


def extract_details(data: pd.Series):
    """
    extracts the necessary details of a task, such as students, comment on the task and its grade.
    @returns students, grade, comment, has_comment
    """
    students = [name.strip() for name in data["students"].split(",")]
    grade = int(data[ex_str])
    comment = data[ex_str + "_comments"]
    has_comment = pd.notna(comment)
    return students, grade, comment, has_comment


def uncheck_notifications():
    checkbox = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, NOTIFICATIONS_CB))
    )
    # Check if the checkbox is currently checked
    if checkbox.is_selected():
        # If checked, uncheck it by clicking
        checkbox.click()


for task in to_check:
    class_data = classes[task]
    task_num = class_data["task_number_in_excel"][0]
    path = class_data["path"]
    task_to_fill = class_data["task_code_in_moodle"][0]
    ex_str = f"ex{task_num}"
    df = pd.read_excel(os.path.join(path, "grades.xlsx"))

    # Navigate to the grading page
    path = f"https://moodle.ruppin.ac.il/mod/assign/view.php?id={task_to_fill}&action=grader"
    driver.get(path)

    uncheck_notifications()

    # loop to fill each students grade
    for i, data in df.iterrows():
        students, grade, comment, has_comment = extract_details(data)
        print(f"Filling grades for {str(students)}, {str(comment)}")
        time.sleep(1)
        for student in students:
            time.sleep(1)
            search_user(student)
            time.sleep(1)
            grade_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, GRADE))
            )
            grade_input.clear()
            # Fill the input field with the desired value
            grade_input.send_keys(grade)
            print("sent grade")
            time.sleep(1)
            # fill comment if needed
            if has_comment == True:
                textbox_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, COMMENTS_TEXT))
                )

                textbox_element.clear()
                # Fill the textbox with the desired text
                textbox_element.send_keys(comment)
                time.sleep(1)

            save = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "savechanges"))
            )
            save.click()
            time.sleep(1)

    print(f"finished to check {task}")


driver.close()
