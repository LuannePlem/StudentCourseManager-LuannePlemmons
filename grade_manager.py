# grade_manager.py
"""
Student Grade Management System (Waterfall - OOP, Menu-driven)
Author: Luanne Plemmons (with help from ChatGPT)

Classes:
- Course: holds a course name and multiple numeric grades for a student.
- Student: holds student_id, name, mapping of course_name -> Course.
- GradeManager: orchestrates student operations and JSON persistence.

Persistence format (JSON):
{
  "students": {
    "<student_id>": {
      "name": "<name>",
      "courses": {
        "<course_name>": [<grade1>, <grade2>, ...]
      }
    },
    ...
  }
}
"""
from __future__ import annotations
import json
from typing import Dict, List, Optional

class Course:
    def __init__(self, name: str):
        self.name = name
        self.grades: List[float] = []

    def add_grade(self, grade: float) -> None:
        if not isinstance(grade, (int, float)):
            raise ValueError("Grade must be numeric.")
        self.grades.append(float(grade))

    def remove_all_grades(self) -> None:
        self.grades.clear()

    def average(self) -> Optional[float]:
        if not self.grades:
            return None
        return sum(self.grades) / len(self.grades)

    def to_dict(self) -> List[float]:
        return list(self.grades)

    @staticmethod
    def from_list(name: str, grades: List[float]) -> "Course":
        c = Course(name)
        for g in grades:
            c.add_grade(g)
        return c

    def __repr__(self) -> str:
        avg = self.average()
        avg_str = f"{avg:.2f}" if avg is not None else "N/A"
        return f"{self.name}: grades={self.grades} avg={avg_str}"


class Student:
    def __init__(self, student_id: str, name: str):
        self.student_id = student_id
        self.name = name
        self.courses: Dict[str, Course] = {}

    def enroll_course(self, course_name: str) -> None:
        if course_name in self.courses:
            raise ValueError(f"{self.name} is already enrolled in '{course_name}'.")
        self.courses[course_name] = Course(course_name)

    def remove_course(self, course_name: str) -> None:
        if course_name not in self.courses:
            raise ValueError(f"{self.name} is not enrolled in '{course_name}'.")
        del self.courses[course_name]

    def add_grade(self, course_name: str, grade: float) -> None:
        if course_name not in self.courses:
            raise ValueError(f"{self.name} is not enrolled in '{course_name}'.")
        self.courses[course_name].add_grade(grade)

    def course_average(self, course_name: str) -> Optional[float]:
        if course_name not in self.courses:
            raise ValueError(f"{self.name} is not enrolled in '{course_name}'.")
        return self.courses[course_name].average()

    def gpa(self) -> Optional[float]:
        avgs = [c.average() for c in self.courses.values() if c.average() is not None]
        if not avgs:
            return None
        return sum(avgs) / len(avgs)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "courses": {name: c.to_dict() for name, c in self.courses.items()}
        }

    @staticmethod
    def from_dict(student_id: str, data: dict) -> "Student":
        s = Student(student_id, data["name"])
        for cname, grades in data.get("courses", {}).items():
            s.courses[cname] = Course.from_list(cname, grades)
        return s

    def __repr__(self) -> str:
        return f"Student(id={self.student_id!r}, name={self.name!r}, courses={list(self.courses)})"


class GradeManager:
    def __init__(self):
        self.students: Dict[str, Student] = {}

    # CRUD for students
    def add_student(self, student_id: str, name: str) -> None:
        if student_id in self.students:
            raise ValueError(f"Student with ID '{student_id}' already exists.")
        self.students[student_id] = Student(student_id, name)

    def remove_student(self, student_id: str) -> None:
        if student_id not in self.students:
            raise ValueError(f"Student with ID '{student_id}' not found.")
        del self.students[student_id]

    # Course ops
    def enroll_student_in_course(self, student_id: str, course_name: str) -> None:
        self._get_student(student_id).enroll_course(course_name)

    def remove_course_from_student(self, student_id: str, course_name: str) -> None:
        self._get_student(student_id).remove_course(course_name)

    def add_grade(self, student_id: str, course_name: str, grade: float) -> None:
        self._get_student(student_id).add_grade(course_name, grade)

    def course_average(self, student_id: str, course_name: str) -> Optional[float]:
        return self._get_student(student_id).course_average(course_name)

    def student_gpa(self, student_id: str) -> Optional[float]:
        return self._get_student(student_id).gpa()

    def display_student(self, student_id: str) -> str:
        s = self._get_student(student_id)
        lines = [f"ID: {s.student_id} | Name: {s.name}"]
        if not s.courses:
            lines.append("  (no courses)")
        for cname, course in s.courses.items():
            avg = course.average()
            avg_str = f"{avg:.2f}" if avg is not None else "N/A"
            lines.append(f"  - {cname}: grades={course.grades} | avg={avg_str}")
        g = s.gpa()
        gpa_str = f"{g:.2f}" if g is not None else "N/A"
        lines.append(f"  Overall GPA: {gpa_str}")
        return "\n".join(lines)

    def display_all(self) -> str:
        if not self.students:
            return "(no students)"
        return "\n\n".join([self.display_student(sid) for sid in sorted(self.students)])

    # Persistence
    def save_json(self, path: str) -> None:
        data = {
            "students": {sid: s.to_dict() for sid, s in self.students.items()}
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_json(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.students.clear()
        for sid, sdict in data.get("students", {}).items():
            self.students[sid] = Student.from_dict(sid, sdict)

    def _get_student(self, student_id: str) -> Student:
        if student_id not in self.students:
            raise ValueError(f"Student with ID '{student_id}' not found.")
        return self.students[student_id]


def _prompt(msg: str) -> str:
    return input(msg).strip()

def _prompt_float(msg: str) -> float:
    while True:
        try:
            return float(_prompt(msg))
        except ValueError:
            print("Please enter a valid number.")

def _menu() -> None:
    gm = GradeManager()
    FILENAME = "students.json"
    while True:
        print("\n======== Student Grade Management System ========")
        print("1. Add student")
        print("2. Remove student")
        print("3. Enroll student in a course")
        print("4. Remove a course from a student")
        print("5. Add grade for a course")
        print("6. Display student info")
        print("7. Display all students")
        print("8. Save data")
        print("9. Load data")
        print("10. Exit")

        choice = _prompt("Select an option (1-10): ")
        try:
            if choice == "1":
                sid = _prompt("Enter student ID: ")
                name = _prompt("Enter student name: ")
                gm.add_student(sid, name)
                print("Student added.")
            elif choice == "2":
                sid = _prompt("Enter student ID: ")
                gm.remove_student(sid)
                print("Student removed.")
            elif choice == "3":
                sid = _prompt("Enter student ID: ")
                course = _prompt("Enter course name: ")
                gm.enroll_student_in_course(sid, course)
                print("Course enrolled.")
            elif choice == "4":
                sid = _prompt("Enter student ID: ")
                course = _prompt("Enter course name: ")
                gm.remove_course_from_student(sid, course)
                print("Course removed from student.")
            elif choice == "5":
                sid = _prompt("Enter student ID: ")
                course = _prompt("Enter course name: ")
                grade = _prompt_float("Enter grade (numeric): ")
                gm.add_grade(sid, course, grade)
                avg = gm.course_average(sid, course)
                print(f"Grade added. {course} average now: {avg:.2f}" if avg is not None else "Grade added.")
            elif choice == "6":
                sid = _prompt("Enter student ID: ")
                print(gm.display_student(sid))
            elif choice == "7":
                print(gm.display_all())
            elif choice == "8":
                path = _prompt(f"Enter filename to save [{FILENAME}]: ") or FILENAME
                gm.save_json(path)
                print(f"Data saved to '{path}'.")
            elif choice == "9":
                path = _prompt(f"Enter filename to load [{FILENAME}]: ") or FILENAME
                gm.load_json(path)
                print(f"Data loaded from '{path}'.")
            elif choice == "10":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please select 1-10.")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    _menu()
