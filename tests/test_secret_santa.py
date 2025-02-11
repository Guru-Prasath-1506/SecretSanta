import pytest
import pandas as pd
import os
from app import EmployeeManager, FileManager, AssignmentManager

# Sample test data paths
TEST_EMPLOYEE_FILE = "test_employees.csv"
TEST_HISTORY_FILE = "test_previous_assignments.csv"
TEST_OUTPUT_FILE = "test_new_secret_santa.csv"

@pytest.fixture
def sample_employees():
    """Creates a test employee CSV file."""
    data = [
        {"Employee_Name": "Alice", "Employee_EmailID": "alice@example.com"},
        {"Employee_Name": "Bob", "Employee_EmailID": "bob@example.com"},
        {"Employee_Name": "Charlie", "Employee_EmailID": "charlie@example.com"}
    ]
    df = pd.DataFrame(data)
    df.to_csv(TEST_EMPLOYEE_FILE, index=False)
    yield data  # Yield the data for test functions
    os.remove(TEST_EMPLOYEE_FILE)  # Cleanup after test


def test_load_employees(sample_employees):
    """Test if employees are loaded correctly."""
    employees = EmployeeManager.load_employees(TEST_EMPLOYEE_FILE)
    assert employees is not None
    assert len(employees) == 3
    assert employees[0]["Employee_EmailID"] == "alice@example.com"


@pytest.fixture
def sample_previous_assignments():
    """Creates a test previous assignments CSV file."""
    data = [
        {"Employee_EmailID": "alice@example.com", "Secret_Child_EmailID": "bob@example.com"},
        {"Employee_EmailID": "bob@example.com", "Secret_Child_EmailID": "charlie@example.com"},
        {"Employee_EmailID": "charlie@example.com", "Secret_Child_EmailID": "alice@example.com"}
    ]
    df = pd.DataFrame(data)
    df.to_csv(TEST_HISTORY_FILE, index=False)
    yield  # Yield control for test functions
    os.remove(TEST_HISTORY_FILE)  # Cleanup after test


def test_load_previous_assignments(sample_previous_assignments):
    """Test if previous assignments are loaded correctly."""
    previous_assignments = FileManager.load_previous_assignments(TEST_HISTORY_FILE)
    assert previous_assignments is not None
    assert len(previous_assignments) == 3
    assert "bob@example.com" in previous_assignments["alice@example.com"]


@pytest.fixture
def sample_assignments(sample_employees, sample_previous_assignments):
    """Loads employees and previous assignments after ensuring files exist."""
    employees = EmployeeManager.load_employees(TEST_EMPLOYEE_FILE)
    previous_assignments = FileManager.load_previous_assignments(TEST_HISTORY_FILE)
    return employees, previous_assignments


def test_assign_secret_santa(sample_assignments):
    """Test Secret Santa assignments ensuring no repetition."""
    employees, previous_assignments = sample_assignments
    assert employees, "Error: No employees loaded"

    manager = AssignmentManager(employees, previous_assignments)

    assert manager.assign_secret_santa() is True, "Assignment failed!"

    assignments = manager.assignments
    assert len(assignments) == len(employees), f"Mismatch: Expected {len(employees)}, got {len(assignments)}"

    for giver, receiver in assignments.items():
        assert giver != receiver, f"Invalid assignment: {giver} was assigned to themselves"
        assert receiver not in previous_assignments.get(giver,
                                                        set()), f"Repeat match: {giver} was assigned to {receiver} again"


@pytest.fixture
def sample_save_assignments():
    """Fixture to create and clean up the output file."""
    yield  # Yield control to test function
    if os.path.exists(TEST_OUTPUT_FILE):
        os.remove(TEST_OUTPUT_FILE)  # Cleanup after test


def test_save_assignments(sample_save_assignments):
    """Test saving assignments to a CSV file."""
    sample_data = [
        {"Employee_Name": "Alice", "Employee_EmailID": "alice@example.com",
         "Secret_Child_Name": "Charlie", "Secret_Child_EmailID": "charlie@example.com"}
    ]

    FileManager.save_assignments(TEST_OUTPUT_FILE, sample_data, append=False)
    df = pd.read_csv(TEST_OUTPUT_FILE)

    assert len(df) == 1
    assert df.iloc[0]["Employee_Name"] == "Alice"
