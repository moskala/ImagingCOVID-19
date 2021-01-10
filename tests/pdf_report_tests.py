from context import CustomKivyWidgets
from CustomKivyWidgets.ResultPopupWidget import ResultPopup

from context import Methods

from Analysis.Analysis import Analysis
from Analysis.Result import SeverityResult, AlexnetResult, HaralickGlcmResult, NeuralNetworkResult
from CTWindowing import CTWindow
from ImageClass import ImageType
from ExaminationType import ExaminationType

import numpy as np

print("hello")

image = np.ones((512, 512))

analysis = Analysis(slices_number=10)

info1 = {
            "Filename": "not_exists",
            "File type": ImageType.DCM,
            "Height": 512,
            "Width": 512,
            "CT Window Type": CTWindow.GrayscaleWindow
}
analysis.add_to_list(SeverityResult((15, 1), image, info1, 1, ExaminationType.CT))
analysis.add_to_list(SeverityResult((15, 2), image, info1, 1, ExaminationType.CT))
analysis.add_to_list(SeverityResult((15, 2), image, info1, 1, ExaminationType.CT))
analysis.add_to_list(SeverityResult((0, 0), image, info1, 1, ExaminationType.CT))
analysis.add_to_list(SeverityResult((15, 4), image, info1, 1, ExaminationType.CT))

result = NeuralNetworkResult('COVID-19', image, 512, 512, CTWindow.BoneWindow, "not_exists", 5, ExaminationType.CT)
analysis.add_to_list(result)

analysis.result_list.append([])
analysis.dictionary.append({})
analysis.current_analysis_index += 1
analysis.slices_number.append(7)



result = AlexnetResult('Normal', image, 512, 512, CTWindow.BoneWindow, "not_exists", 5, ExaminationType.CT, None)
analysis.add_to_list(result)


result = HaralickGlcmResult('Normal', image, 512, 512, CTWindow.BoneWindow, "not_exists", 5, ExaminationType.CT, None)
analysis.add_to_list(result)


popup = ResultPopup(analysis)
popup.dismiss()

popup.generate_report_pdf(".", "test.pdf")

print("done pdf")
