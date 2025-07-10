const express = require('express');
const router = express.Router();
const Product = require('../models/Product');

router.get('/add-product', (req, res) => {
  res.send(`
    <form method="POST" action="/admin/add-product" style="display:flex;flex-direction:column;gap:8px;width:300px">
      <input name="name" placeholder="Product Name" required />
      <input name="price" type="number" step="0.01" placeholder="Price" required />
      <input name="category" placeholder="Category" />
      <input name="image" placeholder="Image URL" />
      <textarea name="description" placeholder="Description"></textarea>
      <button type="submit">Add Product</button>
    </form>
  `);
});

router.post('/add-product', express.json(), async (req, res) => {
  const { name, price, description, category, image } = req.body;
  try {
    const newProduct = new Product({ name, price, description, category, image });
    await newProduct.save();
    res.status(201).json({ message: 'Product added!' });
  } catch (err) {
    res.status(500).json({ error: 'Error adding product: ' + err.message });
  }
});

module.exports = router;
