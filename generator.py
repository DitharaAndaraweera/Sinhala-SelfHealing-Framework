import os
import json
import copy
import random
from bs4 import BeautifulSoup

random.seed(42)

# ============================================================
# T2 (Sinhala) Mutation Catalogue - EXPANDED
# Phrase එකකට variants 6ක් (imperative, infinitive, past, future,
# passive, habitual-present) - genuinely challenging character-level
# divergence, root word එකම, semantic meaning එකම.
# ============================================================
mutation_catalogue = {
    # Ecommerce
    "පිවිසෙන්න": ["පිවිසීමට", "පිවිසුණා", "පිවිසෙනු ඇත", "පිවිසෙනු ලැබේ", "පිවිසෙනවා"],
    "කරත්තයට එකතු කරන්න": ["කරත්තයට එකතු කිරීමට", "කරත්තයට එකතු කළා", "කරත්තයට එකතු කරනු ඇත", "කරත්තයට එකතු කරනු ලැබේ", "කරත්තයට එකතු කරනවා"],
    "මිලදී ගන්න": ["මිලදී ගැනීමට", "මිලදී ගත්තා", "මිලදී ගනු ඇත", "මිලදී ගනු ලැබේ", "මිලදී ගන්නවා"],
    "ඉවත් කරන්න": ["ඉවත් කිරීමට", "ඉවත් කළා", "ඉවත් කරනු ඇත", "ඉවත් කරනු ලැබේ", "ඉවත් කරනවා"],
    "ඇණවුම නිරීක්ෂණය කරන්න": ["ඇණවුම නිරීක්ෂණය කිරීමට", "ඇණවුම නිරීක්ෂණය කළා", "ඇණවුම නිරීක්ෂණය කරනු ඇත", "ඇණවුම නිරීක්ෂණය කරනවා"],
    "කූපනය යොදන්න": ["කූපනය යැදීමට", "කූපනය යෙදුවා", "කූපනය යොදනු ඇත", "කූපනය යෙදෙනවා"],
    "සාප්පු සවාරිය දිගටම කරගෙන යන්න": ["සාප්පු සවාරිය දිගටම කරගෙන යෑමට", "සාප්පු සවාරිය දිගටම කරගෙන ගියා", "සාප්පු සවාරිය දිගටම කරගෙන යනු ඇත"],
    "කැමති ලැයිස්තුවට එකතු කරන්න": ["කැමති ලැයිස්තුවට එකතු කිරීමට", "කැමති ලැයිස්තුවට එකතු කළා", "කැමති ලැයිස්තුවට එකතු කරනවා"],
    "සමාලෝචනයක් ලියන්න": ["සමාලෝචනයක් ලිවීමට", "සමාලෝචනයක් ලීවා", "සමාලෝචනයක් ලියනු ඇත"],
    "සංසන්දනය කරන්න": ["සංසන්දනය කිරීමට", "සංසන්දනය කළා", "සංසන්දනය කරනවා"],

    # Healthcare
    "වෙන් කරවා ගන්න": ["වෙන් කරවා ගැනීමට", "වෙන් කරවා ගත්තා", "වෙන් කරවා ගනු ඇත", "වෙන් කරවා ගන්නවා"],
    "අවලංගු කරන්න": ["අවලංගු කිරීමට", "අවලංගු කළා", "අවලංගු කරනු ඇත", "අවලංගු කරනු ලැබේ", "අවලංගු කරනවා"],
    "ලක්ෂණ ඉදිරිපත් කරන්න": ["ලක්ෂණ ඉදිරිපත් කිරීමට", "ලක්ෂණ ඉදිරිපත් කළා", "ලක්ෂණ ඉදිරිපත් කරනු ඇත"],
    "වාර්තා බලන්න": ["වාර්තා බැලීමට", "වාර්තා බැලුවා", "වාර්තා බලනු ඇත", "වාර්තා බලනවා"],
    "සහාය අමතන්න": ["සහාය ඇමතීමට", "සහාය ඇමතුවා", "සහාය අමතනු ඇත"],
    "බිල ගෙවන්න": ["බිල ගෙවීමට", "බිල ගෙව්වා", "බිල ගෙවනු ඇත", "බිල ගෙවනු ලැබේ", "බිල ගෙවනවා"],
    "බෙහෙත් වට්ටෝරුව බලන්න": ["බෙහෙත් වට්ටෝරුව බැලීමට", "බෙහෙත් වට්ටෝරුව බැලුවා", "බෙහෙත් වට්ටෝරුව බලනවා"],
    "නැවත කාලසටහන් කරන්න": ["නැවත කාලසටහන් කිරීමට", "නැවත කාලසටහන් කළා", "නැවත කාලසටහන් කරනවා"],
    "ප්‍රතිපෝෂණය ලබා දෙන්න": ["ප්‍රතිපෝෂණය ලබා දීමට", "ප්‍රතිපෝෂණය ලබා දුන්නා", "ප්‍රතිපෝෂණය ලබා දෙනවා"],

    # Government
    "ඉල්ලුම් කරන්න": ["ඉල්ලුම් කිරීමට", "ඉල්ලුම් කළා", "ඉල්ලුම් කරනු ඇත", "ඉල්ලුම් කරනු ලැබේ", "ඉල්ලුම් කරනවා"],
    "ලේඛනය බාගන්න": ["ලේඛනය බාගැනීමට", "ලේඛනය බාගත්තා", "ලේඛනය බාගනු ඇත", "ලේඛනය බාගන්නවා"],
    "තත්ත්වය පරීක්ෂා කරන්න": ["තත්ත්වය පරීක්ෂා කිරීමට", "තත්ත්වය පරීක්ෂා කළා", "තත්ත්වය පරීක්ෂා කරනු ඇත", "තත්ත්වය පරීක්ෂා කරනවා"],
    "බලපත්‍රය අලුත් කරන්න": ["බලපත්‍රය අලුත් කිරීමට", "බලපත්‍රය අලුත් කළා", "බලපත්‍රය අලුත් කරනු ලැබේ"],
    "දඩය ගෙවන්න": ["දඩය ගෙවීමට", "දඩය ගෙව්වා", "දඩය ගෙවනු ඇත", "දඩය ගෙවනවා"],
    "අප අමතන්න": ["අප ඇමතීමට", "අප ඇමතුවා", "අප අමතනු ඇත"],
    "ලේඛන උඩුගත කරන්න": ["ලේඛන උඩුගත කිරීමට", "ලේඛන උඩුගත කළා", "ලේඛන උඩුගත කරනවා"],
    "හමුවීමක් වෙන් කරන්න": ["හමුවීමක් වෙන් කිරීමට", "හමුවීමක් වෙන් කළා", "හමුවීමක් වෙන් කරනවා"],
    "පැමිණිල්ලක් ඉදිරිපත් කරන්න": ["පැමිණිල්ලක් ඉදිරිපත් කිරීමට", "පැමිණිල්ලක් ඉදිරිපත් කළා", "පැමිණිල්ලක් ඉදිරිපත් කරනු ඇත"],

    # Education
    "පාඩම අරඹන්න": ["පාඩම ආරම්භ කිරීමට", "පාඩම ආරම්භ කළා", "පාඩම ආරම්භ කරනු ඇත", "පාඩම ආරම්භ කරනවා"],
    "පැවරුම ඉදිරිපත් කරන්න": ["පැවරුම ඉදිරිපත් කිරීමට", "පැවරුම ඉදිරිපත් කළා", "පැවරුම ඉදිරිපත් කරනු ලැබේ"],
    "ලියාපදිංචි වන්න": ["ලියාපදිංචි වීමට", "ලියාපදිංචි වුණා", "ලියාපදිංචි වනු ඇත", "ලියාපදිංචි වෙනවා"],
    "ප්‍රශ්නාවලිය ආරම්භ කරන්න": ["ප්‍රශ්නාවලිය ආරම්භ කිරීමට", "ප්‍රශ්නාවලිය ආරම්භ කළා", "ප්‍රශ්නාවලිය ආරම්භ කරනවා"],
    "ලකුණු බලන්න": ["ලකුණු බැලීමට", "ලකුණු බැලුවා", "ලකුණු බලනු ඇත", "ලකුණු බලනවා"],
    "ද්‍රව්‍ය බාගන්න": ["ද්‍රව්‍ය බාගැනීමට", "ද්‍රව්‍ය බාගත්තා", "ද්‍රව්‍ය බාගනු ඇත", "ද්‍රව්‍ය බාගන්නවා"],
    "සහතිකය බාගන්න": ["සහතිකය බාගැනීමට", "සහතිකය බාගත්තා", "සහතිකය බාගන්නවා"],
    "සාකච්ඡාවට එකතු වන්න": ["සාකච්ඡාවට එකතු වීමට", "සාකච්ඡාවට එකතු වුණා", "සාකච්ඡාවට එකතු වෙනවා"],
    "කාලසටහන බලන්න": ["කාලසටහන බැලීමට", "කාලසටහන බැලුවා", "කාලසටහන බලනවා"],

    # Common
    "පිටවෙන්න": ["පිටවීමට", "පිටවුණා", "පිටවෙනු ඇත", "පිටවෙනු ලැබේ", "පිටවෙනවා"],
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