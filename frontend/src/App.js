import { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AppointmentForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    sex: '',
    age: '',
    complaint: '',
    time_slot: '',
    appointment_date: ''
  });
  
  const [availableSlots, setAvailableSlots] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');
  const [errors, setErrors] = useState({});

  const timeSlots = [
    "9:00–10:00 AM",
    "10:00–11:00 AM", 
    "11:00–12:00 PM",
    "12:00–1:00 PM",
    "2:00–3:00 PM",
    "3:00–4:00 PM"
  ];

  // Fetch available slots when date changes
  useEffect(() => {
    if (formData.appointment_date) {
      fetchAvailableSlots(formData.appointment_date);
    }
  }, [formData.appointment_date]);

  const fetchAvailableSlots = async (date) => {
    try {
      const response = await axios.get(`${API}/appointments/available-slots?appointment_date=${date}`);
      setAvailableSlots(response.data.available_slots);
      
      // Clear selected time slot if it's no longer available
      if (formData.time_slot && !response.data.available_slots.includes(formData.time_slot)) {
        setFormData(prev => ({ ...prev, time_slot: '' }));
      }
    } catch (error) {
      console.error('Error fetching available slots:', error);
      setAvailableSlots([]);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters long';
    }
    
    if (!formData.sex) {
      newErrors.sex = 'Sex is required';
    }
    
    if (!formData.age) {
      newErrors.age = 'Age is required';
    } else if (formData.age < 0 || formData.age > 150) {
      newErrors.age = 'Age must be between 0 and 150';
    }
    
    if (!formData.complaint.trim()) {
      newErrors.complaint = 'Complaint is required';
    } else if (formData.complaint.trim().length < 5) {
      newErrors.complaint = 'Complaint must be at least 5 characters long';
    }
    
    if (!formData.appointment_date) {
      newErrors.appointment_date = 'Appointment date is required';
    }
    
    if (!formData.time_slot) {
      newErrors.time_slot = 'Time slot is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    setSubmitMessage('');
    
    try {
      const response = await axios.post(`${API}/appointments`, {
        ...formData,
        age: parseInt(formData.age)
      });
      
      setSubmitMessage('✅ Appointment booked successfully! You will receive a confirmation shortly.');
      
      // Reset form
      setFormData({
        name: '',
        sex: '',
        age: '',
        complaint: '',
        time_slot: '',
        appointment_date: ''
      });
      setAvailableSlots([]);
      
    } catch (error) {
      console.error('Error booking appointment:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to book appointment. Please try again.';
      setSubmitMessage(`❌ ${errorMessage}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Get minimum date (today)
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              🦷 Dental Clinic Appointment
            </h1>
            <p className="text-gray-600">
              Book your appointment with our dental professionals
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white placeholder-gray-500 ${
                  errors.name ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Enter your full name"
              />
              {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
            </div>

            {/* Sex */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sex *
              </label>
              <select
                name="sex"
                value={formData.sex}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white ${
                  errors.sex ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="" className="text-gray-500">Select sex</option>
                <option value="Male" className="text-gray-900">Male</option>
                <option value="Female" className="text-gray-900">Female</option>
                <option value="Other" className="text-gray-900">Other</option>
              </select>
              {errors.sex && <p className="mt-1 text-sm text-red-600">{errors.sex}</p>}
            </div>

            {/* Age */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Age *
              </label>
              <input
                type="number"
                name="age"
                value={formData.age}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white placeholder-gray-500 ${
                  errors.age ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Enter your age"
                min="0"
                max="150"
              />
              {errors.age && <p className="mt-1 text-sm text-red-600">{errors.age}</p>}
            </div>

            {/* Complaint */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Complaint *
              </label>
              <textarea
                name="complaint"
                value={formData.complaint}
                onChange={handleInputChange}
                rows="4"
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white placeholder-gray-500 ${
                  errors.complaint ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Please describe your dental concern or complaint..."
              />
              {errors.complaint && <p className="mt-1 text-sm text-red-600">{errors.complaint}</p>}
            </div>

            {/* Appointment Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Appointment Date *
              </label>
              <input
                type="date"
                name="appointment_date"
                value={formData.appointment_date}
                onChange={handleInputChange}
                min={today}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.appointment_date ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.appointment_date && <p className="mt-1 text-sm text-red-600">{errors.appointment_date}</p>}
            </div>

            {/* Time Slot */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time Slot *
              </label>
              <select
                name="time_slot"
                value={formData.time_slot}
                onChange={handleInputChange}
                disabled={!formData.appointment_date}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.time_slot ? 'border-red-500' : 'border-gray-300'
                } ${!formData.appointment_date ? 'bg-gray-100' : ''}`}
              >
                <option value="">
                  {!formData.appointment_date ? 'Select date first' : 'Select time slot'}
                </option>
                {availableSlots.map(slot => (
                  <option key={slot} value={slot}>
                    {slot}
                  </option>
                ))}
              </select>
              {errors.time_slot && <p className="mt-1 text-sm text-red-600">{errors.time_slot}</p>}
              {formData.appointment_date && availableSlots.length === 0 && (
                <p className="mt-1 text-sm text-orange-600">
                  No slots available for this date
                </p>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSubmitting ? 'Booking Appointment...' : 'Book Appointment'}
            </button>

            {/* Submit Message */}
            {submitMessage && (
              <div className={`p-4 rounded-lg ${
                submitMessage.includes('✅') ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
              }`}>
                {submitMessage}
              </div>
            )}
          </form>

          {/* OPD Note */}
          <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              <span className="font-semibold">❗ Important:</span> The provided slot is for OPD (Outpatient Department) consultation only. 
              Further treatment dates will be scheduled based on the outcome of the OPD assessment.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <AppointmentForm />
    </div>
  );
}

export default App;