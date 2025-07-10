const mongoose = require('mongoose');

const orderSchema = new mongoose.Schema({
  productId: mongoose.Schema.Types.ObjectId,
  customerEmail: String,
  paymentStatus: String, 
  createdAt: { type: Date, default: Date.now },
});

module.exports = mongoose.model('Order', orderSchema);
