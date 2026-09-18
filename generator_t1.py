import os
import json
import copy
import random
from bs4 import BeautifulSoup

random.seed(42)

mutation_catalogue = {
    # Ecommerce
    "Sign In": ["Log In", "Login", "Sign in to Account"],
    "Add to Cart": ["Add To Cart", "Add to Basket", "Add Item to Cart"],
    "Buy Now": ["Purchase Now", "Buy It Now", "Checkout Now"],
    "Remove Item": ["Remove", "Delete Item", "Remove from Cart"],
    "Track Order": ["Track My Order", "View Order Status", "Order Tracking"],
    "Apply Coupon": ["Use Coupon", "Redeem Coupon", "Enter Coupon Code"],
    "Continue Shopping": ["Keep Shopping", "Back to Shop", "Browse More Items"],
    "Add to Wishlist": ["Save to Wishlist", "Add to Favorites"],
    "Write a Review": ["Leave a Review", "Add Review"],
    "Compare": ["Add to Compare", "Compare Items"],

    # Healthcare
    "Book Appointment": ["Book an Appointment", "Make Appointment", "Schedule Appointment"],
    "Cancel": ["Cancel Booking", "Dismiss", "Cancel Appointment"],
    "Submit Symptoms": ["Report Symptoms", "Send Symptoms", "Describe Symptoms"],
    "View Reports": ["Check Reports", "See Medical Reports", "View Test Results"],
    "Contact Support": ["Get Help", "Reach Support Team", "Contact Help Desk"],
    "Pay Bill": ["Make Payment", "Pay Invoice", "Settle Bill"],
    "View Prescription": ["See Prescription", "Check Medication List"],
    "Reschedule": ["Change Appointment Time", "Reschedule Booking"],
    "Give Feedback": ["Submit Feedback", "Share Your Feedback"],

    # Government
    "Apply": ["Apply Now", "Submit Application", "Start Application"],
    "Download Document": ["Download", "Download File", "Get Document"],
    "Check Status": ["View Status", "Track Status", "Check Application Status"],
    "Renew License": ["Renew", "Update License", "Apply for Renewal"],
    "Pay Fine": ["Pay Penalty", "Make Payment", "Settle Fine"],
    "Contact Us": ["Send Inquiry", "Get in Touch", "Reach Out"],
    "Upload Documents": ["Attach Files", "Upload Files"],
    "Reserve Appointment": ["Book a Slot", "Schedule a Visit"],
    "Submit Complaint": ["File a Complaint", "Send Complaint"],

    # Education
    "Start Lesson": ["Start the Lesson", "Begin Lesson", "Begin the Class"],
    "Submit Assignment": ["Submit", "Upload Assignment", "Turn In Assignment"],
    "Enroll Now": ["Enroll", "Register for Course", "Sign Up for Course"],
    "Start Quiz": ["Begin Quiz", "Take the Quiz", "Start the Test"],
    "View Grades": ["Check Grades", "See Results", "View Marks"],
    "Download Material": ["Download", "Get Course Material", "Download Notes"],
    "Download Certificate": ["Get Certificate", "Download Certification"],
    "Join Discussion": ["Go to Discussion Board", "Join the Conversation"],
    "View Schedule": ["Check Schedule", "See Timetable"],

    # Common
    "Log Out": ["Sign Out", "Logout", "Exit Account"],
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