import click, os, yaml

def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)
    
config = load_config()
required_keys = config['required_keys']
unique_identifiers = config['unique_identifiers']

@click.command()

def main():
    # Load templates
    templates_dir = 'templates'  # Replace with the actual path to your templates folder
    templates = load_yaml_files(templates_dir)
    
    # Set all templates as available
    available_templates = templates.copy()
    # Get the unique keys for the available templates, to create menus
    unique_keys = get_unique_keys(available_templates)
    
    # Create stacks so we don't have to recalculate the available templates and unique keys, better to use RAM than processing time..
    available_templates_stack = []
    unique_keys_stack = []
    
    click.echo('\nWelcome to Pwnllm!\n')

    # Iterates through the unique identifiers to create menus
    count=0
    while (count < len(unique_identifiers)):
        # Get current identifier and create a menu for it
        identifier = list(unique_identifiers)[count]
        
        # If it's the last menu, show the available attacks and prompt the user for a selection
        if count == len(unique_identifiers)-1:
            selection = create_menu(get_available_attacks(available_templates), "Select an attack to generate a payload", True)
            if selection is None:
                # Goes to the previous menu
                count-=1
                # Pop stack
                available_templates = available_templates_stack.pop()
                unique_keys = unique_keys_stack.pop()
                continue
            generate_payload(list(available_templates.values())[selection])
            continue
        else:
            selection = create_menu(unique_keys[identifier], unique_identifiers[identifier], False, count == 0)
        
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
        available_templates, unique_keys = update_templates_choice(available_templates, identifier, selection)
        # Goes on to the next menu..
        count+=1


def create_menu(options, text=None, return_index=False, first=False):
    """
    Creates a menu with the given options and prompts the user for a selection.

    Args:
        options (list): The list of options to display in the menu.
        text (str, optional): The text to display before the menu. Defaults to None.
        return_index (bool, optional): Whether to return the index of the selected option instead of the option itself. Defaults to False.
        first (bool, optional): Whether this is the first menu in the sequence. Defaults to False.

    Returns:
        str or int or None: The selected option or its index. Returns None if the user chooses to exit or go back.
    """
    options = list(options)
    
    if text:
        click.echo(f"\n{text}")

    for i, option in enumerate(options, 1):
        click.echo(f"[{i}] {option}")

    # If it's the first menu, shows "Exit" instead of "Go back"
    if first:
        click.echo('[0] Exit')
    else:
        click.echo('[0] Go back')
    
    # Creating the prompt with right-shift of 1, so we don't start at 0 because it's weird for users
    selection = click.prompt('> ', type=click.Choice([str(i) for i in range(1, len(options)+1)] + ['0'] + ['exit']), prompt_suffix='', show_choices=False)
    
    if selection == "0":
        return None
    elif selection == "exit":
        print("Exiting..")
        exit()
    
    # Returning the selection with left-shift of 1 to match the correct value
    if return_index:
        return int(selection)-1
    
    return options[int(selection)-1]


def update_templates_choice(available_templates, key, selection):
    """
    Update the available templates and unique keys based on the selected option.

    Parameters:
    available_templates (list): A list of available templates.
    key (str): The key to match against the selected option.
    selection (str): The selected option.

    Returns:
    tuple: A tuple containing the updated available templates and unique keys.
    """

    # Remove all templates that don't match the selected option
    for template_key in list(available_templates.keys()):  # create a copy of the keys
        if type(available_templates[template_key][key]) == list:
            if selection not in available_templates[template_key][key]:
                del available_templates[template_key]
        else:
            if available_templates[template_key][key] != selection:
                del available_templates[template_key]
    
    #def remove_templates_choice(templates, key, value):
    # Recalculate the unique keys based on the available templates
    unique_keys = get_unique_keys(available_templates)
    return available_templates, unique_keys


def get_available_attacks(available_templates):
    """
    Get a list of available attacks by showing their name, description and quantity of payloads.

    Args:
        available_templates (dict): A dictionary containing available templates.

    Returns:
        list: A list of strings representing the available attacks, including the name, description, and number of payloads for each template.
    """
    attacks = []
    for template in available_templates.values():
        attacks.append(f"{template['name']} - {template['description']} - ({str(len(template['payloads']))})")
    return attacks


def generate_payload(payload):
    """
    Generate the LLM payload based on the given payload dictionary, merging techniques and bypasses.

    Args:
        payload (dict): A dictionary containing the payload information.

    Returns:
        None
    """
    print(f"Generating payload: {payload['name']}")
    for p in payload['payloads']:
        print(p)


def load_yaml_files(directory):
    """
    Load YAML files from a directory and return a dictionary of templates.

    Args:
        directory (str): The directory path where the YAML files are located.

    Returns:
        dict: A dictionary containing the loaded templates, where the keys are the filenames and the values are the templates.

    Raises:
        ValueError: If any of the required keys are not found in the template.
    """
    templates = {}
    for filename in os.listdir(directory):
        try:
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                with open(os.path.join(directory, filename), 'r') as file:
                    template = yaml.safe_load(file)
                    
                    # Check if certain keys are on the template
                    for key in required_keys:
                        if key not in template:
                            raise ValueError(f"Key '{key}' not found")
                    # Create a temporary template to save values, so we can strip strings and replace newlines
                    tmp_template = {}
                    for key, value in template.items():
                        if type(value) == str:
                            value = value.strip().replace('\n', ' ')
                        tmp_template[key] = value
                    templates[filename] = tmp_template
        except Exception as e:
            print(f"Error loading template '{filename}': {e}, skipping...")
            continue
    return templates


def get_unique_keys(templates):
    """
    Get the unique keys from the given templates. Unique keys are the values that help identify them, like
    what they achieve, what's the deploy method, what's the exploration type, etc.

    Args:
        templates (dict): A dictionary of templates.

    Returns:
        dict: A dictionary containing unique keys for each identifier in the templates.
    """
    unique_keys = {}

    # Initialize the unique keys with empty sets
    for identifier in unique_identifiers:
        unique_keys[identifier] = set()

    # Iterates through each template and adds the unique keys to the sets, parsing if they're lists
    for template in templates.values():
        try:
            for identifier in unique_identifiers:
                if type(template[identifier]) == list:
                    for value in template[identifier]:
                        unique_keys[identifier].add(value)
                else:
                    unique_keys[identifier].add(template[identifier])
        except Exception as e:
            print(f"Error getting unique keys: {e} on template '{template['name']}', skipping..")
            continue

    # TODO: Currently, if one of the template's unique keys fails to load, it will be skipped. This will cause the unique keys to be incomplete,
    # with some keys added and some not. This should be fixed by creating a temporary set for the keys and only adding to
    # the complete set if the template was loaded successfully.

    # Sort the sets by name, so we don't have different orders each time we run the program
    for key in unique_keys.keys():
        unique_keys[key] = sorted(list(unique_keys[key]))
    return unique_keys

if __name__ == '__main__':
    main()