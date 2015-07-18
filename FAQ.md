# General
## Is Coquery just another concordancer?
In a way, yes. You can use Coquery as a concordancer, and it has a keyword in context (KWIC) view like you would expect from such a program. However, it is much more flexible than most of these tools that I've come across so far.

# Results view
## Can I change the order of the columns in the results view?
Yes, you can: Click on the header of the table column and drag it to the position in the table where you want it to be. For example, if you want to have classic KWIC view, click on the Left_context column, and drag it left of the columns containing the query string items.

## How can I sort the results?
Right-click on the column header that you want to sort by, and select the sorting order from the context menu. You can set the sorting order to Ascending or Descending. For columns containing text strings, you can also choose reverse sorting. In this way, you can choose more than one column in sorting. If you do so, a number in parenthesis will indicate the sequence in which the columns are considered, from first to last.

##Is there a way to highlight columns?
Yes, there is. Open the context menu for a column by right-clicking on the header, select Choose color..., and pick the text color for the values of that column.

# Filters
## Why does the color of the filter box change to yellow if I want to add a filter?
A yellow edit box indicates that there is something wrong with your filter. Make sure that you first enter the display name by which you want to filter (e.g. 'genre'), then a valid filter operator (e.g. 'is'), and then a valid value (e.g. 'ACAD'). The string that you would have to enter would be: genre is ACAD.
Only those display names can be chosen that are also shown in the output column tree above the filter box.

## Why isn't the filter that I have entered considered in the query?
Did you press the Enter key after you have typed in the filter text, and does your filter text appear as a little tag above the filter box? Only those texts are considered in the query that appear as filter tags.

## How do I remove a filter?
Simply click on the little 'x' symbol on the right-hand side of the filter tag.
How are the filters evaluated if there is more than one?
The filters in Coquery are additive filters: only those query results are used that match every single filter. This also means that the order in which they were entered does not matter.