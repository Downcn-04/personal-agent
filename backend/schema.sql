-- Personal Agent Database Schema
-- PostgreSQL 14+

-- ============================================
-- 创建数据库
-- ============================================
-- 注意：如果使用 README 中的 Docker 命令启动，数据库 llmchat 已自动创建，可跳过此步骤
-- 如果手动安装 PostgreSQL，需要先创建数据库

-- 方法一：使用 psql 命令行创建
-- psql -U postgres -c "CREATE DATABASE llmchat;"

-- 方法二：在 psql 中执行
-- CREATE DATABASE llmchat
--     WITH 
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'en_US.utf8'
--     LC_CTYPE = 'en_US.utf8'
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1;

-- COMMENT ON DATABASE llmchat IS '个人智能助理应用数据库';

-- 连接到数据库
\c llmchat;

-- ============================================
-- 表：threads (会话线程表)
-- ============================================
CREATE TABLE IF NOT EXISTS threads (
    id TEXT PRIMARY KEY,                          -- 线程唯一标识符 (UUID)
    title TEXT DEFAULT '',                        -- 线程标题（默认为空）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 创建时间
);

-- 为 threads 表创建索引
CREATE INDEX IF NOT EXISTS idx_threads_created_at ON threads(created_at DESC);

-- ============================================
-- 表：messages (消息表)
-- ============================================
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,                        -- 消息自增 ID
    thread_id TEXT NOT NULL,                      -- 关联的线程 ID
    role TEXT NOT NULL,                           -- 消息角色 (user/assistant/system)
    content TEXT NOT NULL,                        -- 消息内容
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    
    -- 外键约束
    CONSTRAINT fk_messages_thread
        FOREIGN KEY (thread_id) 
        REFERENCES threads(id)
        ON DELETE CASCADE                         -- 删除线程时级联删除消息
);

-- 为 messages 表创建索引
CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- ============================================
-- 注释说明
-- ============================================
COMMENT ON TABLE threads IS '会话线程表，存储聊天会话的基本信息';
COMMENT ON COLUMN threads.id IS '线程唯一标识符，使用 UUID 格式';
COMMENT ON COLUMN threads.title IS '线程标题，默认使用第一条用户消息的前50个字符';
COMMENT ON COLUMN threads.created_at IS '线程创建时间';

COMMENT ON TABLE messages IS '消息表，存储会话中的所有消息';
COMMENT ON COLUMN messages.id IS '消息自增 ID';
COMMENT ON COLUMN messages.thread_id IS '关联的线程 ID';
COMMENT ON COLUMN messages.role IS '消息角色：user(用户)、assistant(助手)、system(系统)';
COMMENT ON COLUMN messages.content IS '消息内容文本';
COMMENT ON COLUMN messages.created_at IS '消息创建时间';

-- ============================================
-- 示例数据（可选）
-- ============================================
-- 插入示例线程
-- INSERT INTO threads (id, title) VALUES 
--     ('550e8400-e29b-41d4-a716-446655440000', '示例对话');

-- 插入示例消息
-- INSERT INTO messages (thread_id, role, content) VALUES 
--     ('550e8400-e29b-41d4-a716-446655440000', 'user', '你好，请介绍一下自己'),
--     ('550e8400-e29b-41d4-a716-446655440000', 'assistant', '你好！我是一个基于 LangGraph 的智能助手。');

-- ============================================
-- 查询示例
-- ============================================
-- 查看所有线程
-- SELECT * FROM threads ORDER BY created_at DESC;

-- 查看特定线程的所有消息
-- SELECT * FROM messages WHERE thread_id = '550e8400-e29b-41d4-a716-446655440000' ORDER BY created_at;

-- 统计每个线程的消息数量
-- SELECT t.id, t.title, COUNT(m.id) as message_count
-- FROM threads t
-- LEFT JOIN messages m ON t.id = m.thread_id
-- GROUP BY t.id, t.title
-- ORDER BY t.created_at DESC;
