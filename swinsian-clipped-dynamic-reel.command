#!/bin/zsh

# Swinsian -> Clipped Dynamic Reel
# Standalone Swinsian automation.

set -u
set -o pipefail

# ── Configuration ────────────────────────────────────────────────────────────

CLIPPED_BIN="/Users/rd/Scripts/Riley/clipped/bin/clipped"
TEMPLATE="reel"
PLATFORM="vertical_full"
FADE="0.5"

# Leave OUTPUT_NAME empty to let clipped choose its normal output and copy the
# result to the clipboard. To force a filename, set it without or with .mp4.
OUTPUT_DIR="$HOME/Music/clipped/_video"
OUTPUT_NAME=""
OPEN_OUTPUT="false"

# ── Helpers ──────────────────────────────────────────────────────────────────

show_error() {
  /usr/bin/osascript \
    -e 'on run argv' \
    -e 'display dialog (item 1 of argv) buttons {"OK"} default button "OK" with title "Clipped" with icon stop' \
    -e 'end run' \
    "$1" >/dev/null 2>&1 || true
}

notify() {
  /usr/bin/osascript \
    -e 'on run argv' \
    -e 'display notification (item 1 of argv) with title "Clipped"' \
    -e 'end run' \
    "$1" >/dev/null 2>&1 || true
}

prompt_for_value() {
  local prompt_text="$1"
  local default_value="$2"

  /usr/bin/osascript \
    -e 'on run argv' \
    -e 'set resultDialog to display dialog (item 1 of argv) default answer (item 2 of argv) buttons {"Cancel", "OK"} default button "OK" cancel button "Cancel" with title "Swinsian - Dynamic Reel Range"' \
    -e 'return text returned of resultDialog' \
    -e 'end run' \
    "$prompt_text" "$default_value"
}

# ── Read the selected Swinsian track ─────────────────────────────────────────

TRACK_PATH=$(/usr/bin/osascript 2>/dev/null <<'APPLESCRIPT'
tell application "Swinsian"
	if not running then error "Swinsian is not running."
	set selectedTracks to selection of front window
	if selectedTracks is {} then error "Select one track in Swinsian first."
	return path of item 1 of selectedTracks as text
end tell
APPLESCRIPT
)

if [[ $? -ne 0 || -z "$TRACK_PATH" ]]; then
  show_error "Select one track in Swinsian first, then run this script again."
  exit 1
fi

TRACK_SUMMARY=$(/usr/bin/osascript 2>/dev/null <<'APPLESCRIPT'
tell application "Swinsian"
	set selectedTrack to item 1 of (selection of front window)

	try
		set trackTitle to name of selectedTrack
	on error
		set trackTitle to ""
	end try

	try
		set artistName to artist of selectedTrack
	on error
		set artistName to ""
	end try

	try
		set albumName to album of selectedTrack
	on error
		set albumName to ""
	end try
end tell

set trackSummary to artistName
if trackTitle is not "" then
	if trackSummary is not "" then
		set trackSummary to trackSummary & " - " & trackTitle
	else
		set trackSummary to trackTitle
	end if
end if
if albumName is not "" then
	if trackSummary is not "" then
		set trackSummary to trackSummary & " (" & albumName & ")"
	else
		set trackSummary to albumName
	end if
end if
return trackSummary
APPLESCRIPT
)

[[ -z "$TRACK_SUMMARY" ]] && TRACK_SUMMARY="$TRACK_PATH"

if [[ ! -f "$TRACK_PATH" ]]; then
  show_error "The selected Swinsian track path could not be resolved:\n\n$TRACK_PATH"
  exit 1
fi

if [[ ! -x "$CLIPPED_BIN" ]]; then
  show_error "The clipped CLI is missing or is not executable:\n\n$CLIPPED_BIN"
  exit 1
fi

# ── Ask for the reel range ───────────────────────────────────────────────────

START=$(prompt_for_value \
  "Selected: $TRACK_SUMMARY

Enter the start time for the Dynamic Reel.
Examples: 0, 30, 2:45." \
  "0") || exit 0

END=$(prompt_for_value \
  "Selected: $TRACK_SUMMARY

Start: $START

Enter the end time for the Dynamic Reel.
There is no 60-second export limit.
Examples: 30, 1:00, 3:45." \
  "1:00") || exit 0

if [[ -z "$START" || -z "$END" ]]; then
  show_error "Start and end times are required."
  exit 1
fi

# ── Prepare the detached Terminal job ────────────────────────────────────────

OUTPUT_PATH=""
if [[ -n "$OUTPUT_NAME" ]]; then
  /bin/mkdir -p "$OUTPUT_DIR" || {
    show_error "Could not create the output folder:\n\n$OUTPUT_DIR"
    exit 1
  }
  [[ "$OUTPUT_NAME" != *.* ]] && OUTPUT_NAME="${OUTPUT_NAME}.mp4"
  OUTPUT_PATH="$OUTPUT_DIR/$OUTPUT_NAME"
fi

RUNNER_DIR=$(/usr/bin/mktemp -d -t swinsian-clipped-reel) || {
  show_error "Could not create a temporary rendering job."
  exit 1
}
RUNNER="$RUNNER_DIR/run.zsh"
LOG="$RUNNER_DIR/run.log"

q_clipped=${(qqq)CLIPPED_BIN}
q_source=${(qqq)TRACK_PATH}
q_start=${(qqq)START}
q_end=${(qqq)END}
q_track=${(qqq)TRACK_SUMMARY}
q_template=${(qqq)TEMPLATE}
q_platform=${(qqq)PLATFORM}
q_fade=${(qqq)FADE}
q_output=${(qqq)OUTPUT_PATH}
q_open=${(qqq)OPEN_OUTPUT}
q_log=${(qqq)LOG}

/bin/cat > "$RUNNER" <<EOF
#!/bin/zsh
set -u
set -o pipefail

CLIPPED_BIN=$q_clipped
SOURCE=$q_source
START=$q_start
END=$q_end
TRACK=$q_track
TEMPLATE=$q_template
PLATFORM=$q_platform
FADE=$q_fade
OUTPUT_PATH=$q_output
OPEN_OUTPUT=$q_open
LOG=$q_log

echo "Swinsian -> Clipped Dynamic Reel"
echo "Track    : \$TRACK"
echo "Source   : \$SOURCE"
echo "Range    : \$START -> \$END"
echo "Template : \$TEMPLATE"
echo "Platform : \$PLATFORM"
echo "Fade     : \$FADE"
if [[ -n "\$OUTPUT_PATH" ]]; then
  echo "Output   : \$OUTPUT_PATH"
fi
echo "Log      : \$LOG"
echo

cmd=(
  "\$CLIPPED_BIN" video "\$SOURCE"
  --template "\$TEMPLATE"
  --platform "\$PLATFORM"
  --start "\$START"
  --end "\$END"
  --fade-in "\$FADE"
  --fade-out "\$FADE"
)

if [[ -n "\$OUTPUT_PATH" ]]; then
  cmd+=(--output "\$OUTPUT_PATH")
fi

"\${cmd[@]}" 2>&1 | /usr/bin/tee -a "\$LOG"
render_status=\${pipestatus[1]}

echo
if (( render_status == 0 )); then
  if [[ "\$OPEN_OUTPUT" == "true" && -n "\$OUTPUT_PATH" && -f "\$OUTPUT_PATH" ]]; then
    /usr/bin/open -R "\$OUTPUT_PATH"
  fi
  echo "Done. clipped copied the exported video to the clipboard."
  /usr/bin/osascript -e 'display notification "Dynamic reel export complete." with title "Clipped"' >/dev/null 2>&1 || true
else
  echo "Export failed with status \$render_status. See the log above."
  /usr/bin/osascript -e 'display notification "Dynamic reel export failed. Check Terminal for details." with title "Clipped"' >/dev/null 2>&1 || true
fi

exit \$render_status
EOF

/bin/chmod +x "$RUNNER"

RUNNER_COMMAND="zsh ${(q)RUNNER}"
/usr/bin/osascript \
  -e 'on run argv' \
  -e 'tell application "Terminal"' \
  -e 'activate' \
  -e 'do script (item 1 of argv)' \
  -e 'end tell' \
  -e 'end run' \
  "$RUNNER_COMMAND" >/dev/null

if [[ $? -ne 0 ]]; then
  show_error "Could not start the rendering job in Terminal."
  exit 1
fi

notify "Rendering in Terminal with no 60-second cap."
exit 0
