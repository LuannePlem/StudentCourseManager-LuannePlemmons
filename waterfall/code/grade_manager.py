"""
Student Grade Management System (Waterfall - OOP, Menu-driven)
Author: Luanne Plemmons (with help from ChatGPT)

Classes:
- Course: holds a course name and multiple numeric grades for a student.
- Student: holds name and mapping of course_name -> Course.
- GradeManager: orchestrates student operations and JSON persistence.

Persistence format (JSON):
{
  "students": {
    "<student_name>": {
      "student_id": "<student_id>",
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

# ----------------------------
# Class: Course
# ----------------------------
# Represents a single course that a student is enrolled in.
# Each course has a name and a list of grades for that student.
class Course:
    def __init__(self, name: str):
        self.name = name # Name the course the name given by user
        self.grades: List[float] = [] # Array to store multiple grades for this course

    def add_grade(self, grade: float) -> None:
        # Adds grade to certain course
        if not isinstance(grade, (int, float)):
            raise ValueError("Grade must be numeric.")
        self.grades.append(float(grade))

    def remove_all_grades(self) -> None:
        self.grades.clear() # Clears all the grades if user wants to remove grades

    def average(self) -> Optional[float]:
        # Return avg grade in this course, or N/A if no grades
        if not self.grades:
            return None
        return sum(self.grades) / len(self.grades)

    def to_dict(self) -> List[float]:
        # Convert the course object into dictionary for saving to JSON
        return list(self.grades)

    @staticmethod
    def from_list(name: str, grades: List[float]) -> "Course":
        # This is helping to rebuild a course object from a directory (when loading in a JSON).
        c = Course(name)
        for g in grades:
            c.add_grade(g)
        return c

    def __repr__(self) -> str:
        avg = self.average()
        avg_str = f"{avg:.2f}" if avg is not None else "N/A"
        return f"{self.name}: grades={self.grades} avg={avg_str}"


# -------------------
# Class: Student
# -------------------
# Represents a student with an name, ID, and a set of courses
# Student is called by name
class Student:
    def __init__(self, name: str, student_id: str):
        self.name = name
        self.student_id = student_id
        self.courses: Dict[str, Course] = {} # Dictionary: name -> course object

    def enroll_course(self, course_name: str) -> None:
        # Enrolls student in course given by user. If student is already enrolled, tell user.
        if course_name in self.courses:
            raise ValueError(f"{self.name} is already enrolled in '{course_name}'.")
        self.courses[course_name] = Course(course_name)

    def remove_course(self, course_name: str) -> None:
        # Removes a course from student. If course is not found in dictionary, tell user and exit.
        if course_name not in self.courses:
            raise ValueError(f"{self.name} is not enrolled in '{course_name}'.")
        del self.courses[course_name]

    def add_grade(self, course_name: str, grade: float) -> None:
        # Assign grade to specific course if student is enrolled in course
        if course_name not in self.courses:
            raise ValueError(f"{self.name} is not enrolled in '{course_name}'.")
        self.courses[course_name].add_grade(grade)

    def course_average(self, course_name: str) -> Optional[float]:
        # Calculate course average from all courses.
        if course_name not in self.courses:
            raise ValueError(f"{self.name} is not enrolled in '{course_name}'.")
        return self.courses[course_name].average()

    def gpa(self) -> Optional[float]:
        """
        Calculate GPA on a 4.0 scale.
        Uses common U.S. grading scale:
          90-100 = 4.0
          80-89  = 3.0
          70-79  = 2.0
          60-69  = 1.0
          <60    = 0.0
        """
        gpa_points = []
        for c in self.courses.values():
            avg = c.average()
            if avg is not None:
                if avg >= 90:
                    gpa_points.append(4.0)
                elif avg >= 80:
                    gpa_points.append(3.0)
                elif avg >= 70:
                    gpa_points.append(2.0)
                elif avg >= 60:
                    gpa_points.append(1.0)
                else:
                    gpa_points.append(0.0)
        if not gpa_points:
            return None
        return sum(gpa_points) / len(gpa_points)

    def to_dict(self) -> dict:
        # Convert the student object into dictionary for saving to JSON.
        return {
            "student_id": self.student_id, # Need to make sure student_id is saved
            "courses": {name: c.to_dict() for name, c in self.courses.items()}
        }

    @staticmethod
    def from_dict(name: str, data: dict) -> "Student":
        # pull student_id from JSON, default to "N/A" if missing (for backward compatibility)
        s = Student(name, data["student_id"])
        for cname, grades in data.get("courses", {}).items():
            s.courses[cname] = Course.from_list(cname, grades)
        return s


    def __repr__(self) -> str:
        return f"Student(name={self.name!r}, courses={list(self.courses)})"


# ----------------------------
# Class: GradeManager
# ----------------------------
# Manages all students and provides menu-driven interface
class GradeManager:
    def __init__(self):
        self.students: Dict[str, Student] = {}  # key = name

    # -------------------
    # Student Management
    # -------------------
    def add_student(self, name: str, student_id: str) -> None:
        # Add student if ID does not exist in dictionary
        if name in self.students:
            raise ValueError(f"Student '{name}' already exists.")
        self.students[name] = Student(name, student_id)

    def remove_student(self, name: str) -> None:
        # Remove student if ID does exist in dictionary
        if name not in self.students:
            raise ValueError(f"Student '{name}' not found.")
        del self.students[name]

    # -------------------
    # Course Options
    # -------------------
    def enroll_student_in_course(self, name: str, course_name: str) -> None:
        # Uses student object to enroll
        self._get_student(name).enroll_course(course_name)

    def remove_course_from_student(self, name: str, course_name: str) -> None:
        # Uses student object to remove course
        self._get_student(name).remove_course(course_name)

    def add_grade(self, name: str, course_name: str, grade: float) -> None:
        # Uses Student object to add grade
        self._get_student(name).add_grade(course_name, grade)

    def course_average(self, name: str, course_name: str) -> Optional[float]:
        # Gets course average
        return self._get_student(name).course_average(course_name)

    def student_gpa(self, name: str) -> Optional[float]:
        # Gets student GPA
        return self._get_student(name).gpa()

    # ---------------------
    # Display methods
    # ---------------------
    def display_student(self, name: str) -> str:
        # Print one student's info, their courses, and grades.
        s = self._get_student(name)
        lines = [f"Name: {s.name}", f"Student ID: {s.student_id}"]
        if not s.courses:
            lines.append("  (no courses)")
        else:
            for cname in sorted(s.courses):
                course = s.courses[cname]
                avg = course.average()
                avg_str = f"{avg:.2f}" if avg is not None else "N/A"
                lines.append(f"  - {cname}: grades={course.grades} | avg={avg_str}")
        g = s.gpa()
        gpa_str = f"{g:.2f}" if g is not None else "N/A"
        lines.append(f"  Overall GPA: {gpa_str}")
        return "\n".join(lines)

    def display_all(self) -> str:
        # Print all students and their info if it exists
        if not self.students:
            return "(no students)"
        return "\n\n".join([self.display_student(name) for name in sorted(self.students)])

    # -----------------------
    # Persistence (Save/Load)
    # -----------------------
    def save_json(self, path: str) -> None:
        # Save all student data to JSON file.
        data = {
            "students": {name: s.to_dict() for name, s in sorted(self.students.items())}
        }# Places it into a dictionary
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2) # Adds to file

    def load_json(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.students.clear()
        for name, sdict in data.get("students", {}).items():
            self.students[name] = Student.from_dict(name, sdict)

    def _get_student(self, name: str) -> Student:
        if name not in self.students:
            raise ValueError(f"Student '{name}' not found.")
        return self.students[name]


# Helpers
# String prompt
# Takes prompt and makes it a stripped string.
def _prompt(msg: str) -> str:
    return input(msg).strip()

# Float prompt
# If the number is not a float, the error is given to user.
def _prompt_float(msg: str) -> float:
    while True:
        try:
            return float(_prompt(msg))
        except ValueError:
            print("Please enter a valid number.")


# ---------------
# Main Program (Menu-driven)
# ---------------
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
                name = _prompt("Enter student name: ")
                student_id = _prompt("Enter student ID: ")
                gm.add_student(name, student_id)
                print(f"Student {name} added.")
            elif choice == "2":
                name = _prompt("Enter student name: ")
                gm.remove_student(name)
                print(f"Student {name} removed.")
            elif choice == "3":
                name = _prompt("Enter student name: ")
                course = _prompt("Enter course name: ")
                gm.enroll_student_in_course(name, course)
                print(f"Student {name} entered in {course}.")
            elif choice == "4":
                name = _prompt("Enter student name: ")
                course = _prompt("Enter course name: ")
                gm.remove_course_from_student(name, course)
                print(f"Course {course} removed from student {name}.")
            elif choice == "5":
                name = _prompt("Enter student name: ")
                course = _prompt("Enter course name: ")
                grade = _prompt_float("Enter grade (numeric): ")
                gm.add_grade(name, course, grade)
                avg = gm.course_average(name, course)
                print(f"Grade added for {name}. {course} average now: {avg:.2f}" if avg is not None else "Grade added.")
            elif choice == "6":
                name = _prompt("Enter student name: ")
                print(gm.display_student(name))
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

