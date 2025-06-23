from django.db import models
from django.utils import timezone

class Case(models.Model):
    INSPECTION_TYPE_CHOICES = [
        ('首件', '首件'),
        ('巡檢', '巡檢'),
    ]
    SALE_TYPE_CHOICES = [
        ('內銷', '內銷'),
        ('外銷', '外銷'),
    ]
    DEPARTMENT_CHOICES = [
        ("", ""),
        ('塑膠射出課', '塑膠射出課'),
        ('射出加工組', '射出加工組'),
        ('機械加工課', '機械加工課'),
        ('繞線區', '繞線區'),
        ('泵浦組裝組', '泵浦組裝組'),
        ('電機組立課', '電機組立課'),
        ('燒崁組立課', '燒崁組立課'),
    ]
    INSPECTOR_CHOICES = [
        ('吳小男', '吳小男'),
        ('謝小宸', '謝小宸'),
        ('黃小瀅', '黃小瀅'),
        ('蔡小函', '蔡小函'),
        ('徐小棉', '徐小棉'),
        ('杜小綾', '杜小綾'),
    ]
    DEFECT_CATEGORY_CHOICES = [
        ("", ""),
        ('無圖面', '無圖面'),
        ('圖物不符', '圖物不符'),
        ('無工單', '無工單'),
        ('無檢驗表單', '無檢驗表單'),
        ('尺寸NG', '尺寸NG'),
        ('外觀NG', '外觀NG'),
        ('電阻異常', '電阻異常'),
        ('特性異常', '特性異常'),
        ('扭力值異常', '扭力值異常'),
        ('SOP異常', 'SOP異常'),
        ('無法檢測', '無法檢測'),
        ('無檢驗表單', '無檢驗表單'),
        ('途程單異常', '途程單異常'),
    ]

    inspection_type = models.CharField(verbose_name='首件巡檢', max_length=10, choices=INSPECTION_TYPE_CHOICES, default='首件')
    sale_type = models.CharField(verbose_name='內/外銷', max_length=10, choices=SALE_TYPE_CHOICES, default='外銷')
    customer = models.CharField(verbose_name='客戶', max_length=100, default="")
    department = models.CharField(verbose_name='部門', max_length=50, choices=DEPARTMENT_CHOICES, default="")
    date = models.DateField(verbose_name='日期', default=timezone.now)
    time = models.TimeField(verbose_name='時間', default=timezone.now)
    work_order_number = models.CharField(verbose_name='製令編號', max_length=100, default="")
    operator = models.CharField(verbose_name='作業人員', max_length=100, default="", blank=True)
    drawing_revision = models.CharField(verbose_name='圖面版次', max_length=50, default="", blank=True)
    part_number = models.CharField(verbose_name='品號', max_length=100, default="", blank=True)
    part_name = models.CharField(verbose_name='品名', max_length=100, default="", blank=True)
    quantity = models.IntegerField(verbose_name='數量', default=0)
    inspector = models.CharField(verbose_name='巡檢員', max_length=50, choices=INSPECTOR_CHOICES, default="")
    defect_category = models.CharField(verbose_name='不良分類', max_length=50, choices=DEFECT_CATEGORY_CHOICES, default="", blank=True)
    defect_description = models.CharField(verbose_name='不良狀況', max_length=255, blank=True)
    disposition = models.CharField(verbose_name='處置對策', max_length=255, blank=True)
    inspection_hours = models.DecimalField(verbose_name='檢驗工時(時)', max_digits=5, decimal_places=2, default=0.00, blank=True)
    created_at = models.DateTimeField(verbose_name='建立時間', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新時間', auto_now=True)

    def __str__(self):
        return f"{self.work_order_number} - {self.part_name}"
