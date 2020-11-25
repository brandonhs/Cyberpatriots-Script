import subprocess, glob, os, platform, sys, inspect


''' COMMANDS '''

'''
(music) - .mp3, .wav, .wma, .aac
(movie/video) - .mp4, .mov, .avi '''
RESTRICTED_EXT = ['mp3', 'wav', 'wma', 'aac', 'mp4', 'mov', 'avi']
SYSTEM_OS = platform.system()
DEF_OUTPUT = 'Cannot run given command \'{cmd}\' using system: \'' + SYSTEM_OS + '\''

LIGHTDM_NO_GUEST = '''
    [SeatDefaults]
    greeter-session=unity-greeter
    allow-guest=false
'''

AUTO_LOGIN_EXE_PATH = '/AutoLogon/AutoLogon{os_arch}.exe'


''' MISC '''
def check64():
    ''' Check if os is 64 bit. Returns '64' if true and '' if false '''
    return '64' if platform.machine().endswith('64') else ''

def windows_request_admin():
    ''' modified from https://stackoverflow.com/questions/130763/request-uac-elevation-from-within-a-python-script '''
    if SYSTEM_OS.lower() != 'windows':
        print('Unable to request windows admin (System is not Windows)')
        return
    import win32com.shell.shell as shell
    ASADMIN = 'asadmin'

    if sys.argv[-1] != ASADMIN:
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:] + [ASADMIN])
        shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=params)
        sys.exit(0)

def run_command(command: str, ip=None):
    ''' Run command and return output. Answer from https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output. '''
    result = subprocess.run(command.split(' '), stdout=subprocess.PIPE, input=ip)
    return result.stdout.decode('utf-8')


''' Users and Groups '''
def set_password(user: str, password=''):
    ''' set user password '''
    output = DEF_OUTPUT.format(cmd='set_password')
    if SYSTEM_OS.lower() == 'linux':
        output = run_command('sudo passwd {user}'.format(user=user), password)
    elif SYSTEM_OS.lower() == 'windows':
        output = run_command('net user {user} {password}'.format(user=user, password=password))
    print(output)

def add_user(user: str, password=''):
    ''' Add user "user" '''
    output = DEF_OUTPUT.format(cmd='add_user')
    if SYSTEM_OS.lower() == 'linux':
        output = run_command('sudo useradd {user} -m -s /bin/bash'.format(user=user))
        if password != '':
            output += '\n' + run_command('sudo passwd {user}'.format(user=user), password)
    elif SYSTEM_OS.lower() == 'windows':
        output = run_command('net user /add {user} {password}'.format(user=user, password=password))
    print(output)

def remove_user(user: str):
    ''' Remove user "user" '''
    output = DEF_OUTPUT.format(cmd='remove_user')
    if SYSTEM_OS.lower() == 'linux':
        output = run_command('sudo userdel -r {user}'.format(user=user))
    print(output)

def add_to_group(user: str, group: str):
    ''' Move user to given group '''
    output = DEF_OUTPUT.format(cmd='add_to_group')
    if SYSTEM_OS.lower() == 'linux':
        output = run_command('sudo gpasswd -a {user} {group}'.format(user=user, group=group))
    elif SYSTEM_OS.lower() == 'windows':
        output = run_command('net localgroup {group} {user} /add'.format(group=group, user=user))
    print(output)

def remove_from_group(user: str, group: str):
    ''' Remove user from given group '''
    output = DEF_OUTPUT.format(cmd='remove_from_group')
    if SYSTEM_OS.lower() == 'linux':
        output = run_command('sudo gpasswd -d {user} {group}'.format(user=user, group=group))
    elif SYSTEM_OS.lower() == 'windows':
        output = run_command('net localgroup {group} {user} /delete'.format(group=group, user=user))
    print(output)

def set_admin(user: str):
    ''' Add user to the admin group '''
    group = ''
    if SYSTEM_OS.lower() == 'linux':
        group = 'adm'
    elif SYSTEM_OS.lower() == 'windows':
        group = 'Administrator'
    add_to_group(user=user, group=group)

def remove_admin(user: str):
    ''' Remove user from the admin group '''
    group = ''
    if SYSTEM_OS.lower() == 'linux':
        group = 'adm'
    elif SYSTEM_OS.lower() == 'windows':
        group = 'Administrator'
    remove_from_group(user=user, group=group)

def disable_guest():
    ''' Disable guest user. Only for linux based operating systems '''
    output = DEF_OUTPUT.format(cmd='disable_guest')
    if SYSTEM_OS.lower() == 'linux':
        run_command('echo "{contents}"/etc/lightdm/lightdm.conf.d/50-no-guest.conf'.format(contents=LIGHTDM_NO_GUEST))
    print(output)

def set_auto_login():
    ''' Enable or disable autologin. Windows only '''
    output = DEF_OUTPUT.format(cmd='set_auto_login')
    if SYSTEM_OS.lower() is 'windows':
        output = run_command('netplwiz')
    print(output)


''' Files (Windows Compatible) '''
def search_restricted(root_dir):
    ''' Search from root_dir for restricted file types. '''
    restricted_files = []
    for ext in RESTRICTED_EXT:
        directories, files = search_from(root_dir=root_dir, ext=ext)
        restricted_files = restricted_files + files
    return restricted_files

def remove_restricted(root_dir):
    ''' Delete all restricted files. May require sudo permissions to run. '''
    restricted_files = search_restricted(root_dir=root_dir)
    remove_files(restricted_files)

def search_directory(dir: str, ext: str):
    ''' Search directory for *.ext. Returns list of paths. ** Depreciated as of v1.1, use search_from instead '''
    ext_format = "*.{ext}".format(ext=ext)
    os.chdir(dir)
    return glob.glob(ext_format)

def search_from(root_dir: str, ext: str):
    ''' Run a search from root_dir for *.ext. Returns touple: list of directories in JSON format: { dir: [files_in_dir.ext] }, raw list of paths '''
    directories = []
    ext_format = ".{ext}".format(ext=ext)
    for root, dirs, f in os.walk(root_dir): # loop through all directories starting with root
        files = [] # list of files which end with *.ext in current directory
        for file in f:
            if file.lower().endswith(ext_format):
                files.append(file)
        if len(files) > 0:
            directories.append({
                root: files
            })
    raw_list = []
    for dir in directories:
        for root in dir: # will only go once
            files = dir[root]
            for file in files:
                raw_list.append(root + '/' + file)

    return directories, raw_list

def remove_files(files):
    ''' delete all files from the files list of paths '''
    for file in files:
        os.remove(file)
