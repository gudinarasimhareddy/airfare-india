from bs4 import BeautifulSoup

with open('frontend/booking.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

assert soup.find(id='checkoutStepper') is not None, 'checkoutStepper missing'
assert 'Trip Details' in soup.text
assert 'Travelers' in soup.text
assert 'Review' in soup.text
assert 'Payment' in soup.text
assert 'Confirmation' in soup.text
assert "🎉 You're all set! Your trip is confirmed." in soup.text
assert "Payment wasn't completed" in soup.text
assert "Don't worry — your booking has not been confirmed" in soup.text
assert "Try Again" in soup.text
assert "Change Payment Method" in soup.text
assert "✓ UPI ID format looks valid" in soup.text

print("ALL BOOKING DOM AND MICROCOPY CHECKS PASSED!")
