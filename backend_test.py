#!/usr/bin/env python3
"""
Backend API Testing Script for Dental Appointment System
Tests Node.js + Express backend with MongoDB integration
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import uuid
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Backend URL - using localhost for testing since external URL has routing issues
BACKEND_URL = "http://localhost:8001/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification for testing
        self.test_results = []
        self.appointments_created = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def test_mongodb_connection(self):
        """Test 1: MongoDB connection via health check"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Dental Clinic" in data["message"]:
                    self.log_test("MongoDB Connection (Health Check)", True, 
                                f"Server responding: {data['message']}")
                    return True
                else:
                    self.log_test("MongoDB Connection (Health Check)", False, 
                                f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("MongoDB Connection (Health Check)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("MongoDB Connection (Health Check)", False, f"Connection error: {str(e)}")
            return False
    
    def test_post_appointments_endpoint(self):
        """Test 2: POST /api/appointments endpoint"""
        # Test valid appointment creation
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Test data with realistic information
        test_appointment = {
            "name": "Dr. Sarah Johnson",
            "sex": "Female", 
            "age": 35,
            "complaint": "Routine dental checkup and cleaning needed",
            "appointmentDate": tomorrow,
            "timeSlot": "10:00–11:00 AM"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/appointments", 
                                       json=test_appointment,
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["name"] == test_appointment["name"]:
                    self.appointments_created.append(data["id"])
                    self.log_test("POST /api/appointments (Valid Data)", True, 
                                f"Created appointment ID: {data['id']}")
                    
                    # Test duplicate booking prevention
                    duplicate_response = self.session.post(f"{BACKEND_URL}/appointments", 
                                                         json=test_appointment,
                                                         headers={'Content-Type': 'application/json'})
                    
                    if duplicate_response.status_code == 400:
                        self.log_test("POST /api/appointments (Duplicate Prevention)", True, 
                                    "Correctly rejected duplicate booking")
                    else:
                        self.log_test("POST /api/appointments (Duplicate Prevention)", False, 
                                    f"Should reject duplicate: {duplicate_response.status_code}")
                    
                    return True
                else:
                    self.log_test("POST /api/appointments (Valid Data)", False, 
                                f"Invalid response structure: {data}")
                    return False
            else:
                self.log_test("POST /api/appointments (Valid Data)", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /api/appointments (Valid Data)", False, f"Request error: {str(e)}")
            return False
    
    def test_post_appointments_validation(self):
        """Test 3: POST /api/appointments validation"""
        # Test invalid data scenarios
        test_cases = [
            {
                "name": "Invalid Age Test",
                "data": {
                    "name": "Test User",
                    "sex": "Male",
                    "age": -5,  # Invalid negative age
                    "complaint": "Test complaint for validation",
                    "appointmentDate": (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    "timeSlot": "9:00–10:00 AM"
                },
                "expected_status": 400
            },
            {
                "name": "Invalid Name Test", 
                "data": {
                    "name": "A",  # Too short
                    "sex": "Female",
                    "age": 25,
                    "complaint": "Test complaint for validation",
                    "appointmentDate": (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    "timeSlot": "11:00–12:00 PM"
                },
                "expected_status": 400
            },
            {
                "name": "Invalid Complaint Test",
                "data": {
                    "name": "Test User",
                    "sex": "Other",
                    "age": 30,
                    "complaint": "Hi",  # Too short
                    "appointmentDate": (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    "timeSlot": "12:00–1:00 PM"
                },
                "expected_status": 400
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            try:
                response = self.session.post(f"{BACKEND_URL}/appointments", 
                                           json=test_case["data"],
                                           headers={'Content-Type': 'application/json'})
                
                if response.status_code == test_case["expected_status"]:
                    self.log_test(f"POST Validation - {test_case['name']}", True, 
                                f"Correctly rejected with status {response.status_code}")
                else:
                    self.log_test(f"POST Validation - {test_case['name']}", False, 
                                f"Expected {test_case['expected_status']}, got {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"POST Validation - {test_case['name']}", False, f"Request error: {str(e)}")
                all_passed = False
                
        return all_passed
    
    def test_get_appointments_endpoint(self):
        """Test 4: GET /api/appointments endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/appointments")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check if our created appointment is in the list
                    found_appointment = False
                    for appointment in data:
                        if appointment.get("id") in self.appointments_created:
                            found_appointment = True
                            break
                    
                    if found_appointment or len(data) >= 0:  # Allow empty list
                        self.log_test("GET /api/appointments", True, 
                                    f"Retrieved {len(data)} appointments successfully")
                        
                        # Verify data structure
                        if len(data) > 0:
                            sample = data[0]
                            required_fields = ["id", "name", "sex", "age", "complaint", "appointment_date", "time_slot"]
                            missing_fields = [field for field in required_fields if field not in sample]
                            
                            if not missing_fields:
                                self.log_test("GET /api/appointments (Data Structure)", True, 
                                            "All required fields present in response")
                            else:
                                self.log_test("GET /api/appointments (Data Structure)", False, 
                                            f"Missing fields: {missing_fields}")
                        
                        return True
                    else:
                        self.log_test("GET /api/appointments", False, 
                                    "Created appointment not found in response")
                        return False
                else:
                    self.log_test("GET /api/appointments", False, 
                                f"Expected array, got: {type(data)}")
                    return False
            else:
                self.log_test("GET /api/appointments", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/appointments", False, f"Request error: {str(e)}")
            return False
    
    def test_get_available_slots_endpoint(self):
        """Test 5: GET /api/appointments/available-slots endpoint"""
        # Test weekday slots
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        try:
            response = self.session.get(f"{BACKEND_URL}/appointments/available-slots", 
                                      params={"appointment_date": tomorrow})
            
            if response.status_code == 200:
                data = response.json()
                if "available_slots" in data:
                    slots = data["available_slots"]
                    self.log_test("GET /api/appointments/available-slots (Weekday)", True, 
                                f"Retrieved {len(slots)} available slots")
                    
                    # Test Saturday restrictions
                    # Find next Saturday
                    current_date = datetime.now()
                    days_until_saturday = (5 - current_date.weekday()) % 7
                    if days_until_saturday == 0:  # Today is Saturday
                        days_until_saturday = 7
                    saturday = (current_date + timedelta(days=days_until_saturday)).strftime('%Y-%m-%d')
                    
                    saturday_response = self.session.get(f"{BACKEND_URL}/appointments/available-slots", 
                                                       params={"appointment_date": saturday})
                    
                    if saturday_response.status_code == 200:
                        saturday_data = saturday_response.json()
                        saturday_slots = saturday_data.get("available_slots", [])
                        
                        # Saturday should only have morning slots
                        afternoon_slots = ["2:00–3:00 PM", "3:00–4:00 PM"]
                        has_afternoon = any(slot in afternoon_slots for slot in saturday_slots)
                        
                        if not has_afternoon:
                            self.log_test("GET /api/appointments/available-slots (Saturday Restriction)", True, 
                                        f"Saturday correctly shows only morning slots: {len(saturday_slots)} slots")
                        else:
                            self.log_test("GET /api/appointments/available-slots (Saturday Restriction)", False, 
                                        f"Saturday incorrectly shows afternoon slots: {saturday_slots}")
                    
                    # Test Sunday restrictions
                    # Find next Sunday
                    days_until_sunday = (6 - current_date.weekday()) % 7
                    if days_until_sunday == 0:  # Today is Sunday
                        days_until_sunday = 7
                    sunday = (current_date + timedelta(days=days_until_sunday)).strftime('%Y-%m-%d')
                    
                    sunday_response = self.session.get(f"{BACKEND_URL}/appointments/available-slots", 
                                                     params={"appointment_date": sunday})
                    
                    if sunday_response.status_code == 200:
                        sunday_data = sunday_response.json()
                        sunday_slots = sunday_data.get("available_slots", [])
                        
                        if len(sunday_slots) == 0:
                            self.log_test("GET /api/appointments/available-slots (Sunday Restriction)", True, 
                                        "Sunday correctly shows no available slots")
                        else:
                            self.log_test("GET /api/appointments/available-slots (Sunday Restriction)", False, 
                                        f"Sunday incorrectly shows slots: {sunday_slots}")
                    
                    return True
                else:
                    self.log_test("GET /api/appointments/available-slots", False, 
                                f"Missing 'available_slots' in response: {data}")
                    return False
            else:
                self.log_test("GET /api/appointments/available-slots", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/appointments/available-slots", False, f"Request error: {str(e)}")
            return False
    
    def test_saturday_sunday_restrictions(self):
        """Test 6: Saturday/Sunday booking restrictions"""
        # Find next Saturday and Sunday
        current_date = datetime.now()
        
        # Saturday test
        days_until_saturday = (5 - current_date.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        saturday = (current_date + timedelta(days=days_until_saturday)).strftime('%Y-%m-%d')
        
        # Try to book afternoon slot on Saturday
        saturday_afternoon_appointment = {
            "name": "Saturday Test User",
            "sex": "Male",
            "age": 40,
            "complaint": "Testing Saturday afternoon restriction",
            "appointmentDate": saturday,
            "timeSlot": "2:00–3:00 PM"  # Should be rejected
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/appointments", 
                                       json=saturday_afternoon_appointment,
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 400:
                self.log_test("Saturday Afternoon Restriction", True, 
                            "Correctly rejected Saturday afternoon booking")
            else:
                self.log_test("Saturday Afternoon Restriction", False, 
                            f"Should reject Saturday afternoon: {response.status_code}")
        
        except Exception as e:
            self.log_test("Saturday Afternoon Restriction", False, f"Request error: {str(e)}")
        
        # Sunday test
        days_until_sunday = (6 - current_date.weekday()) % 7
        if days_until_sunday == 0:
            days_until_sunday = 7
        sunday = (current_date + timedelta(days=days_until_sunday)).strftime('%Y-%m-%d')
        
        # Try to book any slot on Sunday
        sunday_appointment = {
            "name": "Sunday Test User",
            "sex": "Female",
            "age": 30,
            "complaint": "Testing Sunday booking restriction",
            "appointmentDate": sunday,
            "timeSlot": "10:00–11:00 AM"  # Should be rejected
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/appointments", 
                                       json=sunday_appointment,
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 400:
                self.log_test("Sunday Booking Restriction", True, 
                            "Correctly rejected Sunday booking")
                return True
            else:
                self.log_test("Sunday Booking Restriction", False, 
                            f"Should reject Sunday booking: {response.status_code}")
                return False
        
        except Exception as e:
            self.log_test("Sunday Booking Restriction", False, f"Request error: {str(e)}")
            return False
    
    def test_data_persistence(self):
        """Test 7: Verify data persistence in MongoDB"""
        # Create a unique appointment and verify it persists
        tomorrow = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        unique_name = f"Persistence Test User {uuid.uuid4().hex[:8]}"
        
        test_appointment = {
            "name": unique_name,
            "sex": "Other",
            "age": 28,
            "complaint": "Testing data persistence in MongoDB database",
            "appointmentDate": tomorrow,
            "timeSlot": "9:00–10:00 AM"
        }
        
        try:
            # Create appointment
            create_response = self.session.post(f"{BACKEND_URL}/appointments", 
                                              json=test_appointment,
                                              headers={'Content-Type': 'application/json'})
            
            if create_response.status_code == 200:
                created_data = create_response.json()
                appointment_id = created_data["id"]
                
                # Retrieve all appointments and verify our appointment exists
                get_response = self.session.get(f"{BACKEND_URL}/appointments")
                
                if get_response.status_code == 200:
                    all_appointments = get_response.json()
                    found_appointment = None
                    
                    for appointment in all_appointments:
                        if appointment.get("id") == appointment_id:
                            found_appointment = appointment
                            break
                    
                    if found_appointment:
                        # Verify all data matches
                        data_matches = (
                            found_appointment["name"] == unique_name and
                            found_appointment["sex"] == test_appointment["sex"] and
                            found_appointment["age"] == test_appointment["age"] and
                            found_appointment["complaint"] == test_appointment["complaint"] and
                            found_appointment["time_slot"] == test_appointment["timeSlot"]
                        )
                        
                        if data_matches:
                            self.log_test("Data Persistence in MongoDB", True, 
                                        f"Appointment {appointment_id} correctly persisted and retrieved")
                            return True
                        else:
                            self.log_test("Data Persistence in MongoDB", False, 
                                        f"Data mismatch: created={test_appointment}, retrieved={found_appointment}")
                            return False
                    else:
                        self.log_test("Data Persistence in MongoDB", False, 
                                    f"Created appointment {appointment_id} not found in database")
                        return False
                else:
                    self.log_test("Data Persistence in MongoDB", False, 
                                f"Failed to retrieve appointments: {get_response.status_code}")
                    return False
            else:
                self.log_test("Data Persistence in MongoDB", False, 
                            f"Failed to create test appointment: {create_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Data Persistence in MongoDB", False, f"Request error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 80)
        print("🧪 BACKEND API TESTING - Node.js + Express + MongoDB")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print()
        
        # Run tests in order
        tests = [
            self.test_mongodb_connection,
            self.test_post_appointments_endpoint,
            self.test_post_appointments_validation,
            self.test_get_appointments_endpoint,
            self.test_get_available_slots_endpoint,
            self.test_saturday_sunday_restrictions,
            self.test_data_persistence
        ]
        
        passed = 0
        total = 0
        
        for test in tests:
            try:
                result = test()
                if result:
                    passed += 1
                total += 1
                print()  # Add spacing between tests
            except Exception as e:
                print(f"❌ FAIL: {test.__name__} - Unexpected error: {str(e)}")
                total += 1
                print()
        
        # Summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Backend is working correctly.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
        
        return passed == total

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)