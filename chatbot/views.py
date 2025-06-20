from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json
import html
from .models import TFurenSho

def index(request):
    return render(request, 'chatbot/index.html')

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('message', '').strip()
            action = data.get('action', 'search')  # デフォルトは検索
            
            if not user_input:
                return JsonResponse({'response': '質問を入力してください。'})
            
            # 検索クエリの構築
            query = Q()
            keywords = user_input.split()
            
            for keyword in keywords:
                query |= (
                    Q(tr_hinban__icontains=keyword) |
                    Q(tr_hinmei__icontains=keyword) |
                    Q(shashu__icontains=keyword) |
                    Q(fuguai_naiyou__icontains=keyword) |
                    Q(suitei_fuguai_genin__icontains=keyword) |
                    Q(taisaku_an__icontains=keyword)
                )
            
            print(f"Query: {query}")  # デバッグ用
            
            # データベース検索
            if action == 'detail':
                # 詳細表示の場合
                detail_type = data.get('detail_type', '')
                results = TFurenSho.objects.filter(query)[:10]
                
                if results:
                    response_text = '<div class="detail-content">'
                    for i, result in enumerate(results, 1):
                        response_text += f'<div class="detail-section">'
                        response_text += f'<h3>検索結果 {i}</h3>'
                        response_text += f'<div class="detail-label">TR品番:</div><div>{result.tr_hinban or "---"}</div><br>'
                        response_text += f'<div class="detail-label">TR品名:</div><div>{result.tr_hinmei or "---"}</div><br>'
                        response_text += f'<div class="detail-label">車種:</div><div>{result.shashu or "---"}</div><br>'
                        response_text += f'<div class="detail-label">不具合内容:</div><div style="white-space: pre-wrap;">{result.fuguai_naiyou or "---"}</div><br>'
                        response_text += f'<div class="detail-label">推定不具合原因:</div><div style="white-space: pre-wrap;">{result.suitei_fuguai_genin or "---"}</div><br>'
                        response_text += f'<div class="detail-label">対策案:</div><div style="white-space: pre-wrap;">{result.taisaku_an or "---"}</div>'
                        response_text += '</div>'
                    response_text += '</div>'
                else:
                    response_text = '<p>該当する詳細情報が見つかりませんでした。</p>'
                
                return JsonResponse({'response': response_text})
            
            elif action == 'summary':
                # 要約の場合は最大10件取得
                results = TFurenSho.objects.filter(query)[:10]
            else:
                # 通常検索は最大5件
                results = TFurenSho.objects.filter(query)[:5]
            
            if results:
                if action == 'summary':
                    # 要約モードの処理
                    response_text = f"「{user_input}」に関連する不具合情報の要約:\n\n"
                    response_text += f"【検索結果】 {len(results)}件\n\n"
                    
                    # 不具合内容の傾向をまとめる
                    fuguai_list = []
                    genin_list = []
                    taisaku_list = []
                    shashu_set = set()
                    
                    for result in results:
                        if result.fuguai_naiyou:
                            fuguai_list.append(result.fuguai_naiyou[:100])  # 最初の100文字
                        if result.suitei_fuguai_genin:
                            genin_list.append(result.suitei_fuguai_genin[:100])
                        if result.taisaku_an:
                            taisaku_list.append(result.taisaku_an[:100])
                        if result.shashu:
                            shashu_set.add(result.shashu)
                    
                    # 要約用のデータを格納
                    summary_data = {
                        'keyword': user_input,
                        'results': results
                    }
                    
                    response_text += f"【関連車種】\n"
                    if shashu_set:
                        for shashu in sorted(shashu_set):
                            # HTMLエスケープを削除してクリック可能にする
                            safe_shashu = shashu.replace("'", "\\'").replace('"', '\\"')
                            response_text += f'<span class="clickable-item" onclick="showDetail(\'{safe_shashu}\', \'shashu\')">{shashu}</span>　'
                        response_text += "\n\n"
                    else:
                        response_text += "車種情報なし\n\n"
                    
                    response_text += f"【主な不具合内容】（クリックで詳細表示）\n"
                    for i, fuguai in enumerate(fuguai_list[:3], 1):
                        # HTMLエスケープを削除してクリック可能にする
                        safe_fuguai = fuguai.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
                        response_text += f'{i}. <span class="clickable-item" onclick="showDetailFromSummary({i-1}, \'fuguai\')">{fuguai}</span>...\n'
                    
                    response_text += f"\n【主な推定原因】（クリックで詳細表示）\n"
                    for i, genin in enumerate(genin_list[:3], 1):
                        # HTMLエスケープを削除してクリック可能にする
                        safe_genin = genin.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
                        response_text += f'{i}. <span class="clickable-item" onclick="showDetailFromSummary({i-1}, \'genin\')">{genin}</span>...\n'
                    
                    response_text += f"\n【主な対策案】（クリックで詳細表示）\n"
                    for i, taisaku in enumerate(taisaku_list[:3], 1):
                        # HTMLエスケープを削除してクリック可能にする
                        safe_taisaku = taisaku.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
                        response_text += f'{i}. <span class="clickable-item" onclick="showDetailFromSummary({i-1}, \'taisaku\')">{taisaku}</span>...\n'
                    
                    # 要約データを保存（セッションまたはキャッシュに保存することも可能）
                    request.session['summary_results'] = [
                        {
                            'hno': r.hno,
                            'tr_hinban': r.tr_hinban,
                            'tr_hinmei': r.tr_hinmei,
                            'shashu': r.shashu,
                            'fuguai_naiyou': r.fuguai_naiyou,
                            'suitei_fuguai_genin': r.suitei_fuguai_genin,
                            'taisaku_an': r.taisaku_an
                        } for r in results
                    ]
                    
                else:
                    # 通常検索モードの処理
                    response_text = f"「{user_input}」に関連する情報を{len(results)}件見つけました:\n\n"
                    
                    for i, result in enumerate(results, 1):
                        response_text += f"【{i}】\n"
                        response_text += f"TR品番: {result.tr_hinban}\n"
                        response_text += f"TR品名: {result.tr_hinmei}\n"
                        response_text += f"車種: {result.shashu}\n"
                        response_text += f"不具合内容: {result.fuguai_naiyou}\n"
                        response_text += f"推定不具合原因: {result.suitei_fuguai_genin}\n"
                        response_text += f"対策案: {result.taisaku_an}\n"
                        response_text += "-" * 50 + "\n"
            else:
                response_text = f"申し訳ございませんが、「{user_input}」に関連する情報が見つかりませんでした。\n\nTR品番、TR品名、車種名などで検索してみてください。"
            
            return JsonResponse({'response': response_text})
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in chat view: {error_details}")  # サーバーログに出力
            return JsonResponse({'response': f'エラーが発生しました: {str(e)}'})
    
    return JsonResponse({'response': 'POSTリクエストのみ対応しています。'})

@csrf_exempt
def detail(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            index = data.get('index', 0)
            detail_type = data.get('type', '')
            
            # セッションから要約結果を取得
            summary_results = request.session.get('summary_results', [])
            
            if 0 <= index < len(summary_results):
                result = summary_results[index]
                
                response_text = '<div class="detail-content">'
                response_text += f'<div class="detail-section">'
                response_text += f'<div class="detail-label">TR品番:</div><div>{html.escape(result.get("tr_hinban", "") or "---")}</div><br>'
                response_text += f'<div class="detail-label">TR品名:</div><div>{html.escape(result.get("tr_hinmei", "") or "---")}</div><br>'
                response_text += f'<div class="detail-label">車種:</div><div>{html.escape(result.get("shashu", "") or "---")}</div><br>'
                response_text += f'<div class="detail-label">不具合内容:</div><div style="white-space: pre-wrap;">{html.escape(result.get("fuguai_naiyou", "") or "---")}</div><br>'
                response_text += f'<div class="detail-label">推定不具合原因:</div><div style="white-space: pre-wrap;">{html.escape(result.get("suitei_fuguai_genin", "") or "---")}</div><br>'
                response_text += f'<div class="detail-label">対策案:</div><div style="white-space: pre-wrap;">{html.escape(result.get("taisaku_an", "") or "---")}</div>'
                response_text += '</div>'
                response_text += '</div>'
            else:
                response_text = '<p>詳細情報が見つかりませんでした。</p>'
                
            return JsonResponse({'response': response_text})
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in detail view: {error_details}")
            return JsonResponse({'response': f'エラーが発生しました: {str(e)}'})
    
    return JsonResponse({'response': 'POSTリクエストのみ対応しています。'})