from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime

# Create your models here.
class Product(models.Model):
    pcode = models.CharField(max_length=10)
    pname = models.TextField(null=False)
    pclass = models.CharField(max_length=16)
    pMain = models.TextField(null=False)
    pSoup = models.TextField(null=False)
    pSub1 = models.TextField(null=False)
    pSub2 = models.TextField(null=False)
    pSub3 = models.TextField(null=False)
    unitprice = models.IntegerField(default=0)
    discountrate = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=datetime.datetime.now)
    modify_date = models.DateTimeField(null=True, blank=True)
    # 추가 항목(MEDIA)
    imgfile = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.pcode + " " + self.pname + " " + str(self.unitprice) + " " + str(self.discountrate)
