#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# @Time    : 2021/2/20 上午11:52
# @File    : phoneModel.py
# @Software: PyCharm

import os
import re
import pandas as pd
from git import Repo  # rely on gitpython


class PhoneModel:
    def __init__(self):
        """获取手机品牌型号"""
        if os.path.exists(repo_path) == 0:  # 拉取仓库
            repo = Repo.clone_from(repo_address, repo_path)
        else:  # 拉取最新数据
            repo = Repo(repo_path)
        repo.remotes.origin.pull()
        self.new_commit = repo.head.commit.hexsha
        print("MobileModels latest commit: " + str(self.new_commit))
        os.environ["LATEST_COMMIT"] = self.new_commit
        # 获取所有的品牌名
        self.brands = [brand for brand in os.listdir(os.path.join(repo_path, 'brands')) if brand.endswith('md')]

    def get_model(self, brand):
        """读取原始数据"""
        with open(os.path.join(repo_path, 'brands', brand), 'rt') as f:
            brand_info = f.read()
        brand_info_list = [item for item in brand_info.split('\n') if re.match('[`.+:|\\*.+:]', item) is not None]

        model_df = pd.DataFrame(columns=['brand', 'model', 'area', 'brand_name', 'model_name', 'big_brand'])
        big_brand = 'UNKNOWN'
        for record in brand_info_list:
            record_list = record.split(':')
            if record_list[1] == '**':
                big_brand = record_list[0].replace('*', '')
                if '] ' in big_brand:
                    big_brand = big_brand.split('] ')[1]

                if ' (`' in big_brand:
                    big_brand = big_brand.split(' (`', 1 )[0]
                continue
            model_str = record_list[0].replace(brand[:-3].split('_')[0].upper(), '').strip()
            model_list = [x for x in model_str.split('` `') if x not in ('SHARK', 'HUAWEI', 'Letv', 'Le', 'ONE')]
            # head = model_list[0][:3]
            # tail = model_list[0][-3:]
            # if all([x.startswith(head) or x.endswith(tail) or x.find('-') > 0 for x in model_list]):
            for model in model_list:
                model_df.loc[len(model_df)] = (
                brand[:-3].split('_')[0], model.replace('`', ''), 'en' if brand.find('_en') > 0 else 'cn',
                brand_map.get(brand[:-3].split('_')[0], '其他'), record_list[1].lstrip(), big_brand)
        return model_df

    def get_all(self):
        brand_model = pd.DataFrame(columns=['brand', 'model', 'area', 'brand_name', 'model_name', 'big_brand'])

        for brand in self.brands:
            self.get_model(brand)
            brand_model = brand_model.append(self.get_model(brand))

        self.brand_model = brand_model.reset_index(drop=True).drop_duplicates().reset_index(drop=True)

    def data_save(self):
        project_path = os.path.dirname(os.path.realpath(__file__))
        self.brand_model.to_csv(os.path.join(project_path, 'brand_model.csv'), index=False, encoding='utf-8-sig')
        # 保存新的commit值
        with open('sync.log', 'wt') as f:
            f.write(self.new_commit)


if __name__ == '__main__':
    # repo_path = os.path.join(os.path.expanduser('~'), 'MobileModels')
    repo_path = './MobileModelss'
    repo_address = 'https://github.com/lipusheng/MobileModels.git'

    brand_map = {'meizu': '魅族', 'smartisan': '锤子', 'vivo': 'VIVO', 'realme': '真我',
                 'xiaomi': '小米', 'apple': '苹果', 'oppo': 'OPPO', 'nokia': '诺基亚',
                 'mitv': '小米电视', 'huawei': '华为', 'oneplus': '一加', 'motorola': '摩托罗拉',
                 'samsung': '三星', 'zte': '中兴', 'letv': '乐视', 'honor': '荣耀', 'lenovo': '联想',
                 '360shouji': '奇酷', 'nubia': '努比亚', 'google': 'Google', 'zhixuan': '华为智选',
                 'sony': '索尼'}

    try:
        with open('sync.log', 'rt') as f:
            last_commit = f.readline()
    except FileNotFoundError:
        last_commit = ''

    pm = PhoneModel()  # 初始 pm=PhoneModel(0),后续更新可不填
    # if pm.new_commit != last_commit:
    pm.get_all()
    pm.data_save()
    # else:
    print("No update, skip.")
