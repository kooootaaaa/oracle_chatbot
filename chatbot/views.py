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
            page = data.get('page', 1)  # ページ番号（1から開始）
            
            if not user_input:
                return JsonResponse({'response': '質問を入力してください。'})
            
            # 検索クエリの構築（AND検索：すべてのキーワードを含むレコード）
            import re
            # 読点、全角カンマ、半角カンマ、スペースで分割してキーワードを抽出
            keywords = re.split(r'[,、，\s]+', user_input.strip())
            keywords = [k.strip() for k in keywords if k.strip()]  # 空文字列を除去
            
            query = Q()
            for keyword in keywords:
                # 各キーワードについて、いずれかのフィールドに含まれる条件
                keyword_query = (
                    Q(hno__icontains=keyword) |
                    Q(keikaku_no__icontains=keyword) |
                    Q(tr_hinban__icontains=keyword) |
                    Q(tr_hinmei__icontains=keyword) |
                    Q(shashu__icontains=keyword) |
                    Q(fuguai_naiyou__icontains=keyword) |
                    Q(suitei_fuguai_genin__icontains=keyword) |
                    Q(taisaku_an__icontains=keyword)
                )
                # すべてのキーワード条件をANDで結合
                if query:
                    query &= keyword_query
                else:
                    query = keyword_query
            
            print(f"Original input: {user_input}")  # デバッグ用
            print(f"Keywords: {keywords}")  # デバッグ用
            print(f"Query: {query}")  # デバッグ用
            
            # データベース検索
            if action == 'detail':
                # 詳細表示の場合（計画書NO降順）
                detail_type = data.get('detail_type', '')
                results = TFurenSho.objects.filter(query).order_by('-hno')[:10]
                
                if results:
                    response_text = '<div class="detail-content">'
                    for i, result in enumerate(results, 1):
                        response_text += f'<div class="detail-section">'
                        response_text += f'<h3>検索結果 {i}</h3>'
                        response_text += f'<div class="detail-label">評技連No.:</div><div>{result.hno or "---"}</div><br>'
                        response_text += f'<div class="detail-label">計画書No.:</div><div>{result.keikaku_no or "---"}</div><br>'
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
                # 要約の場合はすべて取得（計画書NO降順）
                results = TFurenSho.objects.filter(query).order_by('-hno')
                
                if results:
                    # データ分析
                    hno_list = [r.hno for r in results if r.hno]
                    keikaku_no_list = [r.keikaku_no for r in results if r.keikaku_no]
                    tr_hinban_set = set([r.tr_hinban for r in results if r.tr_hinban])
                    tr_hinmei_set = set([r.tr_hinmei for r in results if r.tr_hinmei])
                    shashu_set = set([r.shashu for r in results if r.shashu])
                    
                    # 不具合内容、原因、対策の要約（最初の3件から抜粋）
                    fuguai_samples = [r.fuguai_naiyou for r in results[:3] if r.fuguai_naiyou]
                    genin_samples = [r.suitei_fuguai_genin for r in results[:3] if r.suitei_fuguai_genin]
                    taisaku_samples = [r.taisaku_an for r in results[:3] if r.taisaku_an]
                    
                    # 要約レスポンス作成
                    response_text = f"「{user_input}」全{len(results)}件の要約\n\n"
                    
                    # 評技連No.
                    if len(hno_list) > 5:
                        response_text += f"評技連No.: {hno_list[0]}～{hno_list[-1]} 他{len(hno_list)-2}件\n"
                    else:
                        response_text += f"評技連No.: {', '.join(hno_list)}\n"
                    
                    # 計画書No.
                    if keikaku_no_list:
                        if len(keikaku_no_list) > 5:
                            response_text += f"計画書No.: {keikaku_no_list[0]}～{keikaku_no_list[-1]} 他{len(keikaku_no_list)-2}件\n"
                        else:
                            response_text += f"計画書No.: {', '.join(keikaku_no_list)}\n"
                    else:
                        response_text += "計画書No.: データなし\n"
                    
                    # TR品番
                    if len(tr_hinban_set) > 3:
                        tr_list = sorted(tr_hinban_set)
                        response_text += f"TR品番: {', '.join(tr_list[:3])} 他{len(tr_hinban_set)-3}種類\n"
                    else:
                        response_text += f"TR品番: {', '.join(sorted(tr_hinban_set))}\n"
                    
                    # TR品名
                    if len(tr_hinmei_set) > 3:
                        hinmei_list = sorted(tr_hinmei_set)
                        response_text += f"TR品名: {', '.join(hinmei_list[:3])} 他{len(tr_hinmei_set)-3}種類\n"
                    else:
                        response_text += f"TR品名: {', '.join(sorted(tr_hinmei_set))}\n"
                    
                    # 車種
                    if len(shashu_set) > 3:
                        shashu_list = sorted(shashu_set)
                        response_text += f"車種: {', '.join(shashu_list[:3])} 他{len(shashu_set)-3}種類\n\n"
                    else:
                        response_text += f"車種: {', '.join(sorted(shashu_set))}\n\n"
                    
                    # 不具合内容要約
                    response_text += "【主な不具合内容】\n"
                    for i, fuguai in enumerate(fuguai_samples, 1):
                        response_text += f"{i}. {fuguai[:100]}{'...' if len(fuguai) > 100 else ''}\n"
                    
                    response_text += "\n【主な推定原因】\n"
                    for i, genin in enumerate(genin_samples, 1):
                        response_text += f"{i}. {genin[:100]}{'...' if len(genin) > 100 else ''}\n"
                    
                    response_text += "\n【主な対策案】\n"
                    for i, taisaku in enumerate(taisaku_samples, 1):
                        response_text += f"{i}. {taisaku[:100]}{'...' if len(taisaku) > 100 else ''}\n"
                    
                    return JsonResponse({'response': response_text})
                else:
                    return JsonResponse({'response': '要約対象のデータが見つかりませんでした。'})
            else:
                # 通常検索はページネーション対応（10件ずつ）計画書NO降順
                total_count = TFurenSho.objects.filter(query).count()
                start_index = (page - 1) * 10
                end_index = start_index + 10
                results = TFurenSho.objects.filter(query).order_by('-hno')[start_index:end_index]
            
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
                    # 通常検索モードの処理（ページネーション対応）
                    current_start = (page - 1) * 10 + 1
                    current_end = min(page * 10, total_count)
                    total_pages = (total_count + 9) // 10  # 切り上げ計算
                    
                    response_text = f"「{user_input}」の検索結果: {current_start}-{current_end}件 / 全{total_count}件\n\n"
                    
                    for i, result in enumerate(results, current_start):
                        response_text += f"【{i}】\n"
                        response_text += f"評技連No.: {result.hno}\n"
                        response_text += f"計画書No.: {result.keikaku_no or '---'}\n"
                        response_text += f"TR品番: {result.tr_hinban}\n"
                        response_text += f"TR品名: {result.tr_hinmei}\n"
                        response_text += f"車種: {result.shashu}\n"
                        response_text += f"不具合内容: {result.fuguai_naiyou}\n"
                        response_text += f"推定不具合原因: {result.suitei_fuguai_genin}\n"
                        response_text += f"対策案: {result.taisaku_an}\n"
                        response_text += "-" * 50 + "\n"
                    
                    # ページネーションと要約ボタンを追加
                    response_text += '\n<div class="pagination-container">'
                    
                    if page > 1:
                        response_text += f'<button class="btn pagination-btn" onclick="searchPage(\'{user_input}\', {page - 1})">← 前の10件</button>'
                    if page < total_pages:
                        response_text += f'<button class="btn pagination-btn" onclick="searchPage(\'{user_input}\', {page + 1})">次の10件 →</button>'
                    
                    # 要約ボタンを追加
                    safe_keyword = user_input.replace("'", "\\'").replace('"', '\\"')
                    response_text += f'<button class="btn summary-btn" onclick="showSummary(\'{safe_keyword}\')">📊 要約</button>'
                    
                    response_text += '</div>'
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