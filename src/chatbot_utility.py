import os

working_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(working_dir)

def get_chapter_list(selected_subject):
    if selected_subject == "Biology":
        subject_name = selected_subject.lower()
        chapters_dir = f"{parent_dir}/data/class_12/{subject_name}"
        chapter_list = os.listdir(chapters_dir)
        chapter_list.sort(key=lambda x: int(x.split('.')[0]))
        return chapter_list
    return []