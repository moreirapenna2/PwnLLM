import os, yaml

def load_yaml_files(directory, required_keys):
    """
    Load YAML files from a directory and return a dictionary of templates.

    Args:
        directory (str): The directory path where the YAML files are located.
        required_keys (list): A list of required keys that must be present in the templates.

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


def get_unique_keys(templates, unique_identifiers):
    """
    Get the unique keys from the given templates. Unique keys are the values that help identify them, like
    what they achieve, what's the deploy method, what's the exploration type, etc.

    Args:
        templates (dict): A dictionary of templates.
        unique_identifiers (list): A list of unique identifiers to get from the templates.

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

def update_templates_choice(available_templates, key, selection, unique_identifiers):
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
    unique_keys = get_unique_keys(available_templates, unique_identifiers)
    return available_templates, unique_keys