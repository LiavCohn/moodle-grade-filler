import tkinter as tk
from tkinter import messagebox
import threading
import sqlite3
import time


class MoodleGradeFillerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Moodle Grade Filler")

        self.conn = sqlite3.connect("courses.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.thread_status = {}

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(
            self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)

        self.display_courses()

        add_course_btn = tk.Button(
            root, text="Add Course", command=self.add_course_popup
        )
        add_course_btn.pack(pady=10)

    def add_course(self, course_id, data):
        self.cursor.execute(
            """
            INSERT INTO courses (course_id, name, path) VALUES (?, ?, ?)
        """,
            (course_id, data["name"], data["path"]),
        )
        self.conn.commit()

    def display_courses(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT * FROM courses")
        courses = self.cursor.fetchall()

        for course in courses:
            course_id, name, path = course

            self.cursor.execute(
                "SELECT task_number_in_excel, task_code_in_moodle FROM tasks WHERE course_id = ?",
                (course_id,),
            )
            tasks = self.cursor.fetchall()
            task_numbers = [task[0] for task in tasks]
            task_codes = [task[1] for task in tasks]

            course_frame = tk.LabelFrame(
                self.scrollable_frame, text=f"Course {course_id}"
            )
            course_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

            tk.Label(course_frame, text="Name:").grid(row=0, column=0, sticky=tk.W)
            tk.Label(course_frame, text=name).grid(row=0, column=1, sticky=tk.W)

            tk.Label(course_frame, text="Path:").grid(row=1, column=0, sticky=tk.W)
            tk.Label(course_frame, text=path).grid(row=1, column=1, sticky=tk.W)

            tk.Label(course_frame, text="Task Numbers in Excel:").grid(
                row=2, column=0, sticky=tk.W
            )
            tk.Label(course_frame, text=", ".join(task_numbers)).grid(
                row=2, column=1, sticky=tk.W
            )

            tk.Label(course_frame, text="Task Codes in Moodle:").grid(
                row=3, column=0, sticky=tk.W
            )
            tk.Label(course_frame, text=", ".join(task_codes)).grid(
                row=3, column=1, sticky=tk.W
            )

            edit_btn = tk.Button(
                course_frame,
                text="Edit Course",
                command=lambda id=course_id: self.edit_course_popup(id),
            )
            edit_btn.grid(row=4, column=0, padx=5, pady=5)

            delete_btn = tk.Button(
                course_frame,
                text="Delete Course",
                command=lambda id=course_id: self.delete_course(id),
            )
            delete_btn.grid(row=4, column=1, padx=5, pady=5)
            fill_btn = tk.Button(
                course_frame,
                text="Fill Grades",
                command=lambda id=course_id: self.start_filler_thread(id),
            )
            fill_btn.grid(row=4, column=2, padx=5, pady=5)

            status_label = tk.Label(
                course_frame, text=self.thread_status.get(course_id, "Not Started")
            )
            status_label.grid(row=4, column=3, padx=5, pady=5)
            self.thread_status[course_id] = status_label

    def add_course_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add New Course")

        tk.Label(popup, text="Course ID:").grid(
            row=0, column=0, padx=10, pady=10, sticky=tk.W
        )
        course_id_entry = tk.Entry(popup)
        course_id_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(popup, text="Course Name:").grid(
            row=1, column=0, padx=10, pady=10, sticky=tk.W
        )
        course_name_entry = tk.Entry(popup)
        course_name_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(popup, text="File Path:").grid(
            row=2, column=0, padx=10, pady=10, sticky=tk.W
        )
        file_path_entry = tk.Entry(popup)
        file_path_entry.grid(row=2, column=1, padx=10, pady=10)

        def save_course():
            course_id = course_id_entry.get().strip()
            course_name = course_name_entry.get().strip()
            file_path = file_path_entry.get().strip()

            self.add_course(
                course_id,
                {
                    "name": course_name,
                    "path": file_path,
                    "task_number_in_excel": [],
                    "task_code_in_moodle": [],
                },
            )

            popup.destroy()
            self.display_courses()

        save_btn = tk.Button(popup, text="Save Course", command=save_course)
        save_btn.grid(row=3, columnspan=2, pady=10)

        popup.mainloop()

    def edit_course_popup(self, course_id):
        popup = tk.Toplevel(self.root)
        popup.title(f"Edit Course {course_id}")

        self.cursor.execute("SELECT * FROM courses WHERE course_id = ?", (course_id,))
        course = self.cursor.fetchone()
        name, path = course[1], course[2]

        tk.Label(popup, text="Course ID:").grid(
            row=0, column=0, padx=10, pady=10, sticky=tk.W
        )
        course_id_label = tk.Label(popup, text=course_id)
        course_id_label.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(popup, text="Course Name:").grid(
            row=1, column=0, padx=10, pady=10, sticky=tk.W
        )
        course_name_entry = tk.Entry(popup)
        course_name_entry.insert(tk.END, name)
        course_name_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(popup, text="File Path:").grid(
            row=2, column=0, padx=10, pady=10, sticky=tk.W
        )
        file_path_entry = tk.Entry(popup)
        file_path_entry.insert(tk.END, path)
        file_path_entry.grid(row=2, column=1, padx=10, pady=10)

        self.cursor.execute(
            "SELECT task_number_in_excel, task_code_in_moodle FROM tasks WHERE course_id = ?",
            (course_id,),
        )
        tasks = self.cursor.fetchall()
        task_numbers = [task[0] for task in tasks]
        task_codes = [task[1] for task in tasks]

        tk.Label(popup, text="Task Numbers in Excel:").grid(
            row=3, column=0, padx=10, pady=10, sticky=tk.W
        )
        task_numbers_display = tk.Label(popup, text=", ".join(task_numbers))
        task_numbers_display.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(popup, text="Task Codes in Moodle:").grid(
            row=4, column=0, padx=10, pady=10, sticky=tk.W
        )
        task_codes_display = tk.Label(popup, text=", ".join(task_codes))
        task_codes_display.grid(row=4, column=1, padx=10, pady=10)

        def add_tasks():
            task_popup = tk.Toplevel(popup)
            task_popup.title("Add Task Numbers & Codes")

            tk.Label(task_popup, text="Task Numbers (comma-separated):").grid(
                row=0, column=0, padx=10, pady=10, sticky=tk.W
            )
            task_numbers_entry = tk.Entry(task_popup)
            task_numbers_entry.grid(row=0, column=1, padx=10, pady=10)

            tk.Label(task_popup, text="Task Codes (comma-separated):").grid(
                row=1, column=0, padx=10, pady=10, sticky=tk.W
            )
            task_codes_entry = tk.Entry(task_popup)
            task_codes_entry.grid(row=1, column=1, padx=10, pady=10)

            def save_tasks():
                task_numbers = task_numbers_entry.get().strip()
                task_codes = task_codes_entry.get().strip()
                if task_codes and task_numbers:
                    splitted_task_numbers = [
                        num.strip() for num in task_numbers.split(",")
                    ]
                    splitted_task_codes = [num.strip() for num in task_codes.split(",")]
                    for task_code, task_number in zip(
                        splitted_task_codes, splitted_task_numbers
                    ):
                        self.cursor.execute(
                            """
                            INSERT INTO tasks (course_id, task_number_in_excel, task_code_in_moodle) VALUES (?, ?, ?)
                        """,
                            (course_id, task_number, task_code),
                        )

                    self.conn.commit()
                task_popup.destroy()
                self.edit_course_popup(course_id)

            save_tasks_btn = tk.Button(
                task_popup, text="Save Tasks", command=save_tasks
            )
            save_tasks_btn.grid(row=2, columnspan=2, pady=10)

            task_popup.mainloop()

        def clear_tasks():
            self.cursor.execute("DELETE FROM tasks WHERE course_id = ?", (course_id,))
            self.conn.commit()
            task_numbers_display.config(text="")
            task_codes_display.config(text="")

        add_tasks_btn = tk.Button(
            popup, text="Add Task Numbers & Codes", command=add_tasks
        )
        add_tasks_btn.grid(row=5, columnspan=2, pady=10)

        clear_tasks_btn = tk.Button(
            popup, text="Clear Task Numbers & Codes", command=clear_tasks
        )
        clear_tasks_btn.grid(row=6, columnspan=2, pady=10)

        def save_course():
            new_name = course_name_entry.get().strip()
            new_path = file_path_entry.get().strip()

            self.cursor.execute(
                """
                UPDATE courses SET name = ?, path = ? WHERE course_id = ?
            """,
                (new_name, new_path, course_id),
            )
            self.conn.commit()

            popup.destroy()
            self.display_courses()

        save_btn = tk.Button(popup, text="Save Changes", command=save_course)
        save_btn.grid(row=7, columnspan=2, pady=10)

        popup.mainloop()

    def delete_course(self, course_id):
        confirm = messagebox.askyesno(
            "Delete Confirmation",
            f"Are you sure you want to delete Course {course_id}?",
        )
        if confirm:
            self.cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
            self.cursor.execute("DELETE FROM tasks WHERE course_id = ?", (course_id,))
            self.conn.commit()
            self.display_courses()

    def filler(self, task_nums, task_codes, path):
        threads = []
        for task_num, task_code in zip(task_nums, task_codes):
            t = threading.Thread(
                target=self.temp,
                args=(
                    task_num,
                    task_code,
                    path,
                ),
            )
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            try:
                thread.join()
            except Exception as e:
                print("error: ", e)

        print("All threads are done!")

    def temp(self, task_num, task_code, path):
        time.sleep(1)
        if task_code == "1111":
            raise Exception("Oops!!")
        print(f"Task Num: {task_num}. Task Code: {task_code}. Path: {path}")
        time.sleep(3)

    def fill_grades(self, course_id):
        try:
            self.cursor.execute(
                "SELECT path FROM courses WHERE course_id = ?", (course_id,)
            )
            path = self.cursor.fetchone()[0]

            self.cursor.execute(
                "SELECT task_number_in_excel, task_code_in_moodle FROM tasks WHERE course_id = ?",
                (course_id,),
            )
            tasks = self.cursor.fetchall()

            task_nums = [task[0] for task in tasks]
            task_codes = [task[1] for task in tasks]

            self.filler(task_nums, task_codes, path)
            self.thread_status[course_id].config(text="Completed")
        except Exception as e:
            print(e)
            self.thread_status[course_id].config(text=f"Failed: {str(e)}")

    def start_filler_thread(self, course_id):
        self.thread_status[course_id].config(text="Running")
        threading.Thread(target=self.fill_grades, args=(course_id,)).start()


# Create the main tkinter window
root = tk.Tk()
root.geometry("780x300")
app = MoodleGradeFillerApp(root)
root.mainloop()
