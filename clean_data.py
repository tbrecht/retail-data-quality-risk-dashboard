import pandas as pd

data = {
    "Region": ["North", "South", None, "West"],
    "Sales": [100, 250, None, 500]
}

df = pd.DataFrame(data)

print("Original Data:")
print(df)

df["Sales"] = df["Sales"].fillna(df["Sales"].median())
df["Region"] = df["Region"].fillna("Unknown")

print("\nCleaned Data:")
print(df)

df.to_csv("cleaned_output.csv", index=False)