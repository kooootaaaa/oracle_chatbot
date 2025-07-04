from django import forms

class ExportForm(forms.Form):
    """Excel出力用フォーム"""
    
    # フィールド選択用チェックボックス
    FIELD_CHOICES = [
        ('hno', '評技連No. (HNO)'),
        ('keikaku_no', '計画書NO'),
        ('tr_hinban', 'TR品番'),
        ('tr_hinmei', 'TR品名'),
        ('shashu', '車種'),
        ('fuguai_naiyou', '不具合内容'),
        ('suitei_fuguai_genin', '推定不具合原因'),
        ('taisaku_an', '対策案等'),
    ]
    
    # 出力フィールド選択
    fields = forms.MultipleChoiceField(
        choices=FIELD_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='出力する項目を選択してください',
        initial=['hno', 'tr_hinban', 'tr_hinmei', 'shashu']  # デフォルトで選択される項目
    )
    
    # 検索条件フィールド
    search_query = forms.CharField(
        max_length=500,
        required=False,
        label='検索キーワード（オプション）',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'キーワードを入力（例：TR品番、車種など）'
        })
    )
    
    # 最大出力件数
    max_records = forms.IntegerField(
        min_value=1,
        max_value=10000,
        initial=1000,
        required=True,
        label='最大出力件数',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'style': 'width: 150px;'
        })
    )