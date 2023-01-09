# !/usr/bin/env python3
# -*- coding:utf-8 -*-


# https://cafemaker.wakingsands.com 中文查找


import urllib.request, urllib.parse, json, os, time, datetime
import prettytable

command_help = '''
?/H/h: 打开此帮助
F/f/Find: 根据名称查询物品ID
A/a/Add: 添加一个比对市场监视，用法: Add 物品ID
R/r/Remove: 移除一个监视
S/s/Start: 开始运行
Ctrl+c: 退出
'''

filename = 'save.json'

recipe_list = []
should_show_materials = True
running = False

id_to_name_buffer = {}

with open(filename) as f:
    recipe_list = json.load(f)


def save_json():
     with open(filename, 'w') as f:
        json.dump(recipe_list, f)


def find_item(item_name):
    with urllib.request.urlopen('https://cafemaker.wakingsands.com/search?string='+urllib.parse.quote(item_name)) as res:
        res_detail = json.loads(res.read())
        ret_str = '----------------------------------------\n'
        ret_str += f'找到：{res_detail["Pagination"]["ResultsTotal"]}\n'
        for item_detail in res_detail['Results']:
            ret_str += f'{item_detail["ID"]:<10} {item_detail["Name"]:<10}\n'
        ret_str += '----------------------------------------\n'
        return ret_str


def get_name(id):
    if id in id_to_name_buffer:
        return id_to_name_buffer[id]
    with urllib.request.urlopen(f'https://cafemaker.wakingsands.com/item/{id}') as res:
        res_detail = json.loads(res.read())
        id_to_name_buffer[id]=res_detail['Name_chs']
        return id_to_name_buffer[id]

moguli = urllib.parse.quote('莫古力')
def get_market():
    updated = False
    now = time.time()
    for recipe in recipe_list:
        if ('t' not in recipe) or now-recipe['t']>1800:
            print('进行了请求\n')
            updated = True
            recipe['t']=now
            with urllib.request.urlopen(urllib.request.Request(f'https://universalis.app/api/v2/{moguli}/{recipe["item"]}?listings=0&entries=0', headers={'User-Agent': 'Mozilla/5.0'})) as res:
                res_detail = json.loads(res.read())
                recipe['regular_sale_velocity'] = 0
                for stack, number in res_detail['stackSizeHistogram'].items():
                    recipe['regular_sale_velocity'] += float(stack) * float(number)
                recipe['regular_sale_velocity'] /= 7
                recipe['average_price'] = res_detail['averagePrice']
                cost = 0
                for material in recipe['materials']:
                    with urllib.request.urlopen(urllib.request.Request(f'https://universalis.app/api/v2/{moguli}/{material["id"]}?listings=0&entries=0', headers={'User-Agent': 'Mozilla/5.0'})) as mres:
                        mres_detail = json.loads(mres.read())
                        material['average_price'] = mres_detail['averagePrice']
                        cost += float(material['average_price']) * float(material['count'])
                recipe['cost'] = cost
                recipe['rank'] = (float(recipe['average_price']) - float(recipe['cost'])) * float(recipe['regular_sale_velocity'])
                save_json()
                return
    if not updated:
        print('未进行请求\n')


def print_recipes():
    tb = prettytable.PrettyTable(['ID', '名称', '周价', '流动', '成本', '评级'])
    for recipe in recipe_list:
        if 'regular_sale_velocity' in recipe:
            tb.add_row([recipe['item'], get_name(recipe['item']), recipe['average_price'], recipe['regular_sale_velocity'], recipe['cost'], recipe['rank']])
    print(tb)


print('''
**************
* 光之葛朗台 *
**************
''')
print(find_item('弦月'))


while True:
    if running:
        os.system('cls')
        get_market()
        print_recipes()
        print(datetime.datetime.now())
        time.sleep(3)
        continue
    command = input('指令：')
    ls = command.split()
    try:
        if ls[0]=='?' or ls[0]=='H' or ls[0]=='h':
            print(command_help)
        elif ls[0]=='F' or ls[0]=='f' or ls[0]=='Find':
            print(find_item(ls[1]))
        elif ls[0]=='A' or ls[0]=='a' or ls[0]=='Add':
            materials = []
            print('    持续输入材料id与数量, 输入E/e/End结束')
            while True:
                item_str = input('    材料：')
                item = item_str.split()
                print(item)
                if item[0]=='E' or item[0] =='e' or item[0]=='End':
                    if len(materials)<=0:
                        print('未添加原材料，添加监视失败')
                    else:
                        recipe_list.append({'item':ls[1], 'materials':materials})
                        save_json()

                        print(f'添加了物品{get_name(ls[1])}的监视配方, id为{ls[1]}')
                    break
                else:
                    materials.append({'id':item[0], 'count':item[1]})
        elif ls[0]=='R' or ls[0]=='r' or ls[0]=='Remove':
            for recipe in recipe_list:
                if recipe['item']==ls[1]:
                    recipe_list.remove(recipe)
                    save_json()
                    break
        elif ls[0]=='S' or ls[0]=='s' or ls[0]=='Start':
            running = True
        else:
            print((command_help))
    except:
        print('输入了无效指令，请参考帮助：')
        print(command_help)