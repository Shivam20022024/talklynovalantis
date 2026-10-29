import os
import hmac
import hashlib
from typing import Dict, Any, Optional
import razorpay


class RazorpayProvider:
    def __init__(self):
        self.key_id = os.environ.get("RAZORPAY_KEY_ID", "").strip()
        self.key_secret = os.environ.get("RAZORPAY_KEY_SECRET", "").strip()
        self.webhook_secret = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "").strip()
        self.client = razorpay.Client(auth=(self.key_id, self.key_secret)) if self.is_configured() else None

    def is_configured(self) -> bool:
        return bool(self.key_id and self.key_secret)

    def create_order(self, amount: float, currency: str = "INR", notes: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a Razorpay order for the given rupee amount. Unlike Cashfree's
        provider, this never returns a mock success when unconfigured - an
        unconfigured gateway must fail loudly, not silently hand out credit."""
        if not self.is_configured():
            raise RuntimeError("Razorpay is not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.")

        order = self.client.order.create({
            "amount": int(round(amount * 100)),  # Razorpay amounts are in paise
            "currency": currency,
            "notes": notes or {},
            "payment_capture": 1
        })
        return {
            "id": order.get("id"),
            "amount": order.get("amount"),
            "currency": order.get("currency"),
            "status": order.get("status"),
            "key_id": self.key_id
        }

    def verify_payment_signature(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
        """Verifies the signature Razorpay Checkout returns to the browser on
        success. This must pass before crediting a wallet from the
        verify-payment endpoint - it's what stops a user from forging a fake
        success response client-side."""
        if not self.is_configured():
            return False
        payload = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected_signature = hmac.new(
            self.key_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, razorpay_signature)

    def verify_webhook_signature(self, payload_body: str, signature: str) -> bool:
        """Verifies Razorpay's async webhook callback, which uses a separate
        secret (RAZORPAY_WEBHOOK_SECRET, configured in the Razorpay dashboard)
        from the API key secret used for order/payment signatures above."""
        if not self.webhook_secret:
            return False
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload_body.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, signature)


razorpay_provider = RazorpayProvider()
