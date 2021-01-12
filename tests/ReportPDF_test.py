import numpy as np
import os

from TestsContext import CustomKivyWidgets, Methods
from CustomKivyWidgets.ResultPopupWidget import ResultPopup

from Methods.Analysis.Analysis import Analysis
from Methods.Analysis.Result import SeverityResult, AlexnetResult, HaralickGlcmResult, NeuralNetworkResult
from Methods.ImageMedical.CTWindowing import CTWindow
from Methods.ImageMedical.ImageClass import ImageType
from Methods.ExaminationType import ExaminationType


def add_new_examintation(test_analysis):
    test_analysis.result_list.append([])
    test_analysis.dictionary.append({})
    test_analysis.current_analysis_index += 1
    test_analysis.slices_number.append(7)


def add_severity_results(test_analysis):
    image = np.ones((512, 512))

    info1 = {
        "Filename": "not_exists",
        "File type": ImageType.DCM,
        "Height": 512,
        "Width": 512,
        "CT Window Type": CTWindow.GrayscaleWindow
    }
    test_analysis.add_to_list(SeverityResult((15, 1), image, info1, 1, ExaminationType.CT))
    test_analysis.add_to_list(SeverityResult((15, 2), image, info1, 1, ExaminationType.CT))
    test_analysis.add_to_list(SeverityResult((15, 2), image, info1, 1, ExaminationType.CT))
    test_analysis.add_to_list(SeverityResult((0, 0), image, info1, 1, ExaminationType.CT))
    test_analysis.add_to_list(SeverityResult((15, 4), image, info1, 1, ExaminationType.CT))


def add_neural_network_results(test_analysis):
    image = np.ones((512, 512))
    result = NeuralNetworkResult('COVID-19', image, 512, 512, CTWindow.BoneWindow, "not_exists", 5, ExaminationType.CT)
    test_analysis.add_to_list(result)


def add_alexnet_results(test_analysis):
    image = np.ones((512, 512))
    result = AlexnetResult('Normal', image, 512, 512, CTWindow.BoneWindow, "not_exists", 5, ExaminationType.CT, None)
    test_analysis.add_to_list(result)


def add_haralick_results(test_analysis):
    image = np.ones((512, 512))
    result = HaralickGlcmResult('Normal', image, 512, 512, CTWindow.BoneWindow, "not_exists", 5, ExaminationType.CT,
                                None)
    test_analysis.add_to_list(result)


def prepare_analysis():
    test_analysis = Analysis(slices_number=10)

    add_new_examintation(test_analysis)
    add_severity_results(test_analysis)

    add_new_examintation(test_analysis)
    add_neural_network_results(test_analysis)

    add_new_examintation(test_analysis)
    add_alexnet_results(test_analysis)
    add_haralick_results(test_analysis)

    return test_analysis


def test_popup(test_analysis, folder, filename):
    popup = ResultPopup(test_analysis)
    popup.dismiss()

    popup.generate_report_pdf(folder, filename)


def test_file_exists(folder, filename):
    check = os.path.isfile(os.path.join(folder, filename))
    assert check is True, "File does exist!"


def delete_file(folder, filename):
    os.remove(os.path.join(folder, filename))


def test_file_not_exists(folder, filename):
    check = os.path.isfile(os.path.join(folder, filename))
    assert check is False, "File does exist!"


if __name__ == "__main__":
    analysis = prepare_analysis()
    folder = os.path.abspath(os.path.dirname(__file__))
    filename = "test.pdf"
    test_popup(analysis, folder, filename)
    test_file_exists(folder, filename)
    delete_file(folder, filename)
    test_file_not_exists(folder, filename)
    print("Everything passed")





