const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Name is required'],
    trim: true,
    maxlength: [100, 'Name cannot exceed 100 characters']
  },
  phone: {
    type: String,
    required: [true, 'Phone number is required'],
    unique: true,
    trim: true,
    match: [/^\+?[\d\s\-\(\)]+$/, 'Please enter a valid phone number']
  },
  email: {
    type: String,
    required: [true, 'Email is required'],
    unique: true,
    lowercase: true,
    trim: true,
    match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Please enter a valid email']
  },
  password: {
    type: String,
    required: [true, 'Password is required'],
    minlength: [6, 'Password must be at least 6 characters long'],
    select: false // Don't include password in queries by default
  },
  isActive: {
    type: Boolean,
    default: true
  },
  role: {
    type: String,
    enum: ['user', 'admin'],
    default: 'user'
  },
  profilePicture: {
    type: String,
    default: null
  },
  cognitoId: {
    type: String,
    sparse: true, // Allow null values but enforce uniqueness when present
    unique: true
  },
  lastLogin: {
    type: Date,
    default: null
  },
  emailVerified: {
    type: Boolean,
    default: false
  },
  phoneVerified: {
    type: Boolean,
    default: false
  },
  preferences: {
    notifications: {
      email: { type: Boolean, default: true },
      sms: { type: Boolean, default: false },
      push: { type: Boolean, default: true }
    },
    language: {
      type: String,
      default: 'en',
      enum: ['en', 'es', 'fr', 'de', 'it']
    },
    timezone: {
      type: String,
      default: 'UTC'
    }
  },
  metadata: {
    registrationSource: {
      type: String,
      enum: ['web', 'mobile', 'api'],
      default: 'api'
    },
    ipAddress: String,
    userAgent: String
  }
}, {
  timestamps: true, // Adds createdAt and updatedAt fields
  versionKey: false // Removes __v field
});

// Indexes for better query performance
userSchema.index({ email: 1 });
userSchema.index({ phone: 1 });
userSchema.index({ cognitoId: 1 });
userSchema.index({ isActive: 1 });
userSchema.index({ createdAt: -1 });

// Virtual for user's full profile URL
userSchema.virtual('profileUrl').get(function() {
  if (this.profilePicture) {
    return process.env.AWS_S3_BUCKET_URL + '/' + this.profilePicture;
  }
  return null;
});

// Virtual for user's display name
userSchema.virtual('displayName').get(function() {
  return this.name || this.email.split('@')[0];
});

// Ensure virtual fields are serialized
userSchema.set('toJSON', {
  virtuals: true,
  transform: function(doc, ret) {
    delete ret.password;
    delete ret._id;
    delete ret.id;
    return ret;
  }
});

userSchema.set('toObject', {
  virtuals: true,
  transform: function(doc, ret) {
    delete ret.password;
    delete ret._id;
    return ret;
  }
});

// Pre-save middleware
userSchema.pre('save', function(next) {
  // Update the lastLogin field if it's a login operation
  if (this.isModified('lastLogin')) {
    this.lastLogin = new Date();
  }
  
  // Normalize phone number format
  if (this.isModified('phone')) {
    this.phone = this.phone.replace(/\s+/g, '').replace(/[^\d+]/g, '');
  }
  
  next();
});

// Instance methods
userSchema.methods.toSafeObject = function() {
  const userObject = this.toObject();
  delete userObject.password;
  return userObject;
};

userSchema.methods.updateLastLogin = function() {
  this.lastLogin = new Date();
  return this.save();
};

userSchema.methods.isValidPassword = async function(password) {
  const bcrypt = require('bcryptjs');
  return await bcrypt.compare(password, this.password);
};

// Static methods
userSchema.statics.findByEmail = function(email) {
  return this.findOne({ email: email.toLowerCase(), isActive: true });
};

userSchema.statics.findByPhone = function(phone) {
  const normalizedPhone = phone.replace(/\s+/g, '').replace(/[^\d+]/g, '');
  return this.findOne({ phone: normalizedPhone, isActive: true });
};

userSchema.statics.findByCognitoId = function(cognitoId) {
  return this.findOne({ cognitoId, isActive: true });
};

userSchema.statics.getActiveUsers = function(options = {}) {
  const { page = 1, limit = 10, sortBy = 'createdAt', sortOrder = -1, search } = options;
  
  const query = { isActive: true };
  
  if (search) {
    query.$or = [
      { name: { $regex: search, $options: 'i' } },
      { email: { $regex: search, $options: 'i' } },
      { phone: { $regex: search, $options: 'i' } }
    ];
  }
  
  return this.find(query)
    .sort({ [sortBy]: sortOrder })
    .skip((page - 1) * limit)
    .limit(limit)
    .select('-password');
};

userSchema.statics.getUserStats = async function() {
  const totalUsers = await this.countDocuments({ isActive: true });
  const newUsersToday = await this.countDocuments({
    isActive: true,
    createdAt: {
      $gte: new Date(new Date().setHours(0, 0, 0, 0))
    }
  });
  const verifiedUsers = await this.countDocuments({
    isActive: true,
    emailVerified: true
  });
  
  return {
    totalUsers,
    newUsersToday,
    verifiedUsers,
    verificationRate: totalUsers > 0 ? (verifiedUsers / totalUsers * 100).toFixed(2) : 0
  };
};

// Model
const User = mongoose.model('User', userSchema);

module.exports = User;
