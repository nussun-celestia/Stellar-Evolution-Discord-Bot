import re

def generate_embed(stdout: str):
    stdout = """Main sequence Star            Time        0.0 Mass   5.000
Hertzsprung Gap               Time       87.8 Mass   5.000
Core Helium Burning           Time       88.3 Mass   4.999
First AGB                     Time       98.8 Mass   4.961
Second AGB                    Time       99.2 Mass   4.935
Carbon/Oxygen WD              Time      100.1 Mass   1.200
Carbon/Oxygen WD              Time    12000.0 Mass   1.200"""

    matches = re.findall("(.+\\b)\s+Time\s+([\d.]+)\s+Mass\s+([\d.]+)", stdout)
    print(matches)    



if __name__ == "__main__":
    generate_embed("")