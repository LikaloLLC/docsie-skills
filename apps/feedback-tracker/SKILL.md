---
name: feedback-tracker
description: Log customer feedback, feature requests and complaints, triage them by sentiment and status, and show them on the feedback board.
---

# Feedback Tracker

## When to use
The user shares customer feedback: a feature request, a complaint, praise or a bug report from a call, an email, a ticket or a survey.

## Log feedback
1. List the rows with the data tool (`app__feedback-tracker__data`, action `list`). If the request is already there, update that row instead of adding a duplicate.
2. Add one row per distinct request (action `add`, table `feedback`):
   - `title`: what the customer wants or reports, in under 10 words.
   - `details`: the customer's words, shortened.
   - `customer`: the company name.
   - `sentiment`: Positive for praise, Neutral for requests and questions, Negative for complaints, bugs and churn risk.
   - `status`: New.
   - `area`: the product area, if clear.
   - `received`: the date, YYYY-MM-DD. Use today if unknown.
3. Open the board (`app__feedback-tracker__board`) with `highlight` set to the new row id.

## Rules
- Keep names, email addresses and phone numbers out of the title.
- Change a status only when the user asks.
- To review one status, open the board with `status`.
- Summarize only from rows in the table.
