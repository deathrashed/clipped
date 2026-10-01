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

prompt_for_range() {
  local track_summary="$1"

  /usr/bin/osascript - "$track_summary" <<'APPLESCRIPT'
on run argv
  set resultDialog to display dialog "Selected: " & (item 1 of argv) & return & return & "Enter start - end for the Dynamic Reel." & return & "Examples: 0 - 1:00 or 4:10 - 5:40." default answer "0 - 1:00" buttons {"Cancel", "OK"} default button "OK" cancel button "Cancel" with title "Swinsian - Dynamic Reel Range"
  return text returned of resultDialog
end run
APPLESCRIPT
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

RANGE=$(prompt_for_range "$TRACK_SUMMARY") || exit 0
if [[ "$RANGE" != *" - "* ]]; then
  show_error "Enter the range as start - end."
  exit 1
fi
START="${RANGE%% - *}"
END="${RANGE#* - }"
if [[ -z "$START" || -z "$END" ]]; then
  show_error "Start and end times are required."
  exit 1
fi

# ── Prepare the detached Terminal job ────────────────────────────────────────

DEFAULT_OUTPUT_DIR="${OUTPUT_DIR:-$HOME/Music/clipped/_video}"
if [[ "$DEFAULT_OUTPUT_DIR" == "~/"* ]]; then
  DEFAULT_OUTPUT_DIR="$HOME/${DEFAULT_OUTPUT_DIR#~/}"
fi
mkdir -p "$DEFAULT_OUTPUT_DIR"

if ! OUTPUT_DIR="$(/usr/bin/osascript - "$DEFAULT_OUTPUT_DIR" <<'APPLESCRIPT'
on run argv
  set resultDialog to display dialog "Output directory for the Dynamic Reel:" default answer (item 1 of argv) buttons {"Cancel", "Save"} default button "Save" cancel button "Cancel" with title "Clipped - Output Directory"
  return text returned of resultDialog
end run
APPLESCRIPT
)"; then
  exit 0
fi
OUTPUT_DIR="${OUTPUT_DIR/#\~/$HOME}"
mkdir -p "$OUTPUT_DIR"

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
q_output_dir=${(qqq)OUTPUT_DIR}
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
OUTPUT_DIR=$q_output_dir
OPEN_OUTPUT=$q_open
LOG=$q_log

echo "Swinsian -> Clipped Dynamic Reel"
echo "Track    : \$TRACK"
echo "Source   : \$SOURCE"
echo "Range    : \$START -> \$END"
echo "Template : \$TEMPLATE"
echo "Platform : \$PLATFORM"
echo "Output dir: \$OUTPUT_DIR"
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
  --output-dir "\$OUTPUT_DIR"
)

"\${cmd[@]}" 2>&1 | /usr/bin/tee -a "\$LOG"
render_status=\${pipestatus[1]}


echo
if (( render_status == 0 )); then
  final_output_path="\$(/usr/bin/sed -n 's/^CLIPPED_OUTPUT_PATH=//p' "\$LOG" | /usr/bin/tail -n 1)"
  if [[ -n "\$final_output_path" ]]; then
    echo "Output path (copy this): \$final_output_path"
    printf '%s' "\$final_output_path" | /usr/bin/pbcopy
  fi
  if [[ "\$OPEN_OUTPUT" == "true" && -n "\$final_output_path" && -f "\$final_output_path" ]]; then
    /usr/bin/open -R "\$final_output_path"
  fi
  if [[ -n "\$final_output_path" ]]; then
    echo "Done. clipped copied the exported video and its path to the clipboard."
  else
    echo "Done. clipped copied the exported video, but its path was not reported."
  fi
  /usr/bin/osascript -e 'display notification "Dynamic reel export complete." with title "Clipped"' >/dev/null 2>&1 || true
else
  echo "Export failed with status \$render_status. See the log above."
  /usr/bin/osascript -e 'display notification "Dynamic reel export failed. Check cmux or Ghostty for details." with title "Clipped"' >/dev/null 2>&1 || true
fi

exit \$render_status
EOF

/bin/chmod +x "$RUNNER"

run_in_cmux() {
  /usr/bin/osascript - "$1" <<'APPLESCRIPT'
on run argv
  tell application "cmux"
    activate
    set targetTerminal to focused terminal of selected tab of front window
    input text ((item 1 of argv) & return) to targetTerminal
  end tell
end run
APPLESCRIPT
}
run_in_ghostty() {
  /usr/bin/osascript - "$1" <<'APPLESCRIPT'
on run argv
  tell application "Ghostty"
    activate
    set targetTerminal to focused terminal of selected tab of front window
    input text (item 1 of argv) to targetTerminal
    send key "enter" to targetTerminal
  end tell
end run
APPLESCRIPT
}

launch_terminal() {
  local command="$1"
  local requested="${CLIPPED_TERMINAL_APP:-}"

  case "$requested" in
    cmux)
      run_in_cmux "$command"
      return
      ;;
    ghostty|Ghostty)
      run_in_ghostty "$command"
      return
      ;;
    "")
      ;;
    *)
      show_error "CLIPPED_TERMINAL_APP must be cmux or ghostty."
      return 1
      ;;
  esac

  if /usr/bin/osascript -e 'id of application "cmux"' >/dev/null 2>&1 &&
     run_in_cmux "$command"; then
    return 0
  fi
  if /usr/bin/osascript -e 'id of application "Ghostty"' >/dev/null 2>&1 &&
     run_in_ghostty "$command"; then
    return 0
  fi

  show_error "Install cmux or Ghostty before starting a Clipped render."
  return 1
}

if ! launch_terminal "zsh ${(q)RUNNER}"; then
  show_error "Could not start the rendering job in cmux or Ghostty."
  exit 1
fi

notify "Rendering in cmux or Ghostty with no 60-second cap."
exit 0
