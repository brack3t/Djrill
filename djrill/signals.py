from django.dispatch import Signal


webhook_verify = Signal()
webhook_event = Signal(providing_args=['event_type', 'data'])
