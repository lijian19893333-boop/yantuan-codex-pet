# 焰团图集格式 / Yantuan sprite layout

本包使用 Codex v2 宠物图集。`pet.json` 通过 `spritesheetPath` 引用 `spritesheet.webp`，并声明 `spriteVersionNumber: 2`。本包提供角色素材；动画触发、节奏和桌面交互由宿主应用实现。

This package uses the Codex v2 pet atlas. The manifest references `spritesheet.webp` with `spritesheetPath` and declares `spriteVersionNumber: 2`. The package supplies character artwork; the host application implements animation triggers, timing, and desktop interaction.

| 属性 / Property | 值 / Value |
| --- | --- |
| 文件 / File | `pets/yantuan-ragdoll/spritesheet.webp` |
| 图像 / Image | Transparent RGBA WebP, 1536 × 2288 px |
| 网格 / Grid | 8 columns × 11 rows |
| 单格 / Cell | 192 × 208 px |
| 索引 / Indexing | Zero-based rows and columns, from the top-left |
| 动作和方向帧 / Action and directional frames | 73 |
| 额外中立帧 / Additional neutral frame | Row 0, column 6 |

## 动作行 / Action rows

每行动画从第 0 列开始，按列顺序播放有效帧。行名是格式与宿主中的状态标识；画面内容可以与字面名称不同。例如 `jumping` 行在焰团中呈现擦玻璃动作。界面中的“工作”“完成”“悬停”描述对应此素材的设计用途，实际触发取决于宿主版本。

Animation rows start at column 0 and use the listed frames in order. State identifiers describe atlas slots, which may contain artwork different from their literal names: Yantuan's `jumping` row contains a glass-wiping gesture. Labels such as working, review, and hover describe the artwork's intended use; actual triggers depend on the host version.

| 行 / Row | 状态 / State | 帧数 / Frames | 焰团画面 / Artwork |
| --- | --- | ---: | --- |
| 0 | `idle` | 6 | 坐姿、眨眼、看蝶、小哈欠与轻微摆尾 / Sitting, blinking, watching butterflies, a small yawn, and subtle tail movement |
| 1 | `running-right` | 8 | 向右追蝶 / Chasing a butterfly to the right |
| 2 | `running-left` | 8 | 向左追蝶 / Chasing a butterfly to the left |
| 3 | `waving` | 4 | 招手 / Waving |
| 4 | `jumping` | 5 | 两只前爪擦玻璃 / Glass-wiping with the front paws |
| 5 | `failed` | 8 | 失落反应 / Disappointed reaction |
| 6 | `waiting` | 6 | 等待、轻微歪头与眨眼 / Waiting, small head tilts, and blinking |
| 7 | `running` | 6 | 工作时追蝶 / Butterfly chase for the working state |
| 8 | `review` | 6 | 擦玻璃 / Glass-wiping |
| 9 | Directional look | 8 | 0°–157.5° |
| 10 | Directional look | 8 | 180°–337.5° |

第 0 行第 6 列是独立的中立注视帧，不属于 6 帧待机循环。其他未使用单元格应保持透明。

Row 0, column 6 is a separate neutral look frame, outside the six-frame idle loop. Other unused cells should remain transparent.

## 注视方向 / Look directions

方向帧是根据目标方位选择的静态姿势，不是连续动画。以正上方为 0°，顺时针每格增加 22.5°。

Look frames are individual poses selected for a target direction, not a continuous animation. Angles begin at 0° pointing up and increase clockwise in steps of 22.5°.

| 列 / Column | 第 9 行 / Row 9 | 第 10 行 / Row 10 |
| ---: | --- | --- |
| 0 | 0° · 上 / Up | 180° · 下 / Down |
| 1 | 22.5° | 202.5° |
| 2 | 45° · 右上 / Up-right | 225° · 左下 / Down-left |
| 3 | 67.5° | 247.5° |
| 4 | 90° · 右 / Right | 270° · 左 / Left |
| 5 | 112.5° | 292.5° |
| 6 | 135° · 右下 / Down-right | 315° · 左上 / Up-left |
| 7 | 157.5° | 337.5° |

裁切坐标 / Crop coordinates:

```text
x = column × 192
y = row × 208
width = 192
height = 208
```

## 离线预览 / Offline preview

直接打开 [`preview/index.html`](../preview/index.html)。页面只引用仓库内的原始 WebP，使用 CSS 背景定位显示单格，不会改写图片，不需要服务器或网络连接。

Open [`preview/index.html`](../preview/index.html) directly. The page references the original local WebP and displays individual cells with CSS background positioning. It does not modify the image and requires no server or network connection.

- 动作选择、播放/暂停、上一帧/下一帧和拖动单帧滑块。 / Select an action, play or pause, step through frames, or move the frame slider.
- 独立选择 16 个注视方向或中立注视帧；静态姿势不自动播放。 / Select any of the 16 look directions or the neutral pose; still poses do not autoplay.
- 浅色或深色背景用于检查透明边缘。 / Use light or dark backgrounds to inspect transparent edges.
- 检测到系统“减少动态效果”偏好时，初始暂停。 / Starts paused when the system requests reduced motion.

预览页的播放时长用于查看画面，不是宿主行为规范。即使静态单元格可正常预览，也不能单凭本页确认某个 Codex 版本中的动作触发与表现。

Preview durations are viewing aids, not a specification of host behavior. A successful atlas preview alone does not verify triggers or presentation in a particular Codex version.
