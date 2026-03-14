user_states = {}  # {user_id: состояние}

def get_user_state(user_id):
    return user_states.get(user_id, "main")

def set_user_state(user_id, state):
    user_states[user_id] = state

def clear_user_state(user_id):
    user_states.pop(user_id, None)
