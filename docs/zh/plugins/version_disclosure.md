# [version_disclosure] 版本泄露

当 `server_tokens` 被设置为不安全的值，或在完整配置模式中缺失该指令时，可能导致版本泄露。

## 能检测什么
- 显式危险值（原有功能）
- 在完整配置分析模式下，缺失 `server_tokens` 指令

## 更佳做法
- 在 HTTP 级或 Server 级合理设置 `server_tokens`；
- 避免在响应中暴露具体版本信息；
- 在仅部分配置可见时，注意分析范围的局限性。

--8<-- "zh/snippets/nginx-extras-cta.md"
