import pytest
from app_sql import *

def test_work(client, auth,app):
    auth.login()
    before_num = WorkHistory.query.filter_by(name='yhma').count()
    response = client.post(
        '/user/opts',
        data={'opts': 'work', 'args':'test'}
    )
    with app.app_context():
        after_num = WorkHistory.query.filter_by(name='yhma').count()
        if b'You can only work once a day!' in response.data:
            assert after_num == before_num
        else:
            assert after_num == before_num+1

def test_treasure_hunt(client, auth, app):
    auth.login()
    before_num = TreasureHuntHistory.query.filter_by(name='yhma').count()
    response = client.post(
        '/user/opts',
        data={'opts': 'treasure_hunt', 'args': 'test'}
    )
    with app.app_context():
        after_num = TreasureHuntHistory.query.filter_by(name='yhma').count()
        if b'You can only hunt for treasure once a day!' in response.data:
            assert after_num == before_num
        else:
            assert after_num == before_num + 1

@pytest.mark.parametrize(('item_name', 'message'), (
    ('test1',  b'This item is on sale, you can not adorn it!'),
    ('sdfasf',  b'This tool is not existed!'),
    ('test2',  b'You must take off your tool!'),
    ('test7',  b'This is not a tool!'),
))
def test_adorn_tool(client, auth ,item_name, message):
    auth.login()
    response = client.post(
        '/user/opts',
        data={'opts': 'adorn_tool', 'args': item_name}
    )
    assert message in response.data


@pytest.mark.parametrize(('item_name', 'message'), (
    ('test8',  b'This item is on sale, you can not adorn it!'),
    ('sdfasf',  b'This decoration is not existed!'),
    ('test7',  b'You must take off your decoration!'),
    ('test3',  b'This is not a decoration!'),
))
def test_adorn_decoration(client, auth ,item_name, message):
    auth.login()
    response = client.post(
        '/user/opts',
        data={'opts': 'adorn_decoration', 'args': item_name}
    )
    assert message in response.data


@pytest.mark.parametrize(('item_name', 'message'), (
    ('sdfasf',  b'This tool is not existed!'),
    ('test4',  b'You take off this tool successfu4ly!')
))
def test_take_off_tool(client, auth ,item_name, message):
    auth.login()
    response = client.post(
        '/user/opts',
        data={'opts': 'take_off_tool', 'args': item_name}
    )
    assert message in response.data

@pytest.mark.parametrize(('item_name', 'message'), (
    ('sdfadf',  b'This decoration is not existed!'),
    ('margaret hugeflip',  b'You take off this decoration successfully!')
))
def test_take_off_decoration(client, auth ,item_name, message):
    auth.login()
    response = client.post(
        '/user/opts',
        data={'opts': 'take_off_decoration', 'args': item_name}
    )
    assert message in response.data