const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const { body, validationResult } = require('express-validator');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const Appointment = require('./models/Appointment');

const app = express();
const PORT = process.env.PORT || 8001;

// Middleware
app.use(helmet());
app.use(cors({
  origin: '*',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// MongoDB connection
const mongoUrl = process.env.MONGO_URL || 'mongodb://localhost:27017';
const dbName = process.env.DB_NAME || 'test_database';

mongoose.connect(`${mongoUrl}/${dbName}`)
  .then(() => {
    console.log('✅ Connected to MongoDB successfully');
  })
  .catch((error) => {
    console.error('❌ MongoDB connection error:', error);
    process.exit(1);
  });

// Helper function to validate appointment slot
const validateAppointmentSlot = (appointmentDate, timeSlot) => {
  const date = new Date(appointmentDate);
  const dayOfWeek = date.getDay(); // Sunday is 0, Monday is 1, etc.
  
  // Sunday - no appointments allowed
  if (dayOfWeek === 0) {
    return {
      isValid: false,
      message: 'Appointments are not available on Sundays'
    };
  }
  
  // Saturday - only until 1:00 PM
  if (dayOfWeek === 6) {
    const afternoonSlots = ['2:00–3:00 PM', '3:00–4:00 PM'];
    if (afternoonSlots.includes(timeSlot)) {
      return {
        isValid: false,
        message: 'On Saturdays, appointments are only available until 1:00 PM'
      };
    }
  }
  
  // Check for past dates
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  date.setHours(0, 0, 0, 0);
  
  if (date < today) {
    return {
      isValid: false,
      message: 'Cannot book appointments for past dates'
    };
  }
  
  return { isValid: true };
};

// Validation middleware
const appointmentValidation = [
  body('name')
    .trim()
    .notEmpty()
    .withMessage('Name is required')
    .isLength({ min: 2, max: 100 })
    .withMessage('Name must be between 2 and 100 characters'),
  
  body('sex')
    .notEmpty()
    .withMessage('Sex is required')
    .isIn(['Male', 'Female', 'Other'])
    .withMessage('Sex must be Male, Female, or Other'),
  
  body('age')
    .isInt({ min: 0, max: 150 })
    .withMessage('Age must be a number between 0 and 150'),
  
  body('complaint')
    .trim()
    .notEmpty()
    .withMessage('Complaint is required')
    .isLength({ min: 5, max: 500 })
    .withMessage('Complaint must be between 5 and 500 characters'),
  
  body('appointmentDate')
    .isISO8601()
    .toDate()
    .withMessage('Valid appointment date is required'),
  
  body('timeSlot')
    .notEmpty()
    .withMessage('Time slot is required')
    .isIn([
      '9:00–10:00 AM',
      '10:00–11:00 AM',
      '11:00–12:00 PM',
      '12:00–1:00 PM',
      '2:00–3:00 PM',
      '3:00–4:00 PM'
    ])
    .withMessage('Invalid time slot selected')
];

// Routes

// Health check
app.get('/api/', (req, res) => {
  res.json({ message: 'Dental Clinic Appointment System API' });
});

// Create appointment
app.post('/api/appointments', appointmentValidation, async (req, res) => {
  try {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        detail: 'Validation failed',
        errors: errors.array()
      });
    }

    const { name, sex, age, complaint, appointmentDate, timeSlot } = req.body;

    // Validate appointment slot availability
    const slotValidation = validateAppointmentSlot(appointmentDate, timeSlot);
    if (!slotValidation.isValid) {
      return res.status(400).json({
        detail: slotValidation.message
      });
    }

    // Check if slot is already booked
    const existingAppointment = await Appointment.findOne({
      appointmentDate: new Date(appointmentDate),
      timeSlot: timeSlot
    });

    if (existingAppointment) {
      return res.status(400).json({
        detail: 'This time slot is already booked for the selected date'
      });
    }

    // Create new appointment
    const appointment = new Appointment({
      id: uuidv4(),
      name,
      sex,
      age,
      complaint,
      appointmentDate: new Date(appointmentDate),
      timeSlot
    });

    await appointment.save();

    // Return appointment with date as ISO string for consistency
    const appointmentResponse = appointment.toObject();
    appointmentResponse.appointment_date = appointmentResponse.appointmentDate.toISOString().split('T')[0];
    appointmentResponse.time_slot = appointmentResponse.timeSlot;
    appointmentResponse.created_at = appointmentResponse.createdAt;

    res.status(200).json(appointmentResponse);

  } catch (error) {
    console.error('Error creating appointment:', error);
    res.status(500).json({
      detail: `Failed to create appointment: ${error.message}`
    });
  }
});

// Get all appointments
app.get('/api/appointments', async (req, res) => {
  try {
    const appointments = await Appointment.find()
      .sort({ appointmentDate: 1 })
      .limit(1000);

    // Transform response to match frontend expectations
    const transformedAppointments = appointments.map(appointment => {
      const appointmentObj = appointment.toObject();
      return {
        ...appointmentObj,
        appointment_date: appointmentObj.appointmentDate.toISOString().split('T')[0],
        time_slot: appointmentObj.timeSlot,
        created_at: appointmentObj.createdAt
      };
    });

    res.json(transformedAppointments);

  } catch (error) {
    console.error('Error fetching appointments:', error);
    res.status(500).json({
      detail: `Failed to fetch appointments: ${error.message}`
    });
  }
});

// Get available slots for a specific date
app.get('/api/appointments/available-slots', async (req, res) => {
  try {
    const { appointment_date } = req.query;

    if (!appointment_date) {
      return res.status(400).json({
        detail: 'appointment_date query parameter is required'
      });
    }

    const targetDate = new Date(appointment_date);
    const dayOfWeek = targetDate.getDay(); // Sunday is 0

    // All available slots
    const allSlots = [
      '9:00–10:00 AM',
      '10:00–11:00 AM',
      '11:00–12:00 PM',
      '12:00–1:00 PM',
      '2:00–3:00 PM',
      '3:00–4:00 PM'
    ];

    // Sunday - no slots
    if (dayOfWeek === 0) {
      return res.json({
        available_slots: [],
        message: 'No appointments available on Sundays'
      });
    }

    // Saturday - only morning slots
    let availableSlots = allSlots;
    if (dayOfWeek === 6) {
      availableSlots = [
        '9:00–10:00 AM',
        '10:00–11:00 AM',
        '11:00–12:00 PM',
        '12:00–1:00 PM'
      ];
    }

    // Get booked slots for the date
    const bookedAppointments = await Appointment.find({
      appointmentDate: targetDate
    });

    const bookedSlots = bookedAppointments.map(appointment => appointment.timeSlot);
    const finalAvailableSlots = availableSlots.filter(slot => !bookedSlots.includes(slot));

    res.json({
      available_slots: finalAvailableSlots
    });

  } catch (error) {
    console.error('Error fetching available slots:', error);
    res.status(500).json({
      detail: `Failed to fetch available slots: ${error.message}`
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  res.status(500).json({
    detail: 'Internal server error'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    detail: 'Route not found'
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Server running on http://0.0.0.0:${PORT}`);
  console.log(`📋 API endpoints available at http://0.0.0.0:${PORT}/api/`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  mongoose.connection.close(() => {
    console.log('MongoDB connection closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  mongoose.connection.close(() => {
    console.log('MongoDB connection closed');
    process.exit(0);
  });
});