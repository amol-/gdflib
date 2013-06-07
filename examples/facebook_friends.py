from contextlib import closing
import requests
import argparse
import functools
from gdflib import GdfEntries, Node

from multiprocessing import Queue, Pool

import logging
logging.basicConfig(level=logging.WARN)
log = logging.getLogger()

API_URL = 'https://graph.facebook.com'
FRIENDS_RELATIVE_URL = '/me/friends'
MUTUAL_RELATIVE_URL = '/me/mutualfriends/%s'

def _fetch_data(url, token):
    resp = requests.get(url, params={'format':'json', 'access_token':token})
    log.debug(resp)
    return resp.json()

def _fetch_paginated_data(url, token):
    results = []

    while True:
        result = _fetch_data(url, token)
        if 'error' in result:
            log.error(result['error'])

        results.extend(result['data'])
        url = result.get('paging', {}).get('next')
        if url is None:
            break

    return results

def get_friends(token):
    return _fetch_paginated_data(API_URL + FRIENDS_RELATIVE_URL, token)

def get_foaf(user, token):
    return _fetch_paginated_data(API_URL + MUTUAL_RELATIVE_URL % user, token)


results_queue = Queue()
class LinkingPerformer(object):
    def __init__(self, token):
        self.token = token

    def __call__(self, friend):
        user_id = friend['id']
        print 'Fetching data of User %s...' % user_id
        for foaf in get_foaf(user_id, self.token):
            results_queue.put((user_id, foaf['id']))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch Facebook Network Graph')
    parser.add_argument('token', help='Your facebook access token')
    args = parser.parse_args()

    entries = GdfEntries()

    print 'Fetching your friends...'
    foaf = {}
    friends = get_friends(args.token)
    for count, user in enumerate(friends):
        user_id = user['id']

        node = Node(name=user_id, label=user['name'])
        entries.add_node(node)

    perform_linking = LinkingPerformer(args.token)

    pool = Pool(15)
    pool.map(perform_linking, friends)

    print 'Storing Graph...'
    while not results_queue.empty():
        entries.link(*results_queue.get())

    print 'Saving file friends.gdf...'
    with closing(open('friends.gdf', 'w')) as f:
        entries.dump(f)
    print 'Saved!'