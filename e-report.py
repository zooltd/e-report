import requests
from lxml import etree
import re
import json
import os

def login(USERNAME, PASSWORD):
    s = requests.Session()
    base_url = "https://portal.neu.edu.cn"
    r = s.get(base_url)
    tree = etree.HTML(r.text)
    nodes = tree.xpath("/html/body/div[2]/div/form/input")
    tpass = nodes[3].attrib["value"]
    playload = {
        "rsa": USERNAME + PASSWORD + tpass,
        "ul": str(len(USERNAME)),
        "pl": str(len(PASSWORD)),
        "lt": tpass,
        "execution": nodes[4].attrib["value"],
        "_eventId": nodes[5].attrib["value"],
    }

    url_node = tree.xpath("/html/body/div[2]/div/form")
    append_url = url_node[0].attrib["action"]

    s.post("https://pass.neu.edu.cn" + append_url, data=playload)
    r = s.get("https://e-report.neu.edu.cn/notes/create")
    tree = etree.HTML(r.text)
    token_node = tree.xpath("/html/head/meta[4]")
    token = token_node[0].attrib["content"]

    js = tree.xpath("/html/body/script[2]/text()")[0]
    regex = r"if \(value == 1\)[\s]*{[\s]*\$.getJSON\(\"([\w\W]*)\"\).then"
    match = re.search(regex, js)
    query_url = match.group(1)
    query_url = query_url.replace("\\", "")
    r = s.get(query_url)
    info_dict = json.loads(r.text)

    report_info = {
        "_token": token,
        "jibenxinxi_shifoubenrenshangbao": "1",
        "profile[xuegonghao]": info_dict["data"]["xuegonghao"],
        "profile[xingming]": info_dict["data"]["xingming"],
        "profile[suoshubanji]": info_dict["data"]["suoshubanji"],
        "jiankangxinxi_muqianshentizhuangkuang": "正常",
        "xingchengxinxi_weizhishifouyoubianhua": "0",
        "cross_city": "无",
    }

    report_api = "https://e-report.neu.edu.cn/api/notes"
    r = s.post(report_api, data=report_info)
    print(r.status_code)


if __name__ == "__main__":
    USERNAME = os.environ["USERNAME"]
    PASSWORD = os.environ["PASSWORD"]
    login(USERNAME, PASSWORD)
