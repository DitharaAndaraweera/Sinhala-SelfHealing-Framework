import os
import json
import copy
from bs4 import BeautifulSoup

# 1. Mutation Rules - domain 4ටම අදාළ button texts
mutation_catalogue = {
    "කරත්තයට එකතු කරන්න": ["භාණ්ඩය එකතු කරන්න", "කරත්තයට දමන්න", "මිලදී ගැනුම් කරත්තයට එකතු කරන්න"],
    "වෙන් කරවා ගන්න": ["චැනල් කරන්න", "වේලාවක් වෙන් කරන්න", "වෙන් කරවා ගැනීම තහවුරු කරන්න"],
    "ඉල්ලුම් කරන්න": ["අයදුම්පත යවන්න", "ඉල්ලුම් පත්‍රය ඉදිරිපත් කරන්න"],
    "පාඩම අරඹන්න": ["පාඩමට පිවිසෙන්න", "ඉගෙනුම් කටයුතු අරඹන්න"],
    "පිවිසෙන්න": ["පිවිසුම", "ලොග් වන්න"],
    "අවලංගු කරන්න": ["අවලංගු කිරීම", "නවත්වන්න"],
    "ලේඛනය බාගන්න": ["බාගත කරන්න", "බාගැනීම"],
    "පැවරුම ඉදිරිපත් කරන්න": ["ඉදිරිපත් කිරීම", "පැවරුම යවන්න"]
}

# (වෙනස් කළ කොටස) ඔයාගේ ෆෝල්ඩර් නම් වලට හරියටම ගැලපෙන Paths
domains = {
    "ecommerce": "Tier2 Synthetic/Ecommerce/ecommerce.html",
    "healthcare": "Tier2 Synthetic/Healthcare/healthcare.html",
    "government": "Tier2 Synthetic/Government/government.html",
    "education": "Tier2 Synthetic/Education/education.html"
}

INTERACTABLE_TAGS = ['button', 'input', 'a', 'select', 'textarea']


def get_xpath(element):
    """Simple XPath builder - id තියෙනවනම් ID-based, නැත්තම් position-based"""
    if element.get('id'):
        return f"//{element.name}[@id='{element.get('id')}']"
    if element.parent:
        siblings = element.parent.find_all(element.name, recursive=False)
        idx = siblings.index(element) + 1
        return f"//{element.name}[{idx}]"
    return f"//{element.name}"


def extract_elements(soup):
    """Page එකේ interactable elements ALL extract කරන function"""
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
                # NOTE: bounding_box static HTML parsing එකෙන් ගන්න බෑ.
                # Real coordinates ඕන T3 tier එකේදී Selenium browser render කරලා ගන්න ඕන.
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

        # ---- BEFORE snapshot record ----
        dataset_records.append({
            "snapshot_id": f"{domain_name}_before",
            "domain": domain_name,
            "state": "before",
            "source_file": file_path,
            "interactable_elements": before_elements
        })

        mutation_counter = 0

        # candidate targets - button tags විතරයි (දැනට)
        for target_element in before_soup.find_all('button'):
            original_text = target_element.text.strip()
            el_id = target_element.get('id')

            if original_text not in mutation_catalogue:
                continue

            for variant in mutation_catalogue[original_text]:
                mutation_counter += 1

                # 1. Original DOM එකේ deep copy එකක් ගන්න (physical "after" file හදන්න)
                mutated_soup = copy.deepcopy(before_soup)
                mutated_element = mutated_soup.find('button', id=el_id)
                if mutated_element is None:
                    continue
                mutated_element.string = variant

                # 2. "After" HTML file එක disk එකට physically save කරන්න
                after_file_path = file_path.replace('.html', f'_after_{mutation_counter}.html')
                with open(after_file_path, 'w', encoding='utf-8') as af:
                    af.write(str(mutated_soup))

                # 3. Mutated DOM එකෙන් ALL candidates extract කරන්න
                after_elements = extract_elements(mutated_soup)

                # 4. "After" record - ground truth (target_element_id) එක්කම
                dataset_records.append({
                    "snapshot_id": f"{domain_name}_after_{mutation_counter}",
                    "domain": domain_name,
                    "state": "after",
                    "source_file": after_file_path,
                    "target_element_id": el_id,          # correct answer මේකයි (healing algorithm එකට)
                    "target_xpath_before": get_xpath(target_element),
                    "before_text": original_text,
                    "after_text": variant,
                    "interactable_elements": after_elements   # candidate pool - element ගණනාවක්
                })

    # (වෙනස් කළ කොටස) JSON file එක save වන පාත් එක
    output_json_path = "Tier2 Synthetic/tier2_dataset.json"
    with open(output_json_path, 'w', encoding='utf-8') as out_f:
        json.dump(dataset_records, out_f, ensure_ascii=False, indent=4)

    print(f"Dataset generation completed! Total snapshot records: {len(dataset_records)}")
    print(f"Physical 'after' HTML files also saved inside each domain folder.")
    print(f"JSON saved to: {output_json_path}")


if __name__ == "__main__":
    generate_dataset()