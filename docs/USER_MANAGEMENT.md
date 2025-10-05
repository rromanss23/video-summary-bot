## User Management Guide

**Users are now managed in the database instead of config files!**

### Initial Setup: Migrate Existing Users

If you're upgrading from the old config-based system, run the migration script:

```bash
uv run python scripts/migrate_users_to_db.py
```

This will:
- Read users from `config/users.py`
- Add them to the database
- Create channel subscriptions

### Managing Users via Database

#### Add a New User

```python
from video_summary_bot.database import Database

db = Database()

# Add user
db.add_user(
    user_id="123456789",      # Telegram chat ID
    username="John Doe",       # Display name
    active=True                # Is user active?
)

# Subscribe user to channels
db.subscribe_user_to_channel("123456789", channel_id=1)  # Use channel_id from channels table
```

#### Using SQL Directly

```bash
# Open the database
sqlite3 data/video_summary.db

# Add a user
INSERT INTO users (user_id, username, active) VALUES ('123456789', 'John Doe', 1);

# Subscribe to a channel (find channel_id first)
SELECT channel_id, channel_handle FROM channels;
INSERT INTO user_channels (user_id, channel_id) VALUES ('123456789', 1);

# View all users
SELECT * FROM users;

# View user subscriptions
SELECT u.username, c.channel_handle
FROM users u
JOIN user_channels uc ON u.user_id = uc.user_id
JOIN channels c ON uc.channel_id = c.channel_id;
```

#### Deactivate a User (Soft Delete)

```python
db.deactivate_user("123456789")
```

Or via SQL:
```sql
UPDATE users SET active = 0 WHERE user_id = '123456789';
```

### Getting Your Telegram Chat ID

To find your Telegram chat ID:

1. Start a chat with your bot
2. Send any message
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for `"chat":{"id":123456789}`

Or use the `/start` command with the bot and check the logs.

### Database Schema

**Users Table:**
```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,      -- Telegram chat ID
    username TEXT,                  -- Display name
    active INTEGER DEFAULT 1,       -- Is user active? (1=yes, 0=no)
    created_at TEXT,
    updated_at TEXT
);
```

**Channels Table:**
```sql
CREATE TABLE channels (
    channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_handle TEXT UNIQUE,     -- e.g., "@JoseLuisCavatv"
    channel_name TEXT,
    youtube_channel_id TEXT,        -- Actual YouTube channel ID
    language TEXT DEFAULT 'es',
    ...
);
```

**User-Channel Subscriptions:**
```sql
CREATE TABLE user_channels (
    user_id TEXT,
    channel_id INTEGER,
    subscribed_at TEXT,
    PRIMARY KEY (user_id, channel_id)
);
```

### Best Practices

1. **Never delete users** - Use `active=0` to deactivate instead
2. **Use meaningful usernames** - Helps with debugging and logs
3. **Backup the database** - `cp data/video_summary.db data/video_summary.db.backup`
4. **Test before production** - Add test user, verify it works, then remove

### Advantages Over Config File

✅ **No code changes** - Add/remove users without touching code
✅ **Dynamic** - Changes take effect on next message poll
✅ **Auditable** - See when users were added (`created_at`)
✅ **Scalable** - Can add hundreds of users easily
✅ **Safer** - No sensitive data in version control
✅ **Relational** - Link users to channels properly
