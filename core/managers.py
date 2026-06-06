from django.db import models

class ShopQuerySet(models.QuerySet):

    def for_shop(self, shop):
        return self.filter(shop=shop)