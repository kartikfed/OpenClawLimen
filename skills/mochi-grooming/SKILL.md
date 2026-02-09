# Mochi Grooming Skill

Book grooming appointments for Mochi at Now You're Clean.

## Trigger Phrases
- "book mochi grooming"
- "schedule mochi's grooming"
- "grooming appointment for mochi"

## Default Configuration

### Dog Details
- **Dog:** Mochi (saved in account)
- **Weight:** S (0-20 Lbs)
- **Matting:** No
- **Coat Type:** Yes (2+ inches)
- **Husky/Samoyed/etc:** No

### Services (Default)
- **Package:** Bath Package ($89-99 base)
- **Add-ons:**
  - ✅ Nail Grinding ($10)
  - ✅ Berry Facial ($10)
  - ✅ Whitening Treatment ($10)

### Location
- **Default:** NYC Williamsburg (228 Berry St, Brooklyn, NY 11249)
- **Alternatives:** East Village, West Village

### Groomer Preference
- **Default:** First available (typically Tati)
- Can specify: Tati, Ilaina, Bruno

### Promo Code
- Check for active promos (Valentine's: VSPECIAL50 through Feb 14)

## How to Use

### Basic (uses all defaults):
```
"Book Mochi grooming"
```
→ Books Bath Package + default add-ons at Williamsburg, first available slot

### With Modifications:
```
"Book Mochi grooming without whitening treatment"
"Book Mochi grooming at East Village"
"Book Mochi grooming for Saturday"
"Book Mochi grooming with Tati"
```

### Full Custom:
```
"Book Mochi grooming: haircut package, add de-shedding, West Village, next Friday"
```

## Booking Flow

### Step 0: Use Isolated Browser
Use `profile="openclaw"` for all grooming bookings — keeps it separate from Kartik's Chrome.

```
browser action=start profile=openclaw
browser action=open profile=openclaw targetUrl="https://www.nowyoureclean.com/pages/groomer-booking"
```

### Step 1: Find Available Slots
1. Navigate to https://www.nowyoureclean.com/pages/groomer-booking
2. Verify logged in as Kartik (if not, go to /account and check)
3. Select package (Bath Package default)
4. Fill dog details, select add-ons
5. Browse available dates/times at preferred location

### Step 2: Confirm with Buttons (REQUIRED)

Before completing any booking, send a confirmation message with buttons:

```
🐕 **Mochi Grooming Appointment**

📍 **Location:** NYC Williamsburg (228 Berry St)
📅 **Date:** Saturday, Feb 15, 2026
🕐 **Time:** 2:30 PM
✂️ **Groomer:** Tati

**Services:**
• Bath Package ($89)
• Nail Grinding ($10)
• Berry Facial ($10)  
• Whitening Treatment ($10)

💰 **Total:** ~$119 + tax

Book this appointment?
```

Use inline buttons:
```json
{
  "buttons": [[
    {"text": "🐕 Confirm", "callback_data": "mochi_book_confirm"},
    {"text": "❌ Change", "callback_data": "mochi_book_change"}
  ]]
}
```

### Step 3: Handle Response

**If user clicks "🐕 Confirm"** (message matches `mochi_book_confirm`):
- Complete the booking on the website
- Apply promo code if active
- Accept terms, click Complete Booking
- Verify "Appointment Created Successfully"
- Send confirmation: "✅ Booked! Confirmation email sent to krishnankartik70@gmail.com"

**If user clicks "❌ Change"** (message matches `mochi_book_change`):
- Ask: "What would you like to change? (date/time, location, services, groomer)"
- Adjust based on response and show new confirmation with buttons

### Step 4: Completion
1. Apply promo code if active
2. Accept terms, Complete Booking
3. Verify "Appointment Created Successfully"
4. Report success with appointment details

## Account Details
- **Website:** nowyoureclean.com
- **Phone:** (332) 257-2376
- **Hours:** Mon-Fri 10am-1pm & 2pm-6:30pm, Sat-Sun 10am-6:30pm
- **Account:** krishnankartik70@gmail.com

## Notes
- Weekend appointments fill fast — book 1-2 weeks ahead
- Williamsburg location is closest to Kartik's apartment
- Payment card is saved on account
- Confirmation email goes to krishnankartik70@gmail.com
