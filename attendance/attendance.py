import sys
import pandas as pd
import os.path
sys.path.append("../util")
from kakao_parse import kko



class Attendance:
    def __init__(self, month):
        with open("./raw_data/memberList.txt", 'r', encoding='UTF8') as f:
            data = f.read()
        self.member_list = data.splitlines()
        temp = [0 for _ in range(len(self.member_list))]
        if not os.path.isfile("./result/attendance.csv"): # 초기 csv 파일이 없으면 생성
            self.attendance = pd.DataFrame({"member": self.member_list, "21년 1월": temp})
            self.attendance = self.attendance.set_index("member")
            self.attendance.to_csv('./result/attendance.csv', encoding="euc-kr")
        else:
            self.attendance = pd.read_csv("./result/attendance.csv", encoding="euc-kr", index_col="member")
            if not month in self.attendance.columns:
                self.attendance[month] = temp
                self.attendance.to_csv('./result/attendance.csv', encoding="euc-kr")

        self.kakao = kko()
        self.parse_result = self.kakao.run(month)

    def run(self, threshold):
        for member in self.member_list:
            mem_parse = self.parse_result[self.parse_result["Speaker"]==member]
            count = 0
            complete_word = "%s 완료" %(member)
            for content in mem_parse['contents']:
                if complete_word in content:
                    count += 1
            self.attendance.loc[member][month] = count
        self.attendance.to_csv('./result/attendance.csv', encoding="euc-kr")
        ban_list = list(self.attendance[self.attendance[month] < threshold].index)
        return ban_list



if __name__ == '__main__':
    threshold = 1 # 1월만 1회
    month = "21년 1월"  # 체크하고 싶은 월수수
    attend = Attendance(month)
    ban_list = attend.run(threshold)
    print(ban_list)

