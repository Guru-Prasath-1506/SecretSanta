import pytest
import os
from app import app


@pytest.fixture
def client():
    """Creates a test client for Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_csv():
    """Creates a sample CSV file for testing and deletes it after the test."""
    filename = "test_employees.csv"
    content = "Employee_Name,Employee_EmailID\nAlice,alice@example.com\nBob,bob@example.com"

    with open(filename, "w") as f:
        f.write(content)

    yield filename  # Provide filename to the test

    # Cleanup after test
    if os.path.exists(filename):
        os.remove(filename)


def test_index_page(client):
    """Test if the index page loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Upload & Generate" in response.data  # Match actual button text


def test_file_upload(client, sample_csv):
    """Test file upload functionality."""
    with open(sample_csv, "rb") as f:
        data = {"file": (f, sample_csv)}
        response = client.post("/", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    assert b"Secret Santa assignments generated successfully!" in response.data  # Updated assertion
