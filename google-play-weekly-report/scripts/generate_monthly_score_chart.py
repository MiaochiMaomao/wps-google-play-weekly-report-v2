from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


COLORS = ["#1F5FBF", "#00A05A", "#F26B00", "#7A4EAB", "#B23A48"]
DARK = "#16243A"
MUTED = "#64748B"
GRID = "#D8DEE9"


def font(size: int, bold: bool = False):
    candidates = [
        Path(r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def centered(draw, x, y, text, text_font, fill=DARK):
    box = draw.textbbox((0, 0), text, font=text_font)
    draw.text((x - (box[2] - box[0]) / 2, y - (box[3] - box[1]) / 2), text, font=text_font, fill=fill)


def validate_history(raw):
    if not isinstance(raw, dict) or not 1 <= len(raw) <= len(COLORS):
        raise ValueError("monthly_score_history must contain one to five year series")
    normalized = []
    for year_text, values in sorted(raw.items(), key=lambda item: int(item[0])):
        year = int(year_text)
        if not isinstance(values, list) or not 1 <= len(values) <= 12:
            raise ValueError(f"{year} must contain 1-12 January-onward values")
        scores = []
        for month, value in enumerate(values, start=1):
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 1 <= float(value) <= 5:
                raise ValueError(f"{year}-{month:02d} score is invalid")
            scores.append(float(value))
        normalized.append((str(year), scores))
    return normalized


def axis_limits(series):
    values = [value for _, scores in series for value in scores]
    low, high = min(values), max(values)
    padding = max(0.05, (high - low) * 0.15)
    y_min = max(1.0, math.floor((low - padding) * 10) / 10)
    y_max = min(5.0, math.ceil((high + padding) * 10) / 10)
    if y_max == y_min:
        y_min = max(1.0, y_min - 0.1)
        y_max = min(5.0, y_max + 0.1)
    return y_min, y_max


def draw_label(draw, x, y, text, color, above):
    label_font = font(28, True)
    box = draw.textbbox((0, 0), text, font=label_font)
    center_y = y - 38 if above else y + 40
    rectangle = (x - (box[2] - box[0]) / 2 - 8, center_y - (box[3] - box[1]) / 2 - 4, x + (box[2] - box[0]) / 2 + 8, center_y + (box[3] - box[1]) / 2 + 4)
    draw.rounded_rectangle(rectangle, radius=7, fill="white")
    centered(draw, x, center_y, text, label_font, color)


def build_chart(history, note, config, output):
    series = validate_history(history)
    width, height = 2398, 1342
    left, top, right, bottom = 180, 245, 2325, 1120
    y_min, y_max = axis_limits(series)
    decimals = config["format"]["score_decimals"]
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    centered(draw, width / 2, 78, config["charts"]["monthly_title"], font(54, True))
    if note:
        draw.text((left, 145), str(note), font=font(25), fill=MUTED)

    def point_xy(month_index, value):
        x = left + (right - left) * month_index / 11
        y = bottom - (value - y_min) / (y_max - y_min) * (bottom - top)
        return x, y

    for tick in range(5):
        value = y_max - (y_max - y_min) * tick / 4
        y = bottom - (value - y_min) / (y_max - y_min) * (bottom - top)
        draw.line((left, y, right, y), fill=GRID, width=2)
        centered(draw, left - 56, y, f"{value:.1f}", font(23), "#334155")
    for month_index in range(12):
        x, _ = point_xy(month_index, y_min)
        centered(draw, x, bottom + 48, str(month_index + 1), font(23), "#334155")

    points = {}
    for series_index, (year, values) in enumerate(series):
        color = COLORS[series_index]
        year_points = [point_xy(index, value) for index, value in enumerate(values)]
        points[year] = year_points
        if len(year_points) > 1:
            draw.line(year_points, fill=color, width=5, joint="curve")
        for x, y in year_points:
            draw.ellipse((x - 10, y - 10, x + 10, y + 10), fill=color)

    positions = {}
    for month_index in range(12):
        month_points = [(index, values[month_index]) for index, (_, values) in enumerate(series) if month_index < len(values)]
        ordered = sorted(month_points, key=lambda item: item[1], reverse=True)
        for rank, (index, _) in enumerate(ordered):
            positions[(index, month_index)] = rank % 2 == 0
    for series_index, (year, values) in enumerate(series):
        for month_index, (value, (x, y)) in enumerate(zip(values, points[year])):
            draw_label(draw, x, y, f"{value:.{decimals}f}", COLORS[series_index], positions[(series_index, month_index)])

    legend_y = 1025
    for series_index, (year, _) in enumerate(series):
        x = 260 + series_index * 310
        draw.line((x, legend_y, x + 90, legend_y), fill=COLORS[series_index], width=6)
        draw.text((x + 108, legend_y - 19), year, font=font(26), fill=DARK)
    centered(draw, width / 2, height - 42, config["charts"]["monthly_x_label"], font(28))
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, optimize=True)
    return series


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.metrics).read_text(encoding="utf-8"))
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    if "monthly_score_history" not in data:
        raise SystemExit("metrics file is missing monthly_score_history")
    output = Path(args.output)
    series = build_chart(data["monthly_score_history"], data.get("monthly_score_note", ""), config, output)
    print(json.dumps({"monthly_score_chart": str(output), "years": [year for year, _ in series], "point_count": sum(len(values) for _, values in series)}))


if __name__ == "__main__":
    main()

