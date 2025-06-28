from numbers_parser import Document
import pandas as pd

doc = Document("/Users/liavc/Documents/grades.numbers")
print("here!")
sheet = doc.sheets[0]
print(sheet.name)
table = sheet.tables[0]
print(table.name)
# header = [cell.value for cell in table.rows[0]]
# data = []
# for row_index in range(1, len(table.rows)):
#     row_values = [cell.value for cell in table.rows[row_index]]
#     data.append(row_values)

# df = pd.DataFrame(data, columns=header)
data = table.rows(values_only=True)
df = pd.DataFrame(data[1:], columns=data[0])
print(df.columns)