"""
Sample Lambda function to use with Step Functions Task state.
Deploy this to test the 08-task-lambda.json state machine.
"""

import json
from datetime import datetime


def handler(event, context):
    """
    Process user action - demonstrates Lambda integration with Step Functions.

    Expected input:
    {
        "email": "user@example.com",
        "action": "register" | "update" | "delete"
    }
    """
    email = event.get('email')
    action = event.get('action', 'unknown')

    # Simulate processing
    result = {
        'email': email,
        'action': action,
        'processed_at': datetime.utcnow().isoformat(),
        'success': True
    }

    if action == 'register':
        result['message'] = f'User {email} registered successfully'
        result['user_id'] = 'usr_' + str(hash(email))[-8:]

    elif action == 'update':
        result['message'] = f'User {email} updated successfully'

    elif action == 'delete':
        result['message'] = f'User {email} deleted successfully'

    else:
        result['success'] = False
        result['message'] = f'Unknown action: {action}'

    return result
