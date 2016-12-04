# -*- coding: utf-8 -*-
from scrapy import Item


class DynamicItem(Item):
    def __setitem__(self, key, value):
        self._values[key] = value
        self.fields[key] = {}
