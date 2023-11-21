import sys, subprocess

if sys.prefix == sys.base_prefix:
    print('Activate your virtual environment')
    sys.exit()

if len(sys.argv) < 2:
    print('Auto Reloading Disabled')
    subprocess.call(['uvicorn', 'server:app'])
else:
    if sys.argv[1] == '--reload' or sys.argv[1] == '-r':
        print('Auto Reloading Enabled')
        subprocess.call(['uvicorn', 'server:app', '--reload'])

    elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
        print("""
        --help, -h : Help Menu
        --reload, -r : Enable automatic reload on code change
        """)
    else:
        print('Unknown Command: %s' % sys.argv[1])
        print('Use "--help" for more information.')
        sys.exit()
