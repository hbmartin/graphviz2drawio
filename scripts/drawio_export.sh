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

render_drawio_png() {
    local input_file="$1"
    local output_file="$2"
    local label="${3:-$input_file}"
    local drawio
    local render_log
    local render_status
    local xvfb_status

    drawio="$(resolve_drawio)" || return 1
    mkdir -p "$(dirname "$output_file")"
    render_log="$(mktemp)"

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
        if xvfb-run -a "$drawio" -x -f png -o "$output_file" "$input_file" > "$render_log" 2>&1; then
            render_status=0
        else
            render_status="$?"
        fi
    elif [[ "$xvfb_status" -eq 1 ]]; then
        if "$drawio" -x -f png -o "$output_file" "$input_file" > "$render_log" 2>&1; then
            render_status=0
        else
            render_status="$?"
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
    if [[ -s "$render_log" ]]; then
        sed -n '1,40p' "$render_log" >&2
    fi
    rm -f "$render_log"
    return 1
}
