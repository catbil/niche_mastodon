#!/usr/bin/env python

from mastodon import Mastodon
import random
import gspread
import datetime
import time
from oauth2client.service_account import ServiceAccountCredentials

#마스토돈 API 인증
mastodon = Mastodon(
    access_token = 'lX3slp3J2nqLi9jq4oufQbWEvCVpeYCVizFuWGnQC_4',
    api_base_url = 'https://occm.masto.host/'
)

#구글 API 인증
scope = [
'https://spreadsheets.google.com/feeds',
'https://www.googleapis.com/auth/drive',
]

json_file_name = 'nicheinfo-8d910e04219c.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)
spreadsheet_notice = 'https://docs.google.com/spreadsheets/d/1LCkbLfVhkOB7iJFAlnJWyAYTLnVIUntlf94yzIosXxo/edit#gid=0'
spreadsheet_log = 'https://docs.google.com/spreadsheets/d/1KJx5iOqSpYASQq9j7azga30LZpQgI9KO0QEgmQHDp2g/edit#gid=1697177339'

###함수###

def select_mentions():
    mentions = []
    if len(mastodon.notifications()) < 20:
        search_range = len(mastodon.notifications())

    else:
        search_range = 20
        
    for i in range(search_range):
        if mastodon.notifications()[i].type == "mention":
            mentions.append(mastodon.notifications()[i])

    return mentions


#트윗 정보
def tweet_info(a_mention):
    
    tweetId = a_mention.status.id
    account_id = a_mention.status.account.id
    userId = a_mention.status.account.username
    username = a_mention.status.account.display_name
    tweetTime = str(a_mention.status.created_at).split(".")[0]
    tweet_txt = a_mention.status.content

    return tweetId, account_id, userId, username, tweetTime, tweet_txt

#파일 내용을 리스트로 반환 
def file_to_list(filename):
    """
    file_txt: List, a list of replied tweet ID
    """
    
    f= open("%s.txt"%filename, 'r', encoding='UTF-8')
    
    file_txt = f.readlines()
    for i in range(len(file_txt)):
        file_txt[i] = file_txt[i].replace("\n", "")
        print(file_txt[i])
    f.close()
        
    return file_txt

#유저 딕셔너리(커뮤 내부 고유번호) 생성
def build_user_dict(account_id_list):
    user_dict={}
    i = 1
    for num in account_id_list:
        user_dict[mastodon.account(num).username] = i
        i += 1

    return user_dict

#accountID 를 display_name으로 변환
def conv_diplay_name(account_id):
    name = mastodon.account(account_id).display_name

    return name

#중복 답변 체크
def duplicate_check(file_txt, tweetId):
    """
    file_txt: List, a list of replied tweet ID
    """
    if str(tweetId) in file_txt:
        return True

#파일에 내용 추가
def add_to_file(filename, tweetId):
    f= open("%s.txt"%filename, 'a')
    f.write(str(tweetId)+"\n")
    f.close()

#txt 파일 읽어서 딕셔너리로 만들기
def vend_dict(filename = "vend_list"):
    """
    vend: Dict,{"name of vending machine": [item list]}
    """
    f = open("%s.txt"%(filename), 'r', encoding='UTF-8')
    lines = f.readlines()
    vend_type = ["basic","pain","costume","drug","animal","room"]
    vend = {}
    for i in range(len(lines) - 1):
        lines[i] = lines[i].replace("\n", "")
        if lines[i] in vend_type:
            vend[lines[i]] = lines[i+1].split(",")
        else:
            continue
    f.close()

    return vend

#리스트에 아이디 있는지 중복체크 후에 없으면 확장
def append_ID_list(filename, tweetId, tweet_txt):
    
    if str(tweetId) not in tweet_txt:
        add_to_file(filename, tweetId)
        

#주사위 범주 분류 
def tweet_category(tweet_txt):
    if ("원샷" in tweet_txt) and not ("주사위" in tweet_txt) and not ("뽑기" in tweet_txt) and not ("잔액" in tweet_txt):
        category = "원샷"
        
    elif ("주사위" in tweet_txt) and not ("원샷" in tweet_txt) and not ("뽑기" in tweet_txt) and not ("잔액" in tweet_txt):
        category = "주사위"
        
    elif ("잔액" in tweet_txt) and not ("원샷" in tweet_txt) and not ("주사위" in tweet_txt) and not ("뽑기" in tweet_txt):
        category = "잔액"

    elif ("복권" in tweet_txt):
        category = "복권"

    else:
        category = "없음"
        
    return category

#뽑기 범주 분류
def vend_category(tweet_txt):
    if ("기본" in tweet_txt) and not ("약물" in tweet_txt) and not ("동물" in tweet_txt) and not ("체벌" in tweet_txt) and not ("코스튬" in tweet_txt) and not ("열쇠" in tweet_txt):
        vend_keyword = "기본"
        
    elif ("약물" in tweet_txt) and not ("기본" in tweet_txt) and not ("동물" in tweet_txt) and not ("체벌" in tweet_txt) and not ("코스튬" in tweet_txt) and not ("열쇠" in tweet_txt):
        vend_keyword = "약물"

    elif ("동물" in tweet_txt) and not ("기본" in tweet_txt) and not ("약물" in tweet_txt) and not ("체벌" in tweet_txt) and not ("코스튬" in tweet_txt) and not ("열쇠" in tweet_txt):
        vend_keyword = "동물"
                
    elif ("체벌" in tweet_txt) and not ("기본" in tweet_txt) and not ("약물" in tweet_txt) and not ("동물" in tweet_txt) and not ("코스튬" in tweet_txt) and not ("열쇠" in tweet_txt):
        vend_keyword = "체벌"

    elif ("코스튬" in tweet_txt) and not ("기본" in tweet_txt) and not ("약물" in tweet_txt) and not ("동물" in tweet_txt) and not ("체벌" in tweet_txt) and not ("열쇠" in tweet_txt):
        vend_keyword = "코스튬"

    elif ("열쇠" in tweet_txt) and not ("기본" in tweet_txt) and not ("약물" in tweet_txt) and not ("동물" in tweet_txt) and not ("체벌" in tweet_txt) and not ("코스튬" in tweet_txt):
        vend_keyword = "열쇠"
                
    else:
        vend_keyword = "없음"

    return vend_keyword

#복권좋아
def lotto(userId, tweet_txt, filename, tweetId):
    if userId == "NicheParty_4":
        if ("복권" in tweet_txt):
            n1 = random.randrange(1,5)
            n2 = random.randrange(1,5)
            n3 = random.randrange(1,5)
            n4 = random.randrange(1,5)
            do_phrase = "@"+userId+" "+str(n1)+str(n2)+str(n3)+str(n4)

            add_to_file(filename, tweetId)
    else:
        do_phrase = "@"+userId+" 직원이 아니면 이용할 수 없는 메뉴입니다."

    add_to_file(filename, tweetId)

    return do_phrase

    
#자동 원샷 주사위    
def dice_oneshot(userId, username, tweetId, tweet_txt):
    """
    user_number: dict, {'user name': number, ...}
    
    """

    if ("원샷" in tweet_txt) and not ("주사위" in tweet_txt) and not ("뽑기" in tweet_txt):
        n1 = random.randrange(1,7)
        n2 = random.randrange(1,7)
        n3 = random.randrange(1,7)
        n4 = n1+n2-n3
        do_phrase = "@"+userId+" "+str(n1)+"+"+str(n2)+"-"+str(n3)+"="+str(n4)
        
        dice_result = {"%s"%userId:[userId, n1, n2, n3, n4]}

    add_to_file(filename, tweetId) #답멘한 멘션리스트
        
    return do_phrase, dice_result

#자동 일반 주사위
def dice_normal(tweet_txt, userId):
    
    if ("주사위" in tweet_txt) and not ("원샷" in tweet_txt) and not ("뽑기" in tweet_txt) and not ("잔액" in tweet_txt):
        dn_phrase = "@"+userId+" "+str(random.randrange(1,7))

    append_ID_list(filename, tweetId, tweet_txt) #답멘한 멘션리스트

    return dn_phrase  

#자판기
def vend_auto(filename, vend, userId, tweetId, tweet_txt, vend_keyword):
    """
    vend: Dict,{"name of vending machine": [items list]}
    user_number: dict, {'user name': number, ...}
    
    """

    if vend_keyword == "기본":
        vend_phrase = "@"+userId+" "+ random.choice(vend["basic"])
        user_vend = {"%s"%userId : "basic"}
        
    elif vend_keyword == "약물":
        vend_phrase = "@"+userId+" "+ random.choice(vend["drug"])
        user_vend  = {"%s"%userId : "drug"}

    elif vend_keyword == "동물":
        vend_phrase = "@"+userId+" "+ random.choice(vend["animal"])
        user_vend  = {"%s"%userId : "animal"}
                
    elif vend_keyword == "코스튬":
        vend_phrase = "@"+userId+" "+ random.choice(vend["costume"])
        user_vend  = {"%s"%userId : "costume"}

    elif vend_keyword == "체벌":
        vend_phrase = "@"+userId+" "+ random.choice(vend["pain"])
        user_vend  = {"%s"%userId : "pain"}
        
    elif vend_keyword == "열쇠":
        if vend["room"] == False:
            vend_phrase = "@"+userId+" "+"남은 열쇠가 없습니다"
        else:
            vend_phrase = "@"+userId+" "+ vend["room"].pop(random.randrange(len(vend["room"])-1))
            user_vend  = {"%s"%userId : "room"}

    append_ID_list(filename, tweetId, tweet_txt) #답멘한 멘션리스트
    
    return vend_phrase, user_vend

def keyword_reply(phrase, tweetId):
    mastodon.status_post(phrase, in_reply_to_id = tweetId)
    

def noKeyword(userId):
    phrase = "@"+userId+" "+"키워드를 이해하지 못 했어요."
    append_ID_list(filename, tweetId, tweet_txt)
    
    return phrase

#멘션 정보와 답멘 정보 리스트 만들기
def reply(tweetTime, username, userId, phrase, tweet_txt):
    """
    user_number: dict, {'user name': number, ...}

    """
    
    log_block = [tweetTime, username, userId, phrase, " ", tweet_txt]
    return log_block

#구글 시트에 로그 백업
def log(log_block, spreadsheet_log):
    """
    log_block: list, [tweetTime, username, userId, phrase, " ", tweet_txt]
    spreadsheet_log: string, google spreadsheet URL

    """
    sh = gc.open_by_url(spreadsheet_log)
    worksheet = sh.worksheet('시트1')
    worksheet.append_row(log_block, table_range = "A:F")

#이용자번호 딕셔너리와 주사위 값 결과 딕셔너리로 시트에 업데이트
def update_dice(user_number, dice_result, spreadsheet_notice, sheet_number = 1):
    """
    user_number: dict, {'user name': number, ...}
    dice_result: dict, {'user name': [name, dice1, dice2, dice3, sum]}
    """
    sh = gc.open_by_url(spreadsheet_notice)
    worksheet = sh.worksheet('시트%d'%sheet_number)
    name_list = list(dice_result.keys())
    
    for name in name_list:
        result_list = dice_result[name]
        
        for i in range(len(result_list) + 1):
            loc_index = ["A", "B", "C", "D", "E", "F"]
            
            if i == 5:
                location = loc_index[i]+ str(user_number[name] + 1)
                dice_total = int(worksheet.acell(location).value)
                worksheet.update_acell(location, dice_total + dice_result[name][i - 1])
                
            else:
                location = loc_index[i] + str(user_number[name] + 1)
                worksheet.update_acell(location, dice_result[name][i])
                print(dice_result[name][i])                 

#이용자 이름과 자판기 이름 딕셔너리로 자판기 사용 내역 업데이트
def update_vend(user_number, vend_result, spreadsheet_notice, sheet_number = 1):
    """
    user_number: dict, {'user name':  number}
    vend_result: dict, {'user name': 'name of vendingmachine']
    """
    sh = gc.open_by_url(spreadsheet_notice)
    worksheet = sh.worksheet('시트%d'%sheet_number)
    name_list = list(vend_result.keys())

    for name in name_list:
        print(vend_result[name])
        if vend_result[name] == "basic":
            print("H")
            location = 'H%d'%(user_number[name] + 1)
        elif (vend_result[name] == "drug") or (vend_result[name] == "animal") or (vend_result[name] == "pain"):
            print("I")
            location = 'I%d'%(user_number[name] + 1)
        elif (vend_result[name] == "costume") or (vend_result[name] == "room"):
            print("J")
            location = 'J%d'%(user_number[name] + 1)

        print(location)
        current_val = int(worksheet.acell(location).value)
        worksheet.update_acell(location, current_val + 1)

#잔액 확인
def check_balance(userId, username, user_number, spreadsheet_notice, sheet_number = 1):
    sh = gc.open_by_url(spreadsheet_notice)
    worksheet = sh.worksheet('시트%d'%sheet_number)
    name_list = list(user_number.keys())

    for name in name_list:
        if name == userId:
            location = 'L%d'%(user_number[name] + 1)
            dice_total = worksheet.acell(location).value
            phrase = "@" + userId + username + "님의 현재 잔액은 " + dice_total + "코인입니다."

    append_ID_list(filename, tweetId, tweet_txt)

    return phrase
        
    
#시간을 체크하고 확인할 멘션 개수를 변경
def time_dice():
    check_num = 10
    
    if 11<=datetime.datetime.today().hour<13 or 21<=datetime.datetime.today().hour<23:
        if 30<=datetime.datetime.today().minute<55:
            check_num = 30

    return check_num

#주사위 게임 시트 값을 0으로 초기화
def empty_result_list(account_id_list):
    reset_list = []
    loc_index = ["A", "B", "C", "D", "E"]
    reset_rows = []
   
    for i in range(len(account_id_list)):
        for j in range(len(loc_index)):
            if j == 0:
                reset_rows = [conv_diplay_name(account_id_list[i])]
            else:
                reset_rows.append(0)

        reset_list.append(reset_rows)

    return reset_list

#시트가 0값이 있는지 없는지 확인
def check_sheet(userId, username, user_number, spreadsheet_notice, sheet_number = 1):
    sh = gc.open_by_url(spreadsheet_notice)
    worksheet = sh.worksheet('시트%d'%sheet_number)
    name_list = list(user_number.keys())

    for name in name_list:
        if name == userId:
            location = 'B%d'%(user_number[name] + 1)
            sheet_v = worksheet.acell(location).value
            check_v = int(sheet_v)
            if check_v != 0:
                append_ID_list(filename, tweetId, tweet_txt)
                return False
            else:
                None
                

#주사위 결과값을 list of list로 저장,[첫번째 주사위, 두번째 주사위, 세번째 주사위, 합계]
def build_result_list(empty_list, userId, user_number, username, dice_result, sheet_number = 1):
    sh = gc.open_by_url(spreadsheet_notice)
    worksheet = sh.worksheet('시트%d'%sheet_number)
    loc = user_number[userId]
    loc = "F"+ str(user_number[userId] + 1)
    dice_total = int(worksheet.acell(loc).value)
    dice_result[userId][0] = username
    empty_list[user_number[userId]] = dice_result[userId]
    empty_list[user_number[userId]].append(dice_total + dice_result[userId][- 1])
    print(empty_list)


#List 값이 0인지 아닌지 확인 (주사위 게임 참가여부 확인)
def check_result_list(userId, user_number, empty_list):
    loc = user_number[userId]
    if empty_list[loc][1] == 0:
        return True
    else:
        return False
    
if __name__ == "__main__":
    
    filename = "twitter_ID_list"
    screen_name = "The_niche_A"
    num = 1
    account_id_list=[106600747368106097,106602140545837349,106602068758011512,106601909073547325,106601653143974866,106601701382237006,106601348501922774,106601523780922310,106601559828669181,106601598303736358,106601607451571195,106601455567872348,106601340063052108,106601315466434344,106601324550082919,106601338579166711,106601271013540069,106601244635069928,106601272584462536,106601195352073049,106601185260184495,106601211188734512,106601156756963712,106601089068133053,106601103025087671,106601126398175630,106601016723839273,106601065298243791,106601022386992356,106601006566711136,106600964377813397,106600869308410739,106600906327135923,106600935413661366]
    user_number = build_user_dict(account_id_list)

    empty_list = empty_result_list(account_id_list)

    vend = vend_dict()

    while datetime.datetime.today().minute >= 0:
        check_num = time_dice()
        file_txt = file_to_list(filename)

        mentions = select_mentions()
        
        for toot in mentions:
            tweetId, account_id, userId, username, tweetTime, tweet_txt= tweet_info(toot)
            dice_name = tweet_category(tweet_txt)
            vend_name = vend_category(tweet_txt)

            try:
                if (datetime.datetime.today().hour == 11 or datetime.datetime.today().hour == 21) and datetime.datetime.today().minute == 00:
                    empty_list = empty_result_list(account_id_list) #내용이 없는 리스트 업데이트(초기화)[시작 30분 전]
                    sh = gc.open_by_url(spreadsheet_notice)
                    worksheet = sh.worksheet('시트1')
                    worksheet.update('A2', empty_list)
                    phrase = "주사위 게임까지 30분 남았습니다."

                if (datetime.datetime.today().hour == 12 or datetime.datetime.today().hour == 22) and datetime.datetime.today().minute == 31:
                    sh = gc.open_by_url(spreadsheet_notice)
                    worksheet = sh.worksheet('시트1')
                    worksheet.update('A2', empty_list) #내용이 있는 리스트 업데이트[시작 1시간 후]
                    phrase = "%d 시 % 분 주사위 게임 결과 업데이트 완료."
                
                if duplicate_check(file_txt, tweetId) == True:#트윗 아이디 리스트에 아이디가 있으면 건너뜀(pass)
                    pass

                elif dice_name == "원샷":
                    check_bool = check_result_list(userId, user_number, empty_list)
                
                    if (datetime.datetime.today().hour == 11 or datetime.datetime.today().hour == 21) and datetime.datetime.today().minute > 1:
                        if check_bool == False:
                            phrase = "@"+userId+" "+username+"님은 이미 주사위 게임에 참여하셨습니다."
                            add_to_file(filename, tweetId)
                        else:
                            phrase, dice_result = dice_oneshot(userId, username, tweetId, tweet_txt)
                            build_result_list(empty_list, userId, user_number, username, dice_result, sheet_number = 1)
                            add_to_file(filename, tweetId)
                                        
                    elif (datetime.datetime.today().hour == 12 or datetime.datetime.today().hour == 22) and datetime.datetime.today().minute <= 30:
                        if check_bool == False:
                            phrase = "@"+userId+" "+username+"님은 이미 주사위 게임에 참여하셨습니다."
                            add_to_file(filename, tweetId)
                        else:
                            phrase, dice_result = dice_oneshot(userId, username, tweetId, tweet_txt)
                            build_result_list(empty_list, userId, user_number, username, dice_result, sheet_number = 1)
                            add_to_file(filename, tweetId)
                    else:
                        phrase = "@"+userId+" 지금은 주사위 게임 참여시간이 아닙니다."
                        add_to_file(filename, tweetId)            
                    keyword_reply(phrase, tweetId)
                    log_block = reply(tweetTime, username, userId, phrase, tweet_txt)
                    log(log_block, spreadsheet_log)

                elif dice_name == "주사위":
                    phrase = dice_normal(tweet_txt, userId)
                    keyword_reply(phrase, tweetId)
                    log_block = reply(tweetTime, username, userId, phrase, tweet_txt)
                    log(log_block, spreadsheet_log)

                elif dice_name == "잔액":
                    phrase = check_balance(userId, username, user_number, spreadsheet_notice, sheet_number = 1)
                    keyword_reply(phrase, tweetId)
                    log_block = reply(tweetTime, username, userId, phrase, tweet_txt)
                    log(log_block, spreadsheet_log)

                elif dice_name == "복권":
                    phrase = lotto(userId, tweet_txt, filename, tweetId)
                    keyword_reply(phrase, tweetId)
                    log_block = reply(tweetTime, username, userId, phrase, tweet_txt)
                    log(log_block, spreadsheet_log)

                elif bool(vend_name) == True:
                    if vend_name == "없음":
                        phrase =  noKeyword(userId)
                        keyword_reply(phrase, tweetId)
                        log_block = reply(tweetTime, username, userId, phrase, tweet_txt)
                        log(log_block, spreadsheet_log)

                    else:
                        phrase, vend_result = vend_auto(filename, vend, userId, tweetId, tweet_txt, vend_name)
                        update_vend(user_number, vend_result, spreadsheet_notice, sheet_number = 1)
                        keyword_reply(phrase, tweetId)
                        log_block = reply(tweetTime, username, userId, phrase, tweet_txt)
                        log(log_block, spreadsheet_log)

                else:
                    phrase =  noKeyword(userId)
                    keyword_reply(phrase, tweetId)
                    log_block = reply(tweetTime, username, userId, phrase, tweet_txt)
                    log(log_block, spreadsheet_log)

            except:
                continue
            
        time.sleep(20)
