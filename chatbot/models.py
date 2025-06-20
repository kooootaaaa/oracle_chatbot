from django.db import models

class TFurenSho(models.Model):
    hno = models.CharField(max_length=50, primary_key=True, db_column='HNO')
    tr_hinban = models.CharField(max_length=50, verbose_name='TR品番', db_column='TR品番')
    tr_hinmei = models.CharField(max_length=200, verbose_name='TR品名', db_column='TR品名')
    shashu = models.CharField(max_length=100, verbose_name='車種', db_column='車種')
    fuguai_naiyou = models.TextField(verbose_name='不具合内容', db_column='不具合内容')
    suitei_fuguai_genin = models.TextField(verbose_name='推定不具合原因', db_column='推定不具合原因')
    taisaku_an = models.TextField(verbose_name='対策案', db_column='対策案等')
    
    class Meta:
        db_table = 'T_不連書'
        managed = False
        
    def __str__(self):
        return f"{self.tr_hinban} - {self.tr_hinmei}"