#!/bin/bash

resolve_drawio() {
    if [[ -n "${DRAWIO:-}" ]]; then
        if [[ -x "$DRAWIO" ]] || command -v "$DRAWIO" > /dev/null 2>&1; then
            echo "$DRAWIO"
            return 0
        fi

        echo "Error: DRAWIO is set but not executable or on PATH: $DRAWIO" >&2
        return 1
    fi

    if command -v drawio > /dev/null 2>&1; then
        command -v drawio
        return 0
    fi

    if command -v draw.io > /dev/null 2>&1; then
        command -v draw.io
        return 0
    fi

    if [[ -x "/Applications/draw.io.app/Contents/MacOS/draw.io" ]]; then
        echo "/Applications/draw.io.app/Contents/MacOS/draw.io"
        return 0
    fi

    echo "Error: draw.io CLI not found. Install with: brew install --cask drawio" >&2
    return 1
}

should_use_xvfb() {
    case "${DRAWIO_USE_XVFB:-auto}" in
        1 | true | yes)
            return 0
            ;;
        0 | false | no)
            return 1
            ;;
        auto)
            [[ "$(uname -s)" == "Linux" ]] && command -v xvfb-run > /dev/null 2>&1
            return
            ;;
        *)
            echo "Error: DRAWIO_USE_XVFB must be auto, true, or false" >&2
            return 2
            ;;
    esac
}

should_disable_chromium_sandbox() {
    case "${DRAWIO_NO_SANDBOX:-auto}" in
        1 | true | yes)
            return 0
            ;;
        0 | false | no)
            return 1
            ;;
        auto)
            [[ "$(uname -s)" == "Linux" ]]
            return
            ;;
        *)
            echo "Error: DRAWIO_NO_SANDBOX must be auto, true, or false" >&2
            return 2
            ;;
    esac
}

render_timeout_command() {
    case "${DRAWIO_RENDER_TIMEOUT:-300s}" in
        0 | false | no)
            return 1
            ;;
    esac

    if command -v timeout > /dev/null 2>&1; then
        command -v timeout
        return 0
    fi

    if command -v gtimeout > /dev/null 2>&1; then
        command -v gtimeout
        return 0
    fi

    return 1
}

render_drawio_png() {
    local input_file="$1"
    local output_file="$2"
    local label="${3:-$input_file}"
    local drawio
    local sandbox_status
    local render_log
    local render_status
    local timeout_bin
    local xvfb_status
    local -a drawio_cmd
    local -a timeout_cmd

    drawio="$(resolve_drawio)" || return 1
    drawio_cmd=("$drawio")
    if should_disable_chromium_sandbox; then
        drawio_cmd+=("--no-sandbox")
    else
        sandbox_status="$?"
        if [[ "$sandbox_status" -gt 1 ]]; then
            return 1
        fi
    fi
    if [[ "$(uname -s)" == "Linux" ]]; then
        drawio_cmd+=("--disable-dev-shm-usage" "--disable-gpu")
    fi

    timeout_cmd=()
    if timeout_bin="$(render_timeout_command)"; then
        timeout_cmd=(
            "$timeout_bin"
            --kill-after="${DRAWIO_RENDER_TIMEOUT_KILL_AFTER:-30s}"
            "${DRAWIO_RENDER_TIMEOUT:-300s}"
        )
    fi

    mkdir -p "$(dirname "$output_file")"
    render_log="$(mktemp)"
    echo "Rendering: $label -> $output_file"

    if should_use_xvfb; then
        xvfb_status=0
    else
        xvfb_status="$?"
    fi

    if [[ "$xvfb_status" -eq 0 ]]; then
        if ! command -v xvfb-run > /dev/null 2>&1; then
            echo "Error: xvfb-run not found but DRAWIO_USE_XVFB requires it" >&2
            rm -f "$render_log"
            return 1
        fi
        if [[ "${#timeout_cmd[@]}" -gt 0 ]]; then
            if "${timeout_cmd[@]}" xvfb-run -a "${drawio_cmd[@]}" -x -f png -o "$output_file" "$input_file" > "$render_log" 2>&1; then
                render_status=0
            else
                render_status="$?"
            fi
        else
            if xvfb-run -a "${drawio_cmd[@]}" -x -f png -o "$output_file" "$input_file" > "$render_log" 2>&1; then
                render_status=0
            else
                render_status="$?"
            fi
        fi
    elif [[ "$xvfb_status" -eq 1 ]]; then
        if [[ "${#timeout_cmd[@]}" -gt 0 ]]; then
            if "${timeout_cmd[@]}" "${drawio_cmd[@]}" -x -f png -o "$output_file" "$input_file" > "$render_log" 2>&1; then
                render_status=0
            else
                render_status="$?"
            fi
        else
            if "${drawio_cmd[@]}" -x -f png -o "$output_file" "$input_file" > "$render_log" 2>&1; then
                render_status=0
            else
                render_status="$?"
            fi
        fi
    else
        rm -f "$render_log"
        return 1
    fi

    if [[ "$render_status" -eq 0 && -s "$output_file" ]]; then
        echo "Rendered: $label -> $output_file"
        rm -f "$render_log"
        return 0
    fi

    echo "Error: draw.io render failed for $label" >&2
    if [[ "$render_status" -eq 124 || "$render_status" -eq 137 ]]; then
        echo "draw.io render timed out after ${DRAWIO_RENDER_TIMEOUT:-300s}" >&2
    fi
    if [[ -s "$render_log" ]]; then
        sed -n '1,40p' "$render_log" >&2
    fi
    rm -f "$render_log"
    return 1
}
