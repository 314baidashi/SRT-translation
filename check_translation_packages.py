import argostranslate.package

installed_packages = argostranslate.package.get_installed_packages()
for package in installed_packages:
    print(f'安装的翻译包: {package.from_code} 到 {package.to_code}')