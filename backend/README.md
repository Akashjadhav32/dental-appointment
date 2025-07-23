# Dental Appointment Booking System - Backend

## Overview
Node.js + Express.js backend for dental appointment booking system with MongoDB database.

## Features
- **Appointment Management**: Create and retrieve appointments
- **Business Logic**: Saturday/Sunday booking restrictions
- **Validation**: Comprehensive input validation
- **Database**: MongoDB with Mongoose ODM
- **API**: RESTful endpoints with proper error handling
- **Security**: CORS and Helmet middleware

## Tech Stack
- **Runtime**: Node.js
- **Framework**: Express.js
- **Database**: MongoDB with Mongoose
- **Validation**: express-validator
- **Security**: Helmet, CORS
- **Environment**: dotenv

## API Endpoints

### Health Check
- **GET** `/api/` - Health check endpoint

### Appointments
- **POST** `/api/appointments` - Create new appointment
- **GET** `/api/appointments` - Get all appointments
- **GET** `/api/appointments/available-slots?appointment_date=YYYY-MM-DD` - Get available slots for date

## Data Model

### Appointment Schema
```javascript
{
  id: String (UUID),
  name: String (required, 2-100 chars),
  sex: String (required, 'Male'|'Female'|'Other'),
  age: Number (required, 0-150),
  complaint: String (required, 5-500 chars),
  appointmentDate: Date (required),
  timeSlot: String (required, predefined slots),
  createdAt: Date (auto-generated),
  status: String (default: 'scheduled')
}
```

### Time Slots
- 9:00–10:00 AM
- 10:00–11:00 AM
- 11:00–12:00 PM
- 12:00–1:00 PM
- 2:00–3:00 PM
- 3:00–4:00 PM

## Business Rules
- **Saturday**: Only morning slots available (9 AM - 1 PM)
- **Sunday**: No appointments allowed
- **Past Dates**: Cannot book appointments for past dates
- **Duplicate Prevention**: Same date/time slot can't be booked twice

## Installation & Setup

### Prerequisites
- Node.js (v16 or higher)
- MongoDB (running locally or MongoDB Atlas)

### Installation
```bash
# Install dependencies
npm install

# Set up environment variables
# Create .env file with:
# MONGO_URL=mongodb://localhost:27017
# DB_NAME=test_database
# PORT=8001

# Start development server
npm run dev

# Start production server
npm start
```

### Environment Variables
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
PORT=8001
```

## Development Commands
```bash
# Install dependencies
npm install

# Run in development mode (with nodemon)
npm run dev

# Run in production mode
npm start

# Run tests (not implemented yet)
npm test
```

## API Usage Examples

### Create Appointment
```bash
curl -X POST http://localhost:8001/api/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "sex": "Male",
    "age": 30,
    "complaint": "Regular dental checkup",
    "appointmentDate": "2024-01-15",
    "timeSlot": "9:00–10:00 AM"
  }'
```

### Get All Appointments
```bash
curl http://localhost:8001/api/appointments
```

### Get Available Slots
```bash
curl "http://localhost:8001/api/appointments/available-slots?appointment_date=2024-01-15"
```

## Error Handling
- **400**: Bad Request (validation errors, business rule violations)
- **404**: Not Found (invalid endpoints)
- **500**: Internal Server Error (database errors, unexpected errors)

## Security Features
- **CORS**: Configured for cross-origin requests
- **Helmet**: Security headers
- **Input Validation**: Comprehensive validation with express-validator
- **Data Sanitization**: Trim and validate all inputs

## Database Indexes
- `appointmentDate + timeSlot`: For efficient duplicate checking and availability queries

## Logging
- Server startup and shutdown logs
- Database connection status
- Error logging for debugging

## Production Considerations
- Use environment variables for sensitive data
- Implement rate limiting for API endpoints
- Add authentication/authorization if needed
- Use PM2 or similar for process management
- Configure MongoDB connection pooling
- Add comprehensive logging and monitoring