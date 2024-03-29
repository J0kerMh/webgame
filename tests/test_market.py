import pytest



@pytest.mark.parametrize(('item_name', 'price', 'message'), (
    ('test8',1,  b'This item is on sale!'),
    ('test9',2,  b'This item is on shelf!'),
    ('sfdsdafs',3,  b'This item is not existed!'),
))
def test_sale_item(client, auth ,item_name,price, message):
    auth.login()
    response = client.post(
        '/market',
        data={'opts': 'sale_item', 'args1': item_name,'args2':price}
    )
    assert message in response.data


@pytest.mark.parametrize(('item_name', 'message'), (
    ('test10',  b'You buy this item!'),
    ('test11',  b'You do not have enough gold.'),
    ('sdfasdfa',  b'This item is not existed!'),
))
def test_buy_item(client, auth ,item_name, message):
    auth.login()
    response = client.post(
        '/market',
        data={'opts': 'buy_item', 'args1': item_name, 'args2': 'test'}
    )
    assert message in response.data


@pytest.mark.parametrize(('item_name', 'message'), (
    ('sdfasf',  b'This item is not existed!'),
    ('test12',  b'You successfully cancelled the sale of this item!')
))
def test_cancel_sale(client, auth ,item_name, message):
    auth.login()
    response = client.post(
        '/market',
        data={'opts': 'cancel_sale', 'args1': item_name, 'args2': 'test'}
    )
    assert message in response.data


@pytest.mark.parametrize(('item_name','price', 'message'), (
    ('sdfasf',1,  b'This item is not existed!'),
    ('test8',2,  b'You change the price of item to'),

))
def test_change_sale(client, auth ,item_name,price, message):
    auth.login()
    response = client.post(
        '/market',
        data={'opts': 'change_sale', 'args1': item_name, 'args2': price}
    )
    assert message in response.data

