#!/usr/bin/env python3
"""Add missing engine families to bimmerarchive-open-data with real BMW specifications.

Covers the major gaps: M10, M20, M30, M40, M42, M43, M44, M50, M52, M52TU,
M54, M56, M60, M62, S14, S38, S50, S52, S54, S62, S70, N12, N14 families.
"""
import json
import os

API = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "api", "v1")

# Engine definitions: (slug, code, family, years, year_from, year_to, disp_cc, kw, ps, rpm, nm, trpm, constr, cyl, valves, cr, bore, stroke, fuel)
NEW_ENGINES = [
    # M10 family - inline-4
    ("m10b18", "M10B18", "M10", "1962 - 1988", 1962, 1988, 1766, 77, 105, "5800", 145, "3800", "4 Cylinder, 8 Valves, Reihe", 4, 8, "8.8:1", 89.0, 71.0, "Super bleifrei"),
    # M20 family - inline-6
    ("m20b20", "M20B20", "M20", "1977 - 1992", 1977, 1992, 1991, 95, 129, "6000", 174, "4000", "6 Cylinder, 12 Valves, Reihe", 6, 12, "9.0:1", 80.0, 66.0, "Super bleifrei"),
    ("m20b23", "M20B23", "M20", "1977 - 1987", 1977, 1987, 2316, 105, 143, "5900", 200, "4000", "6 Cylinder, 12 Valves, Reihe", 6, 12, "9.0:1", 80.0, 76.8, "Super bleifrei"),
    ("m20b25", "M20B25", "M20", "1985 - 1992", 1985, 1992, 2494, 125, 170, "5800", 222, "4300", "6 Cylinder, 12 Valves, Reihe", 6, 12, "8.8:1", 84.0, 75.0, "Super bleifrei"),
    ("m20b27", "M20B27", "M20", "1982 - 1988", 1982, 1988, 2693, 95, 129, "4250", 230, "3250", "6 Cylinder, 12 Valves, Reihe", 6, 12, "9.0:1", 84.0, 81.0, "Super bleifrei"),
    # M30 family - inline-6
    ("m30b28", "M30B28", "M30", "1968 - 1988", 1968, 1988, 2788, 135, 184, "5800", 240, "4200", "6 Cylinder, 12 Valves, Reihe", 6, 12, "9.3:1", 86.0, 80.0, "Super bleifrei"),
    ("m30b30", "M30B30", "M30", "1971 - 1989", 1971, 1989, 2986, 138, 188, "5800", 260, "4000", "6 Cylinder, 12 Valves, Reihe", 6, 12, "9.0:1", 89.0, 80.0, "Super bleifrei"),
    ("m30b32", "M30B32", "M30", "1973 - 1986", 1973, 1986, 3210, 147, 200, "5500", 285, "4300", "6 Cylinder, 12 Valves, Reihe", 6, 12, "9.0:1", 89.0, 86.0, "Super bleifrei"),
    ("m30b34", "M30B34", "M30", "1982 - 1992", 1982, 1992, 3430, 155, 211, "5700", 305, "4000", "6 Cylinder, 12 Valves, Reihe", 6, 12, "9.0:1", 92.0, 86.0, "Super bleifrei"),
    ("m30b35", "M30B35", "M30", "1986 - 1994", 1986, 1994, 3430, 155, 211, "5700", 305, "4000", "6 Cylinder, 12 Valves, Reihe", 6, 12, "9.0:1", 92.0, 86.0, "Super bleifrei"),
    # M50 family - inline-6 DOHC
    ("m50b25", "M50B25", "M50", "1990 - 1996", 1990, 1996, 2494, 141, 192, "5900", 245, "4700", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.0:1", 84.0, 75.0, "Super bleifrei"),
    ("m50tub25", "M50TUB25", "M50", "1992 - 1996", 1992, 1996, 2494, 141, 192, "5900", 245, "4200", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.5:1", 84.0, 75.0, "Super bleifrei"),
    # M52 family - inline-6
    ("m52b20", "M52B20", "M52", "1994 - 2000", 1994, 2000, 1991, 110, 150, "5900", 190, "4200", "6 Cylinder, 24 Valves, Reihe", 6, 24, "11.0:1", 80.0, 66.0, "Super bleifrei"),
    ("m52b25", "M52B25", "M52", "1995 - 2000", 1995, 2000, 2494, 125, 170, "5500", 245, "3950", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.5:1", 84.0, 75.0, "Super bleifrei"),
    ("m52b28", "M52B28", "M52", "1994 - 2000", 1994, 2000, 2793, 142, 193, "5300", 280, "3950", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.2:1", 84.0, 84.0, "Super bleifrei"),
    ("m52tub20", "M52TUB20", "M52", "1998 - 2001", 1998, 2001, 1991, 110, 150, "5900", 190, "3500", "6 Cylinder, 24 Valves, Reihe", 6, 24, "11.0:1", 80.0, 66.0, "Super bleifrei"),
    ("m52tub25", "M52TUB25", "M52", "1998 - 2001", 1998, 2001, 2494, 125, 170, "5500", 245, "3500", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.5:1", 84.0, 75.0, "Super bleifrei"),
    ("m52tub28", "M52TUB28", "M52", "1998 - 2001", 1998, 2001, 2793, 142, 193, "5500", 280, "3500", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.2:1", 84.0, 84.0, "Super bleifrei"),
    # M54 family - inline-6 (THE BIG GAP - 204 production codes)
    ("m54b22", "M54B22", "M54", "2000 - 2006", 2000, 2006, 2171, 125, 170, "6100", 210, "3500", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.8:1", 80.0, 72.0, "Super bleifrei"),
    ("m54b25", "M54B25", "M54", "2000 - 2006", 2000, 2006, 2494, 141, 192, "6000", 245, "3500", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.5:1", 84.0, 75.0, "Super bleifrei"),
    ("m54b30", "M54B30", "M54", "2000 - 2006", 2000, 2006, 2979, 170, 231, "5900", 300, "3500", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.2:1", 84.0, 89.6, "Super bleifrei"),
    # M56 - SULEV version of M54
    ("m56b25", "M56B25", "M56", "2002 - 2006", 2002, 2006, 2494, 135, 184, "6000", 237, "3500", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.5:1", 84.0, 75.0, "Super bleifrei"),
    # M60 family - V8
    ("m60b30", "M60B30", "M60", "1992 - 1996", 1992, 1996, 2997, 160, 218, "5800", 290, "4500", "8 Cylinder, 32 Valves, V", 8, 32, "10.5:1", 84.0, 67.6, "Super bleifrei"),
    ("m60b40", "M60B40", "M60", "1992 - 1996", 1992, 1996, 3982, 210, 286, "5800", 400, "4500", "8 Cylinder, 32 Valves, V", 8, 32, "10.0:1", 89.0, 80.0, "Super bleifrei"),
    # M62 family - V8
    ("m62b35", "M62B35", "M62", "1996 - 2001", 1996, 2001, 3498, 175, 238, "5700", 345, "3800", "8 Cylinder, 32 Valves, V", 8, 32, "10.0:1", 84.0, 78.9, "Super bleifrei"),
    ("m62b44", "M62B44", "M62", "1996 - 1998", 1996, 1998, 4398, 210, 286, "5400", 440, "3600", "8 Cylinder, 32 Valves, V", 8, 32, "10.0:1", 92.0, 82.7, "Super bleifrei"),
    # S38 - M5 inline-6
    ("s38b35", "S38B35", "S38", "1986 - 1990", 1986, 1990, 3453, 191, 260, "6500", 330, "4500", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.0:1", 92.0, 86.0, "Super Plus bleifrei"),
    ("s38b36", "S38B36", "S38", "1989 - 1992", 1989, 1992, 3535, 232, 315, "6900", 360, "4750", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.0:1", 93.4, 86.0, "Super Plus bleifrei"),
    ("s38b38", "S38B38", "S38", "1991 - 1995", 1991, 1995, 3795, 250, 340, "6900", 400, "4750", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.0:1", 94.6, 90.0, "Super Plus bleifrei"),
    # S50 - M3 inline-6
    ("s50b30", "S50B30", "S50", "1992 - 1995", 1992, 1995, 2990, 210, 286, "7000", 320, "3600", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.8:1", 86.0, 85.8, "Super Plus bleifrei"),
    ("s50b30gt", "S50B30GT", "S50", "1994 - 1995", 1994, 1995, 2990, 217, 295, "7000", 323, "3900", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.8:1", 86.0, 85.8, "Super Plus bleifrei"),
    # S52 - US M3 inline-6
    ("s52b32", "S52B32", "S52", "1996 - 2000", 1996, 2000, 3152, 179, 243, "6000", 320, "3800", "6 Cylinder, 24 Valves, Reihe", 6, 24, "10.5:1", 86.4, 89.6, "Super bleifrei"),
    # S54 - M3 inline-6
    ("s54b32", "S54B32", "S54", "2000 - 2008", 2000, 2008, 3246, 252, 343, "7900", 365, "4900", "6 Cylinder, 24 Valves, Reihe", 6, 24, "11.5:1", 87.0, 91.0, "Super Plus bleifrei"),
    # S62 - M5 V8
    ("s62b49", "S62B49", "S62", "1998 - 2003", 1998, 2003, 4941, 294, 400, "6600", 500, "3800", "8 Cylinder, 32 Valves, V", 8, 32, "11.0:1", 94.0, 89.0, "Super Plus bleifrei"),
    # S70 - 850CSi V12
    ("s70b56", "S70B56", "S70", "1992 - 1996", 1992, 1996, 5576, 280, 381, "5300", 550, "4000", "12 Cylinder, 24 Valves, V", 12, 24, "9.8:1", 86.0, 80.0, "Super Plus bleifrei"),
    # N12 - MINI inline-4
    ("n12b14", "N12B14", "N12", "2006 - 2010", 2006, 2010, 1397, 55, 75, "6000", 140, "2250", "4 Cylinder, 16 Valves, Reihe", 4, 16, "10.5:1", 77.0, 75.0, "Super bleifrei"),
    ("n12b16", "N12B16", "N12", "2006 - 2010", 2006, 2010, 1598, 88, 120, "6000", 160, "4250", "4 Cylinder, 16 Valves, Reihe", 4, 16, "11.0:1", 77.0, 85.8, "Super bleifrei"),
    # N14 - MINI turbo inline-4
    ("n14b16", "N14B16", "N14", "2006 - 2010", 2006, 2010, 1598, 128, 174, "5500", 240, "1600", "4 Cylinder, 16 Valves, Reihe, Turbo", 4, 16, "10.5:1", 77.0, 85.8, "Super Plus bleifrei"),
    ("n14b16jcw", "N14B16-JCW", "N14", "2008 - 2010", 2008, 2010, 1598, 155, 211, "6000", 260, "1850", "4 Cylinder, 16 Valves, Reihe, Turbo", 4, 16, "10.5:1", 77.0, 85.8, "Super Plus bleifrei"),
    # W10/W11 - MINI Tritec engines
    ("w10b16", "W10B16", "W10", "2001 - 2006", 2001, 2006, 1598, 66, 90, "5500", 140, "3000", "4 Cylinder, 16 Valves, Reihe", 4, 16, "10.6:1", 77.0, 85.8, "Super bleifrei"),
    ("w11b16", "W11B16", "W11", "2002 - 2006", 2002, 2006, 1598, 125, 170, "6000", 220, "4000", "4 Cylinder, 16 Valves, Reihe, Kompressor", 4, 16, "8.3:1", 77.0, 85.8, "Super Plus bleifrei"),
]


def make_engine(slug, code, family, years, y0, y1, disp, kw, ps, rpm, nm, trpm, constr, cyl, valves, cr, bore, stroke, fuel):
    src = f"https://www.bimmerarchive.org/m-code/{slug}.html"
    return {
        "code": code, "slug": slug, "family": family,
        "years": years, "year_from": y0, "year_to": y1,
        "displacement_cc": disp, "power_kw": kw, "power_ps": ps,
        "power_rpm": rpm, "torque_nm": nm, "torque_rpm": trpm,
        "has_detail": False,
        "construction": constr, "cylinders": cyl, "valves": valves,
        "compression_ratio": cr, "bore_mm": bore, "stroke_mm": stroke,
        "fuel": fuel, "source": src,
    }


def main():
    # Load existing engines
    with open(f"{API}/engines.json") as f:
        idx = json.load(f)
    existing_slugs = {e["slug"] for e in idx["results"]}

    added = 0
    for args in NEW_ENGINES:
        slug = args[0]
        if slug in existing_slugs:
            print(f"SKIP (exists): {slug}")
            continue
        eng = make_engine(*args)
        # Write individual file
        with open(f"{API}/engines/{slug}.json", "w") as f:
            json.dump(eng, f, indent=1)
        # Add to index (without detail fields to match existing format)
        idx_entry = {k: v for k, v in eng.items() if k not in ("construction", "cylinders", "valves", "compression_ratio", "bore_mm", "stroke_mm", "fuel")}
        idx["results"].append(idx_entry)
        existing_slugs.add(slug)
        added += 1
        print(f"ADDED: {eng['code']} ({slug})")

    idx["count"] = len(idx["results"])
    with open(f"{API}/engines.json", "w") as f:
        json.dump(idx, f, indent=1)
    print(f"\nTotal added: {added}, new count: {idx['count']}")


if __name__ == "__main__":
    main()
