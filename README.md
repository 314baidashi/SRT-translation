# SRT字幕翻译工具

## 功能简介
本工具是一款基于Python开发的SRT字幕文件翻译工具，您可以和potplayer生成有声字幕协同使用，支持通过拖放操作快速导入SRT文件，并提供多语言互译功能，可以从日、韩、英译中，日、韩译英。翻译完成后自动生成对应语言后缀的目标语言字幕文件，方便播放器自动读取。

## 下载链接
[点击此处下载最新版exe安装包（157MB）](https://download.csdn.net/download/weixin_45826970/90890917?spm=1001.2014.3001.5503)

为了帮大家节省时间，我帮大家把需要魔法下载的生成有声字幕引擎和英文base模型打包到下方，可以一起下载（两个文件分别对应PotPlayer根目录的两个同名文件夹，直接拖入替换即可，注意我的引擎基于英伟达显卡，如果你的电脑不是请自己找其他版本）

[CUDA版引擎百度云](https://pan.baidu.com/s/1tiQN_B3AnomAAp_Efv18DA?pwd=wr3b)

[英文识别base模型百度云](https://pan.baidu.com/s/166IBw-ygfWi3xUpopTL-WA?pwd=pknu)

## 注意事项
- 模型文件已经尽可能小，但还是需要一点时间加载，耐心等待。
- 当翻译开始时程序出现未响应状态，这是正常现象，请勿关闭程序。
- 翻译完成后，会自动生成`_translated.srt`后缀的目标语言字幕文件，并保存到源文件目录。

## 使用模型
核心翻译功能基于[Argos Translate](https://github.com/argosopentech/argos-translate)开源机器翻译库实现，支持离线翻译。

## 界面演示
### 主界面
![主界面](img/index.png)

### 原文件
![原语言](img/en.png)

### 翻译效果
![目标语言](img/zh.png)


