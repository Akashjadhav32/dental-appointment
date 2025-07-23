#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Dental Appointment Booking System
Tests all endpoints with various validation scenarios
"""

import requests
import json
from datetime import datetime, date, timedelta
import sys
import os

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading backend URL: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("ERROR: Could not get backend URL from frontend/.env")
    sys.exit(1)

print(f"Testing backend at: {BASE_URL}")

# Test results tracking
test_results = []
failed_tests = []

def log_test(test_name, success, details=""):
    """Log test results"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")
    
    test_results.append({
        'test': test_name,
        'success': success,
        'details': details
    })
    
    if not success:
        failed_tests.append(test_name)

def test_health_check():
    """Test GET /api/ - Basic health check"""
    try:
        response = requests.get(f"{BASE_URL}/api/")
        if response.status_code == 200:
            data = response.json()
            if "message" in data:
                log_test("Health Check (GET /api/)", True, f"Response: {data}")
                return True
            else:
                log_test("Health Check (GET /api/)", False, "Missing message in response")
                return False
        else:
            log_test("Health Check (GET /api/)", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test("Health Check (GET /api/)", False, f"Exception: {str(e)}")
        return False

def test_create_appointment_valid():
    """Test POST /api/appointments - Valid appointment creation"""
    try:
        # Get tomorrow's date (weekday)
        tomorrow = date.today() + timedelta(days=1)
        while tomorrow.weekday() >= 5:  # Skip weekends
            tomorrow += timedelta(days=1)
        
        appointment_data = {
            "name": "John Smith",
            "sex": "Male",
            "age": 30,
            "complaint": "Regular dental checkup and cleaning",
            "timeSlot": "9:00–10:00 AM",
            "appointmentDate": tomorrow.isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/api/appointments", json=appointment_data)
        if response.status_code == 200:
            data = response.json()
            if "id" in data and data["name"] == "John Smith":
                log_test("Create Valid Appointment", True, f"Created appointment with ID: {data['id']}")
                return True, data
            else:
                log_test("Create Valid Appointment", False, "Missing required fields in response")
                return False, None
        else:
            log_test("Create Valid Appointment", False, f"Status: {response.status_code}, Response: {response.text}")
            return False, None
    except Exception as e:
        log_test("Create Valid Appointment", False, f"Exception: {str(e)}")
        return False, None

def test_saturday_morning_slot():
    """Test Saturday morning slot (should work)"""
    try:
        # Find next Saturday
        today = date.today()
        days_ahead = 5 - today.weekday()  # Saturday is 5
        if days_ahead <= 0:
            days_ahead += 7
        saturday = today + timedelta(days=days_ahead)
        
        appointment_data = {
            "name": "Sarah Johnson",
            "sex": "Female",
            "age": 25,
            "complaint": "Tooth pain and sensitivity issues",
            "timeSlot": "10:00–11:00 AM",
            "appointmentDate": saturday.isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/api/appointments", json=appointment_data)
        if response.status_code == 200:
            log_test("Saturday Morning Slot", True, "Successfully booked Saturday morning appointment")
            return True
        else:
            log_test("Saturday Morning Slot", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        log_test("Saturday Morning Slot", False, f"Exception: {str(e)}")
        return False

def test_saturday_afternoon_slot():
    """Test Saturday afternoon slot (should be rejected)"""
    try:
        # Find next Saturday
        today = date.today()
        days_ahead = 5 - today.weekday()  # Saturday is 5
        if days_ahead <= 0:
            days_ahead += 7
        saturday = today + timedelta(days=days_ahead)
        
        appointment_data = {
            "name": "Mike Wilson",
            "sex": "Male",
            "age": 35,
            "complaint": "Dental crown replacement needed",
            "timeSlot": "2:00–3:00 PM",
            "appointmentDate": saturday.isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/api/appointments", json=appointment_data)
        if response.status_code == 400:
            log_test("Saturday Afternoon Slot Rejection", True, "Correctly rejected Saturday afternoon slot")
            return True
        else:
            log_test("Saturday Afternoon Slot Rejection", False, f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        log_test("Saturday Afternoon Slot Rejection", False, f"Exception: {str(e)}")
        return False

def test_sunday_appointment():
    """Test Sunday appointment (should be rejected)"""
    try:
        # Find next Sunday
        today = date.today()
        days_ahead = 6 - today.weekday()  # Sunday is 6
        if days_ahead <= 0:
            days_ahead += 7
        sunday = today + timedelta(days=days_ahead)
        
        appointment_data = {
            "name": "Lisa Brown",
            "sex": "Female",
            "age": 28,
            "complaint": "Emergency dental consultation",
            "timeSlot": "9:00–10:00 AM",
            "appointmentDate": sunday.isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/api/appointments", json=appointment_data)
        if response.status_code == 400:
            log_test("Sunday Appointment Rejection", True, "Correctly rejected Sunday appointment")
            return True
        else:
            log_test("Sunday Appointment Rejection", False, f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        log_test("Sunday Appointment Rejection", False, f"Exception: {str(e)}")
        return False

def test_past_date_appointment():
    """Test past date appointment (should be rejected)"""
    try:
        yesterday = date.today() - timedelta(days=1)
        
        appointment_data = {
            "name": "David Lee",
            "sex": "Male",
            "age": 40,
            "complaint": "Routine dental examination",
            "timeSlot": "11:00–12:00 PM",
            "appointmentDate": yesterday.isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/api/appointments", json=appointment_data)
        if response.status_code == 400:
            log_test("Past Date Appointment Rejection", True, "Correctly rejected past date appointment")
            return True
        else:
            log_test("Past Date Appointment Rejection", False, f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        log_test("Past Date Appointment Rejection", False, f"Exception: {str(e)}")
        return False

def test_duplicate_slot_booking():
    """Test duplicate slot booking (should be rejected)"""
    try:
        # Get tomorrow's date (weekday)
        tomorrow = date.today() + timedelta(days=1)
        while tomorrow.weekday() >= 5:  # Skip weekends
            tomorrow += timedelta(days=1)
        
        # First appointment
        appointment_data1 = {
            "name": "Emma Davis",
            "sex": "Female",
            "age": 32,
            "complaint": "Dental cleaning and checkup",
            "timeSlot": "12:00–1:00 PM",
            "appointmentDate": tomorrow.isoformat()
        }
        
        # Create first appointment
        response1 = requests.post(f"{BASE_URL}/api/appointments", json=appointment_data1)
        
        # Try to book same slot
        appointment_data2 = {
            "name": "Robert Taylor",
            "sex": "Male",
            "age": 45,
            "complaint": "Tooth extraction consultation",
            "timeSlot": "12:00–1:00 PM",
            "appointmentDate": tomorrow.isoformat()
        }
        
        response2 = requests.post(f"{BASE_URL}/api/appointments", json=appointment_data2)
        
        if response1.status_code == 200 and response2.status_code == 400:
            log_test("Duplicate Slot Booking Rejection", True, "Correctly rejected duplicate slot booking")
            return True
        else:
            log_test("Duplicate Slot Booking Rejection", False, 
                    f"First: {response1.status_code}, Second: {response2.status_code}")
            return False
    except Exception as e:
        log_test("Duplicate Slot Booking Rejection", False, f"Exception: {str(e)}")
        return False

def test_invalid_age_negative():
    """Test invalid age - negative value"""
    try:
        tomorrow = date.today() + timedelta(days=1)
        while tomorrow.weekday() >= 5:
            tomorrow += timedelta(days=1)
        
        appointment_data = {
            "name": "Invalid Age",
            "sex": "Male",
            "age": -5,
            "complaint": "Testing negative age validation",
            "timeSlot": "9:00–10:00 AM",
            "appointmentDate": tomorrow.isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/api/appointments", json=appointment_data)
        if response.status_code == 400:  # Express validation error
            log_test("Invalid Age (Negative) Rejection", True, "Correctly rejected negative age")
            return True
        else:
            log_test("Invalid Age (Negative) Rejection", False, f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        log_test("Invalid Age (Negative) Rejection", False, f"Exception: {str(e)}")
        return False

def test_invalid_age_over_150():
    """Test invalid age - over 150"""
    try:
        tomorrow = date.today() + timedelta(days=1)
        while tomorrow.weekday() >= 5:
            tomorrow += timedelta(days=1)
        
        appointment_data = {
            "name": "Very Old Person",
            "sex": "Female",
            "age": 200,
            "complaint": "Testing age over 150 validation",
            "timeSlot": "9:00–10:00 AM",
            "appointmentDate": tomorrow.isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/api/appointments", json=appointment_data)
        if response.status_code == 400:  # Express validation error
            log_test("Invalid Age (Over 150) Rejection", True, "Correctly rejected age over 150")
            return True
        else:
            log_test("Invalid Age (Over 150) Rejection", False, f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        log_test("Invalid Age (Over 150) Rejection", False, f"Exception: {str(e)}")
        return False

def test_invalid_name_too_short():
    """Test invalid name - too short"""
    try:
        tomorrow = date.today() + timedelta(days=1)
        while tomorrow.weekday() >= 5:
            tomorrow += timedelta(days=1)
        
        appointment_data = {
            "name": "A",
            "sex": "Male",
            "age": 30,
            "complaint": "Testing short name validation",
            "time_slot": "9:00–10:00 AM",
            "appointment_date": tomorrow.isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/api/appointments", json=appointment_data)
        if response.status_code == 422:  # Pydantic validation error
            log_test("Invalid Name (Too Short) Rejection", True, "Correctly rejected short name")
            return True
        else:
            log_test("Invalid Name (Too Short) Rejection", False, f"Expected 422, got {response.status_code}")
            return False
    except Exception as e:
        log_test("Invalid Name (Too Short) Rejection", False, f"Exception: {str(e)}")
        return False

def test_invalid_complaint_too_short():
    """Test invalid complaint - too short"""
    try:
        tomorrow = date.today() + timedelta(days=1)
        while tomorrow.weekday() >= 5:
            tomorrow += timedelta(days=1)
        
        appointment_data = {
            "name": "Test User",
            "sex": "Male",
            "age": 30,
            "complaint": "Hi",
            "time_slot": "9:00–10:00 AM",
            "appointment_date": tomorrow.isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/api/appointments", json=appointment_data)
        if response.status_code == 422:  # Pydantic validation error
            log_test("Invalid Complaint (Too Short) Rejection", True, "Correctly rejected short complaint")
            return True
        else:
            log_test("Invalid Complaint (Too Short) Rejection", False, f"Expected 422, got {response.status_code}")
            return False
    except Exception as e:
        log_test("Invalid Complaint (Too Short) Rejection", False, f"Exception: {str(e)}")
        return False

def test_get_all_appointments():
    """Test GET /api/appointments - Retrieve all appointments"""
    try:
        response = requests.get(f"{BASE_URL}/api/appointments")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                log_test("Get All Appointments", True, f"Retrieved {len(data)} appointments")
                return True
            else:
                log_test("Get All Appointments", False, "Response is not a list")
                return False
        else:
            log_test("Get All Appointments", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test("Get All Appointments", False, f"Exception: {str(e)}")
        return False

def test_available_slots_weekday():
    """Test available slots for weekday (should show all 6 slots)"""
    try:
        # Get next weekday
        tomorrow = date.today() + timedelta(days=1)
        while tomorrow.weekday() >= 5:  # Skip weekends
            tomorrow += timedelta(days=1)
        
        response = requests.get(f"{BASE_URL}/api/appointments/available-slots?appointment_date={tomorrow.isoformat()}")
        if response.status_code == 200:
            data = response.json()
            if "available_slots" in data:
                slots = data["available_slots"]
                # Should have 6 slots for weekdays (minus any already booked)
                if len(slots) >= 4:  # At least 4 slots should be available
                    log_test("Available Slots Weekday", True, f"Found {len(slots)} available slots")
                    return True
                else:
                    log_test("Available Slots Weekday", False, f"Only {len(slots)} slots available")
                    return False
            else:
                log_test("Available Slots Weekday", False, "Missing available_slots in response")
                return False
        else:
            log_test("Available Slots Weekday", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test("Available Slots Weekday", False, f"Exception: {str(e)}")
        return False

def test_available_slots_saturday():
    """Test available slots for Saturday (should show only 4 morning slots)"""
    try:
        # Find next Saturday
        today = date.today()
        days_ahead = 5 - today.weekday()  # Saturday is 5
        if days_ahead <= 0:
            days_ahead += 7
        saturday = today + timedelta(days=days_ahead)
        
        response = requests.get(f"{BASE_URL}/api/appointments/available-slots?appointment_date={saturday.isoformat()}")
        if response.status_code == 200:
            data = response.json()
            if "available_slots" in data:
                slots = data["available_slots"]
                # Should have only 4 morning slots for Saturday
                if len(slots) <= 4:
                    log_test("Available Slots Saturday", True, f"Found {len(slots)} morning slots")
                    return True
                else:
                    log_test("Available Slots Saturday", False, f"Too many slots: {len(slots)}")
                    return False
            else:
                log_test("Available Slots Saturday", False, "Missing available_slots in response")
                return False
        else:
            log_test("Available Slots Saturday", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test("Available Slots Saturday", False, f"Exception: {str(e)}")
        return False

def test_available_slots_sunday():
    """Test available slots for Sunday (should show no slots)"""
    try:
        # Find next Sunday
        today = date.today()
        days_ahead = 6 - today.weekday()  # Sunday is 6
        if days_ahead <= 0:
            days_ahead += 7
        sunday = today + timedelta(days=days_ahead)
        
        response = requests.get(f"{BASE_URL}/api/appointments/available-slots?appointment_date={sunday.isoformat()}")
        if response.status_code == 200:
            data = response.json()
            if "available_slots" in data:
                slots = data["available_slots"]
                if len(slots) == 0:
                    log_test("Available Slots Sunday", True, "Correctly shows no slots for Sunday")
                    return True
                else:
                    log_test("Available Slots Sunday", False, f"Should have 0 slots, got {len(slots)}")
                    return False
            else:
                log_test("Available Slots Sunday", False, "Missing available_slots in response")
                return False
        else:
            log_test("Available Slots Sunday", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test("Available Slots Sunday", False, f"Exception: {str(e)}")
        return False

def run_all_tests():
    """Run all backend tests"""
    print("=" * 80)
    print("DENTAL APPOINTMENT BOOKING SYSTEM - BACKEND API TESTING")
    print("=" * 80)
    print()
    
    # Run all tests
    test_health_check()
    test_create_appointment_valid()
    test_saturday_morning_slot()
    test_saturday_afternoon_slot()
    test_sunday_appointment()
    test_past_date_appointment()
    test_duplicate_slot_booking()
    test_invalid_age_negative()
    test_invalid_age_over_150()
    test_invalid_name_too_short()
    test_invalid_complaint_too_short()
    test_get_all_appointments()
    test_available_slots_weekday()
    test_available_slots_saturday()
    test_available_slots_sunday()
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total_tests = len(test_results)
    passed_tests = len([t for t in test_results if t['success']])
    failed_tests_count = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests_count}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print("\nFAILED TESTS:")
        for test_name in failed_tests:
            print(f"  ❌ {test_name}")
    
    print("\n" + "=" * 80)
    
    return passed_tests, failed_tests_count

if __name__ == "__main__":
    passed, failed = run_all_tests()
    sys.exit(0 if failed == 0 else 1)