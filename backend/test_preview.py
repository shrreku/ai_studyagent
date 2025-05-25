import requests
import os

def test_preview_endpoint():
    """Test the /preview endpoint with a sample file."""
    url = "http://localhost:8000/preview"
    
    # Create a simple text file for testing
    test_file_path = "test_notes.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file with some study content.\n")
        f.write("Topic 1: Machine Learning Basics\n")
        f.write("Topic 2: Neural Networks\n")
        f.write("Topic 3: Data Preprocessing\n")
    
    try:
        # Prepare the form data
        files = [
            ('notes', ('test_notes.txt', open(test_file_path, 'rb'), 'text/plain'))
        ]
        data = {
            'study_duration_days': '5',
            'study_hours_per_day': '2'
        }
        
        print("Sending request to preview endpoint...")
        response = requests.post(url, files=files, data=data)
        
        # Print the response
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Success! Response data:")
            print(f"Message: {response.json().get('message')}")
            print(f"Raw plan available: {'raw_plan' in response.json()}")
            print(f"Preview plan available: {'preview_plan' in response.json()}")
        else:
            print(f"Error: {response.text}")
    
    finally:
        # Clean up the test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    test_preview_endpoint()
