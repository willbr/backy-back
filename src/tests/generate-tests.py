from pathlib import Path
from shutil import copyfile
from rich import print

here = Path(__file__).parent
groups = list(here.glob("templates/*/"))

root_folders = "tokeniser parse1_indent parse2_syntax".split()

for name in root_folders:
    for group in groups:
        group_folder = here.joinpath(name).joinpath(group.stem)
        for template_file in group.glob("*"):
            assert template_file.is_file()
            new_folder = group_folder.joinpath(template_file.stem)
            # print(new_folder)
            new_folder.mkdir(parents=True, exist_ok=True)

            out_file = new_folder.joinpath("out.txt")
            # print(out_file)
            out_file.touch(exist_ok=True)

            in_file = new_folder.joinpath("in.txt")
            # print(in_file)
            copyfile(src=template_file, dst=in_file)

