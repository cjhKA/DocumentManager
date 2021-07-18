import os
import shutil

#一键打包到dist文件夹下

if os.path.isdir("./dist"):
    shutil.rmtree('./dist')
os.system(f'pyinstaller -y -F -w ./main.py')
os.makedirs("./dist/Data/Image", exist_ok=True)
os.makedirs("./dist/Data/Text", exist_ok=True)
os.makedirs("./dist/Data/Document", exist_ok=True)
shutil.copytree("./media","./dist/media")
shutil.copy("./config.json","./dist/config.json")
shutil.copy("./labelData.json","./dist/labelData.json")
os.rename("./dist/main.exe", "./dist/DocumentManager.exe")


