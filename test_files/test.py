def sort_files(file_list, frame_sep):
    sorted_file_list = []
    patterns = []
    for file in file_list:
        pattern = file.split(".")[0].split(frame_sep)[0]
        if pattern not in patterns:
            patterns.append(pattern)
            sorted_file_list.append([file])
        else:
            sorted_file_list[patterns.index(pattern)].append(file)

    for i, sequence in enumerate(sorted_file_list):
        if len(sequence) > 1:
            sorted_file_list[i] = sorted(
                sequence, key=lambda x: int(x.split(".")[0].split(frame_sep)[-1])
            )

    return sorted_file_list


FILES = [
    "mesh-0.vtk",
    "mesh-2.vtk",
    "particles-0.vtk",
    "particles-1.vtk",
    "particles-2.vtk",
    "blocks.vtm",
    "mesh-1.vtk",
]
print(sort_files(FILES, frame_sep="-"))
