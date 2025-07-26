# 字体文件

请将华文宋体字体文件(.ttf或.otf格式)放在此文件夹中，并在项目中引用。

推荐字体文件名：
- STSongti-SC-Regular.ttf
- STSongti-SC-Bold.ttf

## 如何添加字体到项目：

1. 将字体文件拖入此文件夹
2. 在 Xcode 中将字体文件添加到项目 target
3. 在 Info.plist 中添加字体配置：

```xml
<key>UIAppFonts</key>
<array>
    <string>STSongti-SC-Regular.ttf</string>
    <string>STSongti-SC-Bold.ttf</string>
</array>
```

注意：如果字体文件不存在，应用会自动回退到系统字体。 