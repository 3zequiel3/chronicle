function validateCoupon(code) {
  // no aplica dos veces
  return seen.has(code) ? false : seen.add(code);
}
