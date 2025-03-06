import statistics
import random

def generate_student_grades(num_students: int) -> list:
    """
    Generate a list of random student grades.
    
    Args:
        num_students (int): Number of students to generate grades for
    
    Returns:
        list: Random grades between 50 and 100
    """
    return [random.randint(50, 100) for _ in range(num_students)]

def calculate_grade_stats(grades: list) -> dict:
    """
    Calculate statistical metrics for a list of grades.
    
    Args:
        grades (list): List of student grades
    
    Returns:
        dict: Dictionary containing grade statistics
    """
    return {
        'average': round(statistics.mean(grades), 2),
        'median': statistics.median(grades),
        'highest': max(grades),
        'lowest': min(grades)
    }

def main():
    # Generate 10 student grades
    student_grades = generate_student_grades(10)
    
    # Calculate and print grade statistics
    grade_stats = calculate_grade_stats(student_grades)
    
    print("Student Grades:", student_grades)
    print("Grade Statistics:", grade_stats)

# Run the main function
if __name__ == "__main__":
    main()