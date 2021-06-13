import os
import re

def rename(cut_path):
    all_files = os.listdir(cut_path)
    palsar2_files = [i for i in all_files if i.startswith('palsar2')]
    for f in palsar2_files:
        old_path = os.path.join(cut_path, f)
        date = re.findall(r'\d{8}', f)[0]
        new_name = re.sub(r'palsar2.*slc', date + '_cut_slc', f)
        new_path = os.path.join(cut_path, new_name)
        os.rename(old_path, new_path)


rename(r'C:\thorly\Files\YG\YGSDcut')