# TabExtend 下载

TabExtend 是一个 Chrome 新标签页扩展，可以用工作区、分类和分组整理常用链接，也支持笔记和待办。

**[下载最新版本](https://github.com/blingbling2333/TabExtend-releases/releases/latest)** · [所有版本](https://github.com/blingbling2333/TabExtend-releases/releases)

## 安装

1. 打开上面的下载页面，在 **Assets** 中下载 `tabnav-v版本号.zip`。不要下载 `Source code`。
2. 将 ZIP 解压到一个准备长期保留的目录。
3. 在 Chrome 地址栏打开 `chrome://extensions`，开启右上角的「开发者模式」。
4. 点击「加载已解压的扩展程序」，选择直接包含 `manifest.json` 的目录。
5. 打开新标签页即可使用。Chrome 中目前显示的扩展名称是 **TabNav**。

## 更新

1. 建议先在扩展中导出一份备份。
2. 关闭扩展的新标签页，把新版文件解压到原安装目录中；清理旧程序文件，但保留安装目录的路径。
3. 打开 `chrome://extensions`，点击 TabNav 卡片上的重新加载按钮。

无需先卸载扩展。通过本页面安装的版本需要手动下载更新。

## 校验下载

每个版本都附带 `.zip.sha256` 校验文件。macOS/Linux 可以在下载目录执行：

```bash
shasum -a 256 -c tabnav-v版本号.zip.sha256
```

Windows PowerShell 可使用 `Get-FileHash 文件名.zip -Algorithm SHA256`，将结果与校验文件中的值比较。

## 关于这个仓库

这里提供经过自动测试和构建的安装包、下载说明及发布工具。源码仓库保持私有。安装包包含浏览器运行所需的编译后 JavaScript 和资源。

发现问题可以在本仓库 [Issues](https://github.com/blingbling2333/TabExtend-releases/issues) 中反馈，请附上扩展版本、浏览器版本和复现步骤，不要上传账号凭据或私人收藏数据。
