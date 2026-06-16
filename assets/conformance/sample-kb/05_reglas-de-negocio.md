# Reglas de Negocio — Pagos

Código único `RN-{DOMINIO}-NN` para trazabilidad.

- **RN-PAGOS-01** `[MVP]`: el cupón no se aplica dos veces. `[code · src/payments/rules.ts#validateCoupon ~L42]`
- **RN-PAGOS-02** `[MVP]`: el pago se confirma antes de despachar. `[code · src/payments/confirm.ts#confirm]`
- **RN-PAGOS-03** `[MVP]`: el reembolso expira a los 30 días.
