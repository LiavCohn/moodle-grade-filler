from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidElementStateException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import os
import sys
import pandas as pd
import time
from urllib.parse import urlparse, parse_qs

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from config import username, psw
from consts.consts import CLASSES, LOGIN, NOTIFICATIONS_CB, SAVE
from consts.exceptions import FillerException

# s = Service("C:\chromedriver.exe")
# driver = webdriver.Chrome(service=s)

# driver.maximize_window()

# driver.implicitly_wait(10)  # Implicit wait


def login(driver):
    driver.get("https://moodle.ruppin.ac.il/login/index.php")
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    username_field.clear()
    password_field.clear()
    username_field.send_keys(username)
    password_field.send_keys(psw)
    driver.find_element(By.ID, LOGIN).click()


def extract_details(data: pd.Series, ex_str: str):
    students = [name.strip() for name in data["students"].split(",")]
    has_grade = not pd.isna(data[ex_str])
    grade = int(data[ex_str]) if has_grade else None
    comment_str = f"{ex_str}_comments"
    has_comment = pd.notna(data[comment_str])
    comment = data.get(comment_str) if has_comment else None
    return students, grade, comment


def check_all_students_selected(driver):
    max_retry = 3
    for _ in range(max_retry):
        try:
            wait = WebDriverWait(driver, 20)
            elements = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li > a"))
            )
            target_elements = [
                element
                for element in elements
                if element.get_attribute("innerText") == "הכל"
            ]
            for element in target_elements:
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    print("Clicked!")
            break
        except (StaleElementReferenceException, InvalidElementStateException):
            continue


def uncheck_notifications(driver):
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, NOTIFICATIONS_CB))
    )
    select = Select(select_element)
    select.select_by_value("0")


def set_quick_grading(driver):
    checkbox = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "quickgrading"))
    )
    if not checkbox.is_selected():
        checkbox.click()


def get_id_by_student_name(student_name: str, driver):
    xpath = f'//tr/td[3]/a[text()="{student_name}"]'
    try:
        a_element = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
    except TimeoutException:
        print(f"TimeoutException: Failed to find element for {student_name}.")
        return

    href = a_element.get_attribute("href")
    parsed_url = urlparse(href)
    id_value = parse_qs(parsed_url.query).get("id", [None])[0]
    return id_value


def fill_grade(student_name, grade, driver, comment=None):
    student_moodle_id = get_id_by_student_name(student_name)

    print(f"Student Id: {str(student_moodle_id)}. Student Name: {student_name}.")

    grade_xpath = f'//td/input[@id="quickgrade_{student_moodle_id}"]'
    try:
        grade_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, grade_xpath))
        )
    except TimeoutException:
        print(f"TimeoutException: Failed to find grade input for {student_name}.")
        return

    if grade_input.get_attribute("value") == "":
        grade_input.clear()
        grade_input.send_keys(grade)
    if comment is not None:
        textarea_id = f"quickgrade_comments_{student_moodle_id}"
        textarea_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, textarea_id))
        )
        textarea_element.send_keys(comment)


def save_changes(driver):
    driver.execute_script("document.body.style.zoom='0.0'")

    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, SAVE))
        )

        # Scroll the element into view using JavaScript
        driver.execute_script("arguments[0].scrollIntoView();", element)

        # Wait until the element is clickable
        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.NAME, SAVE))
        )

        # Click the element
        element.click()
    except TimeoutException:
        print(f"TimeoutException: Failed to click on save grades button.")


def wait_until_url_changes(driver, current_url, timeout=60):
    WebDriverWait(driver, timeout).until(EC.url_changes(current_url))


def fill_grades():
    try:
        for task in to_check:
            class_data = CLASSES[task]
            task_num = class_data["task_number_in_excel"]
            path = class_data["path"]
            task_to_fill = class_data["task_code_in_moodle"]
            for task_num, task_moodle_id in zip(task_num, task_to_fill):
                ex_str = f"ex{task_num}"
                df = pd.read_excel(os.path.join(path, "grades.xlsx"))
                grading_page = f"https://moodle.ruppin.ac.il/mod/assign/view.php?id={task_moodle_id}&action=grading"
                driver.get(grading_page)
                uncheck_notifications()
                driver.execute_script("document.body.style.zoom='0.5'")

                for _, data in df.iterrows():
                    students, grade, comment = extract_details(data, ex_str)
                    if grade is None:
                        continue
                    print(f"Filling grades for {students}, {comment}")
                    time.sleep(1)
                    for student in students:
                        fill_grade(student, grade, comment)
                        time.sleep(2)
                    print()
                save_changes()
                wait_until_url_changes(driver, driver.current_url, timeout=120)

    finally:
        print("Done!!!")
        driver.quit()


import time


def grade_filler(task_nums, task_codes, path, course_name):
    print("in grade_filler")
    successful_tasks = []

    for task_num, task_code in zip(task_nums, task_codes):
        try:
            s = Service("C:\\chromedriver.exe")
            driver = webdriver.Chrome(service=s)
            driver.maximize_window()
            driver.implicitly_wait(10)  # Implicit wait
            login(driver)
            ex_str = f"ex{task_num}"
            df = pd.read_excel(os.path.join(path, "grades.xlsx"))
            print(task_num, task_code)
            grading_page = f"https://moodle.ruppin.ac.il/mod/assign/view.php?id={task_code}&action=grading"
            driver.get(grading_page)
            time.sleep(5)
            if task_num == "2":
                raise FillerException(
                    task_code=task_code,
                    task_num=task_num,
                    error="Oops!!",
                    course_name=course_name,
                )
            # Example grading process
            # uncheck_notifications()
            # driver.execute_script("document.body.style.zoom='0.5'")
            # for _, data in df.iterrows():
            #     students, grade, comment = extract_details(data, ex_str)
            #     if grade is None:
            #         continue
            #     print(f"Filling grades for {students}, {comment}")
            #     time.sleep(1)
            #     for student in students:
            #         fill_grade(student, grade, comment)
            #         time.sleep(2)
            #     print()
            # save_changes()
            # wait_until_url_changes(driver, driver.current_url, timeout=120)
            driver.close()

            successful_tasks.append((task_num, task_code))  # Log successful tasks

        except FillerException as e:
            print("Filler has failed!", e.task_code, e.course_name)
            with open("error_log.txt", "a") as log_file:
                log_file.write(
                    f"[{course_name}]: Task failed: {e.task_code}, Course: {e.course_name}\n"
                )
        except Exception as e:
            print(f"Unexpected error for task {task_num}: {e}")
            with open("error_log.txt", "a") as log_file:
                log_file.write(
                    f"[{course_name}]: Unexpected error for task {task_num}: {e}\n"
                )

    print(f"[{course_name}] All tasks are done!")
    return successful_tasks


# if __name__ == "__main__":
#     login()
#     to_check = [1570]
#     fill_grades()
