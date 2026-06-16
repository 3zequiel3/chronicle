# Reglas de Negocio — Pagos

- **RN-PAGOS-01**: el cupón no se aplica dos veces. `[code · src/payments/rules.ts#validateCoupon ~L42]`
- **RN-PAGOS-02**: el pago se confirma antes de despachar. `[code · src/payments/confirm.ts#confirm]`
- **RN-PAGOS-03**: (posible) reintento idempotente. `[code · src/payments/ghost.ts#phantom]`
