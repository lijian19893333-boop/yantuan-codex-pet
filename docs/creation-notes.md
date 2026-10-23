# Creation notes · 创作说明

Yantuan is a seal-bicolor Ragdoll cat with blue eyes, a broad natural white facial blaze and a soft, rounded silhouette. It was developed with OpenAI image generation, then refined for identity consistency, facial markings, animation poses and transparent sprite boundaries. A privately supplied cat photo informed the appearance; that photo is not included.

焰团的形象是一只海双色布偶猫：蓝眼睛、自然宽白额纹、柔和圆润的轮廓。制作使用了 OpenAI 图像生成，并逐步调整角色一致性、额纹、动作和透明边缘。原始私有猫咪参考照片不包含在仓库中。

## Released artwork · 发布素材

- The sprite sheet is copied byte-for-byte from the maintained local installation.
- It includes the September 27, 2026 idle-tail refinement. Only the idle row changed relative to the immediately preceding artwork; all other rows were preserved.
- The editable source delivered here is the flattened transparent sprite sheet. No layered illustration project or deterministic image-generation pipeline is available in this release.
- 图集从维护中的本机安装逐字节复制，包含 2026-09-27 的待机微摆尾修订。相较前一版只修改待机行，其他行保持一致。
- 可继续编辑的素材是透明图集。此版本不包含分层绘画工程，也不提供可确定性复现画稿的生成流水线。

## Editing guide · 修改方法

Keep the same cat identity across all frames: blue eyes, natural broad white blaze, cream-and-brown fur, soft rounded body and consistent body size. Keep the subject within each 192 × 208 cell; preserve full transparency around the silhouette. Use the existing row layout. Edit a working copy, validate it, and inspect the loop transition in the viewer before replacing an installed asset.

继续修改时保持蓝眼睛、宽白额纹、奶白与棕色毛发、圆润体型和动作间的一致尺寸。每帧主体保持在 192 × 208 格位中，轮廓外保留透明。沿用原有行序，先在副本上修改，完成校验并检查循环衔接后再更新安装。

The offline viewer intentionally presents animation at a simple demonstration cadence. Host interactions and playback timing can change between client versions; the viewer is not a reimplementation of the application's pet engine.

离线预览使用便于检查的演示节奏。不同客户端版本的交互与播放时序可能变化，预览器不复刻客户端宠物引擎。
