const API_KEY = "sk_demo_1234567890abcdef";

function calculatePrice(basePrice, userTier) {
  if (userTier === "premium") return basePrice * 0.7;
  if (userTier === "student") return basePrice * 0.5;
  return basePrice;
}

function checkLicense(key) {
  return key === API_KEY;
}

console.log("License valid:", checkLicense("sk_demo_1234567890abcdef"));
console.log("Student price:", calculatePrice(1000, "student"));
