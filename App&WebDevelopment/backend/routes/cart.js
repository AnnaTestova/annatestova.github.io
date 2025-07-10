const express = require('express');
const router = express.Router();
const Cart = require('../models/Cart');
const Product = require('../models/Product');

router.get('/', async (req, res) => {
    try {
      const cart = await Cart.findOne().populate('items.product');
      console.log('Cart found:', cart);
      res.json(cart || { items: [] });
    } catch (err) {
      console.error(err);
      res.status(500).json({ error: err.message });
    }
  });
  

router.post('/add', async (req, res) => {
  const { productId, quantity } = req.body;
  try {
    let cart = await Cart.findOne();
    if (!cart) cart = new Cart({ items: [] });

    const itemIndex = cart.items.findIndex(item => item.product.toString() === productId);
    if (itemIndex > -1) {
      cart.items[itemIndex].quantity += quantity;
    } else {
      cart.items.push({ product: productId, quantity });
    }
    await cart.save();
    res.json(cart.items);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post('/remove', async (req, res) => {
  const { productId } = req.body;
  try {
    const cart = await Cart.findOne();
    if (!cart) return res.status(404).json({ error: 'Cart not found' });

    cart.items = cart.items.filter(item => item.product.toString() !== productId);
    await cart.save();
    res.json(cart.items);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
