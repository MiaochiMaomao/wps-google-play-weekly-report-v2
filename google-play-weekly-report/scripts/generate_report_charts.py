from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def font(size: int, bold: bool = False):
    candidates = [
        Path(r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def category_chart(rows: list[dict], title: str, output: Path) -> None:
    width, height = 1250, 642
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    total = sum(row["count"] for row in rows)
    draw.text((width // 2, 28), title, font=font(34, True), fill="#17365D", anchor="ma")
    colors = ["#4F81BD", "#C0504D", "#9BBB59", "#8064A2", "#F79646", "#4BACC6"]
    box = (85, 105, 535, 555)
    angle = -90
    for index, row in enumerate(rows):
        extent = row["count"] / total * 360 if total else 0
        draw.pieslice(box, angle, angle + extent, fill=colors[index % len(colors)], outline="white", width=3)
        angle += extent
    draw.ellipse((205, 225, 415, 435), fill="white")
    draw.text((310, 315), str(total), font=font(34, True), fill="#17365D", anchor="mm")
    spacing = max(55, min(95, 380 // max(len(rows), 1)))
    for index, row in enumerate(rows):
        y = 135 + index * spacing
        draw.rounded_rectangle((640, y - 15, 674, y + 17), radius=5, fill=colors[index % len(colors)])
        draw.text((695, y), row["name"], font=font(22), fill="#333333", anchor="lm")
        draw.text((1150, y), f"{row['count']}  {row['share']:.2f}%", font=font(23, True), fill="#333333", anchor="rm")
    image.save(output, optimize=True)


def subcategory_chart(rows: list[dict], title: str, output: Path) -> None:
    width = 1472
    row_height = 54
    height = max(500, 150 + row_height * len(rows))
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.text((width // 2, 22), title, font=font(34, True), fill="#17365D", anchor="ma")
    maximum = max((row["count"] for row in rows), default=1)
    left, bar_left, bar_right = 55, 315, 1275
    top, bar_height = 92, 27
    colors = ["#2F75B5", "#5B9BD5", "#70AD47", "#ED7D31", "#A5A5A5", "#4472C4", "#FFC000"]
    for index, row in enumerate(rows):
        y = top + index * row_height
        draw.text((left, y + bar_height / 2), row["name"], font=font(22), fill="#333333", anchor="lm")
        width_value = int((bar_right - bar_left) * row["count"] / maximum)
        draw.rounded_rectangle((bar_left, y, bar_left + width_value, y + bar_height), radius=8, fill=colors[index % len(colors)])
        draw.text((bar_left + width_value + 14, y + bar_height / 2), f"{row['count']}  {row['share']:.2f}%", font=font(21, True), fill="#333333", anchor="lm")
    image.save(output, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.metrics).read_text(encoding="utf-8"))
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    category_output = output_dir / "category-distribution.png"
    subcategory_output = output_dir / "subcategory-distribution.png"
    category_chart(data["major_categories"], config["charts"]["major_title"], category_output)
    subcategory_chart(data["representative_subcategories"], config["charts"]["subcategory_title"], subcategory_output)
    print(json.dumps({"category_chart": str(category_output), "subcategory_chart": str(subcategory_output)}))


if __name__ == "__main__":
    main()

