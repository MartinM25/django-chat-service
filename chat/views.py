from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Message
import json

@csrf_exempt  # Use with caution; adjust security as needed
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = Message.objects.create(
                sender=data['sender'],
                recipient=data['recipient'],
                content=data['content'],
            )
            return JsonResponse({'status': 'success', 'message_id': message.id})
        except (KeyError, json.JSONDecodeError) as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

def get_messages(request, recipient):
    messages = Message.objects.filter(recipient=recipient)
    return JsonResponse({'messages': list(messages.values())})

