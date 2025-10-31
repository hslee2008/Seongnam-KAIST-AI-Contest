import requests
import xml.etree.ElementTree as ET
import json

def get_exhibition_data(service_key, num_of_rows=10, page_no=1):
    url = f"https://api.kcisa.kr/openapi/API_CCA_145/request?serviceKey={service_key}&numOfRows={num_of_rows}&pageNo={page_no}"
    response = requests.get(url, timeout=60)
    if response.status_code == 200:
        return ET.fromstring(response.content)
    else:
        return None

def xml_to_dict(element):
    if element is None:
        return None
    result = {}
    for child in element:
        child_data = xml_to_dict(child)
        if child.tag in result:
            if type(result[child.tag]) is list:
                result[child.tag].append(child_data if child_data else child.text)
            else:
                result[child.tag] = [result[child.tag], child_data if child_data else child.text]
        else:
            if len(child) == 0:
                result[child.tag] = child.text
            else:
                result[child.tag] = child_data
    return result


