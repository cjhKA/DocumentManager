import os
import json
from PyQt5.QtGui import QIcon


class ShareData():
    def __init__(self):
        self.shareDataPath = "./config.json"
        if os.path.exists(self.shareDataPath):
            with open(self.shareDataPath, "r") as f:
                self.config = json.load(f)
                f.close()
        else:
            self.config = {}

        self.labelDatePath = "./labelData.json"
        if os.path.exists(self.labelDatePath):
            with open(self.labelDatePath, "r") as f:
                self.labelData = json.load(f)
                f.close()
        else:
            self.labelData = {}

        # self.icon = QIcon("./media/ustb.jpg")

    def getMaxBorder(self):
        if "MaxBorder" in self.config.keys():
            return int(self.config["MaxBorder"])
        else:
            return 500


    def getLabels(self):
        if "label" in self.config.keys():
            return self.config["label"]
        else:
            return []

    def setLabels(self, list):
        self.config["label"] = list



    def getAllLabelData(self):
        for label in self.getLabels():
            for name in self.labelData:
                if label not in self.labelData[name].keys():
                    self.labelData[name][label] = ""



        for name in self.labelData:
            for key in list(self.labelData[name].keys()):
                if key not in self.getLabels():
                    self.labelData[name].pop(key)

        return self.labelData


    def getLabelData(self, name):
        if name in self.labelData.keys():
            return self.labelData[name]
        else:
            return {}

    def removeLabelData(self, name):
        if name in self.labelData.keys():
            self.labelData.pop(name)



    def setLabelData(self, name, dict):
        self.labelData[name] = dict

    def getRichTextRoot(self):
        if "RichTextRoot" not in self.config.keys():
            self.config["RichTextRoot"] = "./Data/Text/"
        return self.config["RichTextRoot"]

    def getImageRoot(self):
        if "ImageRoot" not in self.config.keys():
            self.config["ImageRoot"] = "./Data/Image/"
        return self.config["ImageRoot"]

    def getDocumentRoot(self):
        if "DocumentRoot" not in self.config.keys():
            self.config["DocumentRoot"] = "./Data/Document/"
        return self.config["DocumentRoot"]


    def setLabelShow(self, list):
        self.config["LabelShow"] = list

    def getLabelShow(self):
        if "LabelShow" not in self.config.keys():
            self.config["LabelShow"] = ["标题"]+self.getLabels()

        res = []
        for label in self.config["LabelShow"]:
            if label in self.getLabels() + ["标题"]:
                res.append(label)
        return res

    def setCategory(self, dict):
        self.config["Category"] = dict

    def getCategory(self):
        all_name = list(self.getAllLabelData().keys())
        res = {}
        if "Category" not in self.config.keys():
            self.config["Category"] = {}
        for cate in self.config["Category"]:
            for name in self.config["Category"][cate]:
                if name not in all_name:
                    self.config["Category"][cate].remove(name)
        return self.config["Category"]


    def getAllName2Category(self):
        all_list = list(self.getAllLabelData().keys())
        in_dict = {}
        t_category = self.getCategory()
        for _type in t_category:
            for name in t_category[_type]:
                in_dict[name] = _type
        for t in all_list:
            if t not in in_dict.keys():
                in_dict[t] = "##OTHERS##"

        return in_dict


    def getCategoryOrder(self):
        if "CategoryOrder" not in self.config.keys():
            self.config["CategoryOrder"] = list(self.getCategory().keys())
        return self.config["CategoryOrder"]

    def setCategoryOrder(self, order):
        self.config["CategoryOrder"] = order

    def saveShareData(self):
        with open(self.shareDataPath, "w") as f:
            json.dump(self.config, f)
            f.close()
        with open(self.labelDatePath, "w") as f:
            json.dump(self.labelData, f)
            f.close()



sharedata = ShareData()