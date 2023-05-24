from lib.roblox.roblox_functions import get_roblox_ids, check_for_promotions, get_role_in_group

def test_get_ids():
    users = get_roblox_ids('Shinyehh <@159435000184307713> 123')
    assert users == [{'username': '123', 'id': None}, {'username': 'hisokachan', 'id': 74851095}, {'username': 'Shinyehh', 'id': 11752468}]

def test_check_for_promotions():
    users = [123, 74851095, 11752468]
    promoted, skipped_ranks = check_for_promotions(users)
    assert promoted == [] and skipped_ranks == []

def test_get_role_in_group():
    role = get_role_in_group(74851095, 17325964)
    assert role == {'id': 96346575, 'name':'[5] Owner','rank':255}

def test_get_role_in_group_2():
    role = get_role_in_group(123, 17325964)
    assert role == {'name':'[0] Visitor','rank':0}