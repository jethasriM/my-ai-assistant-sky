CREATE table IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    deadline_time TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed')),
    delay_count INTEGER DEFAULT 0 CHECK (delay_count >= 0),
    last_aged_at TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE index IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE index IF NOT EXISTS idx_tasks_last_aged_at ON tasks(last_aged_at);