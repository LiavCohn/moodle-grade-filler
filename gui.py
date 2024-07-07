import tkinter as tk
from tkinter import messagebox, simpledialog


class MoodleGradeFillerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Moodle Grade Filler")

        self.classes = {}  # Dictionary to store course data

        # Create main frame with scrollbar
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

        # Example course initialization
        self.add_course(
            "1517",
            {
                "name": "C",
                "path": "C:\\Users\\liavc\\OneDrive\\מסמכים\\בדיקת מטלות\\סמסטר ב\\C ערב",
                "task_number_in_excel": ["9"],
                "task_code_in_moodle": ["138912"],
            },
        )

        # Example: Display course data
        self.display_courses()

        # Button to add new course
        add_course_btn = tk.Button(
            root, text="Add Course", command=self.add_course_popup
        )
        add_course_btn.pack(pady=10)

    def add_course(self, course_id, data):
        self.classes[course_id] = data

    def display_courses(self):
        # Clear previous courses from scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Display all courses
        for course_id, course_data in self.classes.items():
            course_frame = tk.LabelFrame(
                self.scrollable_frame, text=f"Course {course_id}"
            )
            course_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

            tk.Label(course_frame, text="Name:").grid(row=0, column=0, sticky=tk.W)
            tk.Label(course_frame, text=course_data["name"]).grid(
                row=0, column=1, sticky=tk.W
            )

            tk.Label(course_frame, text="Path:").grid(row=1, column=0, sticky=tk.W)
            tk.Label(course_frame, text=course_data["path"]).grid(
                row=1, column=1, sticky=tk.W
            )

            tk.Label(course_frame, text="Task Numbers in Excel:").grid(
                row=2, column=0, sticky=tk.W
            )
            tk.Label(
                course_frame, text=", ".join(course_data["task_number_in_excel"])
            ).grid(row=2, column=1, sticky=tk.W)

            tk.Label(course_frame, text="Task Codes in Moodle:").grid(
                row=3, column=0, sticky=tk.W
            )
            tk.Label(
                course_frame, text=", ".join(course_data["task_code_in_moodle"])
            ).grid(row=3, column=1, sticky=tk.W)

            # Button to edit course
            edit_btn = tk.Button(
                course_frame,
                text="Edit Course",
                command=lambda id=course_id: self.edit_course_popup(id),
            )
            edit_btn.grid(row=4, column=0, padx=5, pady=5)

            # Button to delete course
            delete_btn = tk.Button(
                course_frame,
                text="Delete Course",
                command=lambda id=course_id: self.delete_course(id),
            )
            delete_btn.grid(row=4, column=1, padx=5, pady=5)

    def add_course_popup(self):
        # Create a popup window for adding new course
        popup = tk.Toplevel(self.root)
        popup.title("Add New Course")

        # Entry fields for course details
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

        # Button to save course
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
        # Create a popup window for editing course
        popup = tk.Toplevel(self.root)
        popup.title(f"Edit Course {course_id}")

        # Current course data
        course_data = self.classes[course_id]

        # Entry fields for course details
        tk.Label(popup, text="Course ID:").grid(
            row=0, column=0, padx=10, pady=10, sticky=tk.W
        )
        course_id_entry = tk.Label(popup, text=course_id)
        course_id_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(popup, text="Course Name:").grid(
            row=1, column=0, padx=10, pady=10, sticky=tk.W
        )
        course_name_entry = tk.Entry(popup)
        course_name_entry.insert(tk.END, course_data["name"])
        course_name_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(popup, text="File Path:").grid(
            row=2, column=0, padx=10, pady=10, sticky=tk.W
        )
        file_path_entry = tk.Entry(popup)
        file_path_entry.insert(tk.END, course_data["path"])
        file_path_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(popup, text="Task Numbers in Excel:").grid(
            row=3, column=0, padx=10, pady=10, sticky=tk.W
        )
        task_numbers_display = tk.Label(
            popup, text=", ".join(course_data["task_number_in_excel"])
        )
        task_numbers_display.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(popup, text="Task Codes in Moodle:").grid(
            row=4, column=0, padx=10, pady=10, sticky=tk.W
        )
        task_codes_display = tk.Label(
            popup, text=", ".join(course_data["task_code_in_moodle"])
        )
        task_codes_display.grid(row=4, column=1, padx=10, pady=10)

        def add_tasks():
            # Create a popup window for entering task numbers and codes
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

                if task_numbers:
                    new_task_numbers = [num.strip() for num in task_numbers.split(",")]
                    course_data["task_number_in_excel"].extend(new_task_numbers)
                    task_numbers_display.config(
                        text=", ".join(course_data["task_number_in_excel"])
                    )

                if task_codes:
                    new_task_codes = [code.strip() for code in task_codes.split(",")]
                    course_data["task_code_in_moodle"].extend(new_task_codes)
                    task_codes_display.config(
                        text=", ".join(course_data["task_code_in_moodle"])
                    )

                task_popup.destroy()

            save_tasks_btn = tk.Button(
                task_popup, text="Save Tasks", command=save_tasks
            )
            save_tasks_btn.grid(row=2, columnspan=2, pady=10)

            task_popup.mainloop()

        def clear_tasks():
            course_data["task_number_in_excel"] = []
            course_data["task_code_in_moodle"] = []
            task_numbers_display.config(text="")
            task_codes_display.config(text="")

        # Buttons for task management
        add_tasks_btn = tk.Button(
            popup, text="Add Task Numbers & Codes", command=add_tasks
        )
        add_tasks_btn.grid(row=5, columnspan=2, pady=10)

        clear_tasks_btn = tk.Button(
            popup, text="Clear Task Numbers & Codes", command=clear_tasks
        )
        clear_tasks_btn.grid(row=6, columnspan=2, pady=10)

        # Button to save course
        def save_course():
            new_course_name = course_name_entry.get().strip()
            new_file_path = file_path_entry.get().strip()

            # Update course data
            self.classes[course_id]["name"] = new_course_name
            self.classes[course_id]["path"] = new_file_path

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
            del self.classes[course_id]
            self.display_courses()


# Create the main tkinter window
root = tk.Tk()
app = MoodleGradeFillerApp(root)
root.mainloop()
