# Excel Interview Transcript - Intermediate Level
**Candidate:** Michael Rodriguez  
**Date:** 2024-01-20  
**Duration:** 42 minutes  
**Final Score:** 78/100  
**Performance Level:** Intermediate

## Interview Flow

**Interviewer:** Hello! I'm your Excel interviewer today. I'll be conducting a comprehensive assessment of your Excel skills across various areas including formulas, data analysis, and chart creation. The interview will take approximately 30-45 minutes and will progressively increase in difficulty based on your responses. Please answer as thoroughly as possible and feel free to explain your reasoning. Let's start with a brief introduction: Could you tell me about your experience with Excel and what you consider your strongest Excel skills?

**Michael:** Hi there! I've been using Excel for about 4 years in my role as a data analyst. I'm pretty comfortable with most common functions like VLOOKUP, INDEX/MATCH, and various IF statements. I also work with pivot tables regularly and have some experience with conditional formatting. I'd say my strongest areas are probably data manipulation and creating reports for management.

**Interviewer:** Excellent background! Let's start with cell references. Can you explain the difference between A1, $A1, A$1, and $A$1?

**Michael:** Sure! A1 is a relative reference - both the column and row will change when you copy the formula. $A1 has an absolute column but relative row, so the A stays fixed but the row number changes. A$1 is the opposite - relative column but absolute row. And $A$1 is fully absolute - neither the column nor row changes when copied. This is really useful for referencing fixed values like tax rates or lookup tables.

**Interviewer:** Perfect explanation! Now, let's say you have a large dataset and need to use VLOOKUP, but you're concerned about performance. What alternatives might you consider?

**Michael:** Great question! INDEX/MATCH is usually my go-to alternative. It's more flexible because you can lookup values to the left of your lookup column, and it's generally faster for large datasets. The syntax would be =INDEX(return_range, MATCH(lookup_value, lookup_range, 0)). I also know that XLOOKUP is available in newer versions of Excel, which combines the best of both VLOOKUP and INDEX/MATCH, but I haven't used it much since my company is still on Excel 2019.

**Interviewer:** Excellent knowledge of lookup functions! Let me test your nested IF skills. How would you create a grading formula that assigns: A for 90+, B for 80-89, C for 70-79, D for 60-69, and F for below 60?

**Michael:** I would use nested IF statements. Let me work through this: =IF(B2>=90,"A",IF(B2>=80,"B",IF(B2>=70,"C",IF(B2>=60,"D","F")))). I nest them from highest to lowest grade so that it checks each condition in order. Once it finds a TRUE condition, it stops checking the rest.

**Interviewer:** Spot on! Now let's talk about pivot tables. You mentioned you use them regularly. How would you modify a pivot table to show both count and percentage of total sales by region?

**Michael:** For that, I'd drag the Sales field into the Values area twice. The first instance I'd keep as Sum of Sales, and the second I'd change to show as "% of Grand Total" by right-clicking and going to "Show Values As." If I also wanted count, I could add a third instance of any field and change it to Count. I'd also make sure to format the percentage field appropriately so it's easy to read.

**Interviewer:** Very thorough answer! Let's move to a practical scenario. You have a dataset with columns: Employee Name (A), Department (B), Hire Date (C), Salary (D), Performance Rating 1-5 (E). Data spans rows 2-101. Give me formulas for: 1) Average salary by department, 2) Count of employees with rating 4 or 5, 3) Highest salary in Sales department.

**Michael:** Okay, let me work through each one:

1) For average salary by department, I'd use AVERAGEIF: =AVERAGEIF(B2:B101,"Sales",D2:D101) for Sales specifically, or create a summary table with all departments.

2) For counting employees with rating 4 or 5: =COUNTIFS(E2:E101,">=4") would work, or I could be more explicit with =COUNTIF(E2:E101,4)+COUNTIF(E2:E101,5)

3) For highest salary in Sales: =MAXIFS(D2:D101,B2:B101,"Sales") - this finds the maximum salary where the department equals "Sales."

**Interviewer:** Excellent use of the IFS functions! Those are more efficient than array formulas. Now, let's talk about error handling. How would you modify a VLOOKUP to handle cases where the lookup value isn't found?

**Michael:** I'd wrap it in an IFERROR function: =IFERROR(VLOOKUP(lookup_value,table_array,col_index,FALSE),"Not Found"). This way if the VLOOKUP returns #N/A, it shows "Not Found" instead. I could also use IFNA specifically for #N/A errors, or customize the error message to be more specific to what the user needs to understand.

**Interviewer:** Perfect error handling! Let's discuss data validation. How would you create a dropdown list that only allows values from a specific range, and what happens if someone tries to type an invalid value?

**Michael:** I'd select the cells where I want the dropdown, go to Data > Data Validation, choose "List" as the validation criteria, and then specify my source range - either by typing the range like A1:A10 or by referencing a named range. Excel will show a dropdown arrow and only allow values from that list. If someone tries to type something else, Excel will show an error dialog and reject the entry unless I've unchecked the "Show error alert" option. I can also customize the error message to be more user-friendly.

**Interviewer:** Great understanding of data validation! Final question: You need to create a dynamic chart that automatically updates when new data is added to your dataset. How would you approach this?

**Michael:** I'd create the chart using an Excel Table (Ctrl+T) instead of a regular range. When data is added to an Excel Table, charts based on that table automatically expand to include the new data. Alternatively, I could use dynamic named ranges with OFFSET and COUNTA functions, but the Table approach is cleaner and easier to maintain. I'd also make sure to use descriptive chart titles and labels so the chart is self-explanatory for other users.

**Interviewer:** Excellent answer! That concludes our Excel interview. Thank you for your detailed responses, Michael.

## Performance Analysis

**Strengths:**
- Strong understanding of cell reference types and their applications
- Excellent knowledge of lookup functions including performance considerations
- Solid grasp of nested formulas and logical functions
- Good working knowledge of pivot tables and data analysis
- Understands error handling and data validation concepts
- Shows awareness of Excel Tables and dynamic ranges
- Practical, real-world approach to problem-solving

**Areas for Improvement:**
- Could explore more advanced array formulas and dynamic arrays
- Limited experience with newer Excel functions (XLOOKUP, etc.)
- Could benefit from learning Power Query for more complex data transformations
- Opportunity to learn more advanced charting and dashboard techniques

**Recommendations:**
1. Explore Excel's newer dynamic array functions (FILTER, SORT, UNIQUE)
2. Learn Power Query for advanced data manipulation and automation
3. Practice with more complex nested formulas and array operations
4. Study advanced charting techniques and interactive dashboards
5. Consider learning VBA for process automation
6. Explore Power Pivot for handling larger datasets

**Overall Assessment:**  
Michael demonstrates solid intermediate Excel skills with good practical knowledge. He understands core concepts well and can handle most common business scenarios. With some additional training on advanced features, he could easily move to an advanced skill level.
