from quickfix.audit import log_event
def on_session_creation(login_manager):
    log_event(                   #---here it is calling from the audit.py
        "Session",   
        login_manager.user,
        "Login"
    )

def on_logout(login_manager):
    log_event(
        "Session",
        login_manager.user,
        "Logout"
    )
