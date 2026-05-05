def team_abbr_to_ch(abbr):
    if abbr is None:
        return "未知"

    abbr = str(abbr).upper().strip()
    mapping = {
        "ATL": "亞特蘭大老鷹",
        "BOS": "波士頓塞爾提克",
        "BKN": "布魯克林籃網",
        "CHA": "夏洛特黃蜂",
        "CHI": "芝加哥公牛",
        "CLE": "克里夫蘭騎士",
        "DAL": "達拉斯獨行俠",
        "DEN": "丹佛金塊",
        "DET": "底特律活塞",
        "GSW": "金州勇士",
        "HOU": "休士頓火箭",
        "IND": "印第安那溜馬",
        "LAC": "洛杉磯快艇",
        "LAL": "洛杉磯湖人",
        "MEM": "曼菲斯灰熊",
        "MIA": "邁阿密熱火",
        "MIL": "密爾瓦基公鹿",
        "MIN": "明尼蘇達灰狼",
        "NOP": "新奧爾良鵜鶘",
        "NYK": "紐約尼克",
        "OKC": "奧克拉荷馬雷霆",
        "ORL": "奧蘭多魔術",
        "PHI": "費城七六人",
        "PHX": "鳳凰城太陽",
        "POR": "波特蘭拓荒者",
        "SAC": "薩克拉門托國王",
        "SAS": "聖安東尼奧馬刺",
        "TOR": "多倫多暴龍",
        "UTA": "猶他爵士",
        "WAS": "華盛頓巫師",
        "NOK": "紐奧良黃蜂",
        "PHW": "費城勇士隊",
    }
    return mapping.get(abbr, abbr or "未知")
