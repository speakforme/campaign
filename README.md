# Campaign management software for [Speak For Me](https://www.speakforme.in)

## Overview

This application can:
1. Process incoming HTTP requests sent by [postal](https://github.com/atech/postal), a self-hosted mail service.
2. Auto-respond to each request with an email sent via [Amazon SES](https://aws.amazon.com/ses/), a mail delivery service. The auto-responder can also be configured to respond in the language in which the email was received.
3. Maintain mailing lists (with unsubscribe).

## Tech

- Python 2.7
- Flask
- PostgreSQL
