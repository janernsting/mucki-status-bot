# coding=UTF-8

from safygiphy import Giphy
from random import randint


def search_gif(query, limit=25, offset=0):
    gif = Giphy().search(q=query, limit=limit, offset=offset)
    assert gif['meta']['status'] == 200, gif['meta']
    assert gif['pagination']['total_count'] > 0, gif
    return gif


def random_gif_url(query):
    total_gifs = search_gif(query=query)
    random_offset = randint(0, int((total_gifs['pagination']['total_count'] - 1) / 25))
    gif = search_gif(query=query, limit=25, offset=random_offset)
    random_index = randint(0, gif['pagination']['count'])
    return gif['data'][random_index]['images']['fixed_width']['url']

