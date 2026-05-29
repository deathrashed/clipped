#!/bin/zsh

echo "🎵 Installing Clipped Toolkit..."

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

# 1. Setup config
CONFIG_DIR="$HOME/.config/clipped"
mkdir -p "$CONFIG_DIR"

if [[ ! -f "$CONFIG_DIR/config.toml" ]]; then
    cp config.example.toml "$CONFIG_DIR/config.toml"
    echo "✅ Created default config at $CONFIG_DIR/config.toml"
else
    echo "ℹ️ Config already exists at $CONFIG_DIR/config.toml"
fi

# 2. Setup shared python environment
echo "📦 Installing/updating dependencies in shared runtime..."
GLOBAL_REQ="$HOME/Scripts/.config/python/requirements.txt"
if [[ -f "$GLOBAL_REQ" ]]; then
    for req in typer rich questionary yt-dlp mutagen; do
        if ! grep -q "^$req" "$GLOBAL_REQ"; then
            echo "$req" >> "$GLOBAL_REQ"
        fi
    done
fi
bash "$HOME/Scripts/.config/python/setup.sh"

# 3. Setup wrapper
cat > bin/clipped << 'EOF'
#!/bin/zsh
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$REPO_DIR"
source "$HOME/Scripts/.config/python/env.sh"
exec "$HOME/Scripts/.config/python/run.sh" -m clipped_src.main "$@"
EOF

chmod +x bin/clipped
rm -f bin/clipped-video # Removed as it's now `clipped video`
echo "✅ Set up 'clipped' wrapper script."

# 4. Generate completions
echo "🚀 Setting up completions..."
"$HOME/Scripts/.config/python/run.sh" -m clipped_src.main --install-completion zsh 2>/dev/null || true

# 5. Add to PATH
REPO_BIN="$REPO_DIR/bin"
if grep -q "$REPO_BIN" ~/.zshrc; then
    echo "ℹ️ Path already in ~/.zshrc"
else
    echo "export PATH=\"\$PATH:$REPO_BIN\"" >> ~/.zshrc
    echo "✅ Added $REPO_BIN to ~/.zshrc PATH."
    echo "   Please run 'source ~/.zshrc' or restart your terminal to apply."
fi

echo "🎉 Installation complete! Try running 'clipped --help'"
