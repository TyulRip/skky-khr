from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser

# 회원정보 테이블
class User(AbstractBaseUser):
    username = models.CharField(max_length=50, unique = True)
    password = models.CharField(max_length=128)
    user_name = models.CharField(max_length=50)
    user_phone = models.CharField(max_length=13)
    user_point = models.IntegerField(default=0)
    user_sign = models.DateTimeField(default=timezone.now)
    user_del = models.BooleanField(default=0)
    user_pet = models.IntegerField(default=0)
    user_acc_point = models.IntegerField(default=0)
    user_grade = models.IntegerField(default=1)

    USERNAME_FIELD = 'username'

# 상품정보 테이블
class Product(models.Model):
    product_name = models.CharField(max_length=255)
    product_point = models.IntegerField()
    product_pet = models.IntegerField()
    image = models.CharField(max_length=255, null=True, blank=True)  # 이미지 URL
    product_change = models.IntegerField(default=0)

# 교환 정보 테이블
class Exchange(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    change_cnt = models.IntegerField()
    change_way = models.IntegerField(default=0)
    change_app_dt = models.DateTimeField(default=timezone.now)
    change_dt = models.DateTimeField(null=True, blank=True)

# 배송 테이블
class Delivery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    del_address = models.CharField(max_length=255)
    del_status = models.IntegerField(default=0)
    del_num = models.CharField(max_length=255)

# 기계 정보 테이블
class Machine(models.Model):
    machine_address = models.CharField(max_length=255)
    machine_latitude = models.CharField(max_length=255)
    machine_longitude = models.CharField(max_length=255)
    machine_capacity = models.IntegerField()
    machine_pet = models.IntegerField(default=0)

# 기계 + 사용자 정보 테이블
class MachineUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    ma_us_pet = models.IntegerField()
