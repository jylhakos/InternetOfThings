To debug a Python script in Visual Studio, follow these steps:

1. Initial Setup

Install Python Workload: Ensure the "Python development" workload is installed via the Visual Studio Installer. This provides the necessary Python support and debugging tools.
Open Your File: You can debug a standalone .py file without creating a project by simply opening it in Visual Studio.

2. Set Breakpoints
Insert Breakpoint: Click in the left margin (the "gutter") next to a line number, or press F9 while the cursor is on that line. A red dot will appear, indicating where execution will pause.
Conditional Breakpoints: To pause only when a specific condition is met, right-click a red breakpoint dot and select Conditions. You can enter an expression (e.g., i > 100).

3. Start Debugging
Launch Debugger: Press F5 or select Debug > Start Debugging from the top menu. The script will run until it hits a breakpoint or an error.

Select Environment: Visual Studio typically uses your global default Python environment. 

4. Use Debugging Tools

Inspect Variables: Use the Locals window to see all variables in the current scope, or hover your mouse over a variable in the editor to see its value.

Call Stack: Use the Call Stack window to see the sequence of function calls that led to the current line.

References

Debug your Python code in Visual Studio https://learn.microsoft.com/en-us/visualstudio/python/debugging-python-in-visual-studio?view=visualstudio

Tutorial: Run code in the Visual Studio Debugger https://learn.microsoft.com/en-us/visualstudio/python/tutorial-working-with-python-in-visual-studio-step-04-debugging?view=visualstudio


