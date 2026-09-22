import os
import json
import copy
import random
from bs4 import BeautifulSoup

random.seed(42)

# ============================================================
# T1 (English) Mutation Catalogue - CORRECTED for FAIR comparison
# දැන් T2 (Sinhala) එකේ pattern එකම follow කරනවා: root word එකම
# තියාගෙන, grammar form විතරයි වෙනස් වෙන්නේ
# (imperative → gerund/infinitive → past tense).
# Synonym swaps (Sign In → Log In) දැන් ඉවත් කරලා තියෙනවා,
# මොකද ඒවා T2 එකේ inflection-only approach එකට match වෙන්නේ නෑ.
# ============================================================
mutation_catalogue = {
    # Ecommerce
    "Sign In": ["Signing In", "To Sign In", "Signed In"],
    "Add to Cart": ["Adding to Cart", "To Add to Cart", "Added to Cart"],
    "Buy Now": ["Buying Now", "To Buy Now", "Bought Now"],
    "Remove Item": ["Removing Item", "To Remove Item", "Removed Item"],
    "Track Order": ["Tracking Order", "To Track Order", "Tracked Order"],
    "Apply Coupon": ["Applying Coupon", "To Apply Coupon", "Applied Coupon"],
    "Continue Shopping": ["Continuing Shopping", "To Continue Shopping"],
    "Add to Wishlist": ["Adding to Wishlist", "To Add to Wishlist"],
    "Write a Review": ["Writing a Review", "To Write a Review"],
    "Compare": ["Comparing", "To Compare", "Compared"],

    # Healthcare
    "Book Appointment": ["Booking Appointment", "To Book Appointment", "Booked Appointment"],
    "Cancel": ["Cancelling", "To Cancel", "Cancelled"],
    "Submit Symptoms": ["Submitting Symptoms", "To Submit Symptoms", "Symptoms Submitted"],
    "View Reports": ["Viewing Reports", "To View Reports", "Reports Viewed"],
    "Contact Support": ["Contacting Support", "To Contact Support"],
    "Pay Bill": ["Paying Bill", "To Pay Bill", "Bill Paid"],
    "View Prescription": ["Viewing Prescription", "To View Prescription"],
    "Reschedule": ["Rescheduling", "To Reschedule", "Rescheduled"],
    "Give Feedback": ["Giving Feedback", "To Give Feedback"],

    # Government
    "Apply": ["Applying", "To Apply", "Applied"],
    "Download Document": ["Downloading Document", "To Download Document", "Document Downloaded"],
    "Check Status": ["Checking Status", "To Check Status", "Status Checked"],
    "Renew License": ["Renewing License", "To Renew License", "License Renewed"],
    "Pay Fine": ["Paying Fine", "To Pay Fine", "Fine Paid"],
    "Contact Us": ["Contacting Us", "To Contact Us"],
    "Upload Documents": ["Uploading Documents", "To Upload Documents", "Documents Uploaded"],
    "Reserve Appointment": ["Reserving Appointment", "To Reserve Appointment"],
    "Submit Complaint": ["Submitting Complaint", "To Submit Complaint", "Complaint Submitted"],

    # Education
    "Start Lesson": ["Starting Lesson", "To Start Lesson", "Lesson Started"],
    "Submit Assignment": ["Submitting Assignment", "To Submit Assignment", "Assignment Submitted"],
    "Enroll Now": ["Enrolling Now", "To Enroll Now", "Enrolled"],
    "Start Quiz": ["Starting Quiz", "To Start Quiz", "Quiz Started"],
    "View Grades": ["Viewing Grades", "To View Grades", "Grades Viewed"],
    "Download Material": ["Downloading Material", "To Download Material", "Material Downloaded"],
    "Download Certificate": ["Downloading Certificate", "To Download Certificate"],
    "Join Discussion": ["Joining Discussion", "To Join Discussion"],
    "View Schedule": ["Viewing Schedule", "To View Schedule"],

    # Common
    "Log Out": ["Logging Out", "To Log Out", "Logged Out"],
}

domains = {
    "ecommerce": "Tier1 English/Ecommerce/ecommerce.html",
    "healthcare": "Tier1 English/Healthcare/healthcare.html",
    "government": "Tier1 English/Government/government.html",
    "education": "Tier1 English/Education/education.html"
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
                        decoy.string = 'Temporary Button'
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
    print(f"JSON saved to: {output_json_path}")


if __name__ == "__main__":
    generate_dataset()