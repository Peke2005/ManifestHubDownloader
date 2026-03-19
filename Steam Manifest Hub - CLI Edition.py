#!/usr/bin/env python3
import os
import sys
import requests
import re
import time

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def set_title(title):
    """Set terminal title."""
    if os.name == 'nt':
        os.system(f'title {title}')
    else:
        print(f'\033]0;{title}\007', end='')

def print_red(text):
    """Print text in red."""
    print(f'\033[91m{text}\033[0m', end='')

def print_green(text):
    """Print text in green."""
    print(f'\033[92m{text}\033[0m', end='')

def get_single_key():
    """Get a single keypress without requiring Enter."""
    if os.name == 'nt':
        import msvcrt
        return msvcrt.getch().decode('utf-8').upper()
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1).upper()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

def input_red_single(prompt):
    """Display input prompt in red and get single keypress."""
    print_red(prompt)
    return get_single_key()

def input_green(prompt):
    """Display input prompt in green and return user input in green."""
    print_green(prompt)
    sys.stdout.write('\033[92m')
    user_input = input()
    sys.stdout.write('\033[0m')
    return user_input

def disclaimer():
    """Display disclaimer and get user acceptance."""
    clear_screen()
    print()
    print_red('================================')
    print()
    print_red('[DISCLAIMER]')
    print()
    print_red('================================')
    print()
    print()
    print_red('This script is for informational purposes only.')
    print()
    print_red('We are not responsible for any consequences that may arise from using the provided data.')
    print()
    print()
    
    print_red('Press Y to accept and continue, or N to exit: ')
    sys.stdout.flush()
    response = get_single_key()
    print()
    
    if response != 'Y':
        sys.exit(0)

def validate_appid(appid):
    """Validate that the input is a numeric AppID."""
    return bool(re.match(r'^[0-9]+$', appid))

def check_manifest(appid):
    """Check if manifest exists in the GitHub repository."""
    url = f'https://api.github.com/repos/SteamAutoCracks/ManifestHub/branches/{appid}'
    
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_game_metadata(appid):
    """Fetch game title and LAN support details from Steam's appdetails API."""
    url = 'https://store.steampowered.com/api/appdetails'
    params = {
        'appids': appid,
        'filters': 'basic,categories',
        'l': 'english',
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return None

    app_data = payload.get(str(appid))
    if not isinstance(app_data, dict) or not app_data.get('success'):
        return None

    data = app_data.get('data')
    if not isinstance(data, dict):
        return None

    name = data.get('name')
    if isinstance(name, str):
        name = name.strip() or None
    else:
        name = None

    lan_categories = []
    categories = data.get('categories')
    if isinstance(categories, list):
        for category in categories:
            if not isinstance(category, dict):
                continue

            description = category.get('description')
            if isinstance(description, str) and description.startswith('LAN '):
                lan_categories.append(description)

    return {
        'name': name,
        'lan_categories': lan_categories,
    }

def main():
    """Main program loop."""
    set_title('Steam Manifest Hub - CLI Edition')
    disclaimer()
    
    while True:
        clear_screen()
        print()
        print_green('================================')
        print()
        print_green('Steam Manifest Hub - CLI Edition')
        print()
        print_green('================================')
        print()
        print()
        
        while True:
            appid = input_green('Enter your desired Steam AppID: ').strip()
            
            if not appid:
                continue
            
            if not validate_appid(appid):
                print()
                print_green('[ERROR] Please enter numbers only.')
                print()
                time.sleep(3)
                break
            
            break
        
        if not validate_appid(appid):
            continue
        
        print()
        print_green('> Initiating manifest check for Steam AppID: ' + appid)
        print()
        print_green('> Searching database...')
        print()
        
        if not check_manifest(appid):
            print_green('> Manifest not found.')
            print()
            print()
            print_green('No manifests were found for this Steam application, at least for now...')
            print()
            print()
            input_green('Press ENTER to continue...')
            continue
        
        game_metadata = get_game_metadata(appid)

        print_green('> Manifest found in database!')
        print()
        if game_metadata and game_metadata.get('name'):
            print_green('> Game identified: ' + game_metadata['name'])
        else:
            print_green('> Game title unavailable.')
        print()
        if game_metadata is None:
            print_green('> LAN support unavailable.')
        else:
            lan_categories = game_metadata.get('lan_categories', [])
            if lan_categories:
                print_green('> LAN support: Yes (' + ', '.join(lan_categories) + ')')
            else:
                print_green('> LAN support: No')
        print()
        print_green('> Preparing download link...')
        print()
        print_green('> Ready for download.')
        print()
        print()
        print_green('Download link:')
        print()
        print_green(f'https://codeload.github.com/SteamAutoCracks/ManifestHub/zip/refs/heads/{appid}')
        print()
        print()
        print_green('The manifests are downloaded from the ManifestHub Database.')
        print()
        print_green('Show them support on GitHub: https://github.com/SteamAutoCracks/ManifestHub/')
        print()
        print()
        input_green('Press ENTER to continue...')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print('Exiting...')
        sys.exit(0)
