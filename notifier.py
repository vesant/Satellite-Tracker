from plyer import notification

def send_notification(title, message):
    """
    Send a desktop notification with fallback to terminal print.
    
    Args:
        title: Notification title
        message: Notification message
    """
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=10
        )
    except Exception as e:
        # Fallback to terminal if notification fails
        print(f"\n📢 Notification: {title}")
        print(f"   {message}")
        print(f"   (Desktop notification failed: {e})")
