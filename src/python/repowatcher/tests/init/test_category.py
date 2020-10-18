from repowatcher.entity.category import Category

import pytest


@pytest.fixture
def category():
    '''Returns a Category with name "Category"'''
    return Category(name='Category')


def test_setting_initial_name(category):
    assert category.name == 'Category'


@pytest.mark.parametrize('name,expected_name', [
    ('test', 'test'),
    (1, '1'),
    (None, None)
])
def test_setting_name(name, expected_name):
    category = Category()
    category.name = name

    assert category._name == expected_name
    assert category.name == expected_name


@pytest.mark.parametrize('id_value,expected_id', [
    (-1, -1),
    (0, 0),
    (1, 1),
    (100000, 100000),
    ('1', 1),
    ('-1', -1),
    (None, None)
])
def test_setting_id(id_value, expected_id):
    category = Category()
    category.id = id_value

    assert category._id == expected_id
    assert category.id == expected_id
