import argostranslate.package
import argostranslate.translate
 
# 获取可用的语言模型
available_packages = argostranslate.package.get_available_packages()
print("Available language models:")
for package in available_packages:
    print(f"From {package.from_code} to {package.to_code}")
 
# 下载语言模型（例如：英语到中文）
package_to_installs = [
    next((pkg for pkg in available_packages if pkg.from_code == "ja" and pkg.to_code == "en"), None),
    next((pkg for pkg in available_packages if pkg.from_code == "ko" and pkg.to_code == "en"), None)
]

for package_to_install in package_to_installs:
    if package_to_install:
        argostranslate.package.install_from_path(package_to_install.download())
    else:
        print(f"未找到对应的翻译包，可能需要检查网络或可用包列表。")
argostranslate.package.install_from_path(package_to_install.download())