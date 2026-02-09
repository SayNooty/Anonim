import os

class Config:
    # Telegram
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8514338899:AAEQV5ERm5WaK-7rhtFIQpgt-A165B7rzJI")
    CHANNEL_ID = os.getenv("CHANNEL_ID", "@ваш_канал")
    
    # Payments
    PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN", "YOUR_STRIPE_PROVIDER_TOKEN")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_...")
    
    # Webhook
    WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://your-domain.com")
    WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 8443))
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your_secret_key")
    
    # Prices
    PRICE_PHOTO = 250  # $2.50
    PRICE_VIDEO = 1500  # $15.00