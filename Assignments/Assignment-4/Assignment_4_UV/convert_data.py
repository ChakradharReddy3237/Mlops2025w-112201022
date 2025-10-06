from pathlib import Path
import sys
import pandas as pd


def convert_excel_to_csv(excel_path: Path, csv_path: Path) -> None:
    df = pd.read_excel(excel_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    print(f"Converted {excel_path} -> {csv_path}")


def main() -> int:
    data_dir = Path("data")
    excel_path = data_dir / "online_Retail.xlsx"
    csv_path = data_dir / "online_retail.csv"
    try:
        convert_excel_to_csv(excel_path, csv_path)
        return 0
    except FileNotFoundError:
        print(f"Input not found: {excel_path}")
        return 1
    except Exception as exc:  # keep simple
        print(f"Failed to convert: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
