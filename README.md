Maya Playblast Tool
====
blaster是一个用于Maya便捷自定义信息的拍屏工具


### 使用要求
- 将程序包克隆到Maya可以导入位置。

- 必须安装Shotgun RV，并且`购买正版License`，并在`blasterEnv.py`里配置RV的路径。

- 需要安装 `pillow` 和 `fire` 库。

- 开发人员需要使用 `_Compile_Exe.cmd` `把processor 编译成exe然后放到生产环境`，
  避免每台电脑安装python 和 依赖库。

- 生产环境内，`blasterEnv.py` 里的 第二个 `PROCESSOR`需要注释掉。


### 调用方法
```python
import blaster
blaster.UI()
```

### 工作流程 How it works

- Maya 拍出tga序列图到 我的文档/playblast (文件名为 月份简写+日期+时间+UUID   `Api24135256_CF8DA4B.0001.tga`)

- PIL 批量添加遮幅、文字

- 使用 RVIO 合成视频

- 删除序列图


### 示例
![](https://github.com/SmartPipeline/blaster/blob/master/resource/temp/caixukun.0290.jpg)
