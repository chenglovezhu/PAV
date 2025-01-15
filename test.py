

with open("51CG/data.txt", "r", encoding="utf-8") as file:
    data_list = file.readlines()
    
for data in data_list:
    if "每日大赛" in data:
        print(data)
