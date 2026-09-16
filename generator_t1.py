import os
import json
import copy
from bs4 import BeautifulSoup

# ============================================================
# T1 (English Baseline) Mutation Catalogue
# NOTE: මේවා English UI වල typical inter-release text changes.
# Sinhala වගේ morphological inflection නෙවෙයි - synonym swaps,
# wording changes, capitalization වගේ SURFACE-LEVEL changes විතරයි.
# මේකයි key difference එක - T1 එකේ character-level similarity
# ඉහළයි, T2 එකේ අඩුයි. ඒක තමයි ඔයාගේ RQ1 හි core claim එක.
# ============================================================
mutation_catalogue = {
    "Add to Cart": ["Add To Cart", "Add to Basket", "Add Item to Cart"],
    "Book Appointment": ["Book an Appointment", "Make Appointment", "Schedule Appointment"],
    "Apply": ["Apply Now", "Submit Application"],
    "Start Lesson": ["Start the Lesson", "Begin Lesson"],
    "Sign In": ["Log In", "Login"],
    "Cancel": ["Cancel Booking", "Dismiss"],
    "Download Document": ["Download", "Download File"],
    "Submit Assignment": ["Submit", "Upload Assignment"]
}

domains = {
    "ecommerce": "Tier1 English/Ecommerce/ecommerce.html",
    "healthcare": "Tier1 English/Healthcare/healthcare.html",
    "government": "Tier1 English/Government/government.html",
    "education": "Tier1 English/Education/education.html"
}

INTERACTABLE_TAGS = ['button', 'input', 'a', 'select', 'textarea']


def get_xpath(element):
    """Simple XPath builder - id තියෙනවනම් ID-based, නැත්නම් position-based"""
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
            "tier": "T1_English",
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

                after_file_path = file_path.replace('.html', f'_after_{mutation_counter}.html')
                with open(after_file_path, 'w', encoding='utf-8') as af:
                    af.write(str(mutated_soup))

                after_elements = extract_elements(mutated_soup)

                dataset_records.append({
                    "snapshot_id": f"{domain_name}_after_{mutation_counter}",
                    "domain": domain_name,
                    "tier": "T1_English",
                    "state": "after",
                    "source_file": after_file_path,
                    "target_element_id": el_id,
                    "target_xpath_before": get_xpath(target_element),
                    "before_text": original_text,
                    "after_text": variant,
                    "interactable_elements": after_elements
                })

    output_json_path = "Tier1 English/tier1_dataset.json"
    with open(output_json_path, 'w', encoding='utf-8') as out_f:
        json.dump(dataset_records, out_f, ensure_ascii=False, indent=4)

    print(f"T1 English dataset generation completed! Total snapshot records: {len(dataset_records)}")
    print(f"Physical 'after' HTML files saved inside each domain folder.")
    print(f"JSON saved to: {output_json_path}")


if __name__ == "__main__":
    generate_dataset()