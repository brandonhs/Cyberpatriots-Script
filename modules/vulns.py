import commands

PASSWD = "U$c8_t_EBPH*$gs&ceQP"

def secure_password():
    users_list = commands.get_all_users()

    for user in users_list:
        commands.set_password(user=user, password=PASSWD)

def secure_windows10():
    ''' Secure windows vm '''
    if commands.SYSTEM_OS.lower() != 'windows':
        return

    commands.windows_request_admin()
    commands.remove_restricted('C://')
    secure_password()

def secure_windows_server():
    ''' Secure windows server '''
    if commands.SYSTEM_OS.lower() != 'windows':
        return
    secure_password()

def secure_linux():
    ''' Secure linux based vm '''
    if commands.SYSTEM_OS.lower() != 'linux':
        return
    secure_password()

    
