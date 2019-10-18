import pytest
from application import mongo
from flask import session
def test_work(client, auth,app):
    auth.login()
    before_num = mongo.db.workHistory.find({'name':'yhma'}).count()
    response = client.get('/user/work/test')
    with app.app_context():
        after_num = mongo.db.workHistory.find({'name':'yhma'}).count()
        if b'You can only work once a day!' in response.data:
            assert after_num == before_num
        else:
            assert after_num == before_num+1

def test_treasure_hunt(client, auth, app):
    auth.login()
    before_num = mongo.db.treasureHuntHistory.find({'name': 'yhma'}).count()
    response = client.get('/user/treasure_hunt/test')
    with app.app_context():
        after_num = mongo.db.treasureHuntHistory.find({'name': 'yhma'}).count()
        if b'You can only hunt for treasure once a day!' in response.data:
            assert after_num == before_num
        else:
            assert after_num == before_num + 1

@pytest.mark.parametrize(('item_name', 'message'), (
    ('sdfasf',  b'This item is on sale, you can not adorn it!'),
    ('sdfasf',  b'This tool is not existed!'),
    ('test1',  b'You must take off your tool!'),
    ('test2',  b'This is not a tool!'),
))
def test_adorn_tool(client, auth ,item_name, message):
    auth.login()
    response = client.get(
        '/user/adorn_tool/{item_name}'.format(item_name=item_name)
    )
    assert message in response.data


@pytest.mark.parametrize(('item_name', 'message'), (
    ('sdfasf',  b'This item is on sale, you can not adorn it!'),
    ('sdfasf',  b'This decoration is not existed!'),
    ('test1',  b'You must take off your decoration!'),
    ('test2',  b'This is not a decoration!'),
))
def test_adorn_decoration(client, auth ,item_name, message):
    auth.login()
    response = client.get(
        '/user/adorn_decoration/{item_name}'.format(item_name=item_name)
    )
    assert message in response.data


@pytest.mark.parametrize(('item_name', 'message'), (
    ('sdfasf',  b'This item is on sale, you can not adorn it!'),
    ('sdfasf',  b'This decoration is not existed!'),
    ('test1',  b'You must take off your decoration!'),
    ('test2',  b'This is not a decoration!'),
))
def test_take_off_tool(client, auth ,item_name, message):
    auth.login()
    response = client.get(
        '/user/take_off_tool/{item_name}'.format(item_name=item_name)
    )
    assert message in response.data

@pytest.mark.parametrize(('item_name', 'message'), (
    ('sdfasf',  b'This item is on sale, you can not adorn it!'),
    ('sdfasf',  b'This decoration is not existed!'),
    ('test1',  b'You must take off your decoration!'),
    ('test2',  b'This is not a decoration!'),
))
def test_take_off_decoration(client, auth ,item_name, message):
    auth.login()
    response = client.get(
        '/user/take_off_decoration/{item_name}'.format(item_name=item_name)
    )
    assert message in response.data