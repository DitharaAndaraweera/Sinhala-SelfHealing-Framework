import os
import json
import copy
import random
from bs4 import BeautifulSoup

random.seed(42)

mutation_catalogue = {
    # Ecommerce
    "පිවිසෙන්න": ["පිවිසුම", "ලොග් වන්න", "ගිණුමට පිවිසෙන්න"],
    "කරත්තයට එකතු කරන්න": ["භාණ්ඩය එකතු කරන්න", "කරත්තයට දමන්න", "මිලදී ගැනුම් කරත්තයට එකතු කරන්න"],
    "මිලදී ගන්න": ["මිලට ගන්න", "මිලදී ගැනීම", "දැන් මිලදී ගන්න"],
    "ඉවත් කරන්න": ["ඉවත් කිරීම", "කරත්තයෙන් ඉවත් කරන්න", "මකන්න"],
    "ඇණවුම නිරීක්ෂණය කරන්න": ["ඇණවුම බලන්න", "නිරීක්ෂණය කිරීම", "ප්‍රවේශය පරීක්ෂා කරන්න"],
    "කූපනය යොදන්න": ["වට්ටම් කේතය යොදන්න", "කූපනය භාවිත කරන්න", "කේතය යොදන්න"],
    "සාප්පු සවාරිය දිගටම කරගෙන යන්න": ["දිගටම මිලදී ගැනීම", "සාප්පු සවාරියට ආපසු යන්න", "තවත් භාණ්ඩ බලන්න"],
    "කැමති ලැයිස්තුවට එකතු කරන්න": ["කැමතිතම ලැයිස්තුවට දමන්න", "ප්‍රියතමයන්ට එකතු කරන්න"],
    "සමාලෝචනයක් ලියන්න": ["සමාලෝචනය ලියන්න", "අදහසක් දෙන්න"],
    "සංසන්දනය කරන්න": ["සංසන්දනයට එකතු කරන්න", "සසඳන්න"],

    # Healthcare
    "වෙන් කරවා ගන්න": ["චැනල් කරන්න", "වේලාවක් වෙන් කරන්න", "වෙන් කරවා ගැනීම තහවුරු කරන්න"],
    "අවලංගු කරන්න": ["අවලංගු කිරීම", "නවත්වන්න", "හමුවීම අවලංගු කරන්න"],
    "ලක්ෂණ ඉදිරිපත් කරන්න": ["රෝග ලක්ෂණ යවන්න", "ලක්ෂණ ඉදිරිපත් කිරීම", "රෝග විස්තර දෙන්න"],
    "වාර්තා බලන්න": ["වාර්තා පරීක්ෂා කරන්න", "වෛද්‍ය වාර්තා බලන්න", "පරීක්ෂණ ප්‍රතිඵල බලන්න"],
    "සහාය අමතන්න": ["උදව් ලබාගන්න", "සහායක සේවය අමතන්න", "ආධාර අංශය අමතන්න"],
    "බිල ගෙවන්න": ["ගෙවීම කරන්න", "බිල්පත ගෙවන්න", "මුදල් ගෙවන්න"],
    "බෙහෙත් වට්ටෝරුව බලන්න": ["බෙහෙත් ලැයිස්තුව බලන්න", "වට්ටෝරුව බාගන්න"],
    "නැවත කාලසටහන් කරන්න": ["නැවත වෙලාවක් තියන්න", "කාලසටහන වෙනස් කරන්න"],
    "ප්‍රතිපෝෂණය ලබා දෙන්න": ["අදහස් ලබා දෙන්න", "ප්‍රතිචාර දක්වන්න"],

    # Government
    "ඉල්ලුම් කරන්න": ["අයදුම්පත යවන්න", "ඉල්ලුම් පත්‍රය ඉදිරිපත් කරන්න", "ඉල්ලුම්පත් කරන්න"],
    "ලේඛනය බාගන්න": ["බාගත කරන්න", "බාගැනීම", "ලේඛන බාගත කරන්න"],
    "තත්ත්වය පරීක්ෂා කරන්න": ["තත්ත්වය බලන්න", "පරීක්ෂා කිරීම", "ප්‍රගතිය බලන්න"],
    "බලපත්‍රය අලුත් කරන්න": ["අලුත් කිරීම", "බලපත්‍රය යාවත්කාලීන කරන්න", "අලුත්කිරීමට ඉල්ලුම් කරන්න"],
    "දඩය ගෙවන්න": ["දඩ මුදල ගෙවන්න", "ගෙවීම කරන්න", "දඩය පියවන්න"],
    "අප අමතන්න": ["විමසීමක් යවන්න", "සම්බන්ධ වන්න", "විමසුම් යවන්න"],
    "ලේඛන උඩුගත කරන්න": ["ගොනු උඩුගත කරන්න", "ලේඛන ඇමුණන්න"],
    "හමුවීමක් වෙන් කරන්න": ["හමුවීම වෙන්කරගැනීම", "වේලාවක් වෙන් කරන්න"],
    "පැමිණිල්ලක් ඉදිරිපත් කරන්න": ["පැමිණිල්ලක් ලියන්න", "පැමිණිල්ල යවන්න"],

    # Education
    "පාඩම අරඹන්න": ["පාඩමට පිවිසෙන්න", "ඉගෙනුම් කටයුතු අරඹන්න", "පාඩම පටන් ගන්න"],
    "පැවරුම ඉදිරිපත් කරන්න": ["ඉදිරිපත් කිරීම", "පැවරුම යවන්න", "පැවරුම එවන්න"],
    "ලියාපදිංචි වන්න": ["ලියාපදිංචි වීම", "ලියාපදිංචිය", "පාඨමාලාවට එකතු වන්න"],
    "ප්‍රශ්නාවලිය ආරම්භ කරන්න": ["ප්‍රශ්නාවලිය පටන් ගන්න", "ආරම්භය", "ටෙස්ට් එක පටන් ගන්න"],
    "ලකුණු බලන්න": ["ප්‍රතිඵල බලන්න", "ලකුණු පරීක්ෂා කරන්න", "ලකුණු ලැයිස්තුව බලන්න"],
    "ද්‍රව්‍ය බාගන්න": ["බාගැනීම", "ඉගෙනුම් ද්‍රව්‍ය බාගන්න", "සටහන් බාගන්න"],
    "සහතිකය බාගන්න": ["සහතිකපත්‍රය බාගන්න", "සහතිකය ලබාගන්න"],
    "සාකච්ඡාවට එකතු වන්න": ["සාකච්ඡා පුවරුවට යන්න", "සංවාදයට එකතු වන්න"],
    "කාලසටහන බලන්න": ["කාලසටහන පරීක්ෂා කරන්න", "කාලසටහන් බලන්න"],

    # Common
    "පිටවෙන්න": ["ගිණුමෙන් පිටවෙන්න", "ලොග් අවුට් වන්න", "පිටවීම"],
}

domains = {
    "ecommerce": "Tier2 Synthetic/Ecommerce/ecommerce.html",
    "healthcare": "Tier2 Synthetic/Healthcare/healthcare.html",
    "government": "Tier2 Synthetic/Government/government.html",
    "education": "Tier2 Synthetic/Education/education.html"
}

INTERACTABLE_TAGS = ['button', 'input', 'a', 'select', 'textarea']


def get_xpath(element):
    if element.get('id'):
        return f"//{element.name}[@id='{element.get('id')}']"
    if element.parent:
        siblings = element.parent.find_all(element.name, recursive=False)
        idx = siblings.index(element) + 1
        return f"//{element.name}[{idx}]"
    return f"//{element.name}"


def extract_elements(soup):
    elements = []
    for tag in INTERACTABLE_TAGS:
        for el in soup.find_all(tag):
            visible_text = el.text.strip() if el.text.strip() else (el.get('placeholder', '') or el.get('value', ''))
            elements.append({
                "tag": el.name,
                "id": el.get('id', ''),
                "class_list": el.get('class', []),
                "xpath": get_xpath(el),
                "visible_text": visible_text,
                "bounding_box": None
            })
    return elements


def generate_dataset():
    dataset_records = []

    for domain_name, file_path in domains.items():
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        before_soup = BeautifulSoup(html_content, 'html.parser')
        before_elements = extract_elements(before_soup)

        dataset_records.append({
            "snapshot_id": f"{domain_name}_before",
            "domain": domain_name,
            "state": "before",
            "source_file": file_path,
            "interactable_elements": before_elements
        })

        mutation_counter = 0

        for target_element in before_soup.find_all('button'):
            original_text = target_element.text.strip()
            el_id = target_element.get('id')

            if original_text not in mutation_catalogue:
                continue

            for variant in mutation_catalogue[original_text]:
                mutation_counter += 1

                mutated_soup = copy.deepcopy(before_soup)
                mutated_element = mutated_soup.find('button', id=el_id)
                if mutated_element is None:
                    continue
                mutated_element.string = variant

                roll = random.random()
                if roll < 0.5:
                    original_classes = mutated_element.get('class', [])
                    mutated_element['class'] = original_classes + ['v2']
                elif roll < 0.8:
                    if mutated_element.has_attr('class'):
                        del mutated_element['class']

                if random.random() < 0.5:
                    body_tag = mutated_soup.find('body')
                    if body_tag:
                        decoy = mutated_soup.new_tag('button')
                        decoy['id'] = f'decoy_{domain_name}_{mutation_counter}'
                        decoy['class'] = ['btn-decoy']
                        decoy.string = 'තාවකාලික බොත්තම'
                        children_list = list(body_tag.children)
                        insert_position = random.randint(0, len(children_list))
                        body_tag.insert(insert_position, decoy)

                after_file_path = file_path.replace('.html', f'_after_{mutation_counter}.html')
                with open(after_file_path, 'w', encoding='utf-8') as af:
                    af.write(str(mutated_soup))

                after_elements = extract_elements(mutated_soup)

                dataset_records.append({
                    "snapshot_id": f"{domain_name}_after_{mutation_counter}",
                    "domain": domain_name,
                    "state": "after",
                    "source_file": after_file_path,
                    "target_element_id": el_id,
                    "target_xpath_before": get_xpath(target_element),
                    "before_text": original_text,
                    "after_text": variant,
                    "interactable_elements": after_elements
                })

    output_json_path = "Tier2 Synthetic/tier2_dataset.json"
    with open(output_json_path, 'w', encoding='utf-8') as out_f:
        json.dump(dataset_records, out_f, ensure_ascii=False, indent=4)

    print(f"Dataset generation completed! Total snapshot records: {len(dataset_records)}")
    print(f"JSON saved to: {output_json_path}")


if __name__ == "__main__":
    generate_dataset()