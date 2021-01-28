import numpy as np
import pandas as pd
from pathlib import Path
import PixelArrays as array

# Total severity score in %
total_severity_score = {
    0: (0, 0),
    1: (0, 25),
    2: (26, 50),
    3: (51, 75),
    4: (76, 100)
}


def calculate_ratio_tts(lung_mask, infection_mask):
    lung_area = np.count_nonzero(lung_mask)
    if lung_area == 0:
        return -1, -1
    infection_area = np.count_nonzero(infection_mask)
    if infection_area == 0:
        return 0, 0
    ratio = infection_area / lung_area * 100
    tts = 0
    for score, (lower, upper) in total_severity_score.items():
        if (ratio >= lower) and (ratio <= upper):
            tts = score
            break

    return ratio, tts


def check_examination(lung_slices, infection_slices):
    analyzed_slices = []
    results = []
    for i in range(len(lung_slices)):
        ratio, score = calculate_ratio_tts(lung_slices[i], infection_slices[i])
        if ratio != -1:
            analyzed_slices.append(i)
            results.append([ratio, score])
    return np.column_stack((analyzed_slices, results))


def create_report_severity(lung_slices, infection_slices):
    # Total number of slices of analyzed image
    total_slices = len(lung_slices)
    result = check_examination(lung_slices, infection_slices)
    # Number of slices with nonzero area of lungmask
    analyzed_slices = result.shape[0]
    # Unique values of severity score with number of occurrence
    unique, counts = np.unique(result[:, 2], return_counts=True)
    unique = unique.astype('int')
    # Percentage of the occurrence of score
    percentages = counts / analyzed_slices * 100

    report = {
        "Total slices": total_slices,
        "Analyzed slices": analyzed_slices,
    }
    for i in range(len(unique)):
        score = unique[i]
        report["Score {0} occurence number".format(score)] = counts[i]
        report["Score {0} percentage number %".format(score)] = percentages[i]

    return report


def create_dataframe_from_nitfi_images(folder_path, save_path=None):
    path = Path(folder_path)
    lungs_path = path / "lung_mask"
    infection_path = path / "infection_mask"

    lungs_files = [x for x in lungs_path.glob('**/*') if x.is_file()]
    infection_files = [x for x in infection_path.glob('**/*') if x.is_file()]

    df = pd.DataFrame(columns=["Image name",
                               "Total slices", "Analyzed slices",
                               "Score 0 occurrence number", "Score 0 percentage number %",
                               "Score 1 occurrence number", "Score 1 percentage number %",
                               "Score 2 occurrence number", "Score 2 percentage number %",
                               "Score 3 occurrence number", "Score 3 percentage number %",
                               "Score 4 occurrence number", "Score 4 percentage number %", ])
    for i in range(len(lungs_files)):
        image_name = lungs_files[i].name
        lung = array.get_pixel_array_nii_all(lungs_files[i])
        infection = array.get_pixel_array_nii_all(infection_files[i])
        report = create_report_severity(lung, infection)
        report["Image name"] = image_name
        df = df.append(report, ignore_index=True)

    df = df.fillna(0)

    if save_path is not None:
        df.to_csv(save_path)

    return df

