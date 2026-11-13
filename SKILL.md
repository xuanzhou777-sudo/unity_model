---
name: unity-asset-production
description: Produce or resume batches of researched, textured Unity 3D assets with importable animations, previews, delivery QA, and interruption checkpoints. 用于 Unity 批量资源制作、FBX 材质动画交付和中断续做。
---

# Unity 资源生产与续做

按用户最新要求确定题材、数量、平台、Unity 版本、渲染管线、比例与验收标准。旧要求与新要求冲突时，以较新的明确要求为准；项目特定参数不推广到其他项目。中文任务默认简体中文。

## 流程

1. 先读项目入口、最新有效检查点、逐项清单及需求变更。确认当前资产、引用、授权和预算；对于用户要求先审方案的任务，先提供可审阅方案再等待确认。
2. 制作需求清单，记录固定 ID、分类、型号/版本、尺寸、参考图、来源和许可，以及模型、贴图、动画、图文和 Unity 验收状态。已有 ID 保持稳定。
3. 优先复用授权可用的模型、资料和生产管线。先完成具有代表性的模型、材质、动画和 Unity 导入小样，再扩展批次。质量或历史依据不足时记录缺口，不把生成图当作独立历史证据。
4. 依据平台与镜头距离确定面数，保护轮廓、活动件、分件层级和轴心，用贴图表现适合的细节。按需求制作材质、碰撞、配套物件、展示图、简介及动画。
5. 交付 Unity 可用的真实 FBX、贴图、材质映射及动画。使用目标 Unity 版本和渲染管线实际检查完整 Prefab、贴图、动画、碰撞与比例，再在独立工程验证交付包。按证据分别报告文件存在、技术导入、视觉、比例、历史精度、播放和最终验收状态。
6. 每完成可验证阶段或发生失败时记录检查点。批量任务按项发布进度，恢复时仅重做失效阶段。用户授权清理时核对有效引用、唯一源文件与替代关系，列出并记录删除目标，再验证当前交付。

遵守用户的预算与工具约束，不擅自购买积分。免费或本地方法不能被当作质量合格的证据。用户授权继续后无需重复询问是否开始。

## 按需读取

- [交付及验收规范](delivery-contract.md)：资料、文件夹、FBX/PBR、动画、图片、碰撞和 Unity 验收。
- [二战展馆项目规格](wwii-museum.md)：仅用于本项目，固定清单见 [wwii-catalog.json](wwii-catalog.json)。动态状态以项目最新记录为准。
- [进度与恢复](progress-resume.md)：长任务检查点、实时网页和恢复流程。
- [制作前检查与返工预防](preflight-and-rework-prevention.md)：导出、渲染、清单与打包的易错点。渲染清单校验脚本以本技能根目录解析：`check_render_manifest.py`。
- [Unity 2021 FBX 导入注意事项](unity2021-fbx-import-pitfalls.md)：帧率、材质、层级及动画绑定问题。
- [FBX 回写与表面修订](current-fbx-writeback.md)：Prefab 材质或表面变化后同步当前 FBX。
- [减面与交付验证](lowpoly-validation.md)：减面、GPU 视觉检查及性能范围。

尺寸容差与整体缩放可行性需要分析时，按用户规定的容差运行 `check_uniform_scale_feasibility.py`。数学结果不能代替参考资料或实物测量核验。
