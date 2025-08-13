const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Product name is required'],
    trim: true,
    minlength: [2, 'Product name must be at least 2 characters'],
    maxlength: [100, 'Product name cannot exceed 100 characters']
  },
  description: {
    type: String,
    trim: true,
    maxlength: [500, 'Description cannot exceed 500 characters']
  },
  price: {
    type: Number,
    required: [true, 'Price is required'],
    min: [0, 'Price must be a positive number']
  },
  category: {
    type: String,
    required: [true, 'Category is required'],
    enum: {
      values: ['electronics', 'clothing', 'books', 'home', 'sports', 'other'],
      message: 'Category must be one of: electronics, clothing, books, home, sports, other'
    }
  },
  inStock: {
    type: Boolean,
    default: true
  },
  quantity: {
    type: Number,
    min: [0, 'Quantity cannot be negative'],
    default: 0
  },
  tags: [{
    type: String,
    trim: true
  }],
  images: [{
    url: String,
    alt: String
  }],
  specifications: {
    type: Map,
    of: String
  },
  ratings: {
    average: {
      type: Number,
      min: 0,
      max: 5,
      default: 0
    },
    count: {
      type: Number,
      min: 0,
      default: 0
    }
  }
}, {
  timestamps: true
});

// Indexes for better query performance
productSchema.index({ name: 'text', description: 'text' });
productSchema.index({ category: 1 });
productSchema.index({ price: 1 });
productSchema.index({ inStock: 1 });
productSchema.index({ createdAt: -1 });

// Virtual for formatted price
productSchema.virtual('formattedPrice').get(function() {
  return `$${this.price.toFixed(2)}`;
});

// Virtual for stock status
productSchema.virtual('stockStatus').get(function() {
  if (!this.inStock) return 'Out of Stock';
  if (this.quantity === 0) return 'Out of Stock';
  if (this.quantity < 10) return 'Low Stock';
  return 'In Stock';
});

// Method to update stock
productSchema.methods.updateStock = function(quantity) {
  this.quantity = Math.max(0, quantity);
  this.inStock = this.quantity > 0;
  return this.save();
};

// Static method to find by category
productSchema.statics.findByCategory = function(category) {
  return this.find({ category, inStock: true });
};

// Static method to find products in price range
productSchema.statics.findInPriceRange = function(min, max) {
  return this.find({ 
    price: { $gte: min, $lte: max },
    inStock: true 
  });
};

// Pre-save middleware to update inStock based on quantity
productSchema.pre('save', function(next) {
  if (this.quantity === 0) {
    this.inStock = false;
  }
  next();
});

module.exports = mongoose.model('Product', productSchema);
