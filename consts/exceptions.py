from datetime import datetime


class FillerException(Exception):
    def __init__(self, task_code, task_num, error, course_name):
        self.task_code = task_code
        self.task_num = task_num
        self.error = error
        self.course_name = course_name
        self.message = f"[{course_name}]:Task Number: {task_num} with code {task_code} Failed!. Error: {error}. {datetime.now()}"
        super().__init__(self.message)

    def __repr__(self) -> str:
        return self.message
