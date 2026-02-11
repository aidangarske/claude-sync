# claude-sync

Transfer Claude Code sessions between machines with a single command.

## Installation

```bash
git clone https://github.com/aidangarske/claude-sync.git
cd claude-sync
./install.sh
```

Or install directly:

```bash
curl -fsSL https://raw.githubusercontent.com/aidangarske/claude-sync/master/src/claude-sync -o ~/.local/bin/claude-sync && chmod +x ~/.local/bin/claude-sync
```

**Install on BOTH machines** (source and destination).

## Usage

```bash
# Push a session to another machine
claude-sync push user@host --session abc123

# Pull a session from another machine
claude-sync pull user@host --session abc123

# List sessions on another machine
claude-sync list user@host --details
```

## Commands

| Command | Description |
|---------|-------------|
| `claude-sync` | List local sessions |
| `claude-sync --details` | List with session details |
| `claude-sync list user@host` | List sessions on remote |
| `claude-sync push user@host` | Push all sessions to remote |
| `claude-sync push user@host -s ID` | Push specific session |
| `claude-sync push user@host -p NAME` | Push specific project |
| `claude-sync pull user@host` | Pull all sessions from remote |
| `claude-sync pull user@host -s ID` | Pull specific session |
| `claude-sync pull user@host -p NAME` | Pull specific project |
| `claude-sync export` | Export to local file |
| `claude-sync import FILE` | Import from local file |

## Examples

```bash
# List local sessions with details
claude-sync --details

# Push specific session to remote
claude-sync push aidangarske@192.168.1.50 --session ed5ec4bf

# Push entire project
claude-sync push user@host --project wolfip

# Pull session from remote
claude-sync pull pi@raspberrypi --session abc123

# List what's on remote
claude-sync list user@host --details
```

## Project Structure

```
claude-sync/
├── src/
│   └── claude-sync      # Main executable
├── test/
│   └── test_claude_sync.py
├── docs/
├── install.sh
├── README.md
└── LICENSE
```

## How It Works

1. **push**: Export locally -> transfer via SSH -> import on remote
2. **pull**: Export on remote -> transfer via SSH -> import locally
3. **Path remapping**: Automatically converts `/Users/alice/...` to `/Users/bob/...`

## Requirements

- Python 3.6+
- SSH access between machines
- `claude-sync` installed on both machines

## Testing

```bash
# Run local tests
python3 test/test_claude_sync.py

# Run with remote tests
python3 test/test_claude_sync.py user@host
```

## License

MIT
