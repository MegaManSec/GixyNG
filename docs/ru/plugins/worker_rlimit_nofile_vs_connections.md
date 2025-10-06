# [worker_rlimit_nofile_vs_connections] worker_rlimit_nofile должен быть ≥ 2× worker_connections

Если `worker_rlimit_nofile` слишком мал относительно `worker_connections`, воркеры могут быстро упереться в лимит открытых файловых дескрипторов, что приведёт к сбоям.

## Рекомендация

- Установите `worker_rlimit_nofile` как минимум в два раза больше значения `worker_connections`.

--8<-- "ru/snippets/nginx-extras-cta.md"
