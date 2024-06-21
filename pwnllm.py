import click, os, yaml
from utils import load_yaml_files, get_unique_keys, update_templates_choice
from menu import create_menu, get_available_attacks

def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)
    
config = load_config()
required_keys = config['required_keys']
unique_identifiers = config['unique_identifiers']
unique_identifiers_help = config['unique_identifiers_help']
learn_mode = False

@click.command()

def main():
    global learn_mode

    # Load templates
    templates_dir = 'templates'  # Replace with the actual path to your templates folder
    templates = load_yaml_files(templates_dir, required_keys)
    
    # Set all templates as available
    available_templates = templates.copy()
    # Get the unique keys for the available templates, to create menus
    unique_keys = get_unique_keys(available_templates, unique_identifiers)
    
    # Create stacks so we don't have to recalculate the available templates and unique keys, better to use RAM than processing time..
    available_templates_stack = []
    unique_keys_stack = []
    
    click.echo('''
 _______                       _____     _____     ____    ____  
|_   __ \                     |_   _|   |_   _|   |_   \  /   _| 
  | |__) |_   _   __  _ .--.    | |       | |       |   \/   |   
  |  ___/[ \ [ \ [  ][ `.-. |   | |   _   | |   _   | |\  /| |   
 _| |_    \ \/\ \/ /  | | | |  _| |__/ | _| |__/ | _| |_\/_| |_  
|_____|    \__/\__/  [___||__]|________||________||_____||_____| 
''')
    click.echo('\n\t\t    Welcome to Pwnllm!\n\tType "help" to show the available commands\n')

    # Iterates through the unique identifiers to create menus
    count=0
    while (count < len(unique_identifiers)):
        # Get current identifier and create a menu for it
        identifier = list(unique_identifiers)[count]
        identifier_help = unique_identifiers_help[list(unique_identifiers_help)[count]]
        
        # If it's the last menu, show the available attacks and prompt the user for a selection
        if count == len(unique_identifiers)-1:
            if learn_mode:
                selection, learn_mode = create_menu(get_available_attacks(available_templates), "Select an attack to learn about it:", return_index=True, learn_mode=learn_mode, unique_identifiers_help=identifier_help)
            else:
                selection, learn_mode = create_menu(get_available_attacks(available_templates), "Select an attack to generate a payload:", return_index=True, learn_mode=learn_mode, unique_identifiers_help=identifier_help)
            if selection is None:
                # Goes to the previous menu
                count-=1
                # Pop stack
                available_templates = available_templates_stack.pop()
                unique_keys = unique_keys_stack.pop()
                continue
            if learn_mode:
                learn(list(available_templates.values())[selection])
            else:
                generate_payload(list(available_templates.values())[selection])
            continue
        else:
            selection, learn_mode = create_menu(unique_keys[identifier], unique_identifiers[identifier], return_index=False, first=count == 0, learn_mode=learn_mode, unique_identifiers_help=identifier_help)
        
        # If selection is None and it's the first menu, exit
        if selection is None and count == 0:
            print("Exiting..")
            exit()
        elif selection is None:
            # Goes to the previous menu
            count-=1
            # Pop stack
            available_templates = available_templates_stack.pop()
            unique_keys = unique_keys_stack.pop()
            continue
        
        # If selection is not None, save the current available templates and unique keys to the stack and updates the available templates and unique keys
        available_templates_stack.append(available_templates.copy())
        unique_keys_stack.append(unique_keys.copy())
        available_templates, unique_keys = update_templates_choice(available_templates, identifier, selection, unique_identifiers)
        # Goes on to the next menu..
        count+=1


def generate_payload(payload):
    """
    Generate the LLM payload based on the given payload dictionary, merging techniques and bypasses.

    Args:
        payload (dict): A dictionary containing the payload information.

    Returns:
        None
    """
    print(f"Generating payload: {payload['name']}\n")
    for p in payload['payloads']:
        print(p)


def learn(payload):
    """
    Show information about the given payload, including its name, description, and payloads.

    Args:
        payload (dict): A dictionary containing the payload information.

    Returns:
        None
    """
    print(f"Name: {payload['name']}\n")
    print(f"Description: {payload['description']}\n")
    print("Payloads:")
    for p in payload['payloads']:
        print(p)
    print("About: ", payload['learn'])


if __name__ == '__main__':
    main()