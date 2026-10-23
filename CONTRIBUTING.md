# Contributing · 参与贡献

English and Chinese reports and pull requests are welcome.

1. Describe the problem and expected result. For app integration, include the operating system and client version.
2. Keep changes focused. Preserve the pet ID and row layout unless a migration is documented.
3. Run `python3 scripts/validate.py` and `python3 -m unittest discover -s tests -v`.
4. Inspect affected frames, transparent edges and loop transitions in `preview/index.html`.
5. Include only artwork and code you have permission to contribute. Do not upload personal photos, credentials, private logs or screenshots containing account details.

欢迎中文或英文反馈与 PR。说明问题和预期结果；涉及客户端时附上系统和版本。保持修改范围清楚，运行校验和测试，并在离线预览中查看动作衔接。仅提交有权分享的素材与代码，避免上传私人照片、凭据或包含账号信息的日志截图。

Contributions are provided under this repository's MIT license. Report compatibility limits accurately; a successful preview does not establish that every host version loads the pet.

贡献使用本仓库 MIT 许可。请如实描述兼容性：预览成功不等于所有客户端版本都能加载。
