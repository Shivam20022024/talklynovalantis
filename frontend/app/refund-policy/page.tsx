import LegalPageLayout from '@/components/legal/LegalPageLayout'

export default function RefundPolicyPage() {
  return (
    <LegalPageLayout title="Refund & Cancellation Policy" lastUpdated="October 29, 2026">
      <section>
        <h2>1. Free Trial Minutes</h2>
        <p>
          Every new account receives a limited number of free trial minutes to test live AI calling.
          Trial minutes have no cash value, cannot be refunded, exchanged, or transferred, and expire
          once consumed.
        </p>
      </section>

      <section>
        <h2>2. Wallet Top-Ups</h2>
        <p>
          Paid wallet balance is prepaid credit for AI calling minutes, billed per second of connected
          call time as it's used. Wallet credit does not expire.
        </p>
        <ul>
          <li>
            <strong>Unused balance:</strong> if you have not used any part of a top-up, you may request a
            full refund within 7 days of the payment by contacting support.
          </li>
          <li>
            <strong>Partially or fully used balance:</strong> amounts already consumed by completed calls
            are non-refundable, since the service (AI calling minutes) has already been delivered.
          </li>
          <li>
            <strong>Failed or duplicate payments:</strong> if Razorpay confirms a successful payment but
            your wallet was not credited due to a technical error, we will credit your wallet or issue a
            full refund within 7 business days of you reporting it.
          </li>
        </ul>
      </section>

      <section>
        <h2>3. Monthly Plans</h2>
        <p>
          Monthly plans (e.g. Pro Growth) can be cancelled at any time; cancellation takes effect at the
          end of the current billing period, and you retain access until then. We do not provide prorated
          refunds for the unused portion of a billing period you choose to cancel mid-cycle.
        </p>
      </section>

      <section>
        <h2>4. How to Request a Refund</h2>
        <p>
          Email <a href="mailto:info@novalantis.com">info@novalantis.com</a> with your account email and
          the transaction you're asking about. We aim to respond within 2 business days.
        </p>
      </section>

      <section>
        <h2>5. Refund Processing Time</h2>
        <p>
          Approved refunds are issued back to your original payment method via Razorpay and typically
          reflect in your account within 5–7 business days, depending on your bank or card issuer.
        </p>
      </section>

      <p className="text-xs italic text-muted-foreground">
        This page is a working draft and has not yet been reviewed by a qualified lawyer. It should be
        reviewed for legal accuracy before being relied on for compliance purposes.
      </p>
    </LegalPageLayout>
  )
}
