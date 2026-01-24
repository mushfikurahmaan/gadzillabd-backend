"""
Utility functions for order-related operations.
"""
import logging
from decimal import Decimal
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_order_notification_email(order):
    """
    Send email notification to admin when a new order is placed.
    
    Args:
        order: Order instance with related items loaded
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Check if admin email is configured
    admin_email = getattr(settings, 'ADMIN_EMAIL', '').strip()
    if not admin_email:
        logger.warning("ADMIN_EMAIL not configured. Skipping order notification email.")
        return False
    
    # Check if email backend is configured (not console backend)
    email_backend = getattr(settings, 'EMAIL_BACKEND', '')
    if 'console' in email_backend.lower():
        logger.info(f"Email backend is console. Order notification would be sent to: {admin_email}")
        # Still proceed to render and log the email content
    
    try:
        # Fetch order items if not already loaded
        if not hasattr(order, '_prefetched_objects_cache') or 'items' not in order._prefetched_objects_cache:
            order_items = list(order.items.select_related('product').all())
        else:
            order_items = list(order.items.all())
        
        # Calculate shipping cost based on delivery area
        shipping_cost = Decimal('0.00')
        if order.delivery_area == 'inside':
            shipping_cost = Decimal('40.00')
        elif order.delivery_area == 'outside':
            shipping_cost = Decimal('150.00')
        
        # Calculate subtotal (total - shipping)
        subtotal = order.total - shipping_cost
        
        # Prepare order items data for template
        items_data = []
        for item in order_items:
            items_data.append({
                'name': item.product.name,
                'quantity': item.quantity,
                'size': item.size if item.size else '',
                'price': float(item.price),
                'subtotal': float(item.price * item.quantity),
            })
        
        # Format order date
        order_date = timezone.localtime(order.created_at).strftime('%B %d, %Y at %I:%M %p')
        
        # Prepare email context
        context = {
            'order_id': str(order.id),
            'order_id_short': str(order.id)[:8],
            'order_date': order_date,
            'order_status': order.get_status_display(),
            'customer_name': order.shipping_name or 'N/A',
            'customer_phone': order.phone or '',
            'customer_email': order.email or '',
            'shipping_address': order.shipping_address or 'N/A',
            'delivery_area': order.get_delivery_area_display() if order.delivery_area else 'N/A',
            'order_items': items_data,
            'subtotal': float(subtotal),
            'shipping_cost': float(shipping_cost) if shipping_cost > 0 else None,
            'total': float(order.total),
        }
        
        # Render email template
        html_message = render_to_string('orders/order_notification_email.html', context)
        
        # Create plain text version
        plain_message = f"""
New Order Received

Order ID: {context['order_id']}
Date: {context['order_date']}
Status: {context['order_status']}

Customer Information:
Name: {context['customer_name']}
Phone: {context['customer_phone']}
Email: {context['customer_email']}

Shipping Details:
Address: {context['shipping_address']}
Delivery Area: {context['delivery_area']}

Order Items:
"""
        for item in items_data:
            plain_message += f"- {item['name']} (Qty: {item['quantity']}"
            if item['size']:
                plain_message += f", Size: {item['size']}"
            plain_message += f") - ৳{item['subtotal']}\n"
        
        plain_message += f"""
Subtotal: ৳{context['subtotal']}
"""
        if context['shipping_cost']:
            plain_message += f"Shipping: ৳{context['shipping_cost']}\n"
        plain_message += f"Total: ৳{context['total']}"
        
        # Send email
        subject = f"New Order #{context['order_id_short']} - {context['customer_name']}"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[admin_email],
            html_message=html_message,
            fail_silently=False,  # We'll catch exceptions ourselves
        )
        
        logger.info(f"Order notification email sent successfully for order {order.id} to {admin_email}")
        return True
        
    except Exception as e:
        # Log the error but don't fail the order creation
        logger.error(f"Failed to send order notification email for order {order.id}: {str(e)}", exc_info=True)
        return False
