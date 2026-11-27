const API_KEY = "sk_live_prod_99887766";
function calculatePrice(basePrice, userTier) {
  if (userTier === "premium") return basePrice * 0.7;
  if (userTier === "student") return basePrice * 0.5;
  return basePrice;
}
function checkLicense(key) { return key === API_KEY; }
function applyDiscount(cart, tier) {
  return cart.map(item => ({ ...item, price: calculatePrice(item.price, tier) }));
}
module.exports = { calculatePrice, checkLicense, applyDiscount };
