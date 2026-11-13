# Unity 2021 FBX 实测注意事项

以下来自 Blender 5.2 → Unity 2021.3.30f1 Built-in 的实际资产验证；其他版本应重新验证，不能当作通用硬编码参数。

- 导入glTF前先设置项目采样帧率；FBX往返检查注意导入器的动画起始帧偏移。比较相同时间和相同姿态，不能把不同帧号直接比较。
- Unity动画路径用斜杠分隔层级。对象名称本身含 `/` 等路径分隔符会导致绑定失效：统一修正模型和所有动画中的节点名称，保存旧名→新名映射，不把整个层级路径拍平成一个名字。
- 共享Mesh但对象材质槽覆盖不一致会造成FBX材质索引警告。导出前在内存中复制必要的Mesh数据并保留每个对象的有效材质绑定；不可替代的原工程保留，旧输出按用户保留策略处理。
- Unity可能去掉零面积面。先诊断实际差异，在新版本清理无效面并记录阈值/数量，检查有效轮廓、UV、材质和动画不变；不直接放宽三角面核对来通过验收。
- 旋转部件的Renderer.bounds是保守包围盒。精确导入尺寸检查应把实际顶点变换到同一坐标空间后测量；此检查只能证明格式转换未改比例，不能代替历史尺寸证据。
- 旋转有多种欧拉角表示。复位检查比较位置、缩放和四元数实际旋转，并记录公差；不能因为欧拉角不同就判动画失效，也不能在诊断文件尚未写完时宣布通过。
- FBX内有片段不代表运行时拥有所有恒定通道。逐个片段检查枪口闪光、弹药显示等辅助节点。对未被动画覆盖的TRS通道显式写入正确静止值，保留片段中有意的运动；验证每种片段切换及同片段重播。
- 在编辑器生成.anim时，可把严格恒定的重复关键帧压缩成首尾键；不盲目删除微小但有意的运动。大量曲线使用[AnimationUtility.SetEditorCurves](https://docs.unity3d.com/2021.3/Documentation/ScriptReference/AnimationUtility.SetEditorCurves.html)批量写入，避免每条曲线都重建整段动画。改动后重做姿态和切换检查。
- TextureImporter只在设置实际变化时重导入；共享纹理按语义缓存。glTF AO通常取R，Standard Occlusion读取G，因此要正确重打包，不能把ORM直接当AO或MetallicGloss使用。
- 无图形批处理适合引用、尺度、曲线绑定和Prefab结构检查；Shader存在不能证明画面无粉色。视觉、正常光照PBR、透明材质、Play Mode、构建和平台性能分别标注是否实际测试。
- 创建真正Unity .anim/.mat/.prefab并保留.meta；Legacy Animation与Animator Controller流程分开说明。导出unitypackage时只收录当前有效资产及依赖，原试验按用户保留策略留档或清理，不能混入当前包；检查gzip CRC、tar成员和主Prefab/动画清单。
- “能导入”不等于低面数和低开销。记录模型三角面、材质数、贴图及动画体积；高面数或多材质样板即使技术通过，也应继续标优化待完成。

## 多材质与原生 Specular/Glossiness（纳甘30号实测）

- Unity创建独立材质资源后，`Material.name`可能随资源文件名变为`Material_00`。恢复材质不能以初始Prefab上的运行时名称作为唯一键：先对模型导入器做原始材质ID→目标材质的明确重映射，再按相对Transform路径和槽位，从已映射的FBX给最终Prefab赋值。断言路径唯一、槽位数一致，并在独立项目验证直接FBX与最终Prefab两条入口。
- 源材质含`KHR_materials_pbrSpecularGlossiness`时，GLB再导出的Metallic/Roughness近似不能当作原始材质。保留原始Diffuse、SpecularGloss、Normal、AO及其因子。Built-in可使用`Standard (Specular setup)`；贴图存在时要核实Shader是否真正应用Specular因子，需要派生贴图时对RGB先解码sRGB、乘线性因子、再编码sRGB，保留Gloss Alpha及原文件。
- glTF AO取R、Standard AO取G；即便文件名是独立AO图，也先检查两通道是否相等，不凭名称假设灰度。必要时将原R精确复制到派生图G，保留原图，记录色彩空间与通道验证。纹理修复只重跑材质、GPU和受影响包的独立导入，不重新建模或重烘动画。
- 分组脚本若只支持一个源网格/材质布局，先在创建输出目录前校验各组；跨源网格的附件单列组或实现显式合并槽位，不能直接沿用第一个源网格的面编号。

## 组合武器与共用弹药的Prefab

- UnityEngine.Object 的空对象检查使用 `== null`；编辑器返回的占位对象可能让 `??`/`?.` 与 Unity 重载空值语义不一致。`GetComponent<T>()` 找不到后，显式 `if (component == null)` 再查父节点，避免误报组件缺失。先检查序列化层级及组件再改模型。
- 枪械合并独立弹药Prefab时，先完全解包新版实例，移除弹药自己的Animation组件及嵌套Rigidbody，仅保留合适的运动根刚体。不要修改原共享资源来适配单件组合。
- 对新增弹药节点补全每段动画的完整基准TRS；验证全部片段两两切换、动画路径、可见网格/三角面/材质数、运动学刚体与碰撞随动。旧静态碰撞辅助网格只在新版中替换，不误删原始资产。
- 共用弹药仅放在展品旁边时标“Prefab已整合、装填未联动”，不能把旁侧展示、弹匣位移和根后坐算作真实装填/射击完成。
- 组合Prefab不能套用“一个FBX包含全部网格”的验证器：分别核对枪械与共用模型依赖、组合后的网格/碰撞数量，并在独立项目检验本次包。动画复用/替换不增加有效动画总数。
- 新版仍可能引用旧目录内材质或FBX；清理依据GUID依赖闭包，不依据版本目录名。交付保留Assets相对布局和.meta；导入优先unitypackage，避免将重复GUID源复制进已有Assets。

- 组合资源使用共享弹药时，按父级lossyScale补偿其尺度，并以最终世界空间顶点复核弹药外形尺寸；不能仅相信localScale为1。原展品可能包含弹匣内部展示弹，报告应分清原展品网格与新增独立弹药，不把全部网格称为枪体零件。
- 常量PBR材质和丢失贴图分开判断。对有来源依据的纯色/常量材质，使用明确资产路径白名单并断言Standard Shader、贴图本来为空及参数范围；其他材质仍严格要求贴图，不能为通过检查全局放宽，也不把纯色放大成大纹理冒充新增细节。

## 不同片段数量的组合批次

组合配置逐项指定clipNames、clipsFolder和ammoDimensionsM。源Prefab所在目录不一定包含动画，例如完成材质的Finish目录与Generated动画目录分开。启动前检查所列片段确实存在；不把旧四动画样板套到仅有检视或三展示片段的资产。

预览器同样按实际片段选择视图：缺少Explode时只生成静止检视图，不调用Single查找不存在的拆分动画，也不补造片段来让脚本通过。已有Prefab生成成功而仅预览失败时，修复预览后Validate现有资源，不再重复创建输出目录。

共享弹药新增型号时，外形尺寸从逐项配置读取并按实际顶点验证；不能用二选一型号判断让第三种弹药继承另一口径尺寸。独立源、已整合Prefab、真实装填联动分别记录；补写通道产生的替换动画不计为新增。

## 原生SG材质、批量Editor与来源闭包

- glTF扩展KHR_materials_pbrSpecularGlossiness的Diffuse和SpecularGloss贴图不能按普通Metallic=0近似后称为原生PBR保留。使用Standard (Specular setup)，Specular RGB按sRGB、Gloss在Alpha，保留Glossiness factor、Normal scale、Diffuse factor；Normal为NormalMap且线性，AO线性。Prefab与直接FBX都需重映射至相同材质，并在独立项目核对真实贴图和色彩空间。
- 合法常量BaseColor使用2×2白图加原factor即可；只在源映射没有颜色图且实际未绑定时生成。源声明有图但文件缺失必须报错，不得用白图掩盖。透明Logo/贴花可以alpha factor=1且依赖纹理Alpha；按源BLEND配置，不套用玻璃alpha<0.5的检查。透明正确不代表标识年代正确。
- 深色金属在没有环境反射的审查场景中可能接近黑色。先使用适当环境反射与光照观察纹理，不为审查灯光改坏材质或重复烘焙。临时GPU审查环境与可交付材质分开保存。
- 批量Unity每件重建空场景，避免光源累积；逐件保存完成报告，遇失败只阻止该件的后续采用。技术批次通过后仍需逐件看图。每个工程同一时刻只运行一个Editor；用实际进程完成和报告判断，不盲目等待包含长期子进程的整个进程树。
- GPL来源交付同时放入原始完整源ZIP、许可及当前可编辑源/修改脚本ZIP。只复制txt/json会漏掉COPYING、AC3D源和必要贴图；不要将裸blend放进Unity Assets而意外触发外部Blender转换。授权文字、图片许可与项目原创网格分别标识。
