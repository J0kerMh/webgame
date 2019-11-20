import pytest
from application import mongo



@pytest.mark.parametrize(('item_name', 'price', 'message'), (
    ('test8',1,  b'This item is on sale!'),
    ('test9',2,  b'This item is on shelf!'),
    ('sfdsdafs',3,  b'This item is not existed!'),
))
def test_sale_item(client, auth ,item_name,price, message):
    auth.login()
    response = client.get(
        '/market/sale_item/{item_name}/{price}'.format(item_name=item_name,price = price)
    )
    assert message in response.data


@pytest.mark.parametrize(('item_name', 'message'), (
    ('test10',  b'You buy this item!'),
    ('test11',  b'You do not have enough gold.'),
    ('sdfasdfa',  b'This item is not existed!'),
))
def test_buy_item(client, auth ,item_name, message):
    auth.login()
    response = client.get(
        '/market/buy_item/{item_name}/test'.format(item_name=item_name)
    )
    assert message in response.data


@pytest.mark.parametrize(('item_name', 'message'), (
    ('sdfasf',  b'This item is not existed!'),
    ('test12',  b'You successfully cancelled the sale of this item!')
))
def test_cancel_sale(client, auth ,item_name, message):
    auth.login()
    response = client.get(
        '/market/cancel_sale/{item_name}/test'.format(item_name=item_name)
    )
    assert message in response.data


@pytest.mark.parametrize(('item_name','price', 'message'), (
    ('sdfasf',1,  b'This item is not existed!'),
    ('test8',2,  b'You change the price of item to'),

))
def test_change_sale(client, auth ,item_name,price, message):
    auth.login()
    response = client.get(
        '/market/change_sale/{item_name}/{price}'.format(item_name=item_name,price = price)
    )
    assert message in response.data

