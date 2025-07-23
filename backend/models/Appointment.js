const mongoose = require('mongoose');

const appointmentSchema = new mongoose.Schema({
  id: {
    type: String,
    required: true,
    unique: true
  },
  name: {
    type: String,
    required: true,
    trim: true,
    minlength: 2,
    maxlength: 100
  },
  sex: {
    type: String,
    required: true,
    enum: ['Male', 'Female', 'Other']
  },
  age: {
    type: Number,
    required: true,
    min: 0,
    max: 150
  },
  complaint: {
    type: String,
    required: true,
    trim: true,
    minlength: 5,
    maxlength: 500
  },
  appointmentDate: {
    type: Date,
    required: true
  },
  timeSlot: {
    type: String,
    required: true,
    enum: [
      '9:00–10:00 AM',
      '10:00–11:00 AM',
      '11:00–12:00 PM',
      '12:00–1:00 PM',
      '2:00–3:00 PM',
      '3:00–4:00 PM'
    ]
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  status: {
    type: String,
    default: 'scheduled',
    enum: ['scheduled', 'confirmed', 'cancelled', 'completed']
  }
}, {
  timestamps: true
});

// Index for efficient querying
appointmentSchema.index({ appointmentDate: 1, timeSlot: 1 });

module.exports = mongoose.model('Appointment', appointmentSchema);