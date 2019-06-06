Maya Playblast Tool
====
blaster是一个用于Maya便捷自定义信息的拍屏工具


### 使用要求 Requirements
- 将程序包克隆到Maya可以导入位置。

- 合成视频默认使用FFmpeg，FFmpeg需要自行下载, 下载位置在 resource/ffmpeg/README.txt，或者改为自己的ffmpeg路径。

- 播放视频默认使用Rv，需要安装Shotgun RV，并且`购买正版License`，然后在`blasterEnv.py`里配置RV的路径。

- 需要安装 `numpy` `pillow` `progressbar2` `fire` `pyinstaller` 库。

- 开发人员需要使用 `_Compile_Exe.cmd` `把processor 编译成exe然后放到生产环境`，
  避免每台电脑安装python 和 依赖库。

- 测试环境内，`blasterEnv.py` 里的 第二个 `PROCESSOR`需要打开, 让开发人员使用processor.py测试

- 生产环境内，`blasterEnv.py` 里的 第二个 `PROCESSOR`需要注释掉, 让用户默认使用processor.exe


### 调用方法 How To Use
```python
import blaster
blaster.UI()
```

### 工作流程 How It Works

- Maya 拍出tga序列图到 我的文档/playblast (文件名为 月份简写+日期+时间+UUID   `Api24135256_CF8DA4B.0001.tga`)

- PIL 批量添加遮幅、文字

- 合成视频

- 删除序列图


### 示例 Example
![](https://github.com/SmartPipeline/blaster/blob/master/resource/temp/caixukun.0290.jpg)
