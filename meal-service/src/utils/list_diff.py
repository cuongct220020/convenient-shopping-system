def list_diff(old_list, new_list, key_attr, quantity_attr):
    diff = {}
    old_dict = {getattr(item, key_attr): item for item in old_list}
    new_dict = {getattr(item, key_attr): item for item in new_list}

    for key, new_item in new_dict.items():
        if key in old_dict:
            old_item = old_dict[key]
            quantity_change = getattr(new_item, quantity_attr) - getattr(old_item, quantity_attr)
            if quantity_change != 0:
                diff[key] = quantity_change
        else:
            diff[key] = getattr(new_item, quantity_attr)

    for key, old_item in old_dict.items():
        if key not in new_dict:
            diff[key] = -getattr(old_item, quantity_attr)

    return diff