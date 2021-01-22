import re
import pandas as pd
import datetime as dt

class kko:
    def read_kko_msg(self, filename):
        with open(filename, encoding='utf-8') as f:
            msg_list = f.readlines()
        return msg_list

    def check_admin(self, msg):  # true이면 관리자 메시지이다.
        expect_word = ["님이 들어왔습니다", "채팅방 관리자가 메시지를 가렸습니다", "님이 나갔습니다", "삭제된 메시지입니다"]  # 관리자 메시지 제외
        check = False
        for e_w in expect_word:
            if e_w in msg:
                check = True
        return check

    def apply_kko_regex(self, msg_list):
        kko_pattern = re.compile("\[([\S\s]+)\] \[(오전|오후) ([0-9:\s]+)\] ([^\n]+)")
        kko_date_pattern = re.compile("--------------- ([0-9]+년 [0-9]+월 [0-9]+일) ")

        emoji_pattern = re.compile("["u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   "]+", flags=re.UNICODE)

        kko_parse_result = list()
        cur_date = ""

        for msg in msg_list[3:]:
            # 날짜 부분인 경우

            if len(kko_date_pattern.findall(msg)) > 0:
                cur_date = dt.datetime.strptime(kko_date_pattern.findall(msg)[0], "%Y년 %m월 %d일")
                cur_date = cur_date.strftime("%y-%m")
            elif not self.check_admin(msg):
                kko_pattern_result = kko_pattern.findall(msg)
                if len(kko_pattern_result) > 0:
                    tokens = list(kko_pattern_result[0])
                    # 이모지 데이터 삭제
                    tokens[-1] = re.sub(emoji_pattern, "", tokens[-1])
                    tokens.insert(0, cur_date)
                    kko_parse_result.append(tokens)
                else:
                    kko_parse_result[-1][-1] = kko_parse_result[-1][-1] + "\n" + msg

        kko_parse_result = pd.DataFrame(kko_parse_result, columns=["month", "Speaker", "timetype", "time", "contents"])
        kko_parse_result.to_csv("./result/kko_regex.csv", index=False)

        return kko_parse_result

    def run(self, month): # month는 대화 해당 월수
        msg_list = self.read_kko_msg("./raw_data/%s.txt" % (month))
        parse_result = self.apply_kko_regex(msg_list)
        if month != 0: #0이면 전체 대화 출력
            y = month.split()[0][:-1]
            m = month.split()[1][:-1]
            if (len(m) == 1):
                m = "0" + m
            y_m = "%s-%s" % (y, m)
            parse_result = parse_result[parse_result["month"] == y_m]
        return parse_result
