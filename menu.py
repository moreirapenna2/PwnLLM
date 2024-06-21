import click

def show_help():
    print('''
help        - Shows this help message
?           - Shows you information about the current menu and its options
learn  (L)  - Enters learning mode, showing information about each attack without generating payloads
attack (A)  - Enters attack mode, allowing you to generate payloads
exit        - Exits the program''')


def create_menu(options, text=None, return_index=False, first=False, learn_mode=False, unique_identifiers_help=None):
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

    # uppercase the first letter of each option
    pretty_options = [option[0].upper() + option[1:] for option in options]

    while True:
        if text:
            click.echo(f"\n{text}")

        for i, option in enumerate(pretty_options, 1):
            click.echo(f"[{i}] {option}")

        # If it's the first menu, shows "Exit" instead of "Go back"
        if first:
            click.echo('[0] Exit')
        else:
            click.echo('[0] Go back')
        
        prompt = '(A)'
        if learn_mode:
            prompt = '(L)'

        # Creating the prompt with right-shift of 1, so we don't start at 0 because it's weird for users
        selection = click.prompt(f'{prompt}> ', type=click.Choice([str(i) for i in range(1, len(options)+1)] + ['0', 'exit', 'learn', 'attack', 'help', '?']), prompt_suffix='', show_choices=False).lower()
        
        if selection == "0":
            return None, learn_mode
        elif selection == "exit":
            print("Exiting..")
            exit()
        elif selection == "learn":
            learn_mode = True
            print("You are now in the learning mode, payload generation is disabled. To exit learning mode, type 'attack' or restart the program.")
        elif selection == "attack":
            learn_mode = False
            print("You are now in the attack mode, payload generation is enabled. Hack the planet!")
        elif selection == "help":
            show_help()
        elif selection == "?":
            if unique_identifiers_help:
                print("\n" + unique_identifiers_help.rstrip("\n"))
            else:
                print("No help available for this menu.")
        else:
            # Returning the selection with left-shift of 1 to match the correct value
            if return_index:
                return int(selection)-1, learn_mode
            
            return options[int(selection)-1], learn_mode


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