"""
    Module for dynamically handling the generation and setting of class properties.
"""

from .base import get_class_attribute, set_class_attribute
from .flags import set_properties_from_flags

from typing import Any, Dict, List, Optional
import copy


DEBUG_MODE = False



def getter_method_gen(property_name):
    def get_property(self):
        return get_class_attribute(self, "_" + property_name)
    return get_property


def setter_method_gen(property_name, props=None):
    def set_property(self, property_value):
        if DEBUG_MODE:
            print('classproperties:set_property - %s - props: %s' % (property_name, props))

        if property_value is None:
            if props is not None and 'default_value' in props:
                property_value = props['default_value']
        elif props is not None and 'prop_type' in props:
            prop_type = props['prop_type']
            property_value = prop_type(property_value)
        set_class_attribute(self, "_" + property_name, property_value)
    return set_property


def declare_props(obj, *properties_list, props=None):

    if properties_list is None:
        properties_list = []

    properties_list = list(properties_list)

    if props is not None:
        properties_list.extend(list(props.keys()))
    else:
        props = {}

    for property_name in properties_list:

        getter_method = getter_method_gen(property_name)
        setter_method = setter_method_gen(property_name, props.get(property_name, None))

        set_class_attribute(obj, "_" + property_name, None)
        set_class_attribute(obj.__class__, "_get_" + property_name, getter_method)
        set_class_attribute(obj.__class__, "_set_" + property_name, setter_method)
        set_class_attribute(obj.__class__, property_name, property(getter_method, setter_method))

        # Set default values when defined in props
        if property_name in props and 'default_value' in props[property_name]:
            default_value = props[property_name]['default_value']
            set_class_attribute(obj, "_" + property_name, default_value)


    def properties_setter_gen(props):
        def set_properties(self, properties_dict):
            class_properties = self.class_properties
            for property_name in properties_dict:
                if property_name in class_properties:
                    setter = get_class_attribute(self, "_set_" + property_name)
                    setter(properties_dict[property_name])
                # set_class_attribute(self, "_" + property_name, properties_dict[property_name])
        return set_properties

    def generate_print_properties_method():
        def print_properties(self):
            print(self)
            for prop in self.custom_properties:
                prop_value = getattr(self, "_" + prop)
                print("%s - %s (%s)" % (prop, prop_value, prop_value.__class__))
        return print_properties

    def generate_get_properties_method():
        def get_properties(self, include_only: Optional[List[str]] = None, exclude_props: Optional[List[str]] = None, filter_null: bool = False) -> Dict[str, Any]:
            """
            Generate a dictionary of properties for the instance.

            :param include_only: List of property names to include. If None, all properties are included.
            :param exclude_props: List of property names to exclude. If None, no properties are excluded.
            :param filter_null: Whether to exclude properties with a value of None.
            :return: A dictionary of properties.
            """
            return {
                prop: getattr(self, "_" + prop)
                for prop in self.custom_properties
                if (include_only is None or prop in include_only) and
                (exclude_props is None or prop not in exclude_props) and
                (not filter_null or getattr(self, "_" + prop) is not None)
            }

        return get_properties

    setattr(obj, 'custom_properties', props)
    set_class_attribute(obj, 'class_properties', properties_list)
    set_class_attribute(obj.__class__, 'set_properties', properties_setter_gen(properties_list))
    set_class_attribute(obj.__class__, 'print_properties', generate_print_properties_method())
    setattr(obj.__class__, 'get_properties', generate_get_properties_method())
