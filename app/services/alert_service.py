# app/services/alert_service.py
class AlertService:
    def check_low_stock(self):
        items = Item.query.filter(
            Item.quantity <= Item.minimum_quantity
        ).all()

        for item in items:
            self._send_low_stock_alert(item)

    def check_expiring_items(self):
        threshold = datetime.utcnow() + timedelta(days=30)
        items = Item.query.filter(
            Item.expiry_date <= threshold
        ).all()

        for item in items:
            self._send_expiry_alert(item)