# !/usr/bin/env python3
# -*- coding:utf-8 -*-


# https://cafemaker.wakingsands.com 中文查找


import urllib.request, urllib.parse, json, os, time, datetime


ID_MAX = 40000

def set_single(local_cache, id):
    with urllib.request.urlopen(f'https://garlandtools.cn/api/get.php?type=item&lang=chs&version=3&id={id}') as res:
        res_detail = json.loads(res.read())
        local_cache['recipe'][id] = {}
        if 'item' not in res_detail:
            return
        res_detail_item = res_detail['item']
        local_cache['recipe'][id]['name'] = res_detail_item['name']
        local_cache['name_to_id'][res_detail_item['name']] = id
        if 'craft' not in res_detail_item:
            return
        for recipe in res_detail_item['craft']:
            local_cache['recipe'][id]['rlvl']=recipe['rlvl']
            if 'ingredients' not in recipe:
                return
            local_cache['recipe'][id]['ingredients'] = recipe['ingredients']
            break


def get_local_cache():
    recipe_cache = {}
    name_to_id_cache = {}
    local_cache = {'recipe': recipe_cache, 'name_to_id': name_to_id_cache}

    set_single(local_cache, 5338)
    print(local_cache)
    with open('local_cache.json', 'w') as f:
        json.dump(local_cache, f)

if __name__ == "__main__":
    get_local_cache()
