---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain how to read a spreadsheet file using Python and the `openpyxl` library.**

To read a spreadsheet file using Python and the `openpyxl` library, follow these steps:

1. **Install the `openpyxl` library**: Use pip to install the library if it is not already installed.
   ```bash
   pip install openpyxl
   ```

2. **Import the library**: Import the `openpyxl` module in your Python script.
   ```python
   import openpyxl
   ```

3. **Load the workbook**: Use the `load_workbook` function to load the spreadsheet file.
   ```python
   wb = openpyxl.load_workbook('path/to/your/spreadsheet.xlsx')
   ```

4. **Access a specific sheet**: Select the sheet you want to work with by its name or index.
   ```python
   sheet = wb['Sheet1']
   ```

5. **Read cell values**: Access individual cells to read their values.
   ```python
   cell_value = sheet['A1'].value
   ```

By following these steps, you can read and process data from a spreadsheet file using Python and `openpyxl`.

**Q2. How would you calculate the number of products per supplier from a spreadsheet using Python?**

To calculate the number of products per supplier from a spreadsheet using Python, you can follow these steps:

1. **Load the workbook and select the sheet**:
   ```python
   import openpyxl
   wb = openpyxl.load_workbook('inventory.xlsx')
   sheet = wb.active
   ```

2. **Initialize a dictionary to store the counts**:
   ```python
   products_per_supplier = {}
   ```

3. **Iterate through the rows and count the products**:
   ```python
   for row in range(2, sheet.max_row + 1):
       supplier_name = sheet.cell(row=row, column=4).value
       if supplier_name in products_per_supplier:
           products_per_supplier[supplier_name] += 1
       else:
           products_per_supplier[supplier_name] = 1
   ```

4. **Print the results**:
   ```python
   print(products_per_supplier)
   ```

This code reads the supplier names from the fourth column of each row, starting from the second row, and counts the number of products per supplier.

**Q3. How would you list inventory products that have inventory less than 10 using Python?**

To list inventory products that have inventory less than 10 using Python, you can follow these steps:

1. **Load the workbook and select the sheet**:
   ```python
   import openpyxl
   wb = openpyxl.load_workbook('inventory.xlsx')
   sheet = wb.active
   ```

2. **Initialize a dictionary to store the products with low inventory**:
   ```python
   low_inventory_products = {}
   ```

3. **Iterate through the rows and check the inventory**:
   ```python
   for row in range(2, sheet.max_row + 1):
       product_number = sheet.cell(row=row, column=1).value
       inventory_count = sheet.cell(row=row, column=2).value
       if inventory_count < 10:
           low_inventory_products[product_number] = inventory_count
   ```

4. **Print the results**:
   ```python
   print(low_inventory_products)
   ```

This code reads the product number and inventory count from the first and second columns of each row, starting from the second row, and stores the products with inventory less than 10 in a dictionary.

**Q4. How would you calculate the total inventory value per supplier using Python?**

To calculate the total inventory value per supplier using Python, you can follow these steps:

1. **Load the workbook and select the sheet**:
   ```python
   import openpyxl
   wb = openpyxl.load_workbook('inventory.xlsx')
   sheet = wb.active
   ```

2. **Initialize a dictionary to store the total inventory value per supplier**:
   ```python
   total_value_per_supplier = {}
   ```

3. **Iterate through the rows and calculate the total value**:
   ```python
   for row in range(2, sheet.max_row + 1):
       supplier_name = sheet.cell(row=row, column=4).value
       inventory_count = sheet.cell(row=row, column=2).value
       price = sheet.cell(row=row, column=3).value
       total_value = inventory_count * price
       if supplier_name in total_value_per_supplier:
           total_value_per_supplier[supplier_name] += total_value
       else:
           total_value_per_supplier[supplier_name] = total_value
   ```

4. **Print the results**:
   ```python
   print(total_value_per_supplier)
   ```

This code reads the supplier name, inventory count, and price from the fourth, second, and third columns of each row, starting from the second row, and calculates the total inventory value per supplier.

**Q5. How would you add a new column to a spreadsheet and fill it with calculated values using Python?**

To add a new column to a spreadsheet and fill it with calculated values using Python, you can follow these steps:

1. **Load the workbook and select the sheet**:
   ```python
   import openpyxl
   wb = openpyxl.load_workbook('inventory.xlsx')
   sheet = wb.active
   ```

2. **Calculate the total inventory value for each product and write it to the new column**:
   ```python
   for row in range(2, sheet.max_row + 1):
       inventory_count = sheet.cell(row=row, column=2).value
       price = sheet.cell(row=row, column=3).value
       total_value = inventory_count * price
       sheet.cell(row=row, column=5).value = total_value
   ```

3. **Save the updated workbook to a new file**:
   ```python
   wb.save('inventory_with_total_value.xlsx')
   ```

This code reads the inventory count and price from the second and third columns of each row, starting from the second row, calculates the total inventory value, and writes it to the fifth column. Finally, it saves the updated workbook to a new file.

**Q6. Explain how to handle exceptions when working with spreadsheets using Python.**

When working with spreadsheets using Python, it is important to handle exceptions to ensure that your program runs smoothly even if unexpected issues arise. Here’s how you can handle exceptions:

1. **Use try-except blocks**:
   ```python
   try:
       # Load the workbook and select the sheet
       wb = openpyxl.load_workbook('inventory.xlsx')
       sheet = wb.active
       
       # Perform operations on the sheet
       for row in range(2, sheet.max_row + 1):
           supplier_name = sheet.cell(row=row, column=4).value
           # Other operations...
           
   except FileNotFoundError:
       print("The specified file does not exist.")
   except openpyxl.utils.exceptions.InvalidFileException:
       print("The file is not a valid Excel file.")
   except Exception as e:
       print(f"An error occurred: {e}")
   ```

2. **Handle specific exceptions**:
   - `FileNotFoundError`: Raised if the specified file does not exist.
   - `InvalidFileException`: Raised if the file is not a valid Excel file.
   - General `Exception`: Catches any other exceptions that might occur.

By using try-except blocks, you can gracefully handle errors and provide meaningful feedback to the user.

**Q7. How would you automate the process of updating a spreadsheet file and saving it programmatically using Python?**

To automate the process of updating a spreadsheet file and saving it programmatically using Python, you can follow these steps:

1. **Load the workbook and select the sheet**:
   ```python
   import openpyxl
   wb = openpyxl.load_workbook('inventory.xlsx')
   sheet = wb.active
   ```

2. **Perform updates on the sheet**:
   ```python
   for row in range(2, sheet.max_row + 1):
       inventory_count = sheet.cell(row=row, column=2).value
       price = sheet.cell(row=row, column=3).value
       total_value = inventory_count * price
       sheet.cell(row=row, column=5).value = total_value
   ```

3. **Save the updated workbook to a new file**:
   ```python
   wb.save('inventory_with_total_value.xlsx')
   ```

This code loads the workbook, performs necessary updates on the sheet, and saves the updated workbook to a new file. Automating this process ensures that the spreadsheet is consistently updated and saved without manual intervention.

**Q8. Discuss recent real-world examples where automated spreadsheet processing was crucial.**

Automated spreadsheet processing has been crucial in various real-world scenarios. One notable example is the handling of financial data during the COVID-19 pandemic. Financial institutions and governments needed to quickly analyze large datasets to understand the economic impact and distribute relief funds efficiently.

For instance, the U.S. Small Business Administration (SBA) used automated scripts to process applications for the Paycheck Protection Program (PPP), which required analyzing thousands of spreadsheet entries to determine eligibility and disburse funds. Automated scripts helped streamline the process, reducing the risk of human error and ensuring timely assistance to businesses.

In another example, healthcare organizations used automated scripts to manage and analyze patient data during the pandemic. These scripts processed large volumes of data from various sources, helping to identify trends and allocate resources effectively.

These examples highlight the importance of automated spreadsheet processing in managing large datasets and making informed decisions quickly.

---
<!-- nav -->
[[05-Understanding Modules, Packages, and Libraries in Python|Understanding Modules, Packages, and Libraries in Python]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/06-Automating Spreadsheet Data Processing With Python/00-Overview|Overview]]
